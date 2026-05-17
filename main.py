<<<<<<< HEAD
#!/usr/bin/env python3

import asyncio
import uvicorn
import os
import json
import traceback
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from eticket_endpoints import setup_eticket_routes
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import our custom modules
try:
    from database_manager import DatabaseManager
    print("✓ Successfully imported database_manager")
except ImportError as e:
    print(f"âŒ Failed to import database_manager: {e}")
    exit(1)

try:
    from bus_simulator import EnhancedMultiRouteBusSimulator
    print("✓ Successfully imported EnhancedMultiRouteBusSimulator")
    ENHANCED_FEATURES = True
except ImportError as e:
    print(f"âŒ Failed to import bus_simulator: {e}")
    exit(1)

try:
    from map_visualizer import MapVisualizer
    print("✓ Successfully imported map_visualizer")
except ImportError as e:
    print(f"âŒ Failed to import map_visualizer: {e}")
    exit(1)

# NEW: Import Journey Planning functionality
try:
    from journey_planner import IntelligentConnectionBuilder, Journey
    print("✓ Successfully imported journey_planner")
    JOURNEY_PLANNING_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Journey planner not available: {e}")
    JOURNEY_PLANNING_AVAILABLE = False

# NEW: Import Admin Endpoints
try:
    from admin_endpoints import get_admin_router
    print("✓ Successfully imported admin_endpoints")
    ADMIN_ENDPOINTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Admin endpoints not available: {e}")
    ADMIN_ENDPOINTS_AVAILABLE = False

# NEW: Import Advanced Managers
try:
    from driver_management import DriverRosterManager
    from rush_hour_analytics import RushHourAnalyticsManager
    from performance_analytics import PerformanceAnalyticsManager, PerformanceMetric
    print("✓ Successfully imported advanced management modules")
    ADVANCED_MANAGERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Advanced management modules not available: {e}")
    ADVANCED_MANAGERS_AVAILABLE = False

# NEW: Import Chatbot Endpoints
try:
    from chatbot_endpoints import get_chatbot_router, set_dependencies, initialize_chatbot
    print("✓ Successfully imported chatbot_endpoints")
    CHATBOT_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Chatbot module not available: {e}")
    CHATBOT_AVAILABLE = False

# ORIGINAL Request models - PRESERVED
class RouteActivationRequest(BaseModel):
    route_id: str
    num_buses: int = 10

class RouteDeactivationRequest(BaseModel):
    route_id: str

# NEW Request models - ADDED (not replacing anything)
class ETARequest(BaseModel):
    bus_id: str
    route_id: str = None

# NEW: Journey Planning Request models - ADDED
class JourneyPlanRequest(BaseModel):
    origin_lat: Optional[float] = Field(None, description="Origin latitude")
    origin_lng: Optional[float] = Field(None, description="Origin longitude")
    destination_lat: Optional[float] = Field(None, description="Destination latitude")
    destination_lng: Optional[float] = Field(None, description="Destination longitude")
    origin_stop: Optional[str] = Field(None, description="Origin stop name")
    destination_stop: Optional[str] = Field(None, description="Destination stop name")
    departure_time: Optional[str] = Field(None, description="Departure time in ISO format")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    max_transfers: Optional[int] = Field(2, description="Max bus transfers (0=direct, 1, 2, 3)")
    preference: Optional[str] = Field("hybrid", description="Optimise for: time | money | hybrid")

class JourneyStopRequest(BaseModel):
    origin_stop: str = Field(..., description="Origin stop name")
    destination_stop: str = Field(..., description="Destination stop name")
    max_transfers: Optional[int] = Field(2, description="Max transfers")
    preference: Optional[str] = Field("hybrid", description="time | money | hybrid")

class JourneyUpdateRequest(BaseModel):
    journey_id: str = Field(..., description="Journey ID to get updates for")

# ORIGINAL Global instances - PRESERVED + NEW journey_planner
db_manager = None
simulator = None
visualizer = None
journey_planner = None
driver_manager = None        # NEW
rush_hour_manager = None     # NEW
performance_manager = None   # NEW
active_connections: List[WebSocket] = []
DEBUG_LOG_PATH = "/home/muhammad/Desktop/FYP/.cursor/debug-a6bc00.log"


def _agent_debug_log(location: str, message: str, data: Dict[str, Any], run_id: str, hypothesis_id: str):
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown - ENHANCED but preserves original"""
    global db_manager, simulator, visualizer, journey_planner
    
    # Startup
    print("🚀 Starting Enhanced Metro Bus Multi-Route Simulation Engine...")
    print("🔧 Open http://localhost:8000/map to view live tracking")
    print("📊 API docs available at http://localhost:8000/docs")
    print("✨ Enhanced Bidirectional Features Active:")
    print("  • Alternating departures from both terminals")
    print("  • Bidirectional bus service (forward & reverse)")
    print("  • Scheduled departures every 10 seconds")
    print("  • Up to 10 buses per route")
    print("  • Persistent bus popups during updates")
    print("  • Enhanced traffic simulation")
    print("🤖 NEW: Traffic monitoring and AI-powered ETA predictions")
    print("🗺️ NEW: Intelligent Journey Planning and Multi-Route Connections")
    
    try:
        # Initialize components - SAME AS ORIGINAL
        print("🔧 Initializing database manager...")
        db_manager = DatabaseManager()
        print("✓ Database manager initialized")
        
        print("🚌 Initializing enhanced bidirectional bus simulator...")
        simulator = EnhancedMultiRouteBusSimulator(db_manager)
        print("✓ Enhanced bidirectional bus simulator initialized")
        
        print("🎫 Initializing E-Ticket system...")
        setup_eticket_routes(app, simulator)
        print("✓ E-Ticket system initialized")
        
        print("🗺️ Initializing map visualizer...")
        visualizer = MapVisualizer(simulator)
        print("✓ Map visualizer initialized")
        
        # NEW: Initialize Journey Planner if available
        if JOURNEY_PLANNING_AVAILABLE:
            print("🧠 Initializing Intelligent Connection Builder...")
            journey_planner = IntelligentConnectionBuilder(simulator, db_manager)
            print("✓ Intelligent Connection Builder initialized")
        else:
            print("⚠  Journey Planning features not available")

        # NEW: Initialize Advanced Managers if available
        if ADVANCED_MANAGERS_AVAILABLE:
            print("👔 Initializing Driver Roster Manager...")
            driver_manager = DriverRosterManager(db_manager, simulator)
            print("✓ Driver Roster Manager initialized")
            
            print("🚨 Initializing Rush Hour Analytics...")
            rush_hour_manager = RushHourAnalyticsManager(db_manager, simulator, driver_manager)
            print("✓ Rush Hour Analytics initialized")
            
            print("📈 Initializing Performance Analytics...")
            performance_manager = PerformanceAnalyticsManager(db_manager, simulator)
            print("✓ Performance Analytics initialized")
            
            # Inject dependencies into admin module
            if ADMIN_ENDPOINTS_AVAILABLE:
                import admin_endpoints
                admin_endpoints.driver_manager = driver_manager
                admin_endpoints.rush_hour_manager = rush_hour_manager
                admin_endpoints.performance_analytics = performance_manager
                admin_endpoints.simulator = simulator
                print("✓ Admin module dependencies injected")
        else:
            print("⚠ Advanced management features not available")

        # NEW: Initialize Chatbot if available
        if CHATBOT_AVAILABLE:
            print("🤖 Initializing Intelligent Chatbot...")
            try:
                initialize_chatbot(simulator, db_manager, journey_planner)
                set_dependencies(simulator, db_manager, journey_planner)
                print("✓ Intelligent Chatbot initialized")
            except Exception as e:
                print(f"⚠ Failed to initialize chatbot: {e}")
        else:
            print("⚠ Chatbot module not available")
        
        # Start simulation - SAME AS ORIGINAL
        print("▶️ Starting enhanced bidirectional bus simulation...")
        simulator.start_simulation()
        print("✓ Enhanced bidirectional bus simulation started")
        
        # Start background broadcasting - SAME AS ORIGINAL
        print("📡 Starting WebSocket broadcast...")
        broadcast_task = asyncio.create_task(broadcast_updates())
        print("✓ WebSocket broadcast started")
        
    except Exception as e:
        print(f"âŒ Error during startup: {e}")
        raise
    
    
    # NEW: Initialize Admin Broadcaster
    if ADMIN_ENDPOINTS_AVAILABLE:
        try:
            from admin_endpoints import set_broadcaster
            
            async def broadcast_announcement_data(data):
                """Broadcast arbitrary data to all connected clients"""
                print(f"📡 DEBUG: broadcast_announcement_data called. Active connections: {len(active_connections)}")
                if not active_connections:
                    print("⚠️ DEBUG: No active connections to broadcast to.")
                    return
                
                print(f"📤 DEBUG: Sending data type '{data.get('type')}' to {len(active_connections)} clients")
                
                disconnected = []
                for connection in active_connections:
                    try:
                        await connection.send_json(data)
                    except Exception as e:
                        print(f"❌ Failed to send announcement to client: {e}")
                        disconnected.append(connection)
                
                # Cleanup disconnected
                for connection in disconnected:
                    if connection in active_connections:
                        active_connections.remove(connection)
                        print("❌ DEBUG: Removed disconnected client during broadcast")
                        
            set_broadcaster(broadcast_announcement_data)
            print("✓ Admin broadcaster initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize admin broadcaster: {e}")

    yield
    
    # Shutdown - SAME AS ORIGINAL
    print("🛑 Shutting down...")
    if simulator:
        simulator.stop_simulation()
    if 'broadcast_task' in locals():
        broadcast_task.cancel()
    print("🛑 Application shutdown complete!")

# Create FastAPI app - ENHANCED but preserves original info
app = FastAPI(
    title="Enhanced Metro Bus Bidirectional Simulation API", 
    description="Real-time multi-route metro bus tracking with bidirectional service, traffic monitoring, AI-powered ETA predictions, and intelligent journey planning",
    version="4.2.0",  # Incremented to show journey planning enhancement
    lifespan=lifespan
)

# ADD THIS RIGHT AFTER app creation:

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex="https?://.*",
    allow_credentials=False,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

    # ⭐ NEW: Register Admin Router
if ADMIN_ENDPOINTS_AVAILABLE:
    admin_router = get_admin_router()
    
    # Register the admin router
    app.include_router(admin_router)
    
    print("✓ Admin endpoints registered successfully")

# NEW: Register Chatbot Router
if CHATBOT_AVAILABLE:
    try:
        chatbot_router = get_chatbot_router()
        app.include_router(chatbot_router)
        print("✓ Chatbot endpoints registered successfully")
    except Exception as e:
        print(f"⚠ Failed to register chatbot endpoints: {e}")

# ORIGINAL ROOT ENDPOINT - Enhanced with journey planning info but preserves original structure
@app.get("/")
async def root():
    """Root endpoint - API status with enhanced features including journey planning"""
    bidirectional_stats = {}
    traffic_stats = {}
    eta_stats = {}
    journey_stats = {}
    
    if simulator and hasattr(simulator, 'get_bidirectional_statistics'):
        for route_id in simulator.active_routes:
            bidirectional_stats[route_id] = simulator.get_bidirectional_statistics(route_id)
    
    # NEW: Add traffic and ETA stats
    if simulator and hasattr(simulator, 'get_route_statistics'):
        all_stats = simulator.get_route_statistics()
        traffic_stats = all_stats.get('traffic_overview', {})
        eta_stats = all_stats.get('eta_statistics', {})
    
    # NEW: Add journey planning stats
    if journey_planner:
        journey_stats = {
            "transfer_points": len(journey_planner.transfer_points_cache) if hasattr(journey_planner, 'transfer_points_cache') else 0,
            "max_transfers": getattr(journey_planner, 'max_transfers', 3),
            "max_walking_distance_km": getattr(journey_planner, 'max_walking_distance_km', 0.5),
            "transfer_buffer_minutes": getattr(journey_planner, 'transfer_buffer_minutes', 5)
        }
    
    base_info = {
        "message": "Enhanced Metro Bus Bidirectional Simulation API with Journey Planning", 
        "status": "running",
        "version": "4.2.0",
        "enhanced_bidirectional_features": [
            "Alternating departures from both terminals (source & destination)",
            "Bidirectional bus service (forward & reverse directions)",
            "Intelligent bus scheduling every 10 seconds",
            "Up to 10 buses per route with balanced service",
            "Persistent bus popups during real-time updates",
            "Enhanced traffic simulation with realistic delays"
        ],
        # NEW: Add traffic and ETA features without removing original
        "enhanced_ai_features": [
            "Real-time traffic monitoring with color-coded visualization",
            "AI-powered ETA predictions with machine learning",
            "Traffic-aware bus movement simulation",
            "Historical data learning for improved accuracy",
            "Intelligent multi-route journey planning",
            "Optimal transfer point suggestions",
            "Real-time scheduling with ETA integration",
            "Smart connection builder with confidence scores"
        ],
        "debug_info": {
            "db_manager_status": "initialized" if db_manager else "not initialized",
            "simulator_status": "initialized" if simulator else "not initialized",
            "journey_planner": "initialized" if journey_planner else "not initialized",
            "active_connections": len(active_connections),
            "simulation_running": simulator.simulation_running if simulator else False,
            "available_routes": len(simulator.routes) if simulator else 0,
            "active_routes": len(simulator.active_routes) if simulator else 0,
            "total_buses": len(simulator.buses) if simulator else 0,
            "max_buses_per_route": getattr(simulator, 'max_buses_per_route', 10),
            "departure_interval": getattr(simulator, 'departure_interval', 10),
            "bidirectional_service": len(bidirectional_stats) > 0,
            # NEW: Add traffic and ETA info
            "traffic_segments": len(getattr(simulator, 'traffic_segments', {})),
            "eta_predictor": "active" if hasattr(simulator, 'eta_predictor') else "inactive",
            # NEW: Add journey planning info
            **journey_stats
        },
        "bidirectional_statistics": bidirectional_stats,
        # NEW: Add traffic and ETA statistics
        "traffic_overview": traffic_stats,
        "eta_overview": eta_stats,
        # NEW: Add journey planning statistics
        "journey_planning_overview": journey_stats,
        "endpoints": {
            # ORIGINAL endpoints - PRESERVED
            "live_map": "/map",
            "debug_map": "/debug-map",
            "api_status": "/api/simulation/status",
            "buses": "/api/buses",
            "routes": "/api/routes",
            "activate_route": "/api/routes/activate",
            "deactivate_route": "/api/routes/deactivate",
            "deactivate_all": "/api/routes/deactivate-all",
            "route_stats": "/api/routes/statistics",
            "bidirectional_stats": "/api/routes/{route_id}/bidirectional",
            "websocket": "/ws/live-tracking",
            # NEW endpoints - ADDED
            "traffic_data": "/api/traffic/current",
            "eta_predictions": "/api/eta/all",
            "bus_eta": "/api/eta/bus/{bus_id}",
            "route_traffic": "/api/traffic/route/{route_id}",
            # NEW: Journey Planning endpoints
            "plan_journey": "/api/journey/plan",
            "quick_journey_plan": "/api/journey/quick-plan",
            "journey_updates": "/api/journey/{journey_id}/updates", 
            "transfer_points": "/api/journey/transfer-points",
            "nearby_stops": "/api/journey/nearby-stops",
            "admin_statistics": "/api/admin/statistics",
            "admin_announcement": "/api/admin/announcement",
            "admin_alerts": "/api/admin/alerts",
            "admin_performance": "/api/admin/performance",
            "chat_sessions": "/api/chat/sessions",
            "chat_messages": "/api/chat/sessions/{session_id}/messages",
            "chat_stream": "/api/chat/sessions/{session_id}/messages/stream"
        }
    }
    
    return base_info

# ORIGINAL MAP ENDPOINT - PRESERVED
@app.get("/map", response_class=HTMLResponse)
async def show_map():
    """Display live map with enhanced features"""
    try:
        # Try to find the web template file - SAME AS ORIGINAL
        template_files = [
            "web_template.html",             # Your original template
            "enhanced_web_template.html",    # Enhanced template if available
            "bidirectional_template.html",   # Alternative name
            "web_interface.html"             # Fallback
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                with open(template_file, "r", encoding="utf-8") as file:
                    html_content = file.read()
                    print(f"✓ Successfully loaded {template_file}")
                    return html_content
        
        # Enhanced fallback HTML - IMPROVED but not breaking
        journey_features = ""
        if JOURNEY_PLANNING_AVAILABLE:
            journey_features = """
                    <li>🧠 Intelligent multi-route journey planning</li>
                    <li>🔄 Optimal transfer point suggestions</li>
                    <li>📊 Real-time scheduling with ETA integration</li>
                    <li>🎯 Smart connection builder with confidence scores</li>
            """
        
        return f"""
        <html>
        <head><title>Enhanced Metro Bus Bidirectional Tracking</title></head>
        <body style="font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; max-width: 700px; margin: 0 auto;">
                <h1>🚌 Enhanced Metro Bus Bidirectional System Ready!</h1>
                <h2>✨ Bidirectional Features Active:</h2>
                <ul style="text-align: left; margin: 20px 0;">
                    <li>↔️ Alternating departures from both terminals (source & destination)</li>
                    <li>🔄 Bidirectional bus service (forward & reverse directions)</li>
                    <li>📅 Intelligent scheduling every 10 seconds</li>
                    <li>🚌 Up to 10 buses per route with balanced service</li>
                    <li>📌 Persistent bus popups that don't disappear during updates</li>
                    <li>🤖 Enhanced traffic simulation with realistic behavior</li>
                    <li>📊 Real-time bidirectional statistics tracking</li>
                </ul>
                <h2>🤖 AI Features:</h2>
                <ul style="text-align: left; margin: 20px 0;">
                    <li>🤖 Real-time traffic monitoring with color visualization</li>
                    <li>🤖 AI-powered ETA predictions</li>
                    <li>📈 Historical data learning</li>
                    <li>🎯 Traffic-aware routing</li>
                    {journey_features}
                </ul>
                <p style="margin: 20px 0;">Enhanced template file missing. Please ensure the enhanced web template is available.</p>
                <div style="margin: 20px 0;">
                    <a href="/docs" style="color: #fff; text-decoration: underline; margin: 10px;">API Documentation</a>
                    <a href="/api/routes" style="color: #fff; text-decoration: underline; margin: 10px;">View Routes</a>
                    <a href="/api/traffic/current" style="color: #fff; text-decoration: underline; margin: 10px;">Traffic Data</a>
                    {"<a href='/api/journey/transfer-points' style='color: #fff; text-decoration: underline; margin: 10px;'>Transfer Points</a>" if JOURNEY_PLANNING_AVAILABLE else ""}
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"âŒ Error loading template: {e}")
        return f"<html><body><h1>Error loading template: {e}</h1><p><a href='/docs'>Go to API Documentation</a></p></body></html>"

# ADD THIS NEW ENDPOINT TO main.py (after the /map endpoint)

# ADD THIS TO main.py - After the root endpoint

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Display admin dashboard for metro authorities"""
    try:
        admin_file = "admin_dashboard.html"
        
        if os.path.exists(admin_file):
            with open(admin_file, "r", encoding="utf-8") as file:
                html_content = file.read()
                print(f"✓ Successfully loaded {admin_file}")
                return html_content
        
        return """
        <html>
        <head><title>Admin Dashboard Not Found</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>⚠️ Admin Dashboard Template Missing</h1>
            <p>Please ensure <code>admin_dashboard.html</code> exists in the project root directory.</p>
            <p><a href="/">Go to Main Map</a> | <a href="/docs">API Documentation</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"❌ Error loading admin dashboard: {e}")
        return f"<html><body><h1>Error: {e}</h1><p><a href='/'>Go to Main Map</a></p></body></html>"


# ORIGINAL SIMULATION STATUS ENDPOINT - Enhanced but preserves original behavior
@app.get("/api/simulation/status")
async def get_simulation_status():
    """Get current simulation data with enhanced information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        # Use enhanced method if available, otherwise fall back to original
        if hasattr(simulator, 'get_simulation_data_with_bidirectional_info'):
            data = simulator.get_simulation_data_with_bidirectional_info()
        else:
            data = simulator.get_simulation_data()
        
        # Enhanced logging with additional info
        buses_count = len(data.get('buses', []))
        routes_count = len(data.get('active_routes', []))
        forward_buses = data.get('service_summary', {}).get('forward_buses', 0)
        reverse_buses = data.get('service_summary', {}).get('reverse_buses', 0)
        traffic_segments = len(data.get('traffic_segments', {}))
        
        print(f"📊 Enhanced status: {buses_count} buses on {routes_count} routes "
              f"({forward_buses} forward, {reverse_buses} reverse), {traffic_segments} traffic segments")
        
        return data
    except Exception as e:
        print(f"âŒ Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW ENDPOINTS - Traffic and ETA (ADDED without replacing anything)
@app.get("/api/traffic/current")
async def get_current_traffic():
    """Get current traffic conditions for all segments"""
    if not simulator or not hasattr(simulator, 'get_traffic_data_for_frontend'):
        raise HTTPException(status_code=500, detail="Traffic system not available")
    
    try:
        traffic_data = simulator.get_traffic_data_for_frontend()
        
        # Calculate summary statistics
        all_levels = [seg['traffic_level'] for seg in traffic_data.values()]
        summary = {
            'total_segments': len(traffic_data),
            'average_traffic_level': sum(all_levels) / len(all_levels) if all_levels else 1.0,
            'heavy_traffic_count': len([l for l in all_levels if l <= 0.3]),
            'moderate_traffic_count': len([l for l in all_levels if 0.3 < l <= 0.6]),
            'light_traffic_count': len([l for l in all_levels if l > 0.6]),
            'last_updated': simulator.last_traffic_update.isoformat() if hasattr(simulator, 'last_traffic_update') else None
        }
        
        return {
            'traffic_segments': traffic_data,
            'summary': summary,
            'legend': {
                'heavy_traffic': {'color': '#DC3545', 'description': 'Heavy Traffic (0-30% of normal speed)'},
                'moderate_traffic': {'color': '#FFC107', 'description': 'Moderate Traffic (30-60% of normal speed)'},
                'light_traffic': {'color': '#28A745', 'description': 'Light Traffic (60-90% of normal speed)'},
                'free_flow': {'color': '#007CBA', 'description': 'Free Flow (90%+ of normal speed)'}
            }
        }
    except Exception as e:
        print(f"Error getting traffic data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eta/all")
async def get_all_etas():
    """Get ETA predictions for all active buses"""
    if not simulator or not hasattr(simulator, 'get_all_bus_etas'):
        raise HTTPException(status_code=500, detail="ETA system not available")
    
    try:
        all_etas = simulator.get_all_bus_etas()
        
        # Calculate summary statistics
        total_predictions = sum(len(bus_etas) for bus_etas in all_etas.values())
        
        return {
            'bus_etas': all_etas,
            'summary': {
                'total_buses_with_etas': len(all_etas),
                'total_eta_predictions': total_predictions
            },
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting ETA data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eta/bus/{bus_id}")
async def get_bus_eta(bus_id: str):
    """Get ETA predictions for a specific bus"""
    if not simulator or not hasattr(simulator, 'eta_predictor'):
        raise HTTPException(status_code=500, detail="ETA system not available")
    
    if bus_id not in simulator.buses:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    try:
        bus = simulator.buses[bus_id]
        route = simulator.routes.get(bus.route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        etas = simulator.eta_predictor.predict_eta_to_stops(bus, route, simulator.traffic_segments)
        
        return {
            'bus_id': bus_id,
            'route_id': bus.route_id,
            'route_name': route.name,
            'current_direction': bus.direction,
            'current_position': {
                'lat': bus.current_lat,
                'lng': bus.current_lng,
                'speed': bus.speed,
                'status': bus.status
            },
            'etas': etas,
            'next_stops_count': len(etas)
        }
    except Exception as e:
        print(f"Error getting bus ETA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW ENDPOINTS - Journey Planning (ADDED without replacing anything)
@app.post("/api/journey/plan")
async def plan_journey(request: JourneyPlanRequest):
    if not journey_planner:
        raise HTTPException(status_code=503, detail="Journey planning not available")
    try:
        _agent_debug_log(
            location="main.py:/api/journey/plan:entry",
            message="Journey planning request received",
            data={
                "has_origin_stop": bool(request.origin_stop),
                "has_destination_stop": bool(request.destination_stop),
                "has_origin_latlng": request.origin_lat is not None and request.origin_lng is not None,
                "has_destination_latlng": request.destination_lat is not None and request.destination_lng is not None,
                "preference": request.preference,
                "max_transfers": request.max_transfers
            },
            run_id="run1",
            hypothesis_id="H2"
        )
        max_transfers = request.max_transfers or 2
        preference = (request.preference or 'hybrid').lower()

        if request.origin_stop and request.destination_stop:
            journey_options = await journey_planner.plan_journey_by_stops(
                origin_name=request.origin_stop,
                dest_name=request.destination_stop,
                max_transfers=max_transfers,
                preference=preference,
            )
            planning_mode = "stop_to_stop"
        else:
            if None in (request.origin_lat, request.origin_lng, request.destination_lat, request.destination_lng):
                raise HTTPException(
                    status_code=422,
                    detail="Provide either origin_stop/destination_stop OR full origin/destination coordinates."
                )
            journey_options = await journey_planner.plan_journey(
                origin_lat=request.origin_lat,
                origin_lng=request.origin_lng,
                dest_lat=request.destination_lat,
                dest_lng=request.destination_lng,
                max_transfers=max_transfers,
                preference=preference,
            )
            planning_mode = "location_to_location"
        if not journey_options:
            _agent_debug_log(
                location="main.py:/api/journey/plan:no_results",
                message="Journey planner returned no options",
                data={"planning_mode": planning_mode},
                run_id="run1",
                hypothesis_id="H4"
            )
            return {"success": False, "message": "No viable journey routes found",
                    "suggestions": ["Try different stops", "Increase max transfers",
                                    "Check active routes"]}
        summaries = [journey_planner.get_journey_summary(j) for j in journey_options]
        _agent_debug_log(
            location="main.py:/api/journey/plan:success",
            message="Journey planner returned options",
            data={"planning_mode": planning_mode, "journey_count": len(summaries)},
            run_id="run1",
            hypothesis_id="H2"
        )
        return {
            "success": True,
            "planning_mode": planning_mode,
            "journey_count": len(summaries),
            "best": summaries[0],
            "journeys": summaries
        }
    except Exception as e:
        _agent_debug_log(
            location="main.py:/api/journey/plan:exception",
            message="Journey planning endpoint exception",
            data={"error": str(e), "traceback": traceback.format_exc()},
            run_id="run1",
            hypothesis_id="H2"
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/journey/plan-by-stops")
async def plan_journey_by_stops(request: JourneyStopRequest):
    if not journey_planner:
        raise HTTPException(status_code=503, detail="Journey planning not available")
    try:
        journey_options = await journey_planner.plan_journey_by_stops(
            origin_name=request.origin_stop,
            dest_name=request.destination_stop,
            max_transfers=request.max_transfers or 2,
            preference=request.preference or 'hybrid',
        )
        if not journey_options:
            return {"success": False, "message": "No routes found between these stops",
                    "suggestions": ["Check stop names are correct", "Try increasing max transfers"]}
        summaries = [journey_planner.get_journey_summary(j) for j in journey_options]
        return {
            "success": True,
            "planning_mode": "stop_to_stop",
            "journey_count": len(summaries),
            "best": summaries[0],
            "journeys": summaries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journey/{journey_id}/updates")
async def get_journey_updates(journey_id: str):
    """
    Get real-time updates for an active journey
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        updates = await journey_planner.get_real_time_journey_updates(journey_id)
        
        return {
            "success": True,
            "journey_id": journey_id,
            "updates": updates,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting journey updates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get journey updates: {str(e)}")

@app.get("/api/journey/transfer-points")
async def get_transfer_points():
    """
    Get all available transfer points in the network
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        transfer_points = []
        
        for point in journey_planner.transfer_points_cache.values():
            transfer_points.append({
                "id": point.stop_id,
                "name": point.stop_name,
                "location": [point.latitude, point.longitude],
                "connected_routes": point.routes,
                "transfer_time_minutes": point.transfer_time_minutes,
                "accessibility_features": point.accessibility_features,
                "route_colors": [
                    journey_planner._get_route_color(route_id) 
                    for route_id in point.routes
                ]
            })
        
        transfer_points = journey_planner.get_all_transfer_points()
        return {"success": True, "transfer_points": transfer_points,
                "total_count": len(transfer_points)}
        
    except Exception as e:
        print(f"Error getting transfer points: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transfer points: {str(e)}")

@app.post("/api/journey/quick-plan")
async def quick_journey_plan(
    origin_lat: float, 
    origin_lng: float, 
    dest_lat: float, 
    dest_lng: float,
    max_transfers: Optional[int] = 2
):
    """
    Quick journey planning endpoint with minimal parameters
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        # Set simplified preferences
        preferences = {
            'time_weight': 0.5,
            'transfer_weight': 0.3,
            'walking_weight': 0.2,
            'allow_multiple_transfers': max_transfers > 0
        }
        
        # Use current journey planner max_transfers if specified max is higher
        journey_planner.max_transfers = min(max_transfers, journey_planner.max_transfers)
        
        journey_options = await journey_planner.plan_journey(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            preferences=preferences
        )
        
        if not journey_options:
            return {
                "success": False,
                "message": "No routes found between these locations",
                "quick_suggestions": [
                    f"Try locations within {journey_planner.max_walking_distance_km:.1f}km of bus stops",
                    "Ensure at least one route is currently active",
                    "Consider increasing max_transfers parameter"
                ]
            }
        
        # Return simplified response with just the best option
        best_journey = journey_options[0]
        summary = journey_planner.get_journey_summary(best_journey)
        
        return {
            "success": True,
            "message": "Quick route found",
            "recommended_journey": {
                "journey_id": summary["journey_id"],
                "total_time_minutes": summary["summary"]["total_duration_minutes"],
                "transfers_required": summary["summary"]["transfers_required"],
                "total_fare": summary["summary"]["total_fare"],
                "departure_time": summary["summary"]["departure_time"],
                "arrival_time": summary["summary"]["arrival_time"],
                "confidence": summary["summary"]["confidence_score"],
                "routes": [seg["route_id"] for seg in summary["segments"]],
                "step_by_step": summary["instructions"][:5]  # First 5 steps only
            },
            "alternatives_available": len(journey_options) - 1,
            "search_info": {
                "origin": [origin_lat, origin_lng],
                "destination": [dest_lat, dest_lng],
                "max_transfers_used": max_transfers
            }
        }
        
    except Exception as e:
        print(f"Error in quick journey planning: {e}")
        raise HTTPException(status_code=500, detail=f"Quick planning failed: {str(e)}")

@app.get("/api/journey/nearby-stops")
async def get_nearby_stops(lat: float, lng: float, radius_km: float = 0.5):
    """
    Find nearby bus stops for journey planning
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        # Use journey planner's method to find nearby stops
        nearby_stops = journey_planner._find_nearby_stops(lat, lng, radius_km)
        
        # Group by route for better organization
        stops_by_route = {}
        for stop in nearby_stops:
            route_id = stop['route_id']
            if route_id not in stops_by_route:
                route = simulator.routes.get(route_id)
                stops_by_route[route_id] = {
                    'route_id': route_id,
                    'route_name': route.name if route else route_id,
                'route_color': journey_planner._get_route_color(route_id),
                    'is_active': route_id in simulator.active_routes if simulator else False,
                    'stops': []
                }
            
            stops_by_route[route_id]['stops'].append({
                'stop_name': stop['stop_name'],
                'stop_index': stop['stop_idx'],
                'location': [stop['latitude'], stop['longitude']],
                'distance_km': round(stop['distance_km'], 3),
                'walk_time_minutes': round(stop['walk_min'], 1)
            })
        
        return {
            "success": True,
            "search_location": [lat, lng],
            "search_radius_km": radius_km,
            "routes_found": len(stops_by_route),
            "total_stops_found": len(nearby_stops),
            "nearby_routes": list(stops_by_route.values()),
            "closest_stop": nearby_stops[0] if nearby_stops else None
        }
        
    except Exception as e:
        print(f"Error finding nearby stops: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find nearby stops: {str(e)}")

# ORIGINAL ROUTES ENDPOINT - Enhanced with traffic info but preserves original structure
@app.get("/api/routes")
async def get_available_routes():
    """Get all available routes with enhanced information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        routes = simulator.get_available_routes()
        response = {
            "routes": routes,
            "total_routes": len(routes),
            "active_routes": len([r for r in routes if r['active']]),
            "max_buses_per_route": getattr(simulator, 'max_buses_per_route', 10),
            "departure_interval_seconds": getattr(simulator, 'departure_interval', 10),
            "bidirectional_features": {
                "alternating_departures": True,
                "bidirectional_service": True,
                "terminal_based_scheduling": True,
                "intelligent_bus_distribution": True,
                "persistent_popups": True,
                "enhanced_traffic": True
            },
            # NEW: Add traffic and ETA info
            "enhanced_ai_features": {
                "traffic_monitoring": hasattr(simulator, 'traffic_segments'),
                "eta_predictions": hasattr(simulator, 'eta_predictor'),
                "historical_learning": True,
                "real_time_updates": True,
                "journey_planning": JOURNEY_PLANNING_AVAILABLE and journey_planner is not None
            },
            "service_statistics": {
                "terminals_per_route": 2,
                "departure_pattern": "alternating_between_terminals",
                "max_buses_per_direction": 5
            }
        }
        
        return response
    except Exception as e:
        print(f"Error getting routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ORIGINAL ACTIVATE ROUTE ENDPOINT - Enhanced with additional info but preserves original behavior
@app.post("/api/routes/activate")
async def activate_route(request: RouteActivationRequest):
    """Activate a route with enhanced features"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        # Cap the number of buses to the simulator's maximum - SAME AS ORIGINAL
        max_buses = getattr(simulator, 'max_buses_per_route', 10)
        num_buses = min(request.num_buses, max_buses)
        
        # Use enhanced bidirectional activation method - SAME AS ORIGINAL
        if hasattr(simulator, 'activate_route_with_bidirectional_service'):
            success = simulator.activate_route_with_bidirectional_service(request.route_id, num_buses)
        else:
            success = simulator.activate_route(request.route_id, num_buses)
            
        if success:
            response_data = {
                "success": True,
                "message": f"Route {request.route_id} activated with bidirectional service",
                "route_id": request.route_id,
                "buses_requested": request.num_buses,
                "buses_activated": num_buses,
                "max_buses": max_buses,
                "departure_interval": getattr(simulator, 'departure_interval', 10),
                "bidirectional_features": [
                    "Alternating departures from both terminals",
                    "Forward and reverse direction buses",
                    "Intelligent terminal-based scheduling",
                    "Balanced service distribution",
                    "Enhanced traffic simulation"
                ]
            }
            
            # NEW: Add traffic and ETA info if available
            if hasattr(simulator, 'get_bidirectional_statistics'):
                response_data["bidirectional_statistics"] = simulator.get_bidirectional_statistics(request.route_id)
            
            if hasattr(simulator, 'traffic_segments'):
                response_data["enhanced_features_enabled"] = [
                    "Real-time traffic monitoring",
                    "AI-powered ETA predictions",
                    "Traffic-responsive bus speeds"
                ]
            
            # NEW: Add journey planning info if available
            if journey_planner:
                response_data["journey_planning_features"] = [
                    "Multi-route journey planning available",
                    "Transfer point optimization",
                    "Real-time connection updates"
                ]
            
            return response_data
        else:
            raise HTTPException(status_code=400, detail=f"Failed to activate route {request.route_id}")
    except Exception as e:
        print(f"Error activating route {request.route_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ORIGINAL ENDPOINTS - All preserved exactly
@app.get("/api/routes/{route_id}/bidirectional")
async def get_route_bidirectional_stats(route_id: str):
    """Get detailed bidirectional statistics for a specific route"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    if route_id not in simulator.routes:
        raise HTTPException(status_code=404, detail=f"Route {route_id} not found")
    
    try:
        if hasattr(simulator, 'get_bidirectional_statistics'):
            stats = simulator.get_bidirectional_statistics(route_id)
            return stats
        else:
            # Fallback: basic statistics
            route_buses = [bus for bus in simulator.buses.values() if bus.route_id == route_id]
            forward_buses = [b for b in route_buses if b.direction == 'forward']
            reverse_buses = [b for b in route_buses if b.direction == 'reverse']
            
            return {
                "route_id": route_id,
                "total_buses": len(route_buses),
                "forward_direction": {"count": len(forward_buses)},
                "reverse_direction": {"count": len(reverse_buses)},
                "service_balance": {
                    "forward_percentage": (len(forward_buses) / len(route_buses) * 100) if route_buses else 0,
                    "reverse_percentage": (len(reverse_buses) / len(route_buses) * 100) if route_buses else 0
                }
            }
    except Exception as e:
        print(f"Error getting bidirectional statistics for route {route_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/routes/statistics")
async def get_route_statistics():
    """Get enhanced statistics with traffic and ETA information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        stats = simulator.get_route_statistics()
        
        # Add bidirectional summary if method exists - SAME AS ORIGINAL
        if hasattr(simulator, 'get_bidirectional_statistics'):
            bidirectional_summary = {}
            for route_id in simulator.active_routes:
                bidirectional_summary[route_id] = simulator.get_bidirectional_statistics(route_id)
            
            stats['bidirectional_service_summary'] = bidirectional_summary
            stats['total_terminals_served'] = len(simulator.active_routes) * 2
            stats['alternating_departures_active'] = len(simulator.active_routes) > 0
        
        return stats
    except Exception as e:
        print(f"Error getting route statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/buses")
async def get_all_buses():
    """Get all active buses with enhanced information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        data = simulator.get_simulation_data()
        buses = data.get('buses', [])
        
        # Enhanced bus statistics with bidirectional info - PRESERVED ORIGINAL + NEW
        direction_stats = {
            "forward": len([b for b in buses if b.get('direction') == 'forward']),
            "reverse": len([b for b in buses if b.get('direction') == 'reverse'])
        }
        
        # Terminal-based statistics
        terminal_stats = {}
        for bus in buses:
            route_id = bus.get('route_id')
            direction = bus.get('direction', 'forward')
            if route_id not in terminal_stats:
                terminal_stats[route_id] = {"forward": 0, "reverse": 0}
            terminal_stats[route_id][direction] += 1
        
        response_data = {
            "buses": buses,
            "total_buses": len(buses),
            "routes_with_buses": len(set(bus['route_id'] for bus in buses)),
            "total_background_buses": data.get('total_background_buses', 0),
            "bidirectional_statistics": {
                "direction_distribution": direction_stats,
                "terminal_distribution": terminal_stats,
                "service_balance": {
                    "forward_percentage": (direction_stats["forward"] / len(buses) * 100) if buses else 0,
                    "reverse_percentage": (direction_stats["reverse"] / len(buses) * 100) if buses else 0
                }
            },
            "bus_statuses": {
                "at_stops": len([b for b in buses if b.get('is_at_stop')]),
                "delayed": len([b for b in buses if b.get('status') == 'delayed']),
                "moving": len([b for b in buses if b.get('status') == 'moving']),
                "in_traffic": len([b for b in buses if b.get('speed', 0) < 10 and not b.get('is_at_stop')])
            }
        }
        
        # NEW: Add traffic and ETA statistics if available
        if hasattr(simulator, 'get_all_bus_etas'):
            all_etas = simulator.get_all_bus_etas()
            response_data["eta_information"] = {
                "buses_with_etas": len(all_etas),
                "total_eta_predictions": sum(len(bus_etas) for bus_etas in all_etas.values()),
                "average_predictions_per_bus": sum(len(bus_etas) for bus_etas in all_etas.values()) / len(buses) if buses else 0
            }
        
        return response_data
    except Exception as e:
        print(f"Error getting buses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ORIGINAL ENDPOINTS - Preserved exactly
@app.post("/api/routes/deactivate")
async def deactivate_route(request: RouteDeactivationRequest):
    """Deactivate a specific route"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        simulator.deactivate_route(request.route_id)
        return {
            "success": True,
            "message": f"Route {request.route_id} deactivated",
            "route_id": request.route_id,
            "note": "Bidirectional buses may continue running in background simulation"
        }
    except Exception as e:
        print(f"Error deactivating route {request.route_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/routes/deactivate-all")
async def deactivate_all_routes():
    """Deactivate all active routes"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        deactivated_routes = list(simulator.active_routes)
        for route_id in deactivated_routes:
            simulator.deactivate_route(route_id)
        
        return {
            "success": True,
            "message": f"Deactivated {len(deactivated_routes)} routes",
            "deactivated_routes": deactivated_routes,
            "note": "All bidirectional buses continue running in background"
        }
    except Exception as e:
        print(f"Error deactivating all routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# Setup E-Ticket routes
#setup_eticket_routes(app, simulator)

@app.post("/api/eticket/login")
async def eticket_login(request: dict):
    """Login user"""
    try:
        with open("eticket_users.json", 'r') as f:
            data = json.load(f)
        
        # Find user
        user = next((u for u in data['users'] if u['email'] == request['email']), None)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        if user['password'] != request['password']:
            return {"success": False, "message": "Invalid password"}
        
        # Return user without password
        user_response = {k: v for k, v in user.items() if k != 'password'}
        
        return {
            "success": True,
            "message": "Login successful",
            "user": user_response
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/eticket/active-routes")
async def get_active_routes_for_ticket():
    """Get only currently active routes with buses"""
    try:
        active_routes_list = []
        
        for route_id in simulator.active_routes:
            route = simulator.routes.get(route_id)
            if route:
                # Get active buses for this route
                route_buses = [bus for bus in simulator.buses.values() 
                             if bus.route_id == route_id and bus.status == 'active']
                
                if route_buses:  # Only include routes with active buses
                    # Calculate fare based on distance (Rs. 10 per km, minimum Rs. 20)
                    fare = max(20, int(route.total_distance * 10))
                    
                    active_routes_list.append({
                        "route_id": route_id,
                        "name": route.name,
                        "source": route.source,
                        "destination": route.destination,
                        "fare": fare,
                        "active_buses": len(route_buses),
                        "distance": round(route.total_distance, 1)
                    })
        
        return {
            "success": True,
            "routes": active_routes_list,
            "total_active": len(active_routes_list)
        }
        
    except Exception as e:
        return {"success": False, "message": str(e), "routes": []}

@app.post("/api/eticket/topup")
async def eticket_topup(request: dict):
    """Top up user wallet"""
    try:
        with open("eticket_users.json", 'r') as f:
            data = json.load(f)
        
        # Find user
        user = next((u for u in data['users'] if u['email'] == request['email']), None)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Add amount to balance
        user['balance'] += int(request['amount'])
        
        # Save to file
        with open("eticket_users.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            "success": True,
            "message": "Top-up successful",
            "new_balance": user['balance']
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/eticket/purchase")
async def eticket_purchase(request: dict):
    """Purchase E-Ticket"""
    try:
        with open("eticket_users.json", 'r') as f:
            data = json.load(f)
        
        # Find user
        user = next((u for u in data['users'] if u['email'] == request['email']), None)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Check if route is active
        if request['route_id'] not in simulator.active_routes:
            return {"success": False, "message": "Route not active"}
        
        # Calculate fare (free for seniors)
        fare = 0 if user['is_senior'] else int(request['fare'])
        
        # Check balance if using wallet
        if request.get('payment_method') == 'wallet':
            if user['balance'] < fare:
                return {"success": False, "message": "Insufficient balance"}
            
            user['balance'] -= fare
            
            # Save to file
            with open("eticket_users.json", 'w') as f:
                json.dump(data, f, indent=2)
        
        return {
            "success": True,
            "message": "Ticket purchased successfully",
            "ticket": {
                "route_id": request['route_id'],
                "fare": fare,
                "is_free": user['is_senior'],
                "payment_method": request.get('payment_method'),
                "timestamp": datetime.now().isoformat()
            },
            "new_balance": user['balance']
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}
# ORIGINAL WEBSOCKET - Enhanced with additional data but preserves original behavior
@app.websocket("/ws/live-tracking")
async def websocket_endpoint(websocket: WebSocket):
    """Enhanced WebSocket endpoint for real-time tracking"""
    print(f"📡 New WebSocket connection attempt from {websocket.client}")
    
    try:
        await websocket.accept()
        active_connections.append(websocket)
        print(f"✓ WebSocket connected. Total connections: {len(active_connections)}")
        
        # Send initial enhanced data immediately - SAME AS ORIGINAL but enhanced
        if simulator:
            try:
                if hasattr(simulator, 'get_simulation_data_with_bidirectional_info'):
                    initial_data = simulator.get_simulation_data_with_bidirectional_info()
                else:
                    initial_data = simulator.get_simulation_data()
                
                # Use serializer for initial data
                from bus_simulator import serialize_for_json
                initial_data = serialize_for_json(initial_data)
                
                await websocket.send_json(initial_data)
                print("📤 Sent initial enhanced data to new client")
            except Exception as e:
                print(f"âŒ Error sending initial data: {e}")
        
        # Keep connection alive - SAME AS ORIGINAL
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if message == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.ping()
            except Exception as e:
                print(f"âŒ WebSocket message error: {e}")
                break
                
    except WebSocketDisconnect:
        print("📡 WebSocket disconnected normally")
    except Exception as e:
        print(f"âŒ WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"📡 WebSocket removed. Remaining connections: {len(active_connections)}")

# ORIGINAL BROADCAST - Enhanced with additional data but preserves original behavior
async def broadcast_updates():
    """Enhanced broadcast updates with traffic and ETA information"""
    print("📡 Starting enhanced background broadcast task...")
    
    try:
        while True:
            if active_connections and simulator:
                try:
                    # Use enhanced method if available
                    if hasattr(simulator, 'get_simulation_data_with_bidirectional_info'):
                        data = simulator.get_simulation_data_with_bidirectional_info()
                    else:
                        data = simulator.get_simulation_data()
                    
                    # ✓ FIX: Import and use the serializer
                    from bus_simulator import serialize_for_json
                    data = serialize_for_json(data)  # Convert ALL datetime objects
                    
                    disconnected = []
                    
                    for connection in active_connections:
                        try:
                            await connection.send_json(data)
                        except Exception as e:
                            print(f"âŒ Failed to send to client: {e}")
                            disconnected.append(connection)
                    
                    # Remove disconnected clients
                    for connection in disconnected:
                        if connection in active_connections:
                            active_connections.remove(connection)
                    
                    if len(active_connections) > 0:
                        buses_count = len(data.get('buses', []))
                        routes_count = len(data.get('active_routes', []))
                        forward_buses = data.get('service_summary', {}).get('forward_buses', 0)
                        reverse_buses = data.get('service_summary', {}).get('reverse_buses', 0)
                        
                        print(f"📤 Broadcast to {len(active_connections)} clients - "
                              f"{buses_count} buses on {routes_count} routes "
                              f"({forward_buses} forward, {reverse_buses} reverse)")
                        
                except Exception as e:
                    print(f"âŒ Broadcast error: {e}")
            
            await asyncio.sleep(3)  # Broadcast every 3 seconds - SAME AS ORIGINAL
            
    except asyncio.CancelledError:
        print("📡 Enhanced broadcast task cancelled")
        raise
    except Exception as e:
        print(f"âŒ Broadcast task error: {e}")

# ORIGINAL MAIN FUNCTION - Enhanced with additional info but preserves original structure
def main():
    """Main entry point with enhanced features information"""
    print("🚀 Enhanced Metro Bus Bidirectional Multi-Route Simulation Engine")
    print("=" * 70)
    
    # Check file dependencies - SAME AS ORIGINAL
    required_files = ["models.py", "database_manager.py", "map_visualizer.py", "bus_simulator.py"]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✓ {file} found")
    
    # Check for optional journey planner
    if os.path.exists("journey_planner.py"):
        print(f"✓ journey_planner.py found - Journey planning features available")
    else:
        print(f"⚠ journey_planner.py not found - Journey planning features disabled")
    
    if missing_files:
        print(f"âŒ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all required files are in the same directory")
        return
    
    print("\n✨ Bidirectional Features:")
    print("• Alternating departures from both terminals (source & destination)")
    print("• Bidirectional bus service (forward & reverse directions)")
    print("• Intelligent scheduling every 10 seconds with terminal rotation")
    print("• Up to 10 buses per route with balanced service distribution")
    print("• Persistent bus popups that don't disappear on updates")
    print("• Enhanced traffic simulation with realistic bus behavior")
    print("• Real-time WebSocket updates with bidirectional statistics")
    print("• Background bus simulation for optimal resource management")
    
    print("\n🤖 AI Features:")
    print("• Real-time traffic monitoring with color-coded visualization")
    print("• AI-powered ETA predictions using machine learning")
    print("• Traffic-aware bus movement simulation")
    print("• Historical data learning for improved accuracy over time")
    
    if JOURNEY_PLANNING_AVAILABLE:
        print("\n🧠 Journey Planning Features:")
        print("• Intelligent multi-route journey planning")
        print("• Optimal transfer point suggestions")
        print("• Real-time scheduling with ETA integration")
        print("• Smart connection builder with confidence scores")
        print("• Quick journey planning for immediate routes")
        print("• Nearby stops discovery and route optimization")
    
    try:
        print("\n🚀 Starting Enhanced Metro Bus Simulation Server...")
        print("📍 Access the application at:")
        print("   • Live Map: http://localhost:8000/map")
        print("   • Admin Dashboard: http://localhost:8000/admin")  # ⭐ ADD THIS
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • API Status: http://localhost:8000")
        print("   • Traffic Data: http://localhost:8000/api/traffic/current")
        print("   • ETA Predictions: http://localhost:8000/api/eta/all")
        
        if JOURNEY_PLANNING_AVAILABLE:
            print("   • Transfer Points: http://localhost:8000/api/journey/transfer-points")
            print("   • Journey Planning: http://localhost:8000/api/journey/plan")
        
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested by user")
    except Exception as e:
        print(f"âŒ Server error: {e}")

if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3

import asyncio
import uvicorn
import os
import json
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from eticket_endpoints import setup_eticket_routes
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import our custom modules
try:
    from database_manager import DatabaseManager
    print("✓ Successfully imported database_manager")
except ImportError as e:
    print(f"âŒ Failed to import database_manager: {e}")
    exit(1)

try:
    from bus_simulator import EnhancedMultiRouteBusSimulator
    print("✓ Successfully imported EnhancedMultiRouteBusSimulator")
    ENHANCED_FEATURES = True
except ImportError as e:
    print(f"âŒ Failed to import bus_simulator: {e}")
    exit(1)

try:
    from map_visualizer import MapVisualizer
    print("✓ Successfully imported map_visualizer")
except ImportError as e:
    print(f"âŒ Failed to import map_visualizer: {e}")
    exit(1)

# NEW: Import Journey Planning functionality
try:
    from journey_planner import IntelligentConnectionBuilder, Journey
    print("✓ Successfully imported journey_planner")
    JOURNEY_PLANNING_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Journey planner not available: {e}")
    JOURNEY_PLANNING_AVAILABLE = False

# NEW: Import Admin Endpoints
try:
    from admin_endpoints import get_admin_router
    print("✓ Successfully imported admin_endpoints")
    ADMIN_ENDPOINTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Admin endpoints not available: {e}")
    ADMIN_ENDPOINTS_AVAILABLE = False

# NEW: Import Advanced Managers
try:
    from driver_management import DriverRosterManager
    from rush_hour_analytics import RushHourAnalyticsManager
    from performance_analytics import PerformanceAnalyticsManager, PerformanceMetric
    print("✓ Successfully imported advanced management modules")
    ADVANCED_MANAGERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Advanced management modules not available: {e}")
    ADVANCED_MANAGERS_AVAILABLE = False

# ORIGINAL Request models - PRESERVED
class RouteActivationRequest(BaseModel):
    route_id: str
    num_buses: int = 10

class RouteDeactivationRequest(BaseModel):
    route_id: str

# NEW Request models - ADDED (not replacing anything)
class ETARequest(BaseModel):
    bus_id: str
    route_id: str = None

# NEW: Journey Planning Request models - ADDED
class JourneyPlanRequest(BaseModel):
    origin_lat: Optional[float] = Field(None, description="Origin latitude")
    origin_lng: Optional[float] = Field(None, description="Origin longitude")
    destination_lat: Optional[float] = Field(None, description="Destination latitude")
    destination_lng: Optional[float] = Field(None, description="Destination longitude")
    origin_stop: Optional[str] = Field(None, description="Origin stop name")
    destination_stop: Optional[str] = Field(None, description="Destination stop name")
    departure_time: Optional[str] = Field(None, description="Departure time in ISO format")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    max_transfers: Optional[int] = Field(2, description="Max bus transfers (0=direct, 1, 2, 3)")
    preference: Optional[str] = Field("hybrid", description="Optimise for: time | money | hybrid")

class JourneyStopRequest(BaseModel):
    origin_stop: str = Field(..., description="Origin stop name")
    destination_stop: str = Field(..., description="Destination stop name")
    max_transfers: Optional[int] = Field(2, description="Max transfers")
    preference: Optional[str] = Field("hybrid", description="time | money | hybrid")

class JourneyUpdateRequest(BaseModel):
    journey_id: str = Field(..., description="Journey ID to get updates for")

# ORIGINAL Global instances - PRESERVED + NEW journey_planner
db_manager = None
simulator = None
visualizer = None
journey_planner = None
driver_manager = None        # NEW
rush_hour_manager = None     # NEW
performance_manager = None   # NEW
active_connections: List[WebSocket] = []
DEBUG_LOG_PATH = "/home/muhammad/Desktop/FYP/.cursor/debug-a6bc00.log"


def _agent_debug_log(location: str, message: str, data: Dict[str, Any], run_id: str, hypothesis_id: str):
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown - ENHANCED but preserves original"""
    global db_manager, simulator, visualizer, journey_planner
    
    # Startup
    print("🚀 Starting Enhanced Metro Bus Multi-Route Simulation Engine...")
    print("🔧 Open http://localhost:8000/map to view live tracking")
    print("📊 API docs available at http://localhost:8000/docs")
    print("✨ Enhanced Bidirectional Features Active:")
    print("  • Alternating departures from both terminals")
    print("  • Bidirectional bus service (forward & reverse)")
    print("  • Scheduled departures every 10 seconds")
    print("  • Up to 10 buses per route")
    print("  • Persistent bus popups during updates")
    print("  • Enhanced traffic simulation")
    print("🤖 NEW: Traffic monitoring and AI-powered ETA predictions")
    print("🗺️ NEW: Intelligent Journey Planning and Multi-Route Connections")
    
    try:
        # Initialize components - SAME AS ORIGINAL
        print("🔧 Initializing database manager...")
        db_manager = DatabaseManager()
        print("✓ Database manager initialized")
        
        print("🚌 Initializing enhanced bidirectional bus simulator...")
        simulator = EnhancedMultiRouteBusSimulator(db_manager)
        print("✓ Enhanced bidirectional bus simulator initialized")
        
        print("🎫 Initializing E-Ticket system...")
        setup_eticket_routes(app, simulator)
        print("✓ E-Ticket system initialized")
        
        print("🗺️ Initializing map visualizer...")
        visualizer = MapVisualizer(simulator)
        print("✓ Map visualizer initialized")
        
        # NEW: Initialize Journey Planner if available
        if JOURNEY_PLANNING_AVAILABLE:
            print("🧠 Initializing Intelligent Connection Builder...")
            journey_planner = IntelligentConnectionBuilder(simulator, db_manager)
            print("✓ Intelligent Connection Builder initialized")
        else:
            print("⚠  Journey Planning features not available")

        # NEW: Initialize Advanced Managers if available
        if ADVANCED_MANAGERS_AVAILABLE:
            print("👔 Initializing Driver Roster Manager...")
            driver_manager = DriverRosterManager(db_manager, simulator)
            print("✓ Driver Roster Manager initialized")
            
            print("🚨 Initializing Rush Hour Analytics...")
            rush_hour_manager = RushHourAnalyticsManager(db_manager, simulator, driver_manager)
            print("✓ Rush Hour Analytics initialized")
            
            print("📈 Initializing Performance Analytics...")
            performance_manager = PerformanceAnalyticsManager(db_manager, simulator)
            print("✓ Performance Analytics initialized")
            
            # Inject dependencies into admin module
            if ADMIN_ENDPOINTS_AVAILABLE:
                import admin_endpoints
                admin_endpoints.driver_manager = driver_manager
                admin_endpoints.rush_hour_manager = rush_hour_manager
                admin_endpoints.performance_analytics = performance_manager
                admin_endpoints.simulator = simulator
                print("✓ Admin module dependencies injected")
        else:
            print("⚠ Advanced management features not available")
        
        # Start simulation - SAME AS ORIGINAL
        print("▶️ Starting enhanced bidirectional bus simulation...")
        simulator.start_simulation()
        print("✓ Enhanced bidirectional bus simulation started")
        
        # Start background broadcasting - SAME AS ORIGINAL
        print("📡 Starting WebSocket broadcast...")
        broadcast_task = asyncio.create_task(broadcast_updates())
        print("✓ WebSocket broadcast started")
        
    except Exception as e:
        print(f"âŒ Error during startup: {e}")
        raise
    
    
    # NEW: Initialize Admin Broadcaster
    if ADMIN_ENDPOINTS_AVAILABLE:
        try:
            from admin_endpoints import set_broadcaster
            
            async def broadcast_announcement_data(data):
                """Broadcast arbitrary data to all connected clients"""
                print(f"📡 DEBUG: broadcast_announcement_data called. Active connections: {len(active_connections)}")
                if not active_connections:
                    print("⚠️ DEBUG: No active connections to broadcast to.")
                    return
                
                print(f"📤 DEBUG: Sending data type '{data.get('type')}' to {len(active_connections)} clients")
                
                disconnected = []
                for connection in active_connections:
                    try:
                        await connection.send_json(data)
                    except Exception as e:
                        print(f"❌ Failed to send announcement to client: {e}")
                        disconnected.append(connection)
                
                # Cleanup disconnected
                for connection in disconnected:
                    if connection in active_connections:
                        active_connections.remove(connection)
                        print("❌ DEBUG: Removed disconnected client during broadcast")
                        
            set_broadcaster(broadcast_announcement_data)
            print("✓ Admin broadcaster initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize admin broadcaster: {e}")

    yield
    
    # Shutdown - SAME AS ORIGINAL
    print("🛑 Shutting down...")
    if simulator:
        simulator.stop_simulation()
    if 'broadcast_task' in locals():
        broadcast_task.cancel()
    print("🛑 Application shutdown complete!")

# Create FastAPI app - ENHANCED but preserves original info
app = FastAPI(
    title="Enhanced Metro Bus Bidirectional Simulation API", 
    description="Real-time multi-route metro bus tracking with bidirectional service, traffic monitoring, AI-powered ETA predictions, and intelligent journey planning",
    version="4.2.0",  # Incremented to show journey planning enhancement
    lifespan=lifespan
)

# ADD THIS RIGHT AFTER app creation:

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex="https?://.*",
    allow_credentials=False,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

    # ⭐ NEW: Register Admin Router
if ADMIN_ENDPOINTS_AVAILABLE:
    admin_router = get_admin_router()
    
    # Register the admin router
    app.include_router(admin_router)
    
    print("✓ Admin endpoints registered successfully")

# ORIGINAL ROOT ENDPOINT - Enhanced with journey planning info but preserves original structure
@app.get("/")
async def root():
    """Root endpoint - API status with enhanced features including journey planning"""
    bidirectional_stats = {}
    traffic_stats = {}
    eta_stats = {}
    journey_stats = {}
    
    if simulator and hasattr(simulator, 'get_bidirectional_statistics'):
        for route_id in simulator.active_routes:
            bidirectional_stats[route_id] = simulator.get_bidirectional_statistics(route_id)
    
    # NEW: Add traffic and ETA stats
    if simulator and hasattr(simulator, 'get_route_statistics'):
        all_stats = simulator.get_route_statistics()
        traffic_stats = all_stats.get('traffic_overview', {})
        eta_stats = all_stats.get('eta_statistics', {})
    
    # NEW: Add journey planning stats
    if journey_planner:
        journey_stats = {
            "transfer_points": len(journey_planner.transfer_points_cache) if hasattr(journey_planner, 'transfer_points_cache') else 0,
            "max_transfers": getattr(journey_planner, 'max_transfers', 3),
            "max_walking_distance_km": getattr(journey_planner, 'max_walking_distance_km', 0.5),
            "transfer_buffer_minutes": getattr(journey_planner, 'transfer_buffer_minutes', 5)
        }
    
    base_info = {
        "message": "Enhanced Metro Bus Bidirectional Simulation API with Journey Planning", 
        "status": "running",
        "version": "4.2.0",
        "enhanced_bidirectional_features": [
            "Alternating departures from both terminals (source & destination)",
            "Bidirectional bus service (forward & reverse directions)",
            "Intelligent bus scheduling every 10 seconds",
            "Up to 10 buses per route with balanced service",
            "Persistent bus popups during real-time updates",
            "Enhanced traffic simulation with realistic delays"
        ],
        # NEW: Add traffic and ETA features without removing original
        "enhanced_ai_features": [
            "Real-time traffic monitoring with color-coded visualization",
            "AI-powered ETA predictions with machine learning",
            "Traffic-aware bus movement simulation",
            "Historical data learning for improved accuracy",
            "Intelligent multi-route journey planning",
            "Optimal transfer point suggestions",
            "Real-time scheduling with ETA integration",
            "Smart connection builder with confidence scores"
        ],
        "debug_info": {
            "db_manager_status": "initialized" if db_manager else "not initialized",
            "simulator_status": "initialized" if simulator else "not initialized",
            "journey_planner": "initialized" if journey_planner else "not initialized",
            "active_connections": len(active_connections),
            "simulation_running": simulator.simulation_running if simulator else False,
            "available_routes": len(simulator.routes) if simulator else 0,
            "active_routes": len(simulator.active_routes) if simulator else 0,
            "total_buses": len(simulator.buses) if simulator else 0,
            "max_buses_per_route": getattr(simulator, 'max_buses_per_route', 10),
            "departure_interval": getattr(simulator, 'departure_interval', 10),
            "bidirectional_service": len(bidirectional_stats) > 0,
            # NEW: Add traffic and ETA info
            "traffic_segments": len(getattr(simulator, 'traffic_segments', {})),
            "eta_predictor": "active" if hasattr(simulator, 'eta_predictor') else "inactive",
            # NEW: Add journey planning info
            **journey_stats
        },
        "bidirectional_statistics": bidirectional_stats,
        # NEW: Add traffic and ETA statistics
        "traffic_overview": traffic_stats,
        "eta_overview": eta_stats,
        # NEW: Add journey planning statistics
        "journey_planning_overview": journey_stats,
        "endpoints": {
            # ORIGINAL endpoints - PRESERVED
            "live_map": "/map",
            "debug_map": "/debug-map",
            "api_status": "/api/simulation/status",
            "buses": "/api/buses",
            "routes": "/api/routes",
            "activate_route": "/api/routes/activate",
            "deactivate_route": "/api/routes/deactivate",
            "deactivate_all": "/api/routes/deactivate-all",
            "route_stats": "/api/routes/statistics",
            "bidirectional_stats": "/api/routes/{route_id}/bidirectional",
            "websocket": "/ws/live-tracking",
            # NEW endpoints - ADDED
            "traffic_data": "/api/traffic/current",
            "eta_predictions": "/api/eta/all",
            "bus_eta": "/api/eta/bus/{bus_id}",
            "route_traffic": "/api/traffic/route/{route_id}",
            # NEW: Journey Planning endpoints
            "plan_journey": "/api/journey/plan",
            "quick_journey_plan": "/api/journey/quick-plan",
            "journey_updates": "/api/journey/{journey_id}/updates", 
            "transfer_points": "/api/journey/transfer-points",
            "nearby_stops": "/api/journey/nearby-stops",
            "admin_statistics": "/api/admin/statistics",
            "admin_announcement": "/api/admin/announcement",
            "admin_alerts": "/api/admin/alerts",
            "admin_performance": "/api/admin/performance"
        }
    }
    
    return base_info

# ORIGINAL MAP ENDPOINT - PRESERVED
@app.get("/map", response_class=HTMLResponse)
async def show_map():
    """Display live map with enhanced features"""
    try:
        # Try to find the web template file - SAME AS ORIGINAL
        template_files = [
            "web_template.html",             # Your original template
            "enhanced_web_template.html",    # Enhanced template if available
            "bidirectional_template.html",   # Alternative name
            "web_interface.html"             # Fallback
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                with open(template_file, "r", encoding="utf-8") as file:
                    html_content = file.read()
                    print(f"✓ Successfully loaded {template_file}")
                    return html_content
        
        # Enhanced fallback HTML - IMPROVED but not breaking
        journey_features = ""
        if JOURNEY_PLANNING_AVAILABLE:
            journey_features = """
                    <li>🧠 Intelligent multi-route journey planning</li>
                    <li>🔄 Optimal transfer point suggestions</li>
                    <li>📊 Real-time scheduling with ETA integration</li>
                    <li>🎯 Smart connection builder with confidence scores</li>
            """
        
        return f"""
        <html>
        <head><title>Enhanced Metro Bus Bidirectional Tracking</title></head>
        <body style="font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; max-width: 700px; margin: 0 auto;">
                <h1>🚌 Enhanced Metro Bus Bidirectional System Ready!</h1>
                <h2>✨ Bidirectional Features Active:</h2>
                <ul style="text-align: left; margin: 20px 0;">
                    <li>↔️ Alternating departures from both terminals (source & destination)</li>
                    <li>🔄 Bidirectional bus service (forward & reverse directions)</li>
                    <li>📅 Intelligent scheduling every 10 seconds</li>
                    <li>🚌 Up to 10 buses per route with balanced service</li>
                    <li>📌 Persistent bus popups that don't disappear during updates</li>
                    <li>🤖 Enhanced traffic simulation with realistic behavior</li>
                    <li>📊 Real-time bidirectional statistics tracking</li>
                </ul>
                <h2>🤖 AI Features:</h2>
                <ul style="text-align: left; margin: 20px 0;">
                    <li>🤖 Real-time traffic monitoring with color visualization</li>
                    <li>🤖 AI-powered ETA predictions</li>
                    <li>📈 Historical data learning</li>
                    <li>🎯 Traffic-aware routing</li>
                    {journey_features}
                </ul>
                <p style="margin: 20px 0;">Enhanced template file missing. Please ensure the enhanced web template is available.</p>
                <div style="margin: 20px 0;">
                    <a href="/docs" style="color: #fff; text-decoration: underline; margin: 10px;">API Documentation</a>
                    <a href="/api/routes" style="color: #fff; text-decoration: underline; margin: 10px;">View Routes</a>
                    <a href="/api/traffic/current" style="color: #fff; text-decoration: underline; margin: 10px;">Traffic Data</a>
                    {"<a href='/api/journey/transfer-points' style='color: #fff; text-decoration: underline; margin: 10px;'>Transfer Points</a>" if JOURNEY_PLANNING_AVAILABLE else ""}
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"âŒ Error loading template: {e}")
        return f"<html><body><h1>Error loading template: {e}</h1><p><a href='/docs'>Go to API Documentation</a></p></body></html>"

# ADD THIS NEW ENDPOINT TO main.py (after the /map endpoint)

# ADD THIS TO main.py - After the root endpoint

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Display admin dashboard for metro authorities"""
    try:
        admin_file = "admin_dashboard.html"
        
        if os.path.exists(admin_file):
            with open(admin_file, "r", encoding="utf-8") as file:
                html_content = file.read()
                print(f"✓ Successfully loaded {admin_file}")
                return html_content
        
        return """
        <html>
        <head><title>Admin Dashboard Not Found</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>⚠️ Admin Dashboard Template Missing</h1>
            <p>Please ensure <code>admin_dashboard.html</code> exists in the project root directory.</p>
            <p><a href="/">Go to Main Map</a> | <a href="/docs">API Documentation</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"❌ Error loading admin dashboard: {e}")
        return f"<html><body><h1>Error: {e}</h1><p><a href='/'>Go to Main Map</a></p></body></html>"


# ORIGINAL SIMULATION STATUS ENDPOINT - Enhanced but preserves original behavior
@app.get("/api/simulation/status")
async def get_simulation_status():
    """Get current simulation data with enhanced information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        # Use enhanced method if available, otherwise fall back to original
        if hasattr(simulator, 'get_simulation_data_with_bidirectional_info'):
            data = simulator.get_simulation_data_with_bidirectional_info()
        else:
            data = simulator.get_simulation_data()
        
        # Enhanced logging with additional info
        buses_count = len(data.get('buses', []))
        routes_count = len(data.get('active_routes', []))
        forward_buses = data.get('service_summary', {}).get('forward_buses', 0)
        reverse_buses = data.get('service_summary', {}).get('reverse_buses', 0)
        traffic_segments = len(data.get('traffic_segments', {}))
        
        print(f"📊 Enhanced status: {buses_count} buses on {routes_count} routes "
              f"({forward_buses} forward, {reverse_buses} reverse), {traffic_segments} traffic segments")
        
        return data
    except Exception as e:
        print(f"âŒ Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW ENDPOINTS - Traffic and ETA (ADDED without replacing anything)
@app.get("/api/traffic/current")
async def get_current_traffic():
    """Get current traffic conditions for all segments"""
    if not simulator or not hasattr(simulator, 'get_traffic_data_for_frontend'):
        raise HTTPException(status_code=500, detail="Traffic system not available")
    
    try:
        traffic_data = simulator.get_traffic_data_for_frontend()
        
        # Calculate summary statistics
        all_levels = [seg['traffic_level'] for seg in traffic_data.values()]
        summary = {
            'total_segments': len(traffic_data),
            'average_traffic_level': sum(all_levels) / len(all_levels) if all_levels else 1.0,
            'heavy_traffic_count': len([l for l in all_levels if l <= 0.3]),
            'moderate_traffic_count': len([l for l in all_levels if 0.3 < l <= 0.6]),
            'light_traffic_count': len([l for l in all_levels if l > 0.6]),
            'last_updated': simulator.last_traffic_update.isoformat() if hasattr(simulator, 'last_traffic_update') else None
        }
        
        return {
            'traffic_segments': traffic_data,
            'summary': summary,
            'legend': {
                'heavy_traffic': {'color': '#DC3545', 'description': 'Heavy Traffic (0-30% of normal speed)'},
                'moderate_traffic': {'color': '#FFC107', 'description': 'Moderate Traffic (30-60% of normal speed)'},
                'light_traffic': {'color': '#28A745', 'description': 'Light Traffic (60-90% of normal speed)'},
                'free_flow': {'color': '#007CBA', 'description': 'Free Flow (90%+ of normal speed)'}
            }
        }
    except Exception as e:
        print(f"Error getting traffic data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eta/all")
async def get_all_etas():
    """Get ETA predictions for all active buses"""
    if not simulator or not hasattr(simulator, 'get_all_bus_etas'):
        raise HTTPException(status_code=500, detail="ETA system not available")
    
    try:
        all_etas = simulator.get_all_bus_etas()
        
        # Calculate summary statistics
        total_predictions = sum(len(bus_etas) for bus_etas in all_etas.values())
        
        return {
            'bus_etas': all_etas,
            'summary': {
                'total_buses_with_etas': len(all_etas),
                'total_eta_predictions': total_predictions
            },
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting ETA data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eta/bus/{bus_id}")
async def get_bus_eta(bus_id: str):
    """Get ETA predictions for a specific bus"""
    if not simulator or not hasattr(simulator, 'eta_predictor'):
        raise HTTPException(status_code=500, detail="ETA system not available")
    
    if bus_id not in simulator.buses:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    try:
        bus = simulator.buses[bus_id]
        route = simulator.routes.get(bus.route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        etas = simulator.eta_predictor.predict_eta_to_stops(bus, route, simulator.traffic_segments)
        
        return {
            'bus_id': bus_id,
            'route_id': bus.route_id,
            'route_name': route.name,
            'current_direction': bus.direction,
            'current_position': {
                'lat': bus.current_lat,
                'lng': bus.current_lng,
                'speed': bus.speed,
                'status': bus.status
            },
            'etas': etas,
            'next_stops_count': len(etas)
        }
    except Exception as e:
        print(f"Error getting bus ETA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW ENDPOINTS - Journey Planning (ADDED without replacing anything)
@app.post("/api/journey/plan")
async def plan_journey(request: JourneyPlanRequest):
    if not journey_planner:
        raise HTTPException(status_code=503, detail="Journey planning not available")
    try:
        _agent_debug_log(
            location="main.py:/api/journey/plan:entry",
            message="Journey planning request received",
            data={
                "has_origin_stop": bool(request.origin_stop),
                "has_destination_stop": bool(request.destination_stop),
                "has_origin_latlng": request.origin_lat is not None and request.origin_lng is not None,
                "has_destination_latlng": request.destination_lat is not None and request.destination_lng is not None,
                "preference": request.preference,
                "max_transfers": request.max_transfers
            },
            run_id="run1",
            hypothesis_id="H2"
        )
        max_transfers = request.max_transfers or 2
        preference = (request.preference or 'hybrid').lower()

        if request.origin_stop and request.destination_stop:
            journey_options = await journey_planner.plan_journey_by_stops(
                origin_name=request.origin_stop,
                dest_name=request.destination_stop,
                max_transfers=max_transfers,
                preference=preference,
            )
            planning_mode = "stop_to_stop"
        else:
            if None in (request.origin_lat, request.origin_lng, request.destination_lat, request.destination_lng):
                raise HTTPException(
                    status_code=422,
                    detail="Provide either origin_stop/destination_stop OR full origin/destination coordinates."
                )
            journey_options = await journey_planner.plan_journey(
                origin_lat=request.origin_lat,
                origin_lng=request.origin_lng,
                dest_lat=request.destination_lat,
                dest_lng=request.destination_lng,
                max_transfers=max_transfers,
                preference=preference,
            )
            planning_mode = "location_to_location"
        if not journey_options:
            _agent_debug_log(
                location="main.py:/api/journey/plan:no_results",
                message="Journey planner returned no options",
                data={"planning_mode": planning_mode},
                run_id="run1",
                hypothesis_id="H4"
            )
            return {"success": False, "message": "No viable journey routes found",
                    "suggestions": ["Try different stops", "Increase max transfers",
                                    "Check active routes"]}
        summaries = [journey_planner.get_journey_summary(j) for j in journey_options]
        _agent_debug_log(
            location="main.py:/api/journey/plan:success",
            message="Journey planner returned options",
            data={"planning_mode": planning_mode, "journey_count": len(summaries)},
            run_id="run1",
            hypothesis_id="H2"
        )
        return {
            "success": True,
            "planning_mode": planning_mode,
            "journey_count": len(summaries),
            "best": summaries[0],
            "journeys": summaries
        }
    except Exception as e:
        _agent_debug_log(
            location="main.py:/api/journey/plan:exception",
            message="Journey planning endpoint exception",
            data={"error": str(e), "traceback": traceback.format_exc()},
            run_id="run1",
            hypothesis_id="H2"
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/journey/plan-by-stops")
async def plan_journey_by_stops(request: JourneyStopRequest):
    if not journey_planner:
        raise HTTPException(status_code=503, detail="Journey planning not available")
    try:
        journey_options = await journey_planner.plan_journey_by_stops(
            origin_name=request.origin_stop,
            dest_name=request.destination_stop,
            max_transfers=request.max_transfers or 2,
            preference=request.preference or 'hybrid',
        )
        if not journey_options:
            return {"success": False, "message": "No routes found between these stops",
                    "suggestions": ["Check stop names are correct", "Try increasing max transfers"]}
        summaries = [journey_planner.get_journey_summary(j) for j in journey_options]
        return {
            "success": True,
            "planning_mode": "stop_to_stop",
            "journey_count": len(summaries),
            "best": summaries[0],
            "journeys": summaries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/journey/{journey_id}/updates")
async def get_journey_updates(journey_id: str):
    """
    Get real-time updates for an active journey
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        updates = await journey_planner.get_real_time_journey_updates(journey_id)
        
        return {
            "success": True,
            "journey_id": journey_id,
            "updates": updates,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting journey updates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get journey updates: {str(e)}")

@app.get("/api/journey/transfer-points")
async def get_transfer_points():
    """
    Get all available transfer points in the network
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        transfer_points = []
        
        for point in journey_planner.transfer_points_cache.values():
            transfer_points.append({
                "id": point.stop_id,
                "name": point.stop_name,
                "location": [point.latitude, point.longitude],
                "connected_routes": point.routes,
                "transfer_time_minutes": point.transfer_time_minutes,
                "accessibility_features": point.accessibility_features,
                "route_colors": [
                    journey_planner._get_route_color(route_id) 
                    for route_id in point.routes
                ]
            })
        
        transfer_points = journey_planner.get_all_transfer_points()
        return {"success": True, "transfer_points": transfer_points,
                "total_count": len(transfer_points)}
        
    except Exception as e:
        print(f"Error getting transfer points: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transfer points: {str(e)}")

@app.post("/api/journey/quick-plan")
async def quick_journey_plan(
    origin_lat: float, 
    origin_lng: float, 
    dest_lat: float, 
    dest_lng: float,
    max_transfers: Optional[int] = 2
):
    """
    Quick journey planning endpoint with minimal parameters
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        # Set simplified preferences
        preferences = {
            'time_weight': 0.5,
            'transfer_weight': 0.3,
            'walking_weight': 0.2,
            'allow_multiple_transfers': max_transfers > 0
        }
        
        # Use current journey planner max_transfers if specified max is higher
        journey_planner.max_transfers = min(max_transfers, journey_planner.max_transfers)
        
        journey_options = await journey_planner.plan_journey(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            preferences=preferences
        )
        
        if not journey_options:
            return {
                "success": False,
                "message": "No routes found between these locations",
                "quick_suggestions": [
                    f"Try locations within {journey_planner.max_walking_distance_km:.1f}km of bus stops",
                    "Ensure at least one route is currently active",
                    "Consider increasing max_transfers parameter"
                ]
            }
        
        # Return simplified response with just the best option
        best_journey = journey_options[0]
        summary = journey_planner.get_journey_summary(best_journey)
        
        return {
            "success": True,
            "message": "Quick route found",
            "recommended_journey": {
                "journey_id": summary["journey_id"],
                "total_time_minutes": summary["summary"]["total_duration_minutes"],
                "transfers_required": summary["summary"]["transfers_required"],
                "total_fare": summary["summary"]["total_fare"],
                "departure_time": summary["summary"]["departure_time"],
                "arrival_time": summary["summary"]["arrival_time"],
                "confidence": summary["summary"]["confidence_score"],
                "routes": [seg["route_id"] for seg in summary["segments"]],
                "step_by_step": summary["instructions"][:5]  # First 5 steps only
            },
            "alternatives_available": len(journey_options) - 1,
            "search_info": {
                "origin": [origin_lat, origin_lng],
                "destination": [dest_lat, dest_lng],
                "max_transfers_used": max_transfers
            }
        }
        
    except Exception as e:
        print(f"Error in quick journey planning: {e}")
        raise HTTPException(status_code=500, detail=f"Quick planning failed: {str(e)}")

@app.get("/api/journey/nearby-stops")
async def get_nearby_stops(lat: float, lng: float, radius_km: float = 0.5):
    """
    Find nearby bus stops for journey planning
    """
    if not journey_planner:
        if JOURNEY_PLANNING_AVAILABLE:
            raise HTTPException(status_code=500, detail="Journey planner not initialized")
        else:
            raise HTTPException(status_code=503, detail="Journey planning not available")
    
    try:
        # Use journey planner's method to find nearby stops
        nearby_stops = journey_planner._find_nearby_stops(lat, lng, radius_km)
        
        # Group by route for better organization
        stops_by_route = {}
        for stop in nearby_stops:
            route_id = stop['route_id']
            if route_id not in stops_by_route:
                route = simulator.routes.get(route_id)
                stops_by_route[route_id] = {
                    'route_id': route_id,
                    'route_name': route.name if route else route_id,
                'route_color': journey_planner._get_route_color(route_id),
                    'is_active': route_id in simulator.active_routes if simulator else False,
                    'stops': []
                }
            
            stops_by_route[route_id]['stops'].append({
                'stop_name': stop['stop_name'],
                'stop_index': stop['stop_idx'],
                'location': [stop['latitude'], stop['longitude']],
                'distance_km': round(stop['distance_km'], 3),
                'walk_time_minutes': round(stop['walk_min'], 1)
            })
        
        return {
            "success": True,
            "search_location": [lat, lng],
            "search_radius_km": radius_km,
            "routes_found": len(stops_by_route),
            "total_stops_found": len(nearby_stops),
            "nearby_routes": list(stops_by_route.values()),
            "closest_stop": nearby_stops[0] if nearby_stops else None
        }
        
    except Exception as e:
        print(f"Error finding nearby stops: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find nearby stops: {str(e)}")

# ORIGINAL ROUTES ENDPOINT - Enhanced with traffic info but preserves original structure
@app.get("/api/routes")
async def get_available_routes():
    """Get all available routes with enhanced information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        routes = simulator.get_available_routes()
        response = {
            "routes": routes,
            "total_routes": len(routes),
            "active_routes": len([r for r in routes if r['active']]),
            "max_buses_per_route": getattr(simulator, 'max_buses_per_route', 10),
            "departure_interval_seconds": getattr(simulator, 'departure_interval', 10),
            "bidirectional_features": {
                "alternating_departures": True,
                "bidirectional_service": True,
                "terminal_based_scheduling": True,
                "intelligent_bus_distribution": True,
                "persistent_popups": True,
                "enhanced_traffic": True
            },
            # NEW: Add traffic and ETA info
            "enhanced_ai_features": {
                "traffic_monitoring": hasattr(simulator, 'traffic_segments'),
                "eta_predictions": hasattr(simulator, 'eta_predictor'),
                "historical_learning": True,
                "real_time_updates": True,
                "journey_planning": JOURNEY_PLANNING_AVAILABLE and journey_planner is not None
            },
            "service_statistics": {
                "terminals_per_route": 2,
                "departure_pattern": "alternating_between_terminals",
                "max_buses_per_direction": 5
            }
        }
        
        return response
    except Exception as e:
        print(f"Error getting routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ORIGINAL ACTIVATE ROUTE ENDPOINT - Enhanced with additional info but preserves original behavior
@app.post("/api/routes/activate")
async def activate_route(request: RouteActivationRequest):
    """Activate a route with enhanced features"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        # Cap the number of buses to the simulator's maximum - SAME AS ORIGINAL
        max_buses = getattr(simulator, 'max_buses_per_route', 10)
        num_buses = min(request.num_buses, max_buses)
        
        # Use enhanced bidirectional activation method - SAME AS ORIGINAL
        if hasattr(simulator, 'activate_route_with_bidirectional_service'):
            success = simulator.activate_route_with_bidirectional_service(request.route_id, num_buses)
        else:
            success = simulator.activate_route(request.route_id, num_buses)
            
        if success:
            response_data = {
                "success": True,
                "message": f"Route {request.route_id} activated with bidirectional service",
                "route_id": request.route_id,
                "buses_requested": request.num_buses,
                "buses_activated": num_buses,
                "max_buses": max_buses,
                "departure_interval": getattr(simulator, 'departure_interval', 10),
                "bidirectional_features": [
                    "Alternating departures from both terminals",
                    "Forward and reverse direction buses",
                    "Intelligent terminal-based scheduling",
                    "Balanced service distribution",
                    "Enhanced traffic simulation"
                ]
            }
            
            # NEW: Add traffic and ETA info if available
            if hasattr(simulator, 'get_bidirectional_statistics'):
                response_data["bidirectional_statistics"] = simulator.get_bidirectional_statistics(request.route_id)
            
            if hasattr(simulator, 'traffic_segments'):
                response_data["enhanced_features_enabled"] = [
                    "Real-time traffic monitoring",
                    "AI-powered ETA predictions",
                    "Traffic-responsive bus speeds"
                ]
            
            # NEW: Add journey planning info if available
            if journey_planner:
                response_data["journey_planning_features"] = [
                    "Multi-route journey planning available",
                    "Transfer point optimization",
                    "Real-time connection updates"
                ]
            
            return response_data
        else:
            raise HTTPException(status_code=400, detail=f"Failed to activate route {request.route_id}")
    except Exception as e:
        print(f"Error activating route {request.route_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ORIGINAL ENDPOINTS - All preserved exactly
@app.get("/api/routes/{route_id}/bidirectional")
async def get_route_bidirectional_stats(route_id: str):
    """Get detailed bidirectional statistics for a specific route"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    if route_id not in simulator.routes:
        raise HTTPException(status_code=404, detail=f"Route {route_id} not found")
    
    try:
        if hasattr(simulator, 'get_bidirectional_statistics'):
            stats = simulator.get_bidirectional_statistics(route_id)
            return stats
        else:
            # Fallback: basic statistics
            route_buses = [bus for bus in simulator.buses.values() if bus.route_id == route_id]
            forward_buses = [b for b in route_buses if b.direction == 'forward']
            reverse_buses = [b for b in route_buses if b.direction == 'reverse']
            
            return {
                "route_id": route_id,
                "total_buses": len(route_buses),
                "forward_direction": {"count": len(forward_buses)},
                "reverse_direction": {"count": len(reverse_buses)},
                "service_balance": {
                    "forward_percentage": (len(forward_buses) / len(route_buses) * 100) if route_buses else 0,
                    "reverse_percentage": (len(reverse_buses) / len(route_buses) * 100) if route_buses else 0
                }
            }
    except Exception as e:
        print(f"Error getting bidirectional statistics for route {route_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/routes/statistics")
async def get_route_statistics():
    """Get enhanced statistics with traffic and ETA information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        stats = simulator.get_route_statistics()
        
        # Add bidirectional summary if method exists - SAME AS ORIGINAL
        if hasattr(simulator, 'get_bidirectional_statistics'):
            bidirectional_summary = {}
            for route_id in simulator.active_routes:
                bidirectional_summary[route_id] = simulator.get_bidirectional_statistics(route_id)
            
            stats['bidirectional_service_summary'] = bidirectional_summary
            stats['total_terminals_served'] = len(simulator.active_routes) * 2
            stats['alternating_departures_active'] = len(simulator.active_routes) > 0
        
        return stats
    except Exception as e:
        print(f"Error getting route statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/buses")
async def get_all_buses():
    """Get all active buses with enhanced information"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        data = simulator.get_simulation_data()
        buses = data.get('buses', [])
        
        # Enhanced bus statistics with bidirectional info - PRESERVED ORIGINAL + NEW
        direction_stats = {
            "forward": len([b for b in buses if b.get('direction') == 'forward']),
            "reverse": len([b for b in buses if b.get('direction') == 'reverse'])
        }
        
        # Terminal-based statistics
        terminal_stats = {}
        for bus in buses:
            route_id = bus.get('route_id')
            direction = bus.get('direction', 'forward')
            if route_id not in terminal_stats:
                terminal_stats[route_id] = {"forward": 0, "reverse": 0}
            terminal_stats[route_id][direction] += 1
        
        response_data = {
            "buses": buses,
            "total_buses": len(buses),
            "routes_with_buses": len(set(bus['route_id'] for bus in buses)),
            "total_background_buses": data.get('total_background_buses', 0),
            "bidirectional_statistics": {
                "direction_distribution": direction_stats,
                "terminal_distribution": terminal_stats,
                "service_balance": {
                    "forward_percentage": (direction_stats["forward"] / len(buses) * 100) if buses else 0,
                    "reverse_percentage": (direction_stats["reverse"] / len(buses) * 100) if buses else 0
                }
            },
            "bus_statuses": {
                "at_stops": len([b for b in buses if b.get('is_at_stop')]),
                "delayed": len([b for b in buses if b.get('status') == 'delayed']),
                "moving": len([b for b in buses if b.get('status') == 'moving']),
                "in_traffic": len([b for b in buses if b.get('speed', 0) < 10 and not b.get('is_at_stop')])
            }
        }
        
        # NEW: Add traffic and ETA statistics if available
        if hasattr(simulator, 'get_all_bus_etas'):
            all_etas = simulator.get_all_bus_etas()
            response_data["eta_information"] = {
                "buses_with_etas": len(all_etas),
                "total_eta_predictions": sum(len(bus_etas) for bus_etas in all_etas.values()),
                "average_predictions_per_bus": sum(len(bus_etas) for bus_etas in all_etas.values()) / len(buses) if buses else 0
            }
        
        return response_data
    except Exception as e:
        print(f"Error getting buses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ORIGINAL ENDPOINTS - Preserved exactly
@app.post("/api/routes/deactivate")
async def deactivate_route(request: RouteDeactivationRequest):
    """Deactivate a specific route"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        simulator.deactivate_route(request.route_id)
        return {
            "success": True,
            "message": f"Route {request.route_id} deactivated",
            "route_id": request.route_id,
            "note": "Bidirectional buses may continue running in background simulation"
        }
    except Exception as e:
        print(f"Error deactivating route {request.route_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/routes/deactivate-all")
async def deactivate_all_routes():
    """Deactivate all active routes"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        deactivated_routes = list(simulator.active_routes)
        for route_id in deactivated_routes:
            simulator.deactivate_route(route_id)
        
        return {
            "success": True,
            "message": f"Deactivated {len(deactivated_routes)} routes",
            "deactivated_routes": deactivated_routes,
            "note": "All bidirectional buses continue running in background"
        }
    except Exception as e:
        print(f"Error deactivating all routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# Setup E-Ticket routes
#setup_eticket_routes(app, simulator)

@app.post("/api/eticket/login")
async def eticket_login(request: dict):
    """Login user"""
    try:
        with open("eticket_users.json", 'r') as f:
            data = json.load(f)
        
        # Find user
        user = next((u for u in data['users'] if u['email'] == request['email']), None)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        if user['password'] != request['password']:
            return {"success": False, "message": "Invalid password"}
        
        # Return user without password
        user_response = {k: v for k, v in user.items() if k != 'password'}
        
        return {
            "success": True,
            "message": "Login successful",
            "user": user_response
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/eticket/active-routes")
async def get_active_routes_for_ticket():
    """Get only currently active routes with buses"""
    try:
        active_routes_list = []
        
        for route_id in simulator.active_routes:
            route = simulator.routes.get(route_id)
            if route:
                # Get active buses for this route
                route_buses = [bus for bus in simulator.buses.values() 
                             if bus.route_id == route_id and bus.status == 'active']
                
                if route_buses:  # Only include routes with active buses
                    # Calculate fare based on distance (Rs. 10 per km, minimum Rs. 20)
                    fare = max(20, int(route.total_distance * 10))
                    
                    active_routes_list.append({
                        "route_id": route_id,
                        "name": route.name,
                        "source": route.source,
                        "destination": route.destination,
                        "fare": fare,
                        "active_buses": len(route_buses),
                        "distance": round(route.total_distance, 1)
                    })
        
        return {
            "success": True,
            "routes": active_routes_list,
            "total_active": len(active_routes_list)
        }
        
    except Exception as e:
        return {"success": False, "message": str(e), "routes": []}

@app.post("/api/eticket/topup")
async def eticket_topup(request: dict):
    """Top up user wallet"""
    try:
        with open("eticket_users.json", 'r') as f:
            data = json.load(f)
        
        # Find user
        user = next((u for u in data['users'] if u['email'] == request['email']), None)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Add amount to balance
        user['balance'] += int(request['amount'])
        
        # Save to file
        with open("eticket_users.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            "success": True,
            "message": "Top-up successful",
            "new_balance": user['balance']
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/eticket/purchase")
async def eticket_purchase(request: dict):
    """Purchase E-Ticket"""
    try:
        with open("eticket_users.json", 'r') as f:
            data = json.load(f)
        
        # Find user
        user = next((u for u in data['users'] if u['email'] == request['email']), None)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Check if route is active
        if request['route_id'] not in simulator.active_routes:
            return {"success": False, "message": "Route not active"}
        
        # Calculate fare (free for seniors)
        fare = 0 if user['is_senior'] else int(request['fare'])
        
        # Check balance if using wallet
        if request.get('payment_method') == 'wallet':
            if user['balance'] < fare:
                return {"success": False, "message": "Insufficient balance"}
            
            user['balance'] -= fare
            
            # Save to file
            with open("eticket_users.json", 'w') as f:
                json.dump(data, f, indent=2)
        
        return {
            "success": True,
            "message": "Ticket purchased successfully",
            "ticket": {
                "route_id": request['route_id'],
                "fare": fare,
                "is_free": user['is_senior'],
                "payment_method": request.get('payment_method'),
                "timestamp": datetime.now().isoformat()
            },
            "new_balance": user['balance']
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}
# ORIGINAL WEBSOCKET - Enhanced with additional data but preserves original behavior
@app.websocket("/ws/live-tracking")
async def websocket_endpoint(websocket: WebSocket):
    """Enhanced WebSocket endpoint for real-time tracking"""
    print(f"📡 New WebSocket connection attempt from {websocket.client}")
    
    try:
        await websocket.accept()
        active_connections.append(websocket)
        print(f"✓ WebSocket connected. Total connections: {len(active_connections)}")
        
        # Send initial enhanced data immediately - SAME AS ORIGINAL but enhanced
        if simulator:
            try:
                if hasattr(simulator, 'get_simulation_data_with_bidirectional_info'):
                    initial_data = simulator.get_simulation_data_with_bidirectional_info()
                else:
                    initial_data = simulator.get_simulation_data()
                
                # Use serializer for initial data
                from bus_simulator import serialize_for_json
                initial_data = serialize_for_json(initial_data)
                
                await websocket.send_json(initial_data)
                print("📤 Sent initial enhanced data to new client")
            except Exception as e:
                print(f"âŒ Error sending initial data: {e}")
        
        # Keep connection alive - SAME AS ORIGINAL
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if message == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.ping()
            except Exception as e:
                print(f"âŒ WebSocket message error: {e}")
                break
                
    except WebSocketDisconnect:
        print("📡 WebSocket disconnected normally")
    except Exception as e:
        print(f"âŒ WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"📡 WebSocket removed. Remaining connections: {len(active_connections)}")

# ORIGINAL BROADCAST - Enhanced with additional data but preserves original behavior
async def broadcast_updates():
    """Enhanced broadcast updates with traffic and ETA information"""
    print("📡 Starting enhanced background broadcast task...")
    
    try:
        while True:
            if active_connections and simulator:
                try:
                    # Use enhanced method if available
                    if hasattr(simulator, 'get_simulation_data_with_bidirectional_info'):
                        data = simulator.get_simulation_data_with_bidirectional_info()
                    else:
                        data = simulator.get_simulation_data()
                    
                    # ✓ FIX: Import and use the serializer
                    from bus_simulator import serialize_for_json
                    data = serialize_for_json(data)  # Convert ALL datetime objects
                    
                    disconnected = []
                    
                    for connection in active_connections:
                        try:
                            await connection.send_json(data)
                        except Exception as e:
                            print(f"âŒ Failed to send to client: {e}")
                            disconnected.append(connection)
                    
                    # Remove disconnected clients
                    for connection in disconnected:
                        if connection in active_connections:
                            active_connections.remove(connection)
                    
                    if len(active_connections) > 0:
                        buses_count = len(data.get('buses', []))
                        routes_count = len(data.get('active_routes', []))
                        forward_buses = data.get('service_summary', {}).get('forward_buses', 0)
                        reverse_buses = data.get('service_summary', {}).get('reverse_buses', 0)
                        
                        print(f"📤 Broadcast to {len(active_connections)} clients - "
                              f"{buses_count} buses on {routes_count} routes "
                              f"({forward_buses} forward, {reverse_buses} reverse)")
                        
                except Exception as e:
                    print(f"âŒ Broadcast error: {e}")
            
            await asyncio.sleep(3)  # Broadcast every 3 seconds - SAME AS ORIGINAL
            
    except asyncio.CancelledError:
        print("📡 Enhanced broadcast task cancelled")
        raise
    except Exception as e:
        print(f"âŒ Broadcast task error: {e}")

# ORIGINAL MAIN FUNCTION - Enhanced with additional info but preserves original structure
def main():
    """Main entry point with enhanced features information"""
    print("🚀 Enhanced Metro Bus Bidirectional Multi-Route Simulation Engine")
    print("=" * 70)
    
    # Check file dependencies - SAME AS ORIGINAL
    required_files = ["models.py", "database_manager.py", "map_visualizer.py", "bus_simulator.py"]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✓ {file} found")
    
    # Check for optional journey planner
    if os.path.exists("journey_planner.py"):
        print(f"✓ journey_planner.py found - Journey planning features available")
    else:
        print(f"⚠ journey_planner.py not found - Journey planning features disabled")
    
    if missing_files:
        print(f"âŒ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all required files are in the same directory")
        return
    
    print("\n✨ Bidirectional Features:")
    print("• Alternating departures from both terminals (source & destination)")
    print("• Bidirectional bus service (forward & reverse directions)")
    print("• Intelligent scheduling every 10 seconds with terminal rotation")
    print("• Up to 10 buses per route with balanced service distribution")
    print("• Persistent bus popups that don't disappear on updates")
    print("• Enhanced traffic simulation with realistic bus behavior")
    print("• Real-time WebSocket updates with bidirectional statistics")
    print("• Background bus simulation for optimal resource management")
    
    print("\n🤖 AI Features:")
    print("• Real-time traffic monitoring with color-coded visualization")
    print("• AI-powered ETA predictions using machine learning")
    print("• Traffic-aware bus movement simulation")
    print("• Historical data learning for improved accuracy over time")
    
    if JOURNEY_PLANNING_AVAILABLE:
        print("\n🧠 Journey Planning Features:")
        print("• Intelligent multi-route journey planning")
        print("• Optimal transfer point suggestions")
        print("• Real-time scheduling with ETA integration")
        print("• Smart connection builder with confidence scores")
        print("• Quick journey planning for immediate routes")
        print("• Nearby stops discovery and route optimization")
    
    try:
        print("\n🚀 Starting Enhanced Metro Bus Simulation Server...")
        print("📍 Access the application at:")
        print("   • Live Map: http://localhost:8000/map")
        print("   • Admin Dashboard: http://localhost:8000/admin")  # ⭐ ADD THIS
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • API Status: http://localhost:8000")
        print("   • Traffic Data: http://localhost:8000/api/traffic/current")
        print("   • ETA Predictions: http://localhost:8000/api/eta/all")
        
        if JOURNEY_PLANNING_AVAILABLE:
            print("   • Transfer Points: http://localhost:8000/api/journey/transfer-points")
            print("   • Journey Planning: http://localhost:8000/api/journey/plan")
        
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested by user")
    except Exception as e:
        print(f"âŒ Server error: {e}")

if __name__ == "__main__":
    main()
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
