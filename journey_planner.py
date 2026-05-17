#!/usr/bin/env python3
"""
Metro Bus 360 - Journey Planner

Core rules:
- Fare = 3 Rs per kilometer
- Distances are computed from route stop coordinates
- Supports stop-to-stop and location-to-location planning
- Ranking preferences: time | money | hybrid
"""

import math
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)
DEBUG_LOG_PATH = "/home/muhammad/Desktop/FYP/.cursor/debug-a6bc00.log"


def _agent_debug_log(location: str, message: str, data: Dict, run_id: str, hypothesis_id: str):
    try:
        payload = {
            "sessionId": "a6bc00",
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass

# ─────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────
FARE_PER_KM = 3.0
DEFAULT_BUS_SPEED = 40.0
WALKING_SPEED = 4.5
TRANSFER_WALK_MAX = 0.5
NEARBY_STOP_RADIUS = 2.0
NEARBY_STOP_EXPAND = 5.0
TRANSFER_WAIT_MIN = 3.0


# ─────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────
@dataclass
class Segment:
    route_id: str
    route_name: str
    board_stop: str
    board_lat: float
    board_lng: float
    board_idx: int
    alight_stop: str
    alight_lat: float
    alight_lng: float
    alight_idx: int
    distance_km: float
    travel_min: float
    fare: float
    direction: str

@dataclass
class Journey:
    segments: List[Segment]
    total_time_min: float
    total_fare: float
    total_distance_km: float
    transfers: int
    score: float
    journey_id: str
    origin_walk_km: float = 0.0
    origin_walk_min: float = 0.0
    destination_walk_km: float = 0.0
    destination_walk_min: float = 0.0
    nearest_origin_stop: Optional[str] = None
    nearest_destination_stop: Optional[str] = None


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def haversine(lat1, lng1, lat2, lng2) -> float:
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def route_distance_km(route, start_idx: int, end_idx: int) -> float:
    lo, hi = min(start_idx, end_idx), max(start_idx, end_idx)
    total = 0.0
    for i in range(lo, hi):
        total += haversine(
            route.stops[i].latitude,  route.stops[i].longitude,
            route.stops[i+1].latitude, route.stops[i+1].longitude
        )
    return total


def get_bus_speed(simulator, route_id: str) -> float:
    speeds = [
        b.speed for b in simulator.buses.values()
        if b.route_id == route_id and b.speed > 5
    ]
    return sum(speeds) / len(speeds) if speeds else DEFAULT_BUS_SPEED


class IntelligentConnectionBuilder:

    def __init__(self, simulator, db_manager):
        self.simulator = simulator
        self.db_manager = db_manager
        self.transfer_points_cache = {}
        self.max_transfers = 3
        self.max_walking_distance_km = TRANSFER_WALK_MAX
        self.transfer_buffer_minutes = TRANSFER_WAIT_MIN
        self._jid_counter = 0
        self._build_transfer_index()

    def _build_transfer_index(self):
        self.transfer_index: Dict[str, Dict[str, List[Tuple[int,int]]]] = {}
        routes = list(self.simulator.routes.items())
        for i, (r1_id, r1) in enumerate(routes):
            for j, (r2_id, r2) in enumerate(routes):
                if r1_id >= r2_id:
                    continue
                for s1i, s1 in enumerate(r1.stops):
                    for s2i, s2 in enumerate(r2.stops):
                        d = haversine(s1.latitude, s1.longitude,
                                      s2.latitude, s2.longitude)
                        if d <= TRANSFER_WALK_MAX:
                            self.transfer_index.setdefault(r1_id, {}).setdefault(r2_id, []).append((s1i, s2i))
                            self.transfer_index.setdefault(r2_id, {}).setdefault(r1_id, []).append((s2i, s1i))
        logger.info(f"Transfer index built for {len(self.transfer_index)} routes")

    def _find_nearby_stops(self, lat: float, lng: float, radius: float = NEARBY_STOP_RADIUS) -> List[Dict]:
        hits = []
        for route_id, route in self.simulator.routes.items():
            for idx, stop in enumerate(route.stops):
                d = haversine(lat, lng, stop.latitude, stop.longitude)
                if d <= radius:
                    hits.append({
                        'route_id': route_id,
                        'stop_idx': idx,
                        'stop_name': stop.name,
                        'latitude': stop.latitude,
                        'longitude': stop.longitude,
                        'distance_km': d,
                        'walk_min': (d / WALKING_SPEED) * 60
                    })
        if not hits and radius < NEARBY_STOP_EXPAND:
            return self._find_nearby_stops(lat, lng, NEARBY_STOP_EXPAND)
        hits.sort(key=lambda x: x['distance_km'])
        return hits

    def _find_stops_by_name(self, name: str) -> List[Dict]:
        hits = []
        for route_id, route in self.simulator.routes.items():
            for idx, stop in enumerate(route.stops):
                if stop.name.strip().lower() == name.strip().lower():
                    hits.append({
                        'route_id': route_id,
                        'stop_idx': idx,
                        'stop_name': stop.name,
                        'latitude': stop.latitude,
                        'longitude': stop.longitude,
                        'distance_km': 0.0,
                        'walk_min': 0.0
                    })
        return hits

    def _make_segment(self, route_id: str, from_idx: int, to_idx: int) -> Optional[Segment]:
        route = self.simulator.routes.get(route_id)
        if not route or from_idx == to_idx:
            return None
        stops = route.stops
        if from_idx < 0 or to_idx < 0 or from_idx >= len(stops) or to_idx >= len(stops):
            return None

        dist_km = route_distance_km(route, from_idx, to_idx)
        speed = get_bus_speed(self.simulator, route_id)
        travel_min = (dist_km / speed) * 60
        fare = round(dist_km * FARE_PER_KM, 2)
        direction = 'forward' if to_idx > from_idx else 'reverse'

        return Segment(
            route_id=route_id,
            route_name=route.name,
            board_stop=stops[from_idx].name,
            board_lat=stops[from_idx].latitude,
            board_lng=stops[from_idx].longitude,
            board_idx=from_idx,
            alight_stop = stops[to_idx].name,
            alight_lat=stops[to_idx].latitude,
            alight_lng=stops[to_idx].longitude,
            alight_idx=to_idx,
            distance_km=round(dist_km, 3),
            travel_min=round(travel_min, 2),
            fare=fare,
            direction=direction
        )

    def _score(self, journey: Journey, preference: str) -> float:
        if preference == 'time':
            return journey.total_time_min + (journey.transfers * 8.0)
        if preference == 'money':
            return journey.total_fare + (journey.transfers * 5.0) + (journey.total_time_min * 0.05)
        return (journey.total_time_min * 0.55) + (journey.total_fare * 0.35) + (journey.transfers * 4.0)

    def _next_journey_id(self) -> str:
        self._jid_counter += 1
        return f"jp_{self._jid_counter}"

    def _route_signature(self, journey: Journey) -> tuple:
        return tuple((s.route_id, s.board_idx, s.alight_idx) for s in journey.segments)

    def _rank_and_trim(self, journeys: List[Journey], preference: str) -> List[Journey]:
        for journey in journeys:
            journey.score = round(self._score(journey, preference), 5)
        journeys.sort(key=lambda j: (j.score, j.transfers, j.total_time_min, j.total_fare))
        unique = []
        seen = set()
        for journey in journeys:
            sig = self._route_signature(journey)
            if sig not in seen:
                seen.add(sig)
                unique.append(journey)
        return unique[:5]

    def _build_direct_journeys(self, origin_stops: List[Dict], dest_stops: List[Dict]) -> List[Journey]:
        journeys: List[Journey] = []
        dest_by_route = {}
        for d in dest_stops:
            dest_by_route.setdefault(d['route_id'], []).append(d)
        for origin in origin_stops:
            route_id = origin['route_id']
            for dest in dest_by_route.get(route_id, []):
                if origin['stop_idx'] == dest['stop_idx']:
                    continue
                segment = self._make_segment(route_id, origin['stop_idx'], dest['stop_idx'])
                if not segment:
                    continue
                journeys.append(Journey(
                    segments=[segment],
                    total_time_min=round(segment.travel_min, 2),
                    total_fare=round(segment.fare, 2),
                    total_distance_km=round(segment.distance_km, 3),
                    transfers=0,
                    score=0.0,
                    journey_id=self._next_journey_id()
                ))
        return journeys

    def _build_one_transfer_journeys(self, origin_stops: List[Dict], dest_stops: List[Dict]) -> List[Journey]:
        journeys: List[Journey] = []
        dest_by_route = {}
        for d in dest_stops:
            dest_by_route.setdefault(d['route_id'], []).append(d)

        for origin in origin_stops:
            r1_id = origin['route_id']
            transfer_routes = self.transfer_index.get(r1_id, {})
            for r2_id, pairs in transfer_routes.items():
                if r1_id == r2_id:
                    continue
                possible_destinations = dest_by_route.get(r2_id, [])
                if not possible_destinations:
                    continue

                for s1_idx, s2_idx in pairs:
                    if s1_idx == origin['stop_idx']:
                        continue
                    leg1 = self._make_segment(r1_id, origin['stop_idx'], s1_idx)
                    if not leg1:
                        continue

                    r1 = self.simulator.routes.get(r1_id)
                    r2 = self.simulator.routes.get(r2_id)
                    if not r1 or not r2 or s2_idx >= len(r2.stops):
                        continue
                    transfer_walk_km = haversine(
                        r1.stops[s1_idx].latitude, r1.stops[s1_idx].longitude,
                        r2.stops[s2_idx].latitude, r2.stops[s2_idx].longitude
                    )
                    transfer_walk_min = (transfer_walk_km / WALKING_SPEED) * 60 + TRANSFER_WAIT_MIN

                    for dest in possible_destinations:
                        if s2_idx == dest['stop_idx']:
                            continue
                        leg2 = self._make_segment(r2_id, s2_idx, dest['stop_idx'])
                        if not leg2:
                            continue
                        total_time = leg1.travel_min + transfer_walk_min + leg2.travel_min
                        total_fare = leg1.fare + leg2.fare
                        total_distance = leg1.distance_km + transfer_walk_km + leg2.distance_km
                        journeys.append(Journey(
                            segments=[leg1, leg2],
                            total_time_min=round(total_time, 2),
                            total_fare=round(total_fare, 2),
                            total_distance_km=round(total_distance, 3),
                            transfers=1,
                            score=0.0,
                            journey_id=self._next_journey_id()
                        ))
        return journeys

    def _apply_location_walks(self, journeys: List[Journey], origin_nearest: Dict, dest_nearest: Dict) -> None:
        for journey in journeys:
            journey.origin_walk_km = round(origin_nearest['distance_km'], 3)
            journey.origin_walk_min = round(origin_nearest['walk_min'], 2)
            journey.destination_walk_km = round(dest_nearest['distance_km'], 3)
            journey.destination_walk_min = round(dest_nearest['walk_min'], 2)
            journey.nearest_origin_stop = origin_nearest['stop_name']
            journey.nearest_destination_stop = dest_nearest['stop_name']
            journey.total_time_min = round(
                journey.total_time_min + journey.origin_walk_min + journey.destination_walk_min, 2
            )

    async def plan_journey(self,
                           origin_lat: float,
                           origin_lng: float,
                           dest_lat: float,
                           dest_lng: float,
                           max_transfers: int = 2,
                           preference: str = 'hybrid',
                           departure_time=None,
                           preferences: Dict = None) -> List[Journey]:
        _agent_debug_log(
            location="journey_planner.py:plan_journey:entry",
            message="Location journey planning started",
            data={
                "origin_lat": origin_lat,
                "origin_lng": origin_lng,
                "dest_lat": dest_lat,
                "dest_lng": dest_lng,
                "max_transfers": max_transfers,
                "preference": preference
            },
            run_id="run1",
            hypothesis_id="H3"
        )
        if preferences:
            max_transfers = preferences.get('max_transfers', max_transfers)
            preference = preferences.get('preference', preference)
        preference = (preference or 'hybrid').lower()
        if preference not in ('time', 'money', 'hybrid'):
            preference = 'hybrid'

        origin_nearby = self._find_nearby_stops(origin_lat, origin_lng)
        dest_nearby = self._find_nearby_stops(dest_lat, dest_lng)
        _agent_debug_log(
            location="journey_planner.py:plan_journey:nearby",
            message="Nearby stops lookup complete",
            data={"origin_nearby_count": len(origin_nearby), "dest_nearby_count": len(dest_nearby)},
            run_id="run1",
            hypothesis_id="H5"
        )
        if not origin_nearby or not dest_nearby:
            return []
        origin_nearest = origin_nearby[0]
        dest_nearest = dest_nearby[0]

        journeys = await self.plan_journey_by_stops(
            origin_name=origin_nearest['stop_name'],
            dest_name=dest_nearest['stop_name'],
            max_transfers=max_transfers,
            preference=preference
        )
        self._apply_location_walks(journeys, origin_nearest, dest_nearest)
        _agent_debug_log(
            location="journey_planner.py:plan_journey:result",
            message="Location journey planning completed",
            data={"journey_count_before_rank": len(journeys)},
            run_id="run1",
            hypothesis_id="H3"
        )
        return self._rank_and_trim(journeys, preference)

    def get_journey_summary(self, journey: Journey) -> Dict:
        segments = []
        route_names = []
        for seg in journey.segments:
            if seg.route_name not in route_names:
                route_names.append(seg.route_name)
            segments.append({
                'route_id': seg.route_id,
                'route_name': seg.route_name,
                'direction': seg.direction,
                'board_stop': seg.board_stop,
                'board_location': [seg.board_lat, seg.board_lng],
                'alight_stop': seg.alight_stop,
                'alight_location': [seg.alight_lat, seg.alight_lng],
                'distance_km': seg.distance_km,
                'travel_min': seg.travel_min,
                'fare_rs': seg.fare,
            })

        instructions = []
        step_no = 1
        if journey.origin_walk_min > 0:
            instructions.append({
                'step': step_no,
                'type': 'walk',
                'instruction': f"Walk {journey.origin_walk_km:.2f} km (~{round(journey.origin_walk_min)} min) to {journey.nearest_origin_stop}."
            })
            step_no += 1

        for idx, seg in enumerate(journey.segments):
            instructions.append({
                'step': step_no,
                'type': 'board',
                'instruction': f"Board {seg.route_id} at {seg.board_stop} ({seg.direction})."
            })
            step_no += 1
            instructions.append({
                'step': step_no,
                'type': 'travel',
                'instruction': f"Ride to {seg.alight_stop} ({seg.distance_km:.2f} km, ~{round(seg.travel_min)} min, Rs {seg.fare:.2f})."
            })
            step_no += 1
            if idx < len(journey.segments) - 1:
                nxt = journey.segments[idx + 1]
                instructions.append({
                    'step': step_no,
                    'type': 'transfer',
                    'instruction': f"Transfer to {nxt.route_id} at/near {nxt.board_stop}."
                })
                step_no += 1

        if journey.destination_walk_min > 0:
            instructions.append({
                'step': step_no,
                'type': 'walk',
                'instruction': f"Walk {journey.destination_walk_km:.2f} km (~{round(journey.destination_walk_min)} min) to your destination."
            })

        return {
            'journey_id': journey.journey_id,
            'route_names': route_names,
            'summary': {
                'transfers_required': journey.transfers,
                'total_distance_km': round(journey.total_distance_km, 3),
                'total_fare_rs': round(journey.total_fare, 2),
                'estimated_total_time_minutes': round(journey.total_time_min, 1),
                'score': round(journey.score, 5),
            },
            'nearest_stops': {
                'origin': {
                    'stop_name': journey.nearest_origin_stop,
                    'walking_distance_km': round(journey.origin_walk_km, 3),
                    'walking_time_minutes': round(journey.origin_walk_min, 2),
                },
                'destination': {
                    'stop_name': journey.nearest_destination_stop,
                    'walking_distance_km': round(journey.destination_walk_km, 3),
                    'walking_time_minutes': round(journey.destination_walk_min, 2),
                }
            },
            'segments': segments,
            'instructions': instructions,
        }

    async def plan_journey_by_stops(self,
                                    origin_name: str,
                                    dest_name: str,
                                    max_transfers: int = 2,
                                    preference: str = 'hybrid') -> List[Journey]:
        _agent_debug_log(
            location="journey_planner.py:plan_journey_by_stops:entry",
            message="Stop-to-stop planning started",
            data={
                "origin_name": origin_name,
                "dest_name": dest_name,
                "max_transfers": max_transfers,
                "preference": preference
            },
            run_id="run1",
            hypothesis_id="H3"
        )
        preference = (preference or 'hybrid').lower()
        if preference not in ('time', 'money', 'hybrid'):
            preference = 'hybrid'
        origin_stops = self._find_stops_by_name(origin_name)
        dest_stops = self._find_stops_by_name(dest_name)
        _agent_debug_log(
            location="journey_planner.py:plan_journey_by_stops:stops",
            message="Stop matches found",
            data={"origin_stops_count": len(origin_stops), "dest_stops_count": len(dest_stops)},
            run_id="run1",
            hypothesis_id="H5"
        )
        if not origin_stops or not dest_stops:
            return []

        journeys = []
        journeys.extend(self._build_direct_journeys(origin_stops, dest_stops))
        if max_transfers > 0:
            journeys.extend(self._build_one_transfer_journeys(origin_stops, dest_stops))
        _agent_debug_log(
            location="journey_planner.py:plan_journey_by_stops:computed",
            message="Raw journey options computed",
            data={"raw_journey_count": len(journeys)},
            run_id="run1",
            hypothesis_id="H3"
        )
        return self._rank_and_trim(journeys, preference)

    def get_all_transfer_points(self) -> List[Dict]:
        seen, points = set(), []
        for r1_id, connections in self.transfer_index.items():
            for r2_id, pairs in connections.items():
                r1 = self.simulator.routes.get(r1_id)
                if not r1:
                    continue
                for (s1i, _) in pairs:
                    key = (r1_id, s1i)
                    if key in seen:
                        continue
                    seen.add(key)
                    stop = r1.stops[s1i]
                    all_routes = [r1_id] + [r for r in connections.keys()]
                    points.append({
                        'stop_id':        f"tp_{r1_id}_{s1i}",
                        'stop_name':      stop.name,
                        'location':       [stop.latitude, stop.longitude],
                        'connected_routes': list(set(all_routes)),
                        'transfer_time_minutes': TRANSFER_WAIT_MIN,
                    })
        return points

    @property
    def transfer_points_cache(self):
        return self._tp_cache

    @transfer_points_cache.setter
    def transfer_points_cache(self, v):
        self._tp_cache = v

    def _get_route_color(self, route_id: str) -> str:
        colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a',
                  '#fee140', '#30cfd0', '#a18cd1', '#fccb90', '#e0c3fc']
        idx = abs(hash(route_id)) % len(colors)
        return colors[idx]

    async def get_real_time_journey_updates(self, journey_id: str) -> Dict:
        return {
            "journey_id": journey_id,
            "status": "tracking_not_available",
            "message": "Real-time journey tracking is not implemented yet."
        }
