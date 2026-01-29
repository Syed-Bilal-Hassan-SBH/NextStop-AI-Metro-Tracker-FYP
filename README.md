# 🚌 Metro Bus 360 - Intelligent Transit Management System

A state-of-the-art, real-time bidirectional metro bus simulation and management system powered by AI. This platform integrates live tracking, intelligent journey planning, traffic simulation, and comprehensive administrative controls into a unified solution.

## � Key Systems & Features

### 🌐 Core Simulation Engine (`bus_simulator.py`)
- **Bidirectional Service**: Simultaneous forward and reverse bus operations on all routes.
- **High-Fidelity Simulation**: Supports up to **10 buses per route** with alternating terminal departures every 10 seconds.
- **Traffic Intelligence**: Real-time traffic segment simulation with dynamic congestion levels (Free Flow, Moderate, Heavy) affecting bus speeds.
- **AI-Powered ETA**: Machine learning-based `AIETAPredictor` that continuously refines arrival times based on traffic, distance, and historical data.

### 🧠 Intelligent Journey Planning (`journey_planner.py`)
- **Multi-Route Planning**: Finds optimal paths using **A* Algorithm** and graph-based transfer logic.
- **Smart Transfers**: Automatically identifies optimal transfer points between intersecting routes.
- **Holistic Scoring**: Ranks journeys based on time, cost, walking distance, number of transfers, and even **carbon footprint**.
- **Real-Time Accuracy**: Plans are generated using live bus positions and traffic delays, not just static schedules.

### 👮 Administrator Dashboard (`admin_endpoints.py` & `multi_route_management.py`)
- **Fleet Management**: Real-time monitoring of "Healthy", "Warning", and "Critical" status fleets.
- **Driver Management**: Rostering, shift assignment, and performance tracking (on-time rates, passenger feedback).
- **Route Controls**: Dynamic activation/deactivation of routes, maintenance mode toggles.
- **Crisis Management**: "Deploy Spare Bus" capability for rush hour or emergency demand.
- **Broadcast System**: Send system-wide announcements to all connected clients via WebSockets.

### 📱 Mobile Application (React Native)
- **Cross-Platform**: Built with React Native and TypeScript for iOS and Android.
- **Live Tracking**: Real-time bus movement on interactive maps.
- **Journey Planner**: Native interface for planning trips and viewing step-by-step navigation.

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Uvicorn (ASGI)
- **Real-time**: WebSockets (Broadcasts updates every 3s)
- **Database**: SQLite with `database_manager.py` (DAL)
- **Geospatial**: `geopy` for distance calculations

### Frontend (Web)
- **Map Engine**: Leaflet.js with OpenStreetMap tiles
- **UI**: Custom HTML5/CSS3 with linear gradient aesthetics and responsive design
- **Interaction**: Dynamic DOM updates via WebSocket payloads

### Mobile
- **Framework**: React Native
- **Language**: TypeScript
- **Testing**: Jest (Unit testing infrastructure present)

---

## � Project Structure

```
METRO-BUS-SYSTEM/
├── main.py                     # 🚀 Application Entry Point & API/WS Router
├── bus_simulator.py            # 🚌 Core Logic (Movement, Traffic, ETA AI)
├── journey_planner.py          # 🗺️ A* Journey Finding & Transfer Logic
├── admin_endpoints.py          # 👮 Admin API (Stats, Alerts, Drivers)
├── multi_route_management.py   # 🚦 Route Lifecycle & Performance Metrics
├── database_manager.py         # 💾 SQLite Data Access Layer
├── map_visualizer.py           # 🌍 Static Map Utilities (Folium)
├── web_template.html           # 🖥️ Web Interface Template
├── metro_simulation.db         # 🗄️ Database File
├── requirements.txt            # 📦 Python Dependencies
└── mobile/                     # � React Native Application
    └── MetroBusApp/            #    Mobile Source Code
```

---

## ⚡ Quick Start

### 1. Backend Setup

**Prerequisites**: Python 3.8+

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The system will initialize:
1.  **Database**: Auto-create `metro_simulation.db` and seed routes/stops.
2.  **Simulation**: Start background threads for bus movement and traffic.
3.  **Server**: Listen on `http://localhost:8000`.

### 2. Accessing Interfaces

-   **Live Web Map**: [http://localhost:8000/map](http://localhost:8000/map)
-   **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
-   **Admin Dashboard** (API): `/api/admin/*` endpoints

### 3. Mobile App (Optional)

**Prerequisites**: Node.js, npm/yarn

```bash
cd mobile/MetroBusApp
npm install
npm start
```

---

## 🔌 API Endpoints Summary

### User / Public
-   `GET /map` - Live tracking interface
-   `GET /api/buses` - Real-time locations of all active buses
-   `GET /api/traffic/current` - Live traffic segment data
-   `GET /api/eta/bus/{bus_id}` - AI-predicted ETA for specific bus
-   `POST /api/journey/plan` - Plan a trip (Origin -> Dest)

### Administrator
-   `GET /api/admin/statistics` - System health & uptime
-   `GET /api/admin/alerts` - Real-time delay & incident alerts
-   `POST /api/admin/announcement` - Broadcast messages to users
-   `POST /api/admin/rush-hour/deploy-spare` - Add capacity to a route

---

## 🧪 Testing & Reliability
-   **Unit Tests**: `tests/` directory (if populated) and mobile `__tests__`.
-   **Resilience**: Auto-reconnection for WebSockets.
-   **Safety**: Maintenance mode handling prevents routing through disabled sections.

---

## 🌟 Future Roadmap
-   [ ] Passenger capacity visualization (Heatmaps)
-   [ ] Integration with hardware GPS modules
-   [ ] Fare payment gateway integration
