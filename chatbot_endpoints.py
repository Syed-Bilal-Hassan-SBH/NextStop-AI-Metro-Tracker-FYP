"""
Metro Bus AI assistant — Groq (OpenAI-compatible) chat API.

Configuration: create a `.env` in the project root (see `.env.example`) with
`GROQ_API_KEY`. Optional `GROQ_CHAT_MODEL` overrides the default model name
(check https://console.groq.com/docs/models for current IDs).

Wired from main.py via get_chatbot_router(), set_dependencies(),
and initialize_chatbot(simulator, db_manager, journey_planner).
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Load `.env` from this file's directory (project root), not from the process cwd —
# otherwise Uvicorn/IDE often start elsewhere and GROQ_API_KEY is never seen.
_PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(_PROJECT_DIR / ".env")
load_dotenv()  # optional: merge cwd `.env` if present

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
# Default: fast Groq chat model; override with GROQ_CHAT_MODEL if renamed upstream.
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
MAX_CONTEXT_MESSAGES = 40
MAX_USER_MESSAGE_LEN = 8000

simulator = None
db_manager = None
journey_planner = None

chatbot_router = APIRouter(prefix="/api/chat", tags=["chat"])


def set_dependencies(sim: Any, db: Any, jp: Any = None) -> None:
    """Inject simulator, database manager, and optional journey planner from main application."""
    global simulator, db_manager, journey_planner
    simulator = sim
    db_manager = db
    journey_planner = jp


def initialize_chatbot(sim: Any, db: Any, jp: Any = None) -> None:
    """Startup hook: same as set_dependencies; tables live in DatabaseManager.init_database."""
    set_dependencies(sim, db, jp)


def _groq_api_key() -> str:
    return (os.environ.get("GROQ_API_KEY") or "").strip()


def _groq_model() -> str:
    return (os.environ.get("GROQ_CHAT_MODEL") or DEFAULT_GROQ_MODEL).strip()


def build_system_prompt() -> str:
    """Ground the model in current simulation context."""
    parts = [
        "You are Metro Assistant for Metro Bus 360: metro bus simulation, live ETAs, "
        "journey planning, and e-tickets.",
        "You have tools that read the SAME live backend as the map and journey planner. "
        "Whenever the user asks about routes, trips between places, which bus to take, "
        "arrivals at a stop, or what is running now, you MUST call the appropriate tool(s) first "
        "and then answer in clear language using ONLY tool results (plus this context). "
        "If a tool returns an error or empty data, explain that honestly.",
        "ETAs are simulated predictions for buses on currently active routes only.",
    ]
    if simulator:
        try:
            active = list(getattr(simulator, "active_routes", []) or [])
            parts.append(
                "Currently active feeder route IDs: "
                + (", ".join(active) if active else "none")
                + "."
            )
            lines: List[str] = []
            for rid in active[:20]:
                route = simulator.routes.get(rid) if hasattr(simulator, "routes") else None
                if route:
                    lines.append(
                        f"- {rid}: {route.name} ({route.source} → {route.destination})"
                    )
            if lines:
                parts.append("Active routes detail:\n" + "\n".join(lines))
        except Exception:
            parts.append("(Simulator context unavailable.)")
    return "\n".join(parts)


_MAX_TOOL_JSON_CHARS = 18000
_MAX_TOOL_ROUNDS = 6


def _coerce_optional_int(val: Any, default: Optional[int]) -> Optional[int]:
    """LLMs often emit numbers as strings; Groq validates tool args before we run code."""
    if val is None or val is False:
        return default
    if isinstance(val, bool):
        return default
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return default
        try:
            return int(s)
        except ValueError:
            return default
    return default


CHAT_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_stops",
            "description": (
                "Search loaded metro stop names. Use when the user names a place and you need "
                "the exact stop name string for journey planning or ETAs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to find inside stop names (case-insensitive).",
                    },
                    "limit": {
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "string"},
                        ],
                        "description": "Max stops to return (default 30).",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plan_journey_between_stops",
            "description": (
                "Plan route options from origin stop to destination stop using the same "
                "journey planner as the map app (supports transfers). Requires stop names "
                "as in the database; call search_stops first if unsure."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "origin_stop": {"type": "string"},
                    "destination_stop": {"type": "string"},
                    "max_transfers": {
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "string"},
                        ],
                        "description": "Max transfers 0–3 (default 2). Integer or digit string.",
                    },
                    "preference": {
                        "type": "string",
                        "enum": ["time", "money", "hybrid"],
                        "description": "Optimise for time, fare, or hybrid.",
                    },
                },
                "required": ["origin_stop", "destination_stop"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "next_buses_at_stop",
            "description": (
                "For buses currently on active routes, estimate minutes until each reaches a "
                "stop whose name contains the given text (simulation ETA). Returns soonest buses."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "stop_name_query": {
                        "type": "string",
                        "description": "Substring of the stop name, e.g. 'Police Foundation'.",
                    },
                    "limit": {
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "string"},
                        ],
                        "description": "Max buses to list (default 8). Integer or digit string.",
                    },
                },
                "required": ["stop_name_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_routes_and_buses",
            "description": "List active route IDs and how many simulated buses are on each.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def _tool_json(data: Any) -> str:
    raw = json.dumps(data, default=str)
    if len(raw) > _MAX_TOOL_JSON_CHARS:
        return raw[: _MAX_TOOL_JSON_CHARS - 80] + "…(truncated)"
    return raw


def _tool_search_stops(query: str, limit: int = 30) -> Dict[str, Any]:
    q = (query or "").strip().lower()
    if not q:
        return {"error": "empty_query"}
    if not simulator or not getattr(simulator, "routes", None):
        return {"error": "simulator_not_available"}
    lim = max(1, min(int(limit or 30), 60))
    hits: List[str] = []
    seen: set = set()
    for route in simulator.routes.values():
        for stop in getattr(route, "stops", []) or []:
            name = getattr(stop, "name", "") or ""
            key = name.strip().lower()
            if not key or key in seen:
                continue
            if q in key:
                seen.add(key)
                hits.append(name)
                if len(hits) >= lim:
                    break
        if len(hits) >= lim:
            break
    return {"matches": hits, "count": len(hits)}


def _tool_active_routes_and_buses() -> Dict[str, Any]:
    if not simulator:
        return {"error": "simulator_not_available"}
    active = list(getattr(simulator, "active_routes", []) or [])
    per_route: Dict[str, int] = {rid: 0 for rid in active}
    for bus in getattr(simulator, "buses", {}).values():
        rid = getattr(bus, "route_id", None)
        if rid in per_route:
            per_route[rid] += 1
    details = []
    for rid in active:
        route = simulator.routes.get(rid)
        details.append(
            {
                "route_id": rid,
                "name": route.name if route else None,
                "terminals": f"{getattr(route, 'source', '')} → {getattr(route, 'destination', '')}"
                if route
                else None,
                "buses_on_route": per_route.get(rid, 0),
            }
        )
    return {
        "active_route_ids": active,
        "routes": details,
        "total_active_buses": sum(per_route.values()),
    }


def _tool_next_buses_at_stop(stop_name_query: str, limit: int = 8) -> Dict[str, Any]:
    q = (stop_name_query or "").strip().lower()
    if not q:
        return {"error": "empty_query"}
    if not simulator or not hasattr(simulator, "get_all_bus_etas"):
        return {"error": "eta_not_available"}
    try:
        all_etas = simulator.get_all_bus_etas()
    except Exception as e:
        return {"error": str(e)[:200]}
    if not all_etas:
        return {
            "message": "No ETAs: either no buses or no active routes. Activate routes in the admin/simulation UI.",
            "arrivals": [],
        }
    lim = max(1, min(int(limit or 8), 20))
    arrivals: List[Dict[str, Any]] = []
    for bus_id, by_stop in all_etas.items():
        bus = simulator.buses.get(bus_id)
        route_id = getattr(bus, "route_id", None) if bus else None
        route = simulator.routes.get(route_id) if route_id else None
        route_name = route.name if route else route_id
        for _idx, info in (by_stop or {}).items():
            if not isinstance(info, dict):
                continue
            sname = (info.get("stop_name") or "").lower()
            if q not in sname:
                continue
            arrivals.append(
                {
                    "bus_id": bus_id,
                    "route_id": route_id,
                    "route_name": route_name,
                    "stop_name": info.get("stop_name"),
                    "eta_minutes": round(float(info.get("eta_minutes", 0)), 1),
                    "eta_datetime": info.get("eta_datetime"),
                }
            )
    arrivals.sort(key=lambda x: x["eta_minutes"])
    return {
        "arrivals": arrivals[:lim],
        "note": "Times are model estimates for the current simulation, not field GPS.",
    }


async def _tool_plan_journey_between_stops(
    origin_stop: str,
    destination_stop: str,
    max_transfers: Any = None,
    preference: Optional[str] = None,
) -> Dict[str, Any]:
    if not journey_planner:
        return {"error": "journey_planner_not_available"}
    o = (origin_stop or "").strip()
    d = (destination_stop or "").strip()
    if not o or not d:
        return {"error": "origin_and_destination_required"}
    mt_raw = _coerce_optional_int(max_transfers, 2)
    mt = 2 if mt_raw is None else max(0, min(mt_raw, 4))
    pref = (preference or "hybrid").lower()
    if pref not in ("time", "money", "hybrid"):
        pref = "hybrid"
    try:
        options = await journey_planner.plan_journey_by_stops(
            origin_name=o,
            dest_name=d,
            max_transfers=mt,
            preference=pref,
        )
    except Exception as e:
        return {"error": str(e)[:400]}
    if not options:
        return {
            "success": False,
            "message": "No journeys found. Try search_stops for exact names or different spelling.",
        }
    summaries = [journey_planner.get_journey_summary(j) for j in options[:5]]
    return {"success": True, "journey_count": len(summaries), "journeys": summaries}


async def _dispatch_chat_tool(name: str, arguments: Dict[str, Any]) -> str:
    try:
        if name == "search_stops":
            lim = _coerce_optional_int(arguments.get("limit"), 30) or 30
            out = _tool_search_stops(str(arguments.get("query", "")), lim)
        elif name == "get_active_routes_and_buses":
            out = _tool_active_routes_and_buses()
        elif name == "next_buses_at_stop":
            lim = _coerce_optional_int(arguments.get("limit"), 8) or 8
            out = _tool_next_buses_at_stop(str(arguments.get("stop_name_query", "")), lim)
        elif name == "plan_journey_between_stops":
            out = await _tool_plan_journey_between_stops(
                str(arguments.get("origin_stop", "")),
                str(arguments.get("destination_stop", "")),
                arguments.get("max_transfers"),
                arguments.get("preference"),
            )
        else:
            out = {"error": f"unknown_tool:{name}"}
    except Exception as e:
        out = {"error": str(e)[:400]}
    return _tool_json(out)


async def _groq_chat_with_tools(api_key: str, messages: List[Dict[str, Any]]) -> str:
    """Multi-turn Groq completion with function calling until the model returns text."""
    conv = list(messages)
    for _ in range(_MAX_TOOL_ROUNDS):
        payload: Dict[str, Any] = {
            "model": _groq_model(),
            "messages": conv,
            "tools": CHAT_TOOLS,
            "tool_choice": "auto",
            "temperature": 0.25,
            "max_tokens": 2048,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0)) as client:
            r = await client.post(
                GROQ_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if r.status_code != 200:
            err = r.text[:800]
            raise HTTPException(status_code=502, detail=f"Groq API error ({r.status_code}): {err}")
        data = r.json()
        try:
            choice0 = data["choices"][0]
            msg = choice0["message"]
        except (KeyError, IndexError, TypeError):
            raise HTTPException(status_code=502, detail="Unexpected Groq response shape.")

        tool_calls = msg.get("tool_calls")
        if tool_calls:
            conv.append(msg)
            for tc in tool_calls:
                try:
                    fn = tc.get("function") or {}
                    fname = fn.get("name") or ""
                    raw_args = fn.get("arguments") or "{}"
                    args = json.loads(raw_args) if isinstance(raw_args, str) else {}
                except json.JSONDecodeError:
                    fname = (tc.get("function") or {}).get("name", "")
                    args = {}
                tid = tc.get("id") or "tool_call"
                result = await _dispatch_chat_tool(fname, args if isinstance(args, dict) else {})
                conv.append({"role": "tool", "tool_call_id": tid, "content": result})
            continue

        text = msg.get("content")
        if isinstance(text, str) and text.strip():
            return text.strip()
        return (
            "I could not generate a reply for that request. "
            "Try asking about a specific trip (origin → destination stops) or a stop name for arrivals."
        )

    return (
        "I reached the tool-call limit for one message. Please narrow your question "
        "(one trip or one stop at a time)."
    )


def _require_db():
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized.")
    return db_manager


class CreateSessionBody(BaseModel):
    user_email: Optional[str] = None
    title: Optional[str] = None


class SendMessageBody(BaseModel):
    content: str = Field(..., min_length=1, max_length=MAX_USER_MESSAGE_LEN)


@chatbot_router.post("/sessions")
async def create_session(body: CreateSessionBody = CreateSessionBody()) -> Dict[str, Any]:
    db = _require_db()
    sid = db.create_chat_session(
        user_email=body.user_email,
        title=body.title,
    )
    sess = db.get_chat_session(sid)
    return {"success": True, "session_id": sid, "created_at": sess["created_at"]}


@chatbot_router.get("/sessions/{session_id}/messages")
async def list_messages(
    session_id: str,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    db = _require_db()
    if not db.get_chat_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    rows = db.get_chat_messages(session_id, limit=limit, offset=offset)
    return {"success": True, "messages": rows}


@chatbot_router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, body: SendMessageBody) -> Dict[str, Any]:
    db = _require_db()
    if not db.get_chat_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")

    api_key = _groq_api_key()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Chat is not configured: set GROQ_API_KEY on the server.",
        )

    db.append_chat_message(session_id, "user", body.content.strip())

    history = db.get_chat_messages(session_id, limit=MAX_CONTEXT_MESSAGES, offset=0)
    api_messages: List[Dict[str, Any]] = [{"role": "system", "content": build_system_prompt()}]
    for m in history:
        if m["role"] in ("user", "assistant"):
            api_messages.append({"role": m["role"], "content": m["content"]})

    try:
        reply_text = await _groq_chat_with_tools(api_key, api_messages)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Model request timed out.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Model error: {str(e)[:400]}")

    aid = db.append_chat_message(session_id, "assistant", reply_text)
    return {
        "success": True,
        "assistant_message": {
            "id": aid,
            "role": "assistant",
            "content": reply_text,
            "created_at": datetime.now().isoformat(),
        },
    }


async def _groq_chat_complete(api_key: str, messages: List[Dict[str, Any]]) -> str:
    """Backward-compatible name: completion with tools."""
    return await _groq_chat_with_tools(api_key, messages)


@chatbot_router.post("/sessions/{session_id}/messages/stream")
async def send_message_stream(session_id: str, body: SendMessageBody):
    """SSE stream of assistant tokens; final DB write after full text is known."""
    db = _require_db()
    if not db.get_chat_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")

    api_key = _groq_api_key()
    if not api_key:

        async def err_gen() -> AsyncIterator[str]:
            yield _sse(
                {
                    "error": "Chat is not configured: set GROQ_API_KEY on the server.",
                    "done": True,
                }
            )

        return StreamingResponse(err_gen(), media_type="text/event-stream")

    db.append_chat_message(session_id, "user", body.content.strip())
    history = db.get_chat_messages(session_id, limit=MAX_CONTEXT_MESSAGES, offset=0)
    api_messages: List[Dict[str, Any]] = [{"role": "system", "content": build_system_prompt()}]
    for m in history:
        if m["role"] in ("user", "assistant"):
            api_messages.append({"role": m["role"], "content": m["content"]})

    async def event_gen() -> AsyncIterator[str]:
        try:
            full = await _groq_chat_with_tools(api_key, api_messages)
            chunk_size = 40
            for i in range(0, len(full), chunk_size):
                piece = full[i : i + chunk_size]
                yield _sse({"token": piece, "done": False})
            aid = db.append_chat_message(session_id, "assistant", full)
            yield _sse(
                {
                    "done": True,
                    "assistant_message": {
                        "id": aid,
                        "role": "assistant",
                        "content": full,
                        "created_at": datetime.now().isoformat(),
                    },
                }
            )
        except httpx.TimeoutException:
            yield _sse({"error": "Model request timed out.", "done": True})
        except HTTPException as he:
            yield _sse({"error": (he.detail or str(he))[:400], "done": True})
        except Exception as e:
            yield _sse({"error": str(e)[:400], "done": True})

    return StreamingResponse(event_gen(), media_type="text/event-stream")


def _sse(obj: Dict[str, Any]) -> str:
    return f"data: {json.dumps(obj)}\n\n"


def get_chatbot_router() -> APIRouter:
    return chatbot_router
