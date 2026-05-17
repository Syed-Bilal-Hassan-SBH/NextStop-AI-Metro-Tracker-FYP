"""
rush_hour_analytics.py
=====================
NEW FILE - Rush Hour Analytics and Automatic Spare Service Management
Provides intelligent analysis of rush hour patterns and automatic deployment of spare services

Features:
- Rush hour pattern detection and analysis
- Automatic spare service deployment
- Demand forecasting
- Peak hour optimization
- Service level monitoring
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import random
import statistics

class RushHourLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ServiceAction(Enum):
    DEPLOY_SPARE = "deploy_spare"
    INCREASE_FREQUENCY = "increase_frequency"
    EXTEND_SERVICE = "extend_service"
    NO_ACTION = "no_action"

@dataclass
class RushHourPattern:
    route_id: str
    hour: int
    minute: int
    demand_level: float  # 0.0 - 1.0
    passenger_count: int
    average_delay: float
    service_frequency: float  # buses per hour
    capacity_utilization: float  # 0.0 - 1.0
    date: datetime
    
@dataclass
class SpareService:
    service_id: str
    bus_id: str
    driver_id: Optional[str]
    route_id: str
    deployment_time: datetime
    end_time: datetime
    status: str = "standby"  # standby, deployed, completed
    reason: str = ""
    passengers_served: int = 0
    revenue_generated: float = 0.0
    cost_incurred: float = 0.0

@dataclass
class DemandForecast:
    route_id: str
    forecast_time: datetime
    predicted_demand: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    recommended_action: ServiceAction
    spare_buses_needed: int = 0
    frequency_adjustment: float = 0.0

class RushHourAnalyticsManager:
    """Comprehensive rush hour analytics and automatic spare service management"""
    
    def __init__(self, db_manager=None, simulator=None, driver_manager=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.driver_manager = driver_manager
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.rush_patterns: Dict[str, List[RushHourPattern]] = {}
        self.spare_services: Dict[str, SpareService] = {}
        self.demand_forecasts: Dict[str, DemandForecast] = {}
        
        # Configuration
        self.rush_hour_threshold = 0.7  # 70% capacity utilization triggers rush hour
        self.critical_threshold = 0.9   # 90% triggers critical level
        self.max_spare_buses = 10
        self.deployment_cost_per_hour = 150.0  # Operating cost for spare bus
        self.revenue_per_passenger = 2.5
        
        # Rush hour definitions (can be customized per route)
        self.rush_hour_periods = {
            "morning": [(time(6, 0), time(9, 30))],
            "evening": [(time(16, 0), time(19, 30))],
            "noon": [(time(11, 30), time(13, 30))]
        }
        
        # Initialize with sample data
        self._initialize_sample_patterns()
        self._initialize_spare_services()
    
    def _initialize_sample_patterns(self):
        """Create sample rush hour patterns for demonstration"""
        current_time = datetime.now()
        
        # Generate patterns for major routes
        major_routes = ["FR-01", "FR-02", "FR-03A", "FR-04", "FR-05"]
        
        for route_id in major_routes:
            patterns = []
            
            # Generate patterns for the last 7 days
            for day_offset in range(7):
                date = current_time - timedelta(days=day_offset)
                
                # Generate hourly patterns
                for hour in range(6, 22):  # 6 AM to 10 PM
                    for minute in [0, 30]:  # Every 30 minutes
                        # Simulate realistic demand patterns
                        base_demand = 0.3
                        
                        # Morning rush (7-9 AM)
                        if 7 <= hour <= 9:
                            base_demand = 0.8 + random.uniform(-0.1, 0.2)
                        # Evening rush (5-7 PM)
                        elif 17 <= hour <= 19:
                            base_demand = 0.85 + random.uniform(-0.1, 0.2)
                        # Noon peak (12-1 PM)
                        elif 12 <= hour <= 13:
                            base_demand = 0.6 + random.uniform(-0.1, 0.1)
                        # Regular hours
                        else:
                            base_demand = 0.4 + random.uniform(-0.1, 0.1)
                        
                        demand_level = max(0.1, min(1.0, base_demand))
                        passenger_count = int(demand_level * 80)  # 80 passengers max per bus
                        average_delay = random.uniform(0, 5) if demand_level > 0.7 else random.uniform(0, 2)
                        service_frequency = 6 + demand_level * 4  # 6-10 buses per hour
                        capacity_utilization = demand_level
                        
                        pattern = RushHourPattern(
                            route_id=route_id,
                            hour=hour,
                            minute=minute,
                            demand_level=demand_level,
                            passenger_count=passenger_count,
                            average_delay=average_delay,
                            service_frequency=service_frequency,
                            capacity_utilization=capacity_utilization,
                            date=date
                        )
                        patterns.append(pattern)
            
            self.rush_patterns[route_id] = patterns
    
    def _initialize_spare_services(self):
        """Initialize spare service fleet"""
        spare_buses = ["SPARE-01", "SPARE-02", "SPARE-03", "SPARE-04", "SPARE-05"]
        
        for i, bus_id in enumerate(spare_buses):
            service = SpareService(
                service_id=f"SPARE-SERVICE-{i+1}",
                bus_id=bus_id,
                driver_id=None,  # Will be assigned when deployed
                route_id="",  # Will be assigned when deployed
                deployment_time=datetime.now(),
                end_time=datetime.now(),
                status="standby",
                reason="Available for deployment"
            )
            self.spare_services[service.service_id] = service
    
    def analyze_current_rush_hour(self) -> Dict[str, Any]:
        """Analyze current rush hour conditions across all routes"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        analysis = {
            "timestamp": current_time.isoformat(),
            "overall_level": RushHourLevel.LOW.value,
            "route_analysis": {},
            "critical_routes": [],
            "recommendations": [],
            "average_utilization": 0.0,
            "spare_services_available": len([s for s in self.spare_services.values() if s.status == "standby"])
        }
        
        route_levels = []
        
        for route_id, patterns in self.rush_patterns.items():
            # Find current pattern for this route
            current_pattern = None
            for pattern in patterns:
                if pattern.hour == current_hour and abs(pattern.minute - current_minute) < 30:
                    current_pattern = pattern
                    break
            
            if current_pattern:
                # Determine rush hour level
                if current_pattern.capacity_utilization >= self.critical_threshold:
                    level = RushHourLevel.CRITICAL
                elif current_pattern.capacity_utilization >= self.rush_hour_threshold:
                    level = RushHourLevel.HIGH
                elif current_pattern.capacity_utilization >= 0.5:
                    level = RushHourLevel.MODERATE
                else:
                    level = RushHourLevel.LOW
                
                route_analysis = {
                    "route_id": route_id,
                    "level": level.value,
                    "capacity_utilization": current_pattern.capacity_utilization,
                    "passenger_count": current_pattern.passenger_count,
                    "average_delay": current_pattern.average_delay,
                    "service_frequency": current_pattern.service_frequency,
                    "demand_level": current_pattern.demand_level
                }
                
                analysis["route_analysis"][route_id] = route_analysis
                route_levels.append(current_pattern.capacity_utilization)
                
                if level == RushHourLevel.CRITICAL:
                    analysis["critical_routes"].append(route_id)
        
        # Determine overall level
        if route_levels:
            avg_utilization = statistics.mean(route_levels)
            analysis["average_utilization"] = avg_utilization
            if avg_utilization >= self.critical_threshold:
                analysis["overall_level"] = RushHourLevel.CRITICAL.value
            elif avg_utilization >= self.rush_hour_threshold:
                analysis["overall_level"] = RushHourLevel.HIGH.value
            elif avg_utilization >= 0.5:
                analysis["overall_level"] = RushHourLevel.MODERATE.value
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on rush hour analysis"""
        recommendations = []
        
        # Check for critical routes
        for route_id in analysis["critical_routes"]:
            route_data = analysis["route_analysis"][route_id]
            
            # Recommend spare service deployment
            if analysis["spare_services_available"] > 0:
                recommendations.append({
                    "type": "deploy_spare",
                    "priority": "high",
                    "route_id": route_id,
                    "message": f"Deploy spare bus to route {route_id} - capacity at {route_data['capacity_utilization']*100:.1f}%",
                    "estimated_impact": "Reduce delays by 15-20 minutes",
                    "cost_benefit": self._calculate_cost_benefit(route_data)
                })
            
            # Recommend frequency increase
            recommendations.append({
                "type": "increase_frequency",
                "priority": "medium",
                "route_id": route_id,
                "message": f"Increase service frequency on route {route_id}",
                "current_frequency": route_data["service_frequency"],
                "recommended_frequency": min(12, route_data["service_frequency"] + 2),
                "estimated_impact": "Reduce wait times by 25%"
            })
        
        # Check for high utilization routes
        for route_id, route_data in analysis["route_analysis"].items():
            if route_data["level"] == RushHourLevel.HIGH.value and route_id not in analysis["critical_routes"]:
                recommendations.append({
                    "type": "monitor_closely",
                    "priority": "medium",
                    "route_id": route_id,
                    "message": f"Monitor route {route_id} closely - approaching capacity",
                    "current_utilization": f"{route_data['capacity_utilization']*100:.1f}%"
                })
        
        return recommendations
    
    def _calculate_cost_benefit(self, route_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cost-benefit analysis for spare service deployment"""
        # Estimate additional passengers served
        additional_passengers = int(route_data["passenger_count"] * 0.3)  # 30% of current load
        additional_revenue = additional_passengers * self.revenue_per_passenger
        
        # Estimate costs
        deployment_hours = 3  # Typical deployment duration
        deployment_cost = deployment_hours * self.deployment_cost_per_hour
        
        # Net benefit
        net_benefit = additional_revenue - deployment_cost
        roi = (net_benefit / deployment_cost * 100) if deployment_cost > 0 else 0
        
        return {
            "additional_revenue": additional_revenue,
            "deployment_cost": deployment_cost,
            "net_benefit": net_benefit,
            "roi_percentage": roi
        }
    
    def deploy_spare_service(self, route_id: str, reason: str = "", duration_hours: int = 3) -> Optional[SpareService]:
        """Deploy a spare service to the specified route"""
        available_services = [s for s in self.spare_services.values() if s.status == "standby"]
        
        if not available_services:
            self.logger.warning("No spare services available for deployment")
            return None
        
        # Select the best available service
        spare_service = available_services[0]
        
        # Try to assign a driver
        driver_id = None
        if self.driver_manager:
            available_drivers = self.driver_manager.get_available_drivers()
            if available_drivers:
                driver_id = available_drivers[0].driver_id
                # Assign driver to shift
                self.driver_manager.assign_driver_to_shift(driver_id, f"SPARE-{route_id}", datetime.now())
        
        # Update service
        spare_service.route_id = route_id
        spare_service.driver_id = driver_id
        spare_service.deployment_time = datetime.now()
        spare_service.end_time = datetime.now() + timedelta(hours=duration_hours)
        spare_service.status = "deployed"
        spare_service.reason = reason or f"High demand on route {route_id}"
        
        self.logger.info(f"Deployed spare service {spare_service.service_id} to route {route_id}")
        
        # Log deployment in simulator if available
        if self.simulator and hasattr(self.simulator, 'activate_route'):
            # This would integrate with the bus simulator to actually add the spare bus
            pass
        
        return spare_service
    
    def predict_demand_forecast(self, route_id: str, hours_ahead: int = 2) -> Optional[DemandForecast]:
        """Predict demand forecast for a route"""
        current_time = datetime.now()
        forecast_time = current_time + timedelta(hours=hours_ahead)
        
        # Get historical patterns for this route
        patterns = self.rush_patterns.get(route_id, [])
        if not patterns:
            return None
        
        # Find similar historical patterns (same day of week, similar time)
        similar_patterns = []
        for pattern in patterns:
            if (pattern.date.weekday() == forecast_time.weekday() and
                abs(pattern.hour - forecast_time.hour) <= 1):
                similar_patterns.append(pattern)
        
        if not similar_patterns:
            # Use all patterns as fallback
            similar_patterns = patterns
        
        # Calculate predicted demand
        demand_values = [p.demand_level for p in similar_patterns]
        predicted_demand = statistics.mean(demand_values) if demand_values else 0.5
        
        # Calculate confidence based on pattern consistency
        if len(demand_values) > 1:
            confidence = 1.0 - (statistics.stdev(demand_values) / max(statistics.mean(demand_values), 0.1))
            confidence = max(0.3, min(1.0, confidence))
        else:
            confidence = 0.5
        
        # Determine recommended action
        recommended_action = ServiceAction.NO_ACTION
        spare_buses_needed = 0
        frequency_adjustment = 0.0
        
        if predicted_demand >= self.critical_threshold:
            recommended_action = ServiceAction.DEPLOY_SPARE
            spare_buses_needed = min(2, int((predicted_demand - self.critical_threshold) * 10))
        elif predicted_demand >= self.rush_hour_threshold:
            recommended_action = ServiceAction.INCREASE_FREQUENCY
            frequency_adjustment = min(3, (predicted_demand - self.rush_hour_threshold) * 10)
        
        forecast = DemandForecast(
            route_id=route_id,
            forecast_time=forecast_time,
            predicted_demand=predicted_demand,
            confidence=confidence,
            recommended_action=recommended_action,
            spare_buses_needed=spare_buses_needed,
            frequency_adjustment=frequency_adjustment
        )
        
        self.demand_forecasts[f"{route_id}-{forecast_time.strftime('%H%M')}"] = forecast
        return forecast
    
    def get_rush_hour_trends(self, route_id: str, days: int = 7) -> Dict[str, Any]:
        """Get rush hour trends for a specific route"""
        patterns = self.rush_patterns.get(route_id, [])
        if not patterns:
            return {"error": "No data available for route"}
        
        # Filter patterns for the specified period
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_patterns = [p for p in patterns if p.date >= cutoff_date]
        
        if not recent_patterns:
            return {"error": "No recent data available"}
        
        # Analyze trends by hour
        hourly_trends = {}
        for hour in range(6, 22):
            hour_patterns = [p for p in recent_patterns if p.hour == hour]
            if hour_patterns:
                hourly_trends[hour] = {
                    "avg_demand": statistics.mean([p.demand_level for p in hour_patterns]),
                    "avg_capacity_utilization": statistics.mean([p.capacity_utilization for p in hour_patterns]),
                    "avg_passengers": statistics.mean([p.passenger_count for p in hour_patterns]),
                    "avg_delay": statistics.mean([p.average_delay for p in hour_patterns]),
                    "peak_demand": max([p.demand_level for p in hour_patterns]),
                    "peak_capacity": max([p.capacity_utilization for p in hour_patterns])
                }
        
        # Identify peak hours
        peak_hours = sorted(hourly_trends.items(), 
                          key=lambda x: x[1]["avg_capacity_utilization"], 
                          reverse=True)[:3]
        
        # Calculate overall statistics
        overall_stats = {
            "avg_demand": statistics.mean([p.demand_level for p in recent_patterns]),
            "avg_capacity_utilization": statistics.mean([p.capacity_utilization for p in recent_patterns]),
            "avg_passengers": statistics.mean([p.passenger_count for p in recent_patterns]),
            "avg_delay": statistics.mean([p.average_delay for p in recent_patterns]),
            "peak_demand": max([p.demand_level for p in recent_patterns]),
            "peak_capacity": max([p.capacity_utilization for p in recent_patterns])
        }
        
        return {
            "route_id": route_id,
            "analysis_period_days": days,
            "total_patterns_analyzed": len(recent_patterns),
            "overall_statistics": overall_stats,
            "hourly_trends": hourly_trends,
            "peak_hours": [{"hour": h, **data} for h, data in peak_hours],
            "rush_hour_periods": self._identify_rush_periods(hourly_trends)
        }
    
    def _identify_rush_periods(self, hourly_trends: Dict[int, Dict]) -> List[Dict[str, Any]]:
        """Identify rush hour periods based on hourly trends"""
        rush_periods = []
        
        # Find consecutive hours with high utilization
        high_utilization_hours = [hour for hour, data in hourly_trends.items() 
                                if data["avg_capacity_utilization"] >= self.rush_hour_threshold]
        
        if not high_utilization_hours:
            return rush_periods
        
        # Group consecutive hours
        current_period = [high_utilization_hours[0]]
        for i in range(1, len(high_utilization_hours)):
            if high_utilization_hours[i] == high_utilization_hours[i-1] + 1:
                current_period.append(high_utilization_hours[i])
            else:
                # End current period
                if len(current_period) >= 2:  # At least 2 consecutive hours
                    rush_periods.append({
                        "start_hour": current_period[0],
                        "end_hour": current_period[-1] + 1,  # End of last hour
                        "duration_hours": len(current_period),
                        "avg_utilization": statistics.mean([hourly_trends[h]["avg_capacity_utilization"] 
                                                         for h in current_period])
                    })
                current_period = [high_utilization_hours[i]]
        
        # Add the last period if it meets criteria
        if len(current_period) >= 2:
            rush_periods.append({
                "start_hour": current_period[0],
                "end_hour": current_period[-1] + 1,
                "duration_hours": len(current_period),
                "avg_utilization": statistics.mean([hourly_trends[h]["avg_capacity_utilization"] 
                                                 for h in current_period])
            })
        
        return rush_periods
    
    def get_spare_service_performance(self) -> Dict[str, Any]:
        """Get performance metrics for spare services"""
        deployed_services = [s for s in self.spare_services.values() if s.status == "deployed"]
        completed_services = [s for s in self.spare_services.values() if s.status == "completed"]
        
        total_deployments = len(deployed_services) + len(completed_services)
        
        if total_deployments == 0:
            return {
                "total_deployments": 0,
                "active_deployments": 0,
                "total_passengers_served": 0,
                "total_revenue_generated": 0.0,
                "total_cost_incurred": 0.0,
                "net_roi": 0.0,
                "average_deployment_duration_hours": 0.0,
                "deployment_success_rate": 0.0
            }
        
        total_passengers = sum(s.passengers_served for s in completed_services)
        total_revenue = sum(s.revenue_generated for s in completed_services)
        total_cost = sum(s.cost_incurred for s in completed_services)
        
        # Calculate average deployment duration
        durations = []
        for service in completed_services:
            if service.end_time and service.deployment_time:
                duration = (service.end_time - service.deployment_time).total_seconds() / 3600
                durations.append(duration)
        
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # Calculate success rate (deployments that served passengers)
        successful_deployments = len([s for s in completed_services if s.passengers_served > 0])
        success_rate = (successful_deployments / len(completed_services)) * 100 if completed_services else 0.0
        
        return {
            "total_deployments": total_deployments,
            "active_deployments": len(deployed_services),
            "standby_services": len([s for s in self.spare_services.values() if s.status == "standby"]),
            "total_passengers_served": total_passengers,
            "total_revenue_generated": total_revenue,
            "total_cost_incurred": total_cost,
            "net_roi": ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0.0,
            "average_deployment_duration_hours": avg_duration,
            "deployment_success_rate": success_rate,
            "services": [
                {
                    "service_id": s.service_id,
                    "bus_id": s.bus_id,
                    "route_id": s.route_id,
                    "status": s.status,
                    "deployment_time": s.deployment_time.isoformat(),
                    "passengers_served": s.passengers_served,
                    "revenue_generated": s.revenue_generated
                }
                for s in self.spare_services.values()
            ]
        }
    
    def auto_deploy_if_needed(self) -> List[SpareService]:
        """Automatically deploy spare services based on current conditions"""
        deployed_services = []
        
        # Get current rush hour analysis
        analysis = self.analyze_current_rush_hour()
        
        # Check critical routes first
        for route_id in analysis["critical_routes"]:
            if len([s for s in self.spare_services.values() if s.status == "standby"]) == 0:
                break  # No more spare services available
            
            route_data = analysis["route_analysis"][route_id]
            reason = f"Critical capacity utilization ({route_data['capacity_utilization']*100:.1f}%)"
            
            service = self.deploy_spare_service(route_id, reason)
            if service:
                deployed_services.append(service)
        
        self.logger.info(f"Auto-deployed {len(deployed_services)} spare services")
        return deployed_services
    
    def update_spare_service_performance(self, service_id: str, passengers_served: int, 
                                      revenue_generated: float = None) -> bool:
        """Update performance metrics for a deployed spare service"""
        service = self.spare_services.get(service_id)
        if not service:
            return False
        
        service.passengers_served = passengers_served
        
        if revenue_generated is None:
            revenue_generated = passengers_served * self.revenue_per_passenger
        
        service.revenue_generated = revenue_generated
        
        # Calculate cost incurred
        if service.end_time and service.deployment_time:
            duration_hours = (service.end_time - service.deployment_time).total_seconds() / 3600
            service.cost_incurred = duration_hours * self.deployment_cost_per_hour
        
        self.logger.info(f"Updated performance for service {service_id}: {passengers_served} passengers, ${revenue_generated:.2f} revenue")
        return True
