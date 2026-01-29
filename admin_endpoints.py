"""
admin_endpoints.py
==================
NEW FILE - Add this to your project root directory
Contains all admin-specific API endpoints for the Metro Bus Management System

Integration: Import this in main.py after the existing endpoints
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import traceback

# Create admin router
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

# Broadcaster callback - to be set by main application
_broadcaster = None
simulator = None

def set_broadcaster(func):
    """Set the broadcaster function for real-time updates"""
    global _broadcaster
    _broadcaster = func


# Request models
class AnnouncementRequest(BaseModel):
    route_id: Optional[str] = None
    message: str
    priority: str = "high"

class DriverAssignmentRequest(BaseModel):
    driver_id: str
    shift_id: str
    date: Optional[str] = None

class DriverPerformanceUpdate(BaseModel):
    driver_id: str
    on_time_performance: Optional[float] = None
    passenger_complaints: Optional[int] = None
    passenger_compliments: Optional[int] = None
    fuel_efficiency_score: Optional[float] = None
    accidents_count: Optional[int] = None


# Admin Statistics Endpoint
@admin_router.get("/statistics")
async def get_admin_statistics():
    """Get comprehensive statistics for admin dashboard"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        stats = simulator.get_route_statistics()
        
        # Calculate system health metrics
        total_buses = len(simulator.buses)
        active_buses = len([b for b in simulator.buses.values() if b.route_id in simulator.active_routes])
        delayed_buses = len([b for b in simulator.buses.values() if b.status == 'delayed'])
        
        system_health = {
            'status': 'healthy' if delayed_buses / max(total_buses, 1) < 0.1 else 'warning',
            'uptime_percentage': 99.8,
            'active_routes_percentage': (len(simulator.active_routes) / max(len(simulator.routes), 1)) * 100,
            'buses_on_time_percentage': ((total_buses - delayed_buses) / max(total_buses, 1)) * 100,
            'total_passengers_today': total_buses * 45,
            'total_trips_completed': sum(r.get('scheduled_total_buses', 0) for r in simulator.route_schedules.values())
        }
        
        return {
            'success': True,
            'statistics': stats,
            'system_health': system_health,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting admin statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Announcement Broadcast Endpoint
@admin_router.post("/announcement")
async def broadcast_announcement(request: AnnouncementRequest):
    """Broadcast announcement to specific route or all routes"""
    print(f"🔔 DEBUG: broadcast_announcement called for route {request.route_id} with message: {request.message}")
    
    if not simulator:
        print("❌ DEBUG: Simulator not initialized in broadcast_announcement")
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        # Create announcement payload
        announcement_data = {
            'id': f"ann_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'message': request.message,
            'route_id': request.route_id,
            'priority': request.priority,
            'timestamp': datetime.now().isoformat(),
            'sender': 'Admin Control'
        }
        
        # Log announcement
        print(f"📢 Admin Announcement: [{request.route_id or 'ALL'}] {request.message}")

        # Broadcast via WebSocket
        if _broadcaster:
            await _broadcaster({
                'type': 'announcement',
                'payload': announcement_data
            })
            print("✓ Announcement sent to broadcaster")
        else:
            print("⚠ Broadcaster not initialized - announcement not sent to clients")
        
        return {
            'success': True,
            'message': 'Announcement broadcasted successfully',
            'announcement': announcement_data
        }
    except Exception as e:
        print(f"Error broadcasting announcement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/deploy-bus")
async def deploy_extra_bus(route_id: str):
    """Deploy an extra bus service immediately"""
    print(f"DEBUG: Deploy request for route_id='{route_id}'")
    if not simulator:
        print("DEBUG: Simulator is None!")
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        success, message = simulator.add_extra_bus(route_id)
        if not success:
            print(f"DEBUG: add_extra_bus failed: {message}")
            raise HTTPException(status_code=400, detail=message)
            
        print(f"✅ BUS DEPLOYMENT: {message}")
        return {
            "success": True, 
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error deploying bus: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Real-time Alerts Endpoint
@admin_router.get("/alerts")
async def get_system_alerts(simulator):
    """Get real-time system alerts and warnings"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        alerts = []
        
        # Check for delayed buses
        for bus in simulator.buses.values():
            if bus.status == 'delayed' or (hasattr(bus, 'traffic_delay_accumulated') and bus.traffic_delay_accumulated > 5):
                alerts.append({
                    'id': f"delay-{bus.bus_id}",
                    'type': 'delay',
                    'severity': 'high' if bus.traffic_delay_accumulated > 10 else 'medium',
                    'route': bus.route_id,
                    'bus_id': bus.bus_id,
                    'message': f"Bus {bus.bus_id} delayed by {bus.traffic_delay_accumulated:.1f} minutes",
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check for stopped buses (not at stations)
        stopped_buses = [b for b in simulator.buses.values() if b.speed == 0 and not b.is_at_stop]
        if len(stopped_buses) > 5:
            alerts.append({
                'id': 'stopped-buses-alert',
                'type': 'incident',
                'severity': 'high',
                'route': 'Multiple',
                'message': f"{len(stopped_buses)} buses stopped unexpectedly - possible traffic incident",
                'timestamp': datetime.now().isoformat()
            })
        
        # Check traffic conditions
        if hasattr(simulator, 'traffic_segments'):
            heavy_traffic = sum(1 for seg in simulator.traffic_segments.values() if seg.current_traffic_level <= 0.3)
            if heavy_traffic > 10:
                alerts.append({
                    'id': 'heavy-traffic-alert',
                    'type': 'traffic',
                    'severity': 'medium',
                    'route': 'Network-wide',
                    'message': f"{heavy_traffic} segments experiencing heavy traffic congestion",
                    'timestamp': datetime.now().isoformat()
                })
        
        return {
            'success': True,
            'alerts': alerts,
            'total_alerts': len(alerts),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting system alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Performance Metrics Endpoint
@admin_router.get("/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    if not simulator:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        metrics = {
            'total_buses': len(simulator.buses),
            'active_buses': len([b for b in simulator.buses.values() if b.route_id in simulator.active_routes]),
            'average_speed': sum(b.speed for b in simulator.buses.values()) / max(len(simulator.buses), 1),
            'buses_on_time': len([b for b in simulator.buses.values() if b.status != 'delayed']),
            'total_routes': len(simulator.routes),
            'active_routes': len(simulator.active_routes),
            'total_stops': sum(len(route.stops) for route in simulator.routes.values()),
            'system_efficiency': 0.0
        }
        
        # Calculate system efficiency
        if metrics['active_buses'] > 0:
            on_time_percentage = (metrics['buses_on_time'] / metrics['active_buses']) * 100
            route_coverage = (metrics['active_routes'] / metrics['total_routes']) * 100
            metrics['system_efficiency'] = (on_time_percentage + route_coverage) / 2
        
        return {
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DRIVER MANAGEMENT ENDPOINTS ====================

# Initialize driver manager (will be set in main.py)
driver_manager = None

@admin_router.get("/drivers")
async def get_all_drivers():
    """Get all drivers in the system"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        drivers = []
        for driver in driver_manager.drivers.values():
            drivers.append({
                "driver_id": driver.driver_id,
                "name": driver.name,
                "license_number": driver.license_number,
                "phone": driver.phone,
                "email": driver.email,
                "status": driver.status.value,
                "experience_years": driver.experience_years,
                "performance_rating": driver.performance_rating,
                "current_shift_id": driver.current_shift_id,
                "total_hours_worked": driver.total_hours_worked,
                "total_trips_completed": driver.total_trips_completed,
                "preferred_routes": driver.preferred_routes,
                "certifications": driver.certifications
            })
        
        return {
            "success": True,
            "drivers": sorted(drivers, key=lambda d: d["name"]),
            "total_drivers": len(drivers),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting drivers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/drivers/{driver_id}")
async def get_driver_details(driver_id: str):
    """Get detailed information for a specific driver"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        performance = driver_manager.get_driver_performance_metrics(driver_id)
        if not performance:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        return {
            "success": True,
            "driver": performance,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting driver details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/drivers/available")
async def get_available_drivers(date: Optional[str] = None):
    """Get list of available drivers for a specific date"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        target_date = datetime.now()
        if date:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        available = driver_manager.get_available_drivers(target_date)
        
        drivers = []
        for driver in available:
            drivers.append({
                "driver_id": driver.driver_id,
                "name": driver.name,
                "experience_years": driver.experience_years,
                "performance_rating": driver.performance_rating,
                "preferred_routes": driver.preferred_routes,
                "current_week_hours": driver.current_week_hours,
                "max_weekly_hours": driver.max_weekly_hours
            })
        
        return {
            "success": True,
            "available_drivers": sorted(drivers, key=lambda d: d["performance_rating"], reverse=True),
            "total_available": len(drivers),
            "date": target_date.strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting available drivers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/drivers/assign")
async def assign_driver_to_shift(request: DriverAssignmentRequest):
    """Assign a driver to a specific shift"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        target_date = datetime.now()
        if request.date:
            target_date = datetime.fromisoformat(request.date.replace('Z', '+00:00'))
        
        assignment = driver_manager.assign_driver_to_shift(
            request.driver_id, 
            request.shift_id, 
            target_date
        )
        
        if not assignment:
            raise HTTPException(status_code=400, detail="Failed to assign driver - may be unavailable or shift already covered")
        
        return {
            "success": True,
            "message": f"Driver {request.driver_id} assigned to shift {request.shift_id}",
            "assignment": {
                "assignment_id": assignment.assignment_id,
                "driver_id": assignment.driver_id,
                "shift_id": assignment.shift_id,
                "route_id": assignment.route_id,
                "start_time": assignment.start_time.isoformat(),
                "end_time": assignment.end_time.isoformat(),
                "status": assignment.status
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error assigning driver: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/drivers/{driver_id}/release")
async def release_driver_from_shift(driver_id: str):
    """Release a driver from their current shift"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        success = driver_manager.release_driver_from_shift(driver_id)
        if not success:
            raise HTTPException(status_code=404, detail="Driver not found or not on shift")
        
        return {
            "success": True,
            "message": f"Driver {driver_id} released from shift",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error releasing driver: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/drivers/performance")
async def update_driver_performance(request: DriverPerformanceUpdate):
    """Update driver performance metrics"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        success = driver_manager.update_driver_performance(
            request.driver_id,
            {
                "on_time_performance": request.on_time_performance,
                "passenger_complaints": request.passenger_complaints,
                "passenger_compliments": request.passenger_compliments,
                "fuel_efficiency_score": request.fuel_efficiency_score,
                "accidents_count": request.accidents_count
            }
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        return {
            "success": True,
            "message": f"Performance updated for driver {request.driver_id}",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating driver performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/shifts/coverage")
async def get_shift_coverage(date: Optional[str] = None):
    """Get shift coverage report for a specific date"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        target_date = datetime.now()
        if date:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        coverage = driver_manager.get_shift_coverage_report(target_date)
        
        return {
            "success": True,
            "coverage_report": coverage,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting shift coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/shifts/optimize")
async def optimize_shift_assignments(date: Optional[str] = None):
    """Automatically optimize shift assignments"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        target_date = datetime.now()
        if date:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        assignments = driver_manager.optimize_shift_assignments(target_date)
        
        return {
            "success": True,
            "message": f"Optimized {len(assignments)} shift assignments",
            "assignments": [
                {
                    "assignment_id": a.assignment_id,
                    "driver_id": a.driver_id,
                    "shift_id": a.shift_id,
                    "route_id": a.route_id,
                    "start_time": a.start_time.isoformat(),
                    "end_time": a.end_time.isoformat()
                }
                for a in assignments
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error optimizing assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/roster/statistics")
async def get_roster_statistics():
    """Get comprehensive roster statistics"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        stats = driver_manager.get_roster_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting roster statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/drivers/{driver_id}/schedule")
async def get_driver_schedule(driver_id: str, start_date: str, end_date: str):
    """Get driver's schedule for a date range"""
    if not driver_manager:
        raise HTTPException(status_code=500, detail="Driver manager not initialized")
    
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        schedule = driver_manager.get_driver_schedule(driver_id, start, end)
        
        return {
            "success": True,
            "driver_id": driver_id,
            "schedule": schedule,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting driver schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUSH HOUR ANALYTICS ENDPOINTS ====================

# Initialize rush hour analytics manager (will be set in main.py)
rush_hour_manager = None

@admin_router.get("/rush-hour/current")
async def get_current_rush_hour_analysis():
    """Get current rush hour analysis across all routes"""
    if not rush_hour_manager:
        raise HTTPException(status_code=500, detail="Rush hour manager not initialized")
    
    try:
        analysis = rush_hour_manager.analyze_current_rush_hour()
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting rush hour analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/rush-hour/trends/{route_id}")
async def get_rush_hour_trends(route_id: str, days: int = 7):
    """Get rush hour trends for a specific route"""
    if not rush_hour_manager:
        raise HTTPException(status_code=500, detail="Rush hour manager not initialized")
    
    try:
        trends = rush_hour_manager.get_rush_hour_trends(route_id, days)
        
        return {
            "success": True,
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting rush hour trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/rush-hour/deploy-spare")
async def deploy_spare_service(route_id: str, reason: str = "", duration_hours: int = 3):
    """Manually deploy a spare service to a route"""
    if not rush_hour_manager:
        raise HTTPException(status_code=500, detail="Rush hour manager not initialized")
    
    try:
        service = rush_hour_manager.deploy_spare_service(route_id, reason, duration_hours)
        
        if not service:
            raise HTTPException(status_code=400, detail="No spare services available")
        
        return {
            "success": True,
            "message": f"Spare service deployed to route {route_id}",
            "service": {
                "service_id": service.service_id,
                "bus_id": service.bus_id,
                "driver_id": service.driver_id,
                "deployment_time": service.deployment_time.isoformat(),
                "end_time": service.end_time.isoformat(),
                "reason": service.reason
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deploying spare service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/rush-hour/auto-deploy")
async def auto_deploy_spare_services():
    """Automatically deploy spare services based on current conditions"""
    if not rush_hour_manager:
        raise HTTPException(status_code=500, detail="Rush hour manager not initialized")
    
    try:
        deployed_services = rush_hour_manager.auto_deploy_if_needed()
        
        return {
            "success": True,
            "message": f"Auto-deployed {len(deployed_services)} spare services",
            "deployed_services": [
                {
                    "service_id": s.service_id,
                    "bus_id": s.bus_id,
                    "route_id": s.route_id,
                    "deployment_time": s.deployment_time.isoformat(),
                    "reason": s.reason
                }
                for s in deployed_services
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error auto-deploying services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/rush-hour/forecast/{route_id}")
async def get_demand_forecast(route_id: str, hours_ahead: int = 2):
    """Get demand forecast for a specific route"""
    if not rush_hour_manager:
        raise HTTPException(status_code=500, detail="Rush hour manager not initialized")
    
    try:
        forecast = rush_hour_manager.predict_demand_forecast(route_id, hours_ahead)
        
        if not forecast:
            raise HTTPException(status_code=404, detail="No forecast data available for this route")
        
        return {
            "success": True,
            "forecast": {
                "route_id": forecast.route_id,
                "forecast_time": forecast.forecast_time.isoformat(),
                "predicted_demand": forecast.predicted_demand,
                "confidence": forecast.confidence,
                "recommended_action": forecast.recommended_action.value,
                "spare_buses_needed": forecast.spare_buses_needed,
                "frequency_adjustment": forecast.frequency_adjustment
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting demand forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/rush-hour/spare-performance")
async def get_spare_service_performance():
    """Get performance metrics for spare services"""
    if not rush_hour_manager:
        raise HTTPException(status_code=500, detail="Rush hour manager not initialized")
    
    try:
        performance = rush_hour_manager.get_spare_service_performance()
        
        return {
            "success": True,
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting spare service performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/rush-hour/update-performance/{service_id}")
async def update_spare_service_performance(service_id: str, passengers_served: int, 
                                         revenue_generated: Optional[float] = None):
    """Update performance metrics for a deployed spare service"""
    if not rush_hour_manager:
        raise HTTPException(status_code=500, detail="Rush hour manager not initialized")
    
    try:
        success = rush_hour_manager.update_spare_service_performance(
            service_id, passengers_served, revenue_generated
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return {
            "success": True,
            "message": f"Performance updated for service {service_id}",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating service performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AGENT BEHAVIOR MONITORING ENDPOINTS ====================

# Initialize agent behavior monitor (will be set in main.py)
behavior_monitor = None

@admin_router.get("/behavior/analysis/{bus_id}")
async def get_bus_behavior_analysis(bus_id: str):
    """Get comprehensive behavior analysis for a specific bus"""
    if not behavior_monitor:
        raise HTTPException(status_code=500, detail="Behavior monitor not initialized")
    
    try:
        analysis = behavior_monitor.get_bus_behavior_analysis(bus_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="No behavior data available for this bus")
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting bus behavior analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/behavior/fleet-overview")
async def get_fleet_behavior_overview():
    """Get fleet-wide behavior overview"""
    if not behavior_monitor:
        raise HTTPException(status_code=500, detail="Behavior monitor not initialized")
    
    try:
        overview = behavior_monitor.get_fleet_behavior_overview()
        
        return {
            "success": True,
            "overview": overview,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting fleet behavior overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/behavior/anomalies")
async def get_behavior_anomalies(resolved: Optional[bool] = None, severity: Optional[str] = None):
    """Get behavior anomaly alerts"""
    if not behavior_monitor:
        raise HTTPException(status_code=500, detail="Behavior monitor not initialized")
    
    try:
        anomalies = list(behavior_monitor.anomaly_alerts.values())
        
        # Filter by resolved status
        if resolved is not None:
            anomalies = [a for a in anomalies if a.resolved == resolved]
        
        # Filter by severity
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        # Sort by timestamp (most recent first)
        anomalies.sort(key=lambda a: a.timestamp, reverse=True)
        
        return {
            "success": True,
            "anomalies": [
                {
                    "alert_id": a.alert_id,
                    "bus_id": a.bus_id,
                    "anomaly_type": a.anomaly_type,
                    "severity": a.severity,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat(),
                    "expected_behavior": a.expected_behavior,
                    "actual_behavior": a.actual_behavior,
                    "impact_assessment": a.impact_assessment,
                    "recommended_action": a.recommended_action,
                    "resolved": a.resolved,
                    "resolution_notes": a.resolution_notes
                }
                for a in anomalies[:50]  # Limit to 50 most recent
            ],
            "total_count": len(anomalies),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting behavior anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/behavior/resolve-anomaly/{alert_id}")
async def resolve_behavior_anomaly(alert_id: str, resolution_notes: str):
    """Resolve a behavior anomaly alert"""
    if not behavior_monitor:
        raise HTTPException(status_code=500, detail="Behavior monitor not initialized")
    
    try:
        success = behavior_monitor.resolve_anomaly(alert_id, resolution_notes)
        
        if not success:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        return {
            "success": True,
            "message": f"Anomaly {alert_id} resolved successfully",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resolving anomaly: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/behavior/decision-history/{bus_id}")
async def get_bus_decision_history(bus_id: str, hours: int = 24):
    """Get decision history for a specific bus"""
    if not behavior_monitor:
        raise HTTPException(status_code=500, detail="Behavior monitor not initialized")
    
    try:
        decisions = behavior_monitor.decisions.get(bus_id, [])
        
        # Filter by time range
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_decisions = [d for d in decisions if d.timestamp >= cutoff_time]
        
        # Sort by timestamp (most recent first)
        recent_decisions.sort(key=lambda d: d.timestamp, reverse=True)
        
        return {
            "success": True,
            "bus_id": bus_id,
            "time_range_hours": hours,
            "decisions": [
                {
                    "decision_id": d.decision_id,
                    "decision_type": d.decision_type.value,
                    "timestamp": d.timestamp.isoformat(),
                    "location": d.location,
                    "context": d.context,
                    "chosen_option": d.chosen_option,
                    "efficiency_score": d.efficiency_score,
                    "safety_score": d.safety_score,
                    "passenger_satisfaction": d.passenger_satisfaction,
                    "reasoning": d.reasoning
                }
                for d in recent_decisions[:100]  # Limit to 100 most recent
            ],
            "total_decisions": len(recent_decisions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting decision history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/behavior/performance-comparison")
async def get_behavior_performance_comparison():
    """Get performance comparison across all buses"""
    if not behavior_monitor:
        raise HTTPException(status_code=500, detail="Behavior monitor not initialized")
    
    try:
        profiles = list(behavior_monitor.behavior_profiles.values())
        
        if not profiles:
            return {"success": True, "comparison": [], "timestamp": datetime.now().isoformat()}
        
        # Sort by efficiency for ranking
        sorted_profiles = sorted(profiles, key=lambda p: p.average_efficiency, reverse=True)
        
        comparison = []
        for i, profile in enumerate(sorted_profiles, 1):
            comparison.append({
                "rank": i,
                "bus_id": profile.bus_id,
                "behavior_pattern": profile.behavior_pattern.value,
                "total_decisions": profile.total_decisions,
                "average_efficiency": profile.average_efficiency,
                "average_safety": profile.average_safety,
                "average_passenger_satisfaction": profile.average_passenger_satisfaction,
                "risk_tolerance": profile.risk_tolerance,
                "adaptability_score": profile.adaptability_score,
                "consistency_score": profile.consistency_score,
                "learning_rate": profile.learning_rate,
                "anomaly_count": profile.anomaly_count
            })
        
        return {
            "success": True,
            "comparison": comparison,
            "total_buses": len(comparison),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting performance comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PERFORMANCE ANALYTICS ENDPOINTS ====================

# Initialize performance analytics manager (will be set in main.py)
performance_analytics = None

@admin_router.get("/performance/eta-accuracy")
async def get_eta_accuracy_analysis(route_id: Optional[str] = None, time_period: int = 7):
    """Get ETA accuracy analysis"""
    if not performance_analytics:
        raise HTTPException(status_code=500, detail="Performance analytics not initialized")
    
    try:
        analysis = performance_analytics.calculate_eta_accuracy(route_id, time_period)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting ETA accuracy analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/performance/delay-patterns")
async def get_delay_patterns_analysis(route_id: Optional[str] = None, time_period: int = 7):
    """Get delay patterns analysis"""
    if not performance_analytics:
        raise HTTPException(status_code=500, detail="Performance analytics not initialized")
    
    try:
        analysis = performance_analytics.analyze_delay_patterns(route_id, time_period)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting delay patterns analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/performance/route-efficiency")
async def get_route_efficiency_analysis(route_id: Optional[str] = None, time_period: int = 30):
    """Get route efficiency analysis"""
    if not performance_analytics:
        raise HTTPException(status_code=500, detail="Performance analytics not initialized")
    
    try:
        analysis = performance_analytics.calculate_route_efficiency(route_id, time_period)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting route efficiency analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/performance/report")
async def get_performance_report(report_type: str = "comprehensive"):
    """Generate performance report"""
    if not performance_analytics:
        raise HTTPException(status_code=500, detail="Performance analytics not initialized")
    
    try:
        report = performance_analytics.generate_performance_report(report_type)
        
        return {
            "success": True,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error generating performance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/performance/trends/{metric}")
async def get_performance_trends(metric: str, entity_id: str, time_period: int = 30):
    """Get performance trends for a specific metric"""
    if not performance_analytics:
        raise HTTPException(status_code=500, detail="Performance analytics not initialized")
    
    try:
        # Convert string to PerformanceMetric enum
        try:
            performance_metric = PerformanceMetric(metric)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid metric: {metric}")
        
        trend = performance_analytics.get_performance_trends(performance_metric, entity_id, time_period)
        
        if not trend:
            raise HTTPException(status_code=404, detail="No trend data available")
        
        return {
            "success": True,
            "trend": {
                "metric": trend.metric.value,
                "entity_id": trend.entity_id,
                "direction": trend.direction.value,
                "change_percentage": trend.change_percentage,
                "confidence": trend.confidence,
                "time_period": trend.time_period,
                "analysis_notes": trend.analysis_notes
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting performance trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/performance/dashboard")
async def get_performance_dashboard():
    """Get comprehensive performance dashboard data"""
    if not performance_analytics:
        raise HTTPException(status_code=500, detail="Performance analytics not initialized")
    
    try:
        # Get all analyses for dashboard
        eta_analysis = performance_analytics.calculate_eta_accuracy(time_period=7)
        delay_analysis = performance_analytics.analyze_delay_patterns(time_period=7)
        efficiency_analysis = performance_analytics.calculate_route_efficiency(time_period=30)
        
        # Calculate key metrics
        system_health = performance_analytics._calculate_system_health_score(eta_analysis, delay_analysis, efficiency_analysis)
        
        # Get top issues
        top_issues = performance_analytics._identify_top_performance_issues()
        
        dashboard_data = {
            "system_health": system_health,
            "key_metrics": {
                "eta_accuracy_percentage": eta_analysis.get("within_threshold_percentage", 0),
                "average_delay_minutes": delay_analysis.get("delay_statistics", {}).get("average_delay", 0),
                "on_time_performance_percentage": efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0),
                "average_speed_kmh": efficiency_analysis.get("overall_metrics", {}).get("average_speed_kmh", 0),
                "fuel_efficiency_kmpl": efficiency_analysis.get("overall_metrics", {}).get("fuel_efficiency_kmpl", 0),
                "total_trips": efficiency_analysis.get("overall_metrics", {}).get("total_trips", 0),
                "total_passengers": efficiency_analysis.get("overall_metrics", {}).get("total_passengers", 0),
                "profit_margin_percentage": efficiency_analysis.get("overall_metrics", {}).get("profit_margin_percentage", 0)
            },
            "top_issues": top_issues,
            "eta_accuracy_summary": {
                "average_error": eta_analysis.get("average_error_minutes", 0),
                "within_threshold": eta_analysis.get("within_threshold_percentage", 0),
                "accuracy_distribution": eta_analysis.get("accuracy_distribution", {})
            },
            "delay_summary": {
                "total_delays": delay_analysis.get("total_delays", 0),
                "average_delay": delay_analysis.get("delay_statistics", {}).get("average_delay", 0),
                "major_delays": delay_analysis.get("delay_distribution", {}).get("major", 0),
                "top_causes": dict(list(delay_analysis.get("delay_causes", {}).items())[:3])
            },
            "efficiency_summary": {
                "route_comparison": dict(list(efficiency_analysis.get("route_comparison", {}).items())[:5]),
                "efficiency_trends": efficiency_analysis.get("efficiency_trends", {})
            },
            "recommendations": performance_analytics._generate_quick_recommendations(),
            "additional_insights": performance_analytics._generate_additional_insights()
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting performance dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SYSTEM USAGE STATISTICS ENDPOINTS ====================

# Initialize system usage analytics (will be set in main.py)
usage_analytics = None

@admin_router.get("/usage/system-overview")
async def get_system_usage_overview(time_period: int = 30):
    """Get comprehensive system usage overview"""
    if not usage_analytics:
        raise HTTPException(status_code=500, detail="Usage analytics not initialized")
    
    try:
        overview = usage_analytics.get_system_usage_overview(time_period)
        
        return {
            "success": True,
            "overview": overview,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting system usage overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/usage/commuter-behavior")
async def get_commuter_behavior_analysis(user_category: Optional[str] = None, time_period: int = 30):
    """Analyze commuter behavior patterns"""
    if not usage_analytics:
        raise HTTPException(status_code=500, detail="Usage analytics not initialized")
    
    try:
        # Convert string to UserCategory enum if provided
        category = None
        if user_category:
            try:
                category = UserCategory(user_category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid user category: {user_category}")
        
        analysis = usage_analytics.analyze_commuter_behavior(category, time_period)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting commuter behavior analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/usage/route-popularity")
async def get_route_popularity_analysis(time_period: int = 30):
    """Analyze route popularity and usage patterns"""
    if not usage_analytics:
        raise HTTPException(status_code=500, detail="Usage analytics not initialized")
    
    try:
        analysis = usage_analytics.get_route_popularity_analysis(time_period)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting route popularity analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/usage/peak-analysis")
async def get_peak_usage_analysis(time_period: int = 30):
    """Analyze peak usage patterns across the system"""
    if not usage_analytics:
        raise HTTPException(status_code=500, detail="Usage analytics not initialized")
    
    try:
        analysis = usage_analytics.get_peak_usage_analysis(time_period)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting peak usage analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/usage/user-engagement")
async def get_user_engagement_metrics(time_period: int = 30):
    """Get detailed user engagement metrics"""
    if not usage_analytics:
        raise HTTPException(status_code=500, detail="Usage analytics not initialized")
    
    try:
        metrics = usage_analytics.get_user_engagement_metrics(time_period)
        
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting user engagement metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/usage/dashboard")
async def get_usage_statistics_dashboard():
    """Get comprehensive usage statistics dashboard"""
    if not usage_analytics:
        raise HTTPException(status_code=500, detail="Usage analytics not initialized")
    
    try:
        # Get all usage analyses for dashboard
        system_overview = usage_analytics.get_system_usage_overview(time_period=7)
        commuter_behavior = usage_analytics.analyze_commuter_behavior(time_period=7)
        route_popularity = usage_analytics.get_route_popularity_analysis(time_period=7)
        peak_analysis = usage_analytics.get_peak_usage_analysis(time_period=7)
        user_engagement = usage_analytics.get_user_engagement_metrics(time_period=7)
        
        dashboard_data = {
            "key_metrics": {
                "total_users": system_overview.get("user_activity", {}).get("unique_users", 0),
                "total_trips": system_overview.get("trip_statistics", {}).get("total_trips", 0),
                "total_revenue": system_overview.get("trip_statistics", {}).get("total_revenue", 0),
                "active_users": user_engagement.get("user_engagement", {}).get("active_users", 0),
                "engagement_rate": user_engagement.get("user_engagement", {}).get("engagement_rate", 0),
                "avg_trips_per_day": system_overview.get("trip_statistics", {}).get("avg_trips_per_day", 0)
            },
            "user_activity_summary": {
                "total_activities": system_overview.get("user_activity", {}).get("total_activities", 0),
                "activity_breakdown": system_overview.get("user_activity", {}).get("activity_breakdown", {}),
                "device_breakdown": system_overview.get("user_activity", {}).get("device_breakdown", {}),
                "user_segments": user_engagement.get("user_segments", {})
            },
            "trip_insights": {
                "total_trips": system_overview.get("trip_statistics", {}).get("total_trips", 0),
                "avg_revenue_per_trip": system_overview.get("trip_statistics", {}).get("avg_revenue_per_trip", 0),
                "route_usage": system_overview.get("trip_statistics", {}).get("route_usage", {}),
                "payment_methods": system_overview.get("user_demographics", {}).get("payment_methods", {})
            },
            "commuter_behavior": {
                "peak_hours": peak_analysis.get("peak_hours", []),
                "temporal_patterns": commuter_behavior.get("temporal_patterns", {}),
                "trip_purposes": commuter_behavior.get("behavioral_insights", {}).get("trip_purposes", {}),
                "loyalty_analysis": commuter_behavior.get("loyalty_analysis", {})
            },
            "route_performance": {
                "top_routes": route_popularity.get("route_rankings", [])[:5],
                "system_insights": route_popularity.get("system_insights", {}),
                "top_performers": route_popularity.get("top_performers", {})
            },
            "peak_usage": {
                "busiest_hour": peak_analysis.get("peak_insights", {}).get("busiest_hour"),
                "busiest_day": peak_analysis.get("peak_insights", {}).get("busiest_day"),
                "peak_hour_percentage": peak_analysis.get("peak_insights", {}).get("peak_hour_percentage", 0),
                "recommendations": peak_analysis.get("recommendations", [])
            }
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting usage statistics dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ALERT MANAGEMENT ENDPOINTS ====================

# Initialize alert manager (will be set in main.py)
alert_manager = None

@admin_router.post("/alerts/create")
async def create_alert(title: str, description: str, alert_type: str, severity: str,
                      location: Optional[str] = None, affected_routes: Optional[str] = None,
                      affected_stops: Optional[str] = None, affected_buses: Optional[str] = None,
                      source: str = "system"):
    """Create a new alert"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        # Convert strings to enums
        alert_type_enum = AlertType(alert_type)
        severity_enum = AlertSeverity(severity)
        
        # Parse location if provided
        location_tuple = None
        if location:
            try:
                lat, lng = map(float, location.split(","))
                location_tuple = (lat, lng)
            except:
                pass
        
        # Parse lists if provided
        routes_list = affected_routes.split(",") if affected_routes else None
        stops_list = affected_stops.split(",") if affected_stops else None
        buses_list = affected_buses.split(",") if affected_buses else None
        
        alert = alert_manager.create_alert(
            title=title,
            description=description,
            alert_type=alert_type_enum,
            severity=severity_enum,
            location=location_tuple,
            affected_routes=routes_list,
            affected_stops=stops_list,
            affected_buses=buses_list,
            source=source
        )
        
        if not alert:
            raise HTTPException(status_code=400, detail="Duplicate alert detected")
        
        return {
            "success": True,
            "alert": {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "description": alert.description,
                "category": alert.category.value,
                "severity": alert.severity.value,
                "alert_type": alert.alert_type.value,
                "status": alert.status.value,
                "created_at": alert.created_at.isoformat(),
                "location": alert.location,
                "affected_routes": alert.affected_routes,
                "affected_stops": alert.affected_stops,
                "affected_buses": alert.affected_buses,
                "confidence_score": alert.confidence_score,
                "verification_status": alert.verification_status
            },
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/alerts")
async def get_alerts(status: Optional[str] = None, severity: Optional[str] = None,
                    category: Optional[str] = None, time_period: Optional[int] = None):
    """Get alerts with optional filtering"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        # Convert strings to enums if provided
        status_enum = None
        if status:
            status_enum = AlertStatus(status)
        
        severity_enum = None
        if severity:
            severity_enum = AlertSeverity(severity)
        
        category_enum = None
        if category:
            category_enum = AlertCategory(category)
        
        alerts = alert_manager.get_alerts(status_enum, severity_enum, category_enum, time_period)
        
        return {
            "success": True,
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "description": alert.description,
                    "category": alert.category.value,
                    "severity": alert.severity.value,
                    "alert_type": alert.alert_type.value,
                    "status": alert.status.value,
                    "created_at": alert.created_at.isoformat(),
                    "updated_at": alert.updated_at.isoformat(),
                    "location": alert.location,
                    "affected_routes": alert.affected_routes,
                    "affected_stops": alert.affected_stops,
                    "affected_buses": alert.affected_buses,
                    "passenger_impact": alert.passenger_impact,
                    "financial_impact": alert.financial_impact,
                    "confidence_score": alert.confidence_score,
                    "verification_status": alert.verification_status,
                    "assigned_to": alert.assigned_to
                }
                for alert in alerts
            ],
            "total_count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except Exception as e:
        print(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/alerts/{alert_id}/status")
async def update_alert_status(alert_id: str, status: str, assigned_to: Optional[str] = None,
                             resolution_notes: Optional[str] = None, updated_by: str = "system"):
    """Update alert status"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        status_enum = AlertStatus(status)
        
        success = alert_manager.update_alert_status(
            alert_id=alert_id,
            status=status_enum,
            assigned_to=assigned_to,
            resolution_notes=resolution_notes,
            updated_by=updated_by
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "success": True,
            "message": f"Alert {alert_id} status updated to {status}",
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating alert status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/alerts/{alert_id}")
async def get_alert_details(alert_id: str):
    """Get detailed information about a specific alert"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        details = alert_manager.get_alert_details(alert_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "success": True,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting alert details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/alerts/statistics")
async def get_alert_statistics(time_period: int = 24):
    """Get alert statistics for specified time period"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        statistics = alert_manager.get_alert_statistics(time_period)
        
        return {
            "success": True,
            "statistics": statistics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting alert statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/alerts/analytics")
async def get_alert_analytics(time_period: int = 168):
    """Get comprehensive alert analytics"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        analytics = alert_manager.get_alert_analytics(time_period)
        
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting alert analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/alerts/dashboard")
async def get_alert_management_dashboard():
    """Get comprehensive alert management dashboard"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        # Get all alert data for dashboard
        recent_alerts = alert_manager.get_alerts(time_period=24)
        statistics = alert_manager.get_alert_statistics(time_period=24)
        analytics = alert_manager.get_alert_analytics(time_period=168)
        
        # Get active alerts by severity
        active_alerts = [a for a in recent_alerts if a.status in [AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS]]
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        high_alerts = [a for a in active_alerts if a.severity == AlertSeverity.HIGH]
        
        dashboard_data = {
            "overview": {
                "total_alerts": len(recent_alerts),
                "active_alerts": len(active_alerts),
                "critical_alerts": len(critical_alerts),
                "high_alerts": len(high_alerts),
                "resolved_today": len([a for a in recent_alerts if a.status == AlertStatus.RESOLVED])
            },
            "severity_breakdown": statistics.get("severity_breakdown", {}),
            "status_breakdown": statistics.get("status_breakdown", {}),
            "category_breakdown": statistics.get("category_breakdown", {}),
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "category": alert.category.value,
                    "created_at": alert.created_at.isoformat(),
                    "affected_routes": alert.affected_routes
                }
                for alert in recent_alerts[:10]  # Last 10 alerts
            ],
            "critical_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "description": alert.description,
                    "created_at": alert.created_at.isoformat(),
                    "affected_routes": alert.affected_routes,
                    "passenger_impact": alert.passenger_impact
                }
                for alert in critical_alerts
            ],
            "performance_metrics": {
                "resolution_rate": statistics.get("resolution_metrics", {}).get("resolution_rate", 0),
                "avg_resolution_time": statistics.get("resolution_metrics", {}).get("average_resolution_time_minutes", 0),
                "total_passenger_impact": statistics.get("impact_metrics", {}).get("total_passenger_impact", 0),
                "total_financial_impact": statistics.get("impact_metrics", {}).get("total_financial_impact", 0)
            },
            "trends": analytics.get("trend_analysis", {}),
            "top_alert_types": analytics.get("top_alert_types", []),
            "recommendations": analytics.get("recommendations", [])
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting alert management dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MULTI-ROUTE MANAGEMENT ENDPOINTS ====================

# Initialize multi-route manager (will be set in main.py)
route_manager = None

@admin_router.post("/routes/create")
async def create_route(name: str, description: str, service_type: str, priority: str,
                      base_frequency: int, operating_hours: str, days_of_operation: str,
                      stops: str, distance: float, estimated_duration: float, capacity: int,
                      fare_structure: str, accessibility_features: str, created_by: str):
    """Create a new route"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        # Parse and convert inputs
        service_type_enum = ServiceType(service_type)
        priority_enum = RoutePriority(priority)
        
        # Parse operating hours
        start_hour, end_hour = map(int, operating_hours.split(","))
        
        # Parse days of operation
        days = list(map(int, days_of_operation.split(",")))
        
        # Parse stops
        stops_list = stops.split(",") if stops else []
        
        # Parse fare structure
        fare_dict = json.loads(fare_structure) if fare_structure else {}
        
        # Parse accessibility features
        features_list = accessibility_features.split(",") if accessibility_features else []
        
        route = route_manager.create_route(
            name=name,
            description=description,
            service_type=service_type_enum,
            priority=priority_enum,
            base_frequency=base_frequency,
            operating_hours=(start_hour, end_hour),
            days_of_operation=days,
            stops=stops_list,
            distance=distance,
            estimated_duration=estimated_duration,
            capacity=capacity,
            fare_structure=fare_dict,
            accessibility_features=features_list,
            created_by=created_by
        )
        
        return {
            "success": True,
            "route": {
                "route_id": route.route_id,
                "name": route.name,
                "description": route.description,
                "service_type": route.service_type.value,
                "priority": route.priority.value,
                "base_frequency": route.base_frequency,
                "operating_hours": route.operating_hours,
                "days_of_operation": route.days_of_operation,
                "stops": route.stops,
                "distance": route.distance,
                "estimated_duration": route.estimated_duration,
                "capacity": route.capacity,
                "fare_structure": route.fare_structure,
                "accessibility_features": route.accessibility_features,
                "created_at": route.created_at.isoformat(),
                "created_by": route.created_by
            },
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid fare structure JSON")
    except Exception as e:
        print(f"Error creating route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/routes/{route_id}/activate")
async def activate_route(route_id: str, activated_by: str, reason: str = ""):
    """Activate a route"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        success = route_manager.activate_route(route_id, activated_by, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "success": True,
            "message": f"Route {route_id} activated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error activating route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/routes/{route_id}/deactivate")
async def deactivate_route(route_id: str, deactivated_by: str, reason: str = ""):
    """Deactivate a route"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        success = route_manager.deactivate_route(route_id, deactivated_by, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "success": True,
            "message": f"Route {route_id} deactivated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error deactivating route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/routes/{route_id}/maintenance")
async def set_maintenance_mode(route_id: str, set_by: str, reason: str = "", 
                             estimated_duration_hours: Optional[int] = None):
    """Set route to maintenance mode"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        duration = timedelta(hours=estimated_duration_hours) if estimated_duration_hours else None
        success = route_manager.set_maintenance_mode(route_id, set_by, reason, duration)
        
        if not success:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "success": True,
            "message": f"Route {route_id} set to maintenance mode",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error setting maintenance mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/routes/{route_id}")
async def get_route_status(route_id: str):
    """Get current status and information for a route"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        status = route_manager.get_route_status(route_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "success": True,
            "route_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting route status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/routes")
async def get_all_routes_status():
    """Get status of all routes"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        routes_status = route_manager.get_all_routes_status()
        
        return {
            "success": True,
            "routes": routes_status,
            "total_count": len(routes_status),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting all routes status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/routes/{route_id}/configure")
async def update_route_configuration(route_id: str, updates: str, updated_by: str):
    """Update route configuration"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        updates_dict = json.loads(updates)
        success = route_manager.update_route_configuration(route_id, updates_dict, updated_by)
        
        if not success:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "success": True,
            "message": f"Route {route_id} configuration updated",
            "timestamp": datetime.now().isoformat()
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid updates JSON")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating route configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/routes/{route_id}/schedule")
async def create_special_schedule(route_id: str, valid_from: str, valid_until: str,
                                frequency: int, schedule_type: str, notes: str = "",
                                additional_buses: int = 0, reduced_service: bool = False,
                                created_by: str = "system"):
    """Create a special schedule for a route"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        from_date = datetime.fromisoformat(valid_from)
        until_date = datetime.fromisoformat(valid_until)
        
        success = route_manager.create_special_schedule(
            route_id=route_id,
            valid_from=from_date,
            valid_until=until_date,
            frequency=frequency,
            schedule_type=schedule_type,
            notes=notes,
            additional_buses=additional_buses,
            reduced_service=reduced_service,
            created_by=created_by
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "success": True,
            "message": f"Special schedule created for route {route_id}",
            "timestamp": datetime.now().isoformat()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating special schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/routes/{route_id}/performance")
async def get_route_performance_report(route_id: str, days: int = 30):
    """Get performance report for a specific route"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        report = route_manager.get_route_performance_report(route_id, days)
        
        if not report:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "success": True,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting route performance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/routes/system-overview")
async def get_system_overview():
    """Get system-wide overview of all routes"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        overview = route_manager.get_system_overview()
        
        return {
            "success": True,
            "overview": overview,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting system overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/routes/dashboard")
async def get_route_management_dashboard():
    """Get comprehensive route management dashboard"""
    if not route_manager:
        raise HTTPException(status_code=500, detail="Route manager not initialized")
    
    try:
        # Get all route data for dashboard
        all_routes = route_manager.get_all_routes_status()
        system_overview = route_manager.get_system_overview()
        
        # Calculate dashboard metrics
        active_routes = [r for r in all_routes if r["current_status"] == "active"]
        inactive_routes = [r for r in all_routes if r["current_status"] == "inactive"]
        maintenance_routes = [r for r in all_routes if r["current_status"] == "maintenance"]
        
        # Get routes by priority
        critical_routes = [r for r in all_routes if r["priority"] == "critical"]
        high_priority_routes = [r for r in all_routes if r["priority"] == "high"]
        
        # Get performance summaries
        performance_summaries = {}
        for route in all_routes[:10]:  # Limit to first 10 routes
            if route["performance_summary"]:
                performance_summaries[route["route_id"]] = route["performance_summary"]
        
        dashboard_data = {
            "overview_metrics": {
                "total_routes": len(all_routes),
                "active_routes": len(active_routes),
                "inactive_routes": len(inactive_routes),
                "maintenance_routes": len(maintenance_routes),
                "activation_rate": system_overview.get("route_counts", {}).get("activation_rate", 0)
            },
            "priority_distribution": {
                "critical_routes": len(critical_routes),
                "high_priority_routes": len(high_priority_routes),
                "medium_priority_routes": len([r for r in all_routes if r["priority"] == "medium"]),
                "low_priority_routes": len([r for r in all_routes if r["priority"] == "low"])
            },
            "service_type_distribution": system_overview.get("distribution", {}).get("by_service_type", {}),
            "recent_status_changes": system_overview.get("recent_status_changes", [])[:5],
            "route_performance": performance_summaries,
            "system_performance": system_overview.get("system_performance", {}),
            "routes_requiring_attention": [
                {
                    "route_id": route["route_id"],
                    "name": route["name"],
                    "status": route["current_status"],
                    "priority": route["priority"],
                    "issue": "Low performance" if route.get("performance_summary", {}).get("avg_on_time_rate", 100) < 80 else "Maintenance required"
                }
                for route in all_routes
                if (route["current_status"] in ["maintenance", "inactive"] or 
                    route.get("performance_summary", {}).get("avg_on_time_rate", 100) < 80)
            ][:5]
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting route management dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export router for main.py integration
def get_admin_router():
    """Return the admin router for integration in main.py"""
    return admin_router