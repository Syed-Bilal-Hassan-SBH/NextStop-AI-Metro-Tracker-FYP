"""
multi_route_management.py
==========================
NEW FILE - Multi-route Management with Activation/Deactivation Controls
Comprehensive route management system with dynamic activation, deactivation, and configuration

Features:
- Route activation/deactivation controls
- Route configuration management
- Service scheduling
- Route performance monitoring
- Dynamic route optimization
- Route status tracking
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json
import random

class RouteStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"
    SEASONAL = "seasonal"
    EMERGENCY = "emergency"

class ServiceType(Enum):
    REGULAR = "regular"
    EXPRESS = "express"
    LIMITED = "limited"
    SHUTTLE = "shuttle"
    NIGHT = "night"
    WEEKEND = "weekend"

class RoutePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RouteConfiguration:
    """Route configuration settings"""
    route_id: str
    name: str
    description: str
    service_type: ServiceType
    priority: RoutePriority
    base_frequency: int  # minutes between buses
    operating_hours: Tuple[int, int]  # (start_hour, end_hour)
    days_of_operation: List[int]  # 0=Monday, 6=Sunday
    stops: List[str]
    distance: float  # km
    estimated_duration: float  # minutes
    capacity: int  # passengers per bus
    fare_structure: Dict[str, float]  # different fare types
    accessibility_features: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: str

@dataclass
class RouteSchedule:
    """Route scheduling information"""
    schedule_id: str
    route_id: str
    valid_from: datetime
    valid_until: datetime
    frequency: int  # minutes
    special_schedule: bool = False
    schedule_type: str = "regular"  # regular, holiday, special_event
    modified_frequency: Optional[int] = None
    additional_buses: int = 0
    reduced_service: bool = False
    notes: str = ""

@dataclass
class RoutePerformance:
    """Route performance metrics"""
    route_id: str
    date: datetime
    total_trips: int
    on_time_trips: int
    total_passengers: int
    revenue: float
    average_delay: float
    passenger_satisfaction: float
    fuel_efficiency: float
    incident_count: int
    completion_rate: float

@dataclass
class RouteStatusHistory:
    """Route status change history"""
    history_id: str
    route_id: str
    old_status: RouteStatus
    new_status: RouteStatus
    changed_at: datetime
    changed_by: str
    reason: str
    impact_assessment: str

class MultiRouteManager:
    """Comprehensive multi-route management system"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.routes: Dict[str, RouteConfiguration] = {}
        self.route_statuses: Dict[str, RouteStatus] = {}
        self.route_schedules: Dict[str, List[RouteSchedule]] = {}
        self.route_performance: Dict[str, List[RoutePerformance]] = {}
        self.status_history: List[RouteStatusHistory] = []
        
        # Configuration
        self.max_active_routes = 50
        self.maintenance_window_hours = 4
        self.activation_cooldown = timedelta(minutes=30)
        self.deactivation_threshold = 0.3  # performance threshold for auto-deactivation
        
        # Initialize with sample data
        self._initialize_sample_routes()
        self._initialize_sample_schedules()
        self._initialize_sample_performance()
    
    def _initialize_sample_routes(self):
        """Create sample route configurations"""
        sample_routes = [
            {
                "route_id": "FR-01",
                "name": "Downtown Express",
                "description": "Express service from Airport to Downtown",
                "service_type": ServiceType.EXPRESS,
                "priority": RoutePriority.HIGH,
                "base_frequency": 15,
                "operating_hours": (5, 23),
                "days_of_operation": [0, 1, 2, 3, 4, 5, 6],
                "stops": ["STOP-01", "STOP-02", "STOP-03", "STOP-04", "STOP-05"],
                "distance": 25.5,
                "estimated_duration": 45,
                "capacity": 80,
                "fare_structure": {"adult": 5.0, "senior": 2.5, "student": 3.0},
                "accessibility_features": ["wheelchair", "audio_announcements", "low_floor"]
            },
            {
                "route_id": "FR-02",
                "name": "City Circular",
                "description": "Circular route connecting major city landmarks",
                "service_type": ServiceType.REGULAR,
                "priority": RoutePriority.MEDIUM,
                "base_frequency": 20,
                "operating_hours": (6, 22),
                "days_of_operation": [0, 1, 2, 3, 4, 5, 6],
                "stops": ["STOP-06", "STOP-07", "STOP-08", "STOP-09", "STOP-10"],
                "distance": 18.2,
                "estimated_duration": 35,
                "capacity": 60,
                "fare_structure": {"adult": 3.0, "senior": 1.5, "student": 2.0},
                "accessibility_features": ["wheelchair", "audio_announcements"]
            },
            {
                "route_id": "FR-03A",
                "name": "University Shuttle",
                "description": "Shuttle service to University Campus",
                "service_type": ServiceType.SHUTTLE,
                "priority": RoutePriority.MEDIUM,
                "base_frequency": 10,
                "operating_hours": (7, 21),
                "days_of_operation": [0, 1, 2, 3, 4],
                "stops": ["STOP-11", "STOP-12", "STOP-13", "STOP-14"],
                "distance": 12.8,
                "estimated_duration": 25,
                "capacity": 40,
                "fare_structure": {"adult": 2.0, "senior": 1.0, "student": 1.0},
                "accessibility_features": ["wheelchair", "low_floor"]
            },
            {
                "route_id": "FR-04",
                "name": "Night Owl",
                "description": "Late night service on weekends",
                "service_type": ServiceType.NIGHT,
                "priority": RoutePriority.LOW,
                "base_frequency": 30,
                "operating_hours": (22, 4),
                "days_of_operation": [5, 6],
                "stops": ["STOP-15", "STOP-16", "STOP-17", "STOP-18"],
                "distance": 22.1,
                "estimated_duration": 40,
                "capacity": 50,
                "fare_structure": {"adult": 4.0, "senior": 2.0, "student": 3.0},
                "accessibility_features": ["wheelchair"]
            },
            {
                "route_id": "FR-05",
                "name": "Weekend Express",
                "description": "Weekend express service to shopping district",
                "service_type": ServiceType.WEEKEND,
                "priority": RoutePriority.MEDIUM,
                "base_frequency": 25,
                "operating_hours": (8, 20),
                "days_of_operation": [5, 6],
                "stops": ["STOP-19", "STOP-20", "STOP-21", "STOP-22", "STOP-23"],
                "distance": 30.3,
                "estimated_duration": 50,
                "capacity": 70,
                "fare_structure": {"adult": 4.5, "senior": 2.25, "student": 3.5},
                "accessibility_features": ["wheelchair", "audio_announcements", "low_floor"]
            }
        ]
        
        current_time = datetime.now()
        for route_data in sample_routes:
            route = RouteConfiguration(
                created_at=current_time,
                updated_at=current_time,
                created_by="system",
                **route_data
            )
            self.routes[route.route_id] = route
            self.route_statuses[route.route_id] = RouteStatus.ACTIVE
    
    def _initialize_sample_schedules(self):
        """Create sample route schedules"""
        current_time = datetime.now()
        
        for route_id in self.routes.keys():
            schedules = []
            
            # Regular schedule
            regular_schedule = RouteSchedule(
                schedule_id=f"SCHED-{route_id}-REG",
                route_id=route_id,
                valid_from=current_time - timedelta(days=30),
                valid_until=current_time + timedelta(days=365),
                frequency=self.routes[route_id].base_frequency,
                special_schedule=False,
                schedule_type="regular"
            )
            schedules.append(regular_schedule)
            
            # Weekend schedule for some routes
            if self.routes[route_id].service_type in [ServiceType.WEEKEND, ServiceType.NIGHT]:
                weekend_schedule = RouteSchedule(
                    schedule_id=f"SCHED-{route_id}-WEEK",
                    route_id=route_id,
                    valid_from=current_time - timedelta(days=30),
                    valid_until=current_time + timedelta(days=365),
                    frequency=self.routes[route_id].base_frequency + 5,  # Less frequent on weekends
                    special_schedule=True,
                    schedule_type="weekend"
                )
                schedules.append(weekend_schedule)
            
            # Holiday schedule
            holiday_schedule = RouteSchedule(
                schedule_id=f"SCHED-{route_id}-HOL",
                route_id=route_id,
                valid_from=current_time - timedelta(days=30),
                valid_until=current_time + timedelta(days=365),
                frequency=self.routes[route_id].base_frequency + 10,  # Much less frequent on holidays
                special_schedule=True,
                schedule_type="holiday",
                reduced_service=True
            )
            schedules.append(holiday_schedule)
            
            self.route_schedules[route_id] = schedules
    
    def _initialize_sample_performance(self):
        """Create sample performance data"""
        current_time = datetime.now()
        
        for route_id in self.routes.keys():
            performances = []
            
            # Generate performance data for the last 30 days
            for days_ago in range(30):
                date = current_time - timedelta(days=days_ago)
                
                # Generate daily performance metrics
                total_trips = random.randint(20, 100)
                on_time_trips = int(total_trips * random.uniform(0.7, 0.95))
                total_passengers = random.randint(500, 3000)
                revenue = total_passengers * random.uniform(2, 6)
                average_delay = random.exponential(3)  # Average delay in minutes
                passenger_satisfaction = random.uniform(3.5, 5.0)
                fuel_efficiency = random.uniform(4, 8)
                incident_count = random.randint(0, 3)
                completion_rate = random.uniform(0.9, 1.0)
                
                performance = RoutePerformance(
                    route_id=route_id,
                    date=date,
                    total_trips=total_trips,
                    on_time_trips=on_time_trips,
                    total_passengers=total_passengers,
                    revenue=revenue,
                    average_delay=average_delay,
                    passenger_satisfaction=passenger_satisfaction,
                    fuel_efficiency=fuel_efficiency,
                    incident_count=incident_count,
                    completion_rate=completion_rate
                )
                performances.append(performance)
            
            self.route_performance[route_id] = performances
    
    def create_route(self, name: str, description: str, service_type: ServiceType,
                    priority: RoutePriority, base_frequency: int, operating_hours: Tuple[int, int],
                    days_of_operation: List[int], stops: List[str], distance: float,
                    estimated_duration: float, capacity: int, fare_structure: Dict[str, float],
                    accessibility_features: List[str], created_by: str) -> RouteConfiguration:
        """Create a new route"""
        route_id = f"FR-{len(self.routes) + 1:02d}"
        
        # Check if route ID already exists
        while route_id in self.routes:
            route_id = f"FR-{len(self.routes) + 2:02d}"
        
        route = RouteConfiguration(
            route_id=route_id,
            name=name,
            description=description,
            service_type=service_type,
            priority=priority,
            base_frequency=base_frequency,
            operating_hours=operating_hours,
            days_of_operation=days_of_operation,
            stops=stops,
            distance=distance,
            estimated_duration=estimated_duration,
            capacity=capacity,
            fare_structure=fare_structure,
            accessibility_features=accessibility_features,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=created_by
        )
        
        self.routes[route_id] = route
        self.route_statuses[route_id] = RouteStatus.INACTIVE
        
        # Create default schedule
        default_schedule = RouteSchedule(
            schedule_id=f"SCHED-{route_id}-DEFAULT",
            route_id=route_id,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365),
            frequency=base_frequency,
            special_schedule=False,
            schedule_type="regular"
        )
        
        self.route_schedules[route_id] = [default_schedule]
        
        self.logger.info(f"Route created: {route_id} - {name}")
        return route
    
    def activate_route(self, route_id: str, activated_by: str, reason: str = "") -> bool:
        """Activate a route"""
        if route_id not in self.routes:
            return False
        
        current_status = self.route_statuses[route_id]
        
        # Check if route can be activated
        if current_status == RouteStatus.ACTIVE:
            return True  # Already active
        
        if current_status == RouteStatus.MAINTENANCE:
            self.logger.warning(f"Cannot activate route {route_id} - currently under maintenance")
            return False
        
        # Check cooldown period
        recent_deactivation = [h for h in self.status_history 
                            if h.route_id == route_id and h.new_status == RouteStatus.INACTIVE
                            and (datetime.now() - h.changed_at) < self.activation_cooldown]
        
        if recent_deactivation:
            self.logger.warning(f"Route {route_id} is in cooldown period")
            return False
        
        # Update status
        old_status = current_status
        self.route_statuses[route_id] = RouteStatus.ACTIVE
        
        # Record status change
        history = RouteStatusHistory(
            history_id=f"HIST-{route_id}-{int(datetime.now().timestamp())}",
            route_id=route_id,
            old_status=old_status,
            new_status=RouteStatus.ACTIVE,
            changed_at=datetime.now(),
            changed_by=activated_by,
            reason=reason or "Manual activation",
            impact_assessment=self._assess_activation_impact(route_id)
        )
        
        self.status_history.append(history)
        
        self.logger.info(f"Route {route_id} activated by {activated_by}")
        return True
    
    def deactivate_route(self, route_id: str, deactivated_by: str, reason: str = "") -> bool:
        """Deactivate a route"""
        if route_id not in self.routes:
            return False
        
        current_status = self.route_statuses[route_id]
        
        if current_status == RouteStatus.INACTIVE:
            return True  # Already inactive
        
        if current_status == RouteStatus.CRITICAL and self.routes[route_id].priority == RoutePriority.CRITICAL:
            self.logger.warning(f"Cannot deactivate critical route {route_id}")
            return False
        
        # Update status
        old_status = current_status
        self.route_statuses[route_id] = RouteStatus.INACTIVE
        
        # Record status change
        history = RouteStatusHistory(
            history_id=f"HIST-{route_id}-{int(datetime.now().timestamp())}",
            route_id=route_id,
            old_status=old_status,
            new_status=RouteStatus.INACTIVE,
            changed_at=datetime.now(),
            changed_by=deactivated_by,
            reason=reason or "Manual deactivation",
            impact_assessment=self._assess_deactivation_impact(route_id)
        )
        
        self.status_history.append(history)
        
        self.logger.info(f"Route {route_id} deactivated by {deactivated_by}")
        return True
    
    def set_maintenance_mode(self, route_id: str, set_by: str, reason: str = "", 
                          estimated_duration: Optional[timedelta] = None) -> bool:
        """Set route to maintenance mode"""
        if route_id not in self.routes:
            return False
        
        current_status = self.route_statuses[route_id]
        
        if current_status == RouteStatus.MAINTENANCE:
            return True  # Already in maintenance
        
        # Update status
        old_status = current_status
        self.route_statuses[route_id] = RouteStatus.MAINTENANCE
        
        # Record status change
        impact_assessment = f"Maintenance mode - estimated duration: {estimated_duration}" if estimated_duration else "Maintenance mode"
        
        history = RouteStatusHistory(
            history_id=f"HIST-{route_id}-{int(datetime.now().timestamp())}",
            route_id=route_id,
            old_status=old_status,
            new_status=RouteStatus.MAINTENANCE,
            changed_at=datetime.now(),
            changed_by=set_by,
            reason=reason or "Scheduled maintenance",
            impact_assessment=impact_assessment
        )
        
        self.status_history.append(history)
        
        self.logger.info(f"Route {route_id} set to maintenance mode by {set_by}")
        return True
    
    def _assess_activation_impact(self, route_id: str) -> str:
        """Assess the impact of route activation"""
        route = self.routes[route_id]
        
        impact_factors = []
        
        # Priority impact
        if route.priority == RoutePriority.CRITICAL:
            impact_factors.append("Critical service restoration")
        elif route.priority == RoutePriority.HIGH:
            impact_factors.append("High priority service added")
        
        # Service type impact
        if route.service_type == ServiceType.EXPRESS:
            impact_factors.append("Express service improved connectivity")
        elif route.service_type == ServiceType.SHUTTLE:
            impact_factors.append("Shuttle service enhances last-mile connectivity")
        
        # Capacity impact
        if route.capacity > 60:
            impact_factors.append("High capacity route increases system capacity")
        
        return "; ".join(impact_factors) if impact_factors else "Standard route activation"
    
    def _assess_deactivation_impact(self, route_id: str) -> str:
        """Assess the impact of route deactivation"""
        route = self.routes[route_id]
        
        impact_factors = []
        
        # Priority impact
        if route.priority == RoutePriority.CRITICAL:
            impact_factors.append("Critical service disruption - high impact")
        elif route.priority == RoutePriority.HIGH:
            impact_factors.append("High priority service discontinued")
        
        # Service type impact
        if route.service_type == ServiceType.EXPRESS:
            impact_factors.append("Express service loss affects connectivity")
        elif route.service_type == ServiceType.SHUTTLE:
            impact_factors.append("Shuttle service loss affects last-mile connectivity")
        
        # Passenger impact (based on recent performance)
        recent_performance = self.route_performance.get(route_id, [])
        if recent_performance:
            avg_passengers = statistics.mean([p.total_passengers for p in recent_performance[-7:]])
            if avg_passengers > 1000:
                impact_factors.append(f"High passenger impact ({avg_passengers:.0f} daily passengers)")
        
        return "; ".join(impact_factors) if impact_factors else "Standard route deactivation"
    
    def get_route_status(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Get current status and information for a route"""
        if route_id not in self.routes:
            return None
        
        route = self.routes[route_id]
        status = self.route_statuses[route_id]
        schedules = self.route_schedules.get(route_id, [])
        
        # Get current active schedule
        current_time = datetime.now()
        active_schedule = None
        for schedule in schedules:
            if schedule.valid_from <= current_time <= schedule.valid_until:
                active_schedule = schedule
                break
        
        # Get recent performance
        recent_performance = self.route_performance.get(route_id, [])
        last_7_days = [p for p in recent_performance if p.date >= current_time - timedelta(days=7)]
        
        performance_summary = {}
        if last_7_days:
            performance_summary = {
                "avg_on_time_rate": statistics.mean([p.on_time_trips / p.total_trips for p in last_7_days]) * 100,
                "avg_passengers_per_day": statistics.mean([p.total_passengers for p in last_7_days]),
                "avg_satisfaction": statistics.mean([p.passenger_satisfaction for p in last_7_days]),
                "total_incidents": sum([p.incident_count for p in last_7_days])
            }
        
        return {
            "route_id": route_id,
            "name": route.name,
            "description": route.description,
            "current_status": status.value,
            "service_type": route.service_type.value,
            "priority": route.priority.value,
            "configuration": {
                "base_frequency": route.base_frequency,
                "operating_hours": route.operating_hours,
                "days_of_operation": route.days_of_operation,
                "stops": route.stops,
                "distance": route.distance,
                "estimated_duration": route.estimated_duration,
                "capacity": route.capacity,
                "fare_structure": route.fare_structure,
                "accessibility_features": route.accessibility_features
            },
            "active_schedule": {
                "schedule_id": active_schedule.schedule_id,
                "frequency": active_schedule.frequency,
                "schedule_type": active_schedule.schedule_type,
                "special_schedule": active_schedule.special_schedule
            } if active_schedule else None,
            "performance_summary": performance_summary,
            "last_updated": route.updated_at.isoformat()
        }
    
    def get_all_routes_status(self) -> List[Dict[str, Any]]:
        """Get status of all routes"""
        routes_status = []
        
        for route_id in self.routes.keys():
            route_info = self.get_route_status(route_id)
            if route_info:
                routes_status.append(route_info)
        
        # Sort by priority and status
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        routes_status.sort(key=lambda x: (priority_order.get(x["priority"], 4), x["current_status"]))
        
        return routes_status
    
    def update_route_configuration(self, route_id: str, updates: Dict[str, Any], updated_by: str) -> bool:
        """Update route configuration"""
        if route_id not in self.routes:
            return False
        
        route = self.routes[route_id]
        
        # Update allowed fields
        allowed_fields = [
            "name", "description", "service_type", "priority", "base_frequency",
            "operating_hours", "days_of_operation", "stops", "distance",
            "estimated_duration", "capacity", "fare_structure", "accessibility_features"
        ]
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(route, field):
                setattr(route, field, value)
        
        route.updated_at = datetime.now()
        
        self.logger.info(f"Route {route_id} configuration updated by {updated_by}")
        return True
    
    def create_special_schedule(self, route_id: str, valid_from: datetime, valid_until: datetime,
                              frequency: int, schedule_type: str, notes: str = "",
                              additional_buses: int = 0, reduced_service: bool = False,
                              created_by: str = "system") -> bool:
        """Create a special schedule for a route"""
        if route_id not in self.routes:
            return False
        
        schedule = RouteSchedule(
            schedule_id=f"SCHED-{route_id}-{int(datetime.now().timestamp())}",
            route_id=route_id,
            valid_from=valid_from,
            valid_until=valid_until,
            frequency=frequency,
            special_schedule=True,
            schedule_type=schedule_type,
            additional_buses=additional_buses,
            reduced_service=reduced_service,
            notes=notes
        )
        
        self.route_schedules[route_id].append(schedule)
        
        self.logger.info(f"Special schedule created for route {route_id}: {schedule_type}")
        return True
    
    def get_route_performance_report(self, route_id: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get performance report for a specific route"""
        if route_id not in self.routes:
            return None
        
        performances = self.route_performance.get(route_id, [])
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_performances = [p for p in performances if p.date >= cutoff_date]
        
        if not recent_performances:
            return {"error": "No performance data available for the specified period"}
        
        # Calculate metrics
        total_trips = sum(p.total_trips for p in recent_performances)
        on_time_trips = sum(p.on_time_trips for p in recent_performances)
        total_passengers = sum(p.total_passengers for p in recent_performances)
        total_revenue = sum(p.revenue for p in recent_performances)
        total_incidents = sum(p.incident_count for p in recent_performances)
        
        # Averages
        avg_on_time_rate = (on_time_trips / total_trips) * 100 if total_trips > 0 else 0
        avg_passenger_satisfaction = statistics.mean([p.passenger_satisfaction for p in recent_performances])
        avg_fuel_efficiency = statistics.mean([p.fuel_efficiency for p in recent_performances])
        avg_completion_rate = statistics.mean([p.completion_rate for p in recent_performances])
        
        # Trends
        if len(recent_performances) >= 14:
            # Compare first half to second half
            mid_point = len(recent_performances) // 2
            early_period = recent_performances[:mid_point]
            recent_period = recent_performances[mid_point:]
            
            early_on_time = sum(p.on_time_trips for p in early_period) / sum(p.total_trips for p in early_period) * 100
            recent_on_time = sum(p.on_time_trips for p in recent_period) / sum(p.total_trips for p in recent_period) * 100
            
            on_time_trend = "improving" if recent_on_time > early_on_time + 2 else "declining" if recent_on_time < early_on_time - 2 else "stable"
        else:
            on_time_trend = "insufficient_data"
        
        return {
            "route_id": route_id,
            "period_days": days,
            "performance_metrics": {
                "total_trips": total_trips,
                "on_time_performance_percentage": avg_on_time_rate,
                "total_passengers": total_passengers,
                "total_revenue": total_revenue,
                "average_passenger_satisfaction": avg_passenger_satisfaction,
                "average_fuel_efficiency": avg_fuel_efficiency,
                "average_completion_rate": avg_completion_rate,
                "total_incidents": total_incidents,
                "incident_rate_per_1000_trips": (total_incidents / total_trips) * 1000 if total_trips > 0 else 0
            },
            "trends": {
                "on_time_performance": on_time_trend
            },
            "recommendations": self._generate_route_recommendations(route_id, recent_performances)
        }
    
    def _generate_route_recommendations(self, route_id: str, performances: List[RoutePerformance]) -> List[str]:
        """Generate recommendations for route improvement"""
        recommendations = []
        
        if not performances:
            return ["Insufficient data for recommendations"]
        
        # On-time performance
        avg_on_time = statistics.mean([p.on_time_trips / p.total_trips for p in performances]) * 100
        if avg_on_time < 80:
            recommendations.append("Improve on-time performance through schedule optimization")
        
        # Passenger satisfaction
        avg_satisfaction = statistics.mean([p.passenger_satisfaction for p in performances])
        if avg_satisfaction < 4.0:
            recommendations.append("Address passenger satisfaction issues through service quality improvements")
        
        # Fuel efficiency
        avg_fuel_efficiency = statistics.mean([p.fuel_efficiency for p in performances])
        if avg_fuel_efficiency < 5:
            recommendations.append("Optimize fuel efficiency through driver training and vehicle maintenance")
        
        # Incidents
        total_incidents = sum(p.incident_count for p in performances)
        if total_incidents > len(performances) * 0.5:  # More than 0.5 incidents per day on average
            recommendations.append("Review safety protocols and incident prevention measures")
        
        # Completion rate
        avg_completion = statistics.mean([p.completion_rate for p in performances])
        if avg_completion < 0.95:
            recommendations.append("Improve route completion rate through better reliability measures")
        
        if not recommendations:
            recommendations.append("Route performance is within acceptable parameters")
        
        return recommendations
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide overview of all routes"""
        total_routes = len(self.routes)
        active_routes = len([r for r in self.route_statuses.values() if r == RouteStatus.ACTIVE])
        inactive_routes = len([r for r in self.route_statuses.values() if r == RouteStatus.INACTIVE])
        maintenance_routes = len([r for r in self.route_statuses.values() if r == RouteStatus.MAINTENANCE])
        
        # Service type distribution
        service_type_counts = {}
        for route in self.routes.values():
            service_type_counts[route.service_type.value] = service_type_counts.get(route.service_type.value, 0) + 1
        
        # Priority distribution
        priority_counts = {}
        for route in self.routes.values():
            priority_counts[route.priority.value] = priority_counts.get(route.priority.value, 0) + 1
        
        # System performance
        total_system_trips = 0
        total_system_passengers = 0
        total_system_revenue = 0
        
        for performances in self.route_performance.values():
            recent_performances = [p for p in performances if p.date >= datetime.now() - timedelta(days=7)]
            if recent_performances:
                total_system_trips += sum(p.total_trips for p in recent_performances)
                total_system_passengers += sum(p.total_passengers for p in recent_performances)
                total_system_revenue += sum(p.revenue for p in recent_performances)
        
        return {
            "route_counts": {
                "total": total_routes,
                "active": active_routes,
                "inactive": inactive_routes,
                "maintenance": maintenance_routes,
                "activation_rate": (active_routes / total_routes) * 100 if total_routes > 0 else 0
            },
            "distribution": {
                "by_service_type": service_type_counts,
                "by_priority": priority_counts
            },
            "system_performance": {
                "weekly_trips": total_system_trips,
                "weekly_passengers": total_system_passengers,
                "weekly_revenue": total_system_revenue,
                "avg_passengers_per_trip": total_system_passengers / total_system_trips if total_system_trips > 0 else 0
            },
            "recent_status_changes": [
                {
                    "route_id": h.route_id,
                    "old_status": h.old_status.value,
                    "new_status": h.new_status.value,
                    "changed_at": h.changed_at.isoformat(),
                    "changed_by": h.changed_by,
                    "reason": h.reason
                }
                for h in sorted(self.status_history, key=lambda x: x.changed_at, reverse=True)[:10]
            ]
        }
