# CODEBASE OVERVIEW

## Project Purpose

This repository contains **Metro Bus 360**, a transit simulation and management platform. The system combines:

- A FastAPI backend for simulation, APIs, and real-time updates
- Web dashboards for riders and admins
- A React Native mobile app for map and service access
- Journey planning and e-ticket capabilities

The core goal is to provide a centralized environment for bus operations visibility, route control, trip planning, and passenger-facing ticketing.

## Top-Level Structure

```text
/home/muhammad/Desktop/FYP
├── main.py
├── bus_simulator.py
├── database_manager.py
├── models.py
├── journey_planner.py
├── admin_endpoints.py
├── eticket_endpoints.py
├── web_template.html
├── admin_dashboard.html
├── requirements.txt
├── schema.sql
├── metro_simulation.db
├── eticket_users.json
├── mobile/
│   └── MetroBusApp073/
├── README.md
├── venv/
└── __pycache__/
```

## Technology Stack

### Backend
- **Language:** Python
- **Framework:** FastAPI (with Starlette components)
- **Server:** Uvicorn
- **Validation:** Pydantic
- **Persistence:** SQLite (`metro_simulation.db`) + JSON file storage (`eticket_users.json`)
- **Realtime:** WebSocket endpoint for live tracking
- **Mapping/Geo:** Geospatial utilities (including `geopy` usage in simulation-related logic)

### Web Frontend
- Static HTML/CSS/JavaScript pages
- Leaflet/OpenStreetMap-based map rendering
- REST + WebSocket communication with backend

### Mobile
- React Native (TypeScript)
- WebView-based map embedding + REST fetch/axios calls
- Jest scaffold for testing

### Tooling
- Python dependency management via `pip` and `requirements.txt`
- Node/npm for mobile app (`package.json`, `package-lock.json`)

## Core Architecture

The system is organized as a **single-process backend monolith** where simulation, API serving, and periodic broadcast tasks run together.

### Primary Runtime Boundary
- `main.py` is the main orchestrator:
  - Application startup/shutdown lifecycle
  - Route registration
  - Static page serving (`/map`, `/admin`)
  - WebSocket broadcasting loop
  - Initialization of simulator and supporting modules

### Simulation Layer
- `bus_simulator.py` contains simulation engine behavior:
  - Route loading
  - Traffic segment handling
  - ETA prediction
  - Bus movement, dwell logic, direction switching
  - Active route scheduling

- `models.py` defines core simulation dataclasses:
  - `Stop`
  - `Route`
  - `Bus`

### Data/Persistence Layer
- `database_manager.py`:
  - Initializes schema/tables
  - Seeds routes and stops
  - Stores/loads bus and route information

- `schema.sql`: DB bootstrap reference
- `metro_simulation.db`: local runtime database

### Journey Planning Layer
- `journey_planner.py`:
  - Graph-based planning logic (transfer-aware route search)
  - Nearby-stop matching and ranked route options
  - User-oriented instructions/summary generation

### Ticketing Layer
- `eticket_endpoints.py`:
  - Signup/login
  - Wallet top-up
  - Ticket purchase flow
  - JSON-file persistence for user accounts

### Admin and Analytics Layer
- `admin_endpoints.py`:
  - Broad admin API surface (stats, announcements, operational controls)
- Supporting modules include:
  - `driver_management.py`
  - `rush_hour_analytics.py`
  - `performance_analytics.py`
  - `alert_management.py`
  - `multi_route_management.py`
  - `agent_behavior_monitoring.py`
  - `system_usage_statistics.py`

## Key Files and Responsibilities

- `main.py` - App entrypoint, lifecycle wiring, endpoint aggregation, websocket broadcaster
- `bus_simulator.py` - Core simulation behavior and update loop
- `database_manager.py` - SQLite setup, route/stop data, bus persistence APIs
- `models.py` - Transit entities and movement primitives
- `journey_planner.py` - Multi-route pathfinding and transfer planning
- `admin_endpoints.py` - Admin API domains and orchestration points
- `eticket_endpoints.py` - E-ticket API handlers
- `web_template.html` - Main rider-facing web map and controls
- `admin_dashboard.html` - Admin dashboard interface
- `mobile/MetroBusApp073/App.tsx` - Mobile app entry
- `mobile/MetroBusApp073/src/config/api.ts` - Mobile API base URL/endpoints
- `mobile/MetroBusApp073/src/services/ApiServices.ts` - Mobile API service wrappers
- `mobile/MetroBusApp073/src/screens/MapScreen.tsx` - Main mobile map and service interaction screen

## Component Interaction and Data Flow

### 1) Startup and Initialization
1. `main.py` starts FastAPI app.
2. DB setup and simulator initialization run in lifecycle startup.
3. Route and stop data are loaded from SQLite.
4. Background tasks for simulation updates and websocket broadcasts begin.

### 2) Live Tracking Flow
1. Simulator updates bus states periodically.
2. Current bus snapshots are exposed via REST and WebSocket.
3. Web UI and admin dashboard subscribe to websocket stream.
4. Mobile app consumes REST endpoints (and can integrate websocket service).

### 3) Route Control Flow
1. Client calls route activation/deactivation endpoints.
2. Backend updates simulator active-route state.
3. Bus schedule/activity changes become visible in API responses and websocket updates.

### 4) Journey Planning Flow
1. Client sends journey query (coordinates/stops/preferences).
2. Planner searches graph with transfer handling.
3. Backend returns ranked route options with travel instructions.

### 5) E-Ticket Flow
1. User account created/authenticated via e-ticket endpoints.
2. Wallet top-up updates JSON state.
3. Ticket purchase validates balance and service conditions.
4. Updated ticket/account state is returned to client.

## Folder-Level Notes

### Root Backend
Contains most server modules, HTML dashboards, DB artifacts, and documentation in one location.

### `mobile/MetroBusApp073`
Contains the React Native app with:
- Screens for map/admin/auth flows
- Service and config layers
- Native Android/iOS project scaffolding

### `venv` and `__pycache__`
Environment/cache artifacts are present inside repository workspace.

## Developer Workflow

### Backend
- Install dependencies:
  - `pip install -r requirements.txt`
- Run server:
  - `python main.py`
  - or `uvicorn main:app --reload`
- API docs:
  - `/docs` (FastAPI OpenAPI UI)

### Mobile
- `cd mobile/MetroBusApp073`
- `npm install`
- `npm start`
- `npm run android` (or iOS equivalent if configured)

## Architectural Patterns and Decisions

- **Monolithic runtime design:** Simulation and API hosted in one process.
- **Mixed concurrency model:** Async FastAPI + threaded/background simulation behavior.
- **Feature layering over time:** Multiple modules indicate iterative additions, sometimes with overlapping concerns.
- **Hybrid persistence:** SQL for transit data + JSON for ticket users.
- **Global module wiring:** Some admin subsystems rely on globals injected at startup.

## Notable Risks and Gaps

- E-ticket credentials appear to be handled in plaintext flows (security concern).
- E-ticket functionality appears in both dedicated module and additional definitions in `main.py` (duplication risk).
- CORS is permissive in current backend setup.
- Some admin/analytics modules may be only partially wired at runtime.
- Local environment/runtime artifacts (`venv`, database, caches, temporary files) are tracked in project workspace.
- Mobile API hosts include hardcoded/local-network values, requiring per-environment adjustment.

## Suggested Improvement Directions

1. Consolidate duplicated endpoint logic (especially e-ticket routes) into a single authoritative module.
2. Introduce secure password hashing and stronger auth/session controls.
3. Separate runtime layers more cleanly (API, simulation worker, analytics services) if scale increases.
4. Normalize mobile networking config via environment-based build configs.
5. Add comprehensive automated tests for backend API contracts and planner/simulator behavior.
6. Tighten dependency list in `requirements.txt` to only required runtime packages.

## Current System Understanding Confidence

High confidence on the core backend simulation/API/web/mobile structure and interactions.

Moderate confidence on full admin analytics integration depth, because those modules are large and some wiring appears conditional or incomplete in startup initialization.
