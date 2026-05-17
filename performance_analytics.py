<<<<<<< HEAD
"""
performance_analytics.py
=======================
NEW FILE - Comprehensive Performance Analytics Dashboard
Provides detailed performance analytics, ETA accuracy, delay patterns, and route efficiency

Features:
- ETA accuracy tracking
- Delay pattern analysis
- Route efficiency metrics
- Performance trend analysis
- Comparative analytics
- Predictive insights
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json
import random

class PerformanceMetric(Enum):
    ETA_ACCURACY = "eta_accuracy"
    ON_TIME_PERFORMANCE = "on_time_performance"
    ROUTE_EFFICIENCY = "route_efficiency"
    FUEL_EFFICIENCY = "fuel_efficiency"
    PASSENGER_SATISFACTION = "passenger_satisfaction"
    SERVICE_RELIABILITY = "service_reliability"

class TrendDirection(Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class ETAAccuracyRecord:
    """Record of ETA prediction accuracy"""
    record_id: str
    bus_id: str
    route_id: str
    stop_id: str
    predicted_eta: datetime
    actual_arrival: datetime
    prediction_made_time: datetime
    error_minutes: float
    context: Dict[str, Any]  # Traffic, weather, etc.
    confidence_score: float

@dataclass
class DelayRecord:
    """Record of service delays"""
    delay_id: str
    bus_id: str
    route_id: str
    scheduled_time: datetime
    actual_time: datetime
    delay_minutes: float
    delay_reason: str
    affected_stops: List[str]
    passenger_impact: int
    recovery_time: Optional[datetime] = None

@dataclass
class RouteEfficiencyMetrics:
    """Efficiency metrics for a specific route"""
    route_id: str
    date: datetime
    total_trips: int
    on_time_trips: int
    average_delay: float
    total_distance: float  # km
    total_time: float  # hours
    average_speed: float  # km/h
    fuel_consumed: float  # liters
    passengers_carried: int
    revenue_generated: float
    cost_incurred: float

@dataclass
class PerformanceTrend:
    """Performance trend over time"""
    metric: PerformanceMetric
    entity_id: str  # bus_id, route_id, or system
    direction: TrendDirection
    change_percentage: float
    confidence: float
    time_period: str  # "daily", "weekly", "monthly"
    data_points: List[Tuple[datetime, float]]
    analysis_notes: str = ""

class PerformanceAnalyticsManager:
    """Comprehensive performance analytics system"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.eta_records: Dict[str, List[ETAAccuracyRecord]] = {}  # route_id -> records
        self.delay_records: Dict[str, List[DelayRecord]] = {}  # route_id -> records
        self.route_efficiency: Dict[str, List[RouteEfficiencyMetrics]] = {}  # route_id -> metrics
        self.performance_trends: Dict[str, List[PerformanceTrend]] = {}
        
        # Configuration
        self.eta_accuracy_threshold = 5.0  # minutes
        self.significant_delay_threshold = 10.0  # minutes
        self.trend_analysis_window = timedelta(days=30)
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Create sample performance data for demonstration"""
        routes = ["FR-01", "FR-02", "FR-03A", "FR-04", "FR-05"]
        buses = ["BUS-01", "BUS-02", "BUS-03", "BUS-04", "BUS-05"]
        
        # Generate ETA accuracy records
        for route_id in routes:
            eta_records = []
            
            # Generate records for the last 7 days
            for days_ago in range(7):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 10-20 records per day
                for record_num in range(random.randint(10, 20)):
                    record_time = date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    # Simulate ETA prediction with varying accuracy
                    base_error = random.gauss(0, 3)  # Normal distribution around 0
                    context_factor = random.uniform(0.5, 1.5)  # Context affects accuracy
                    error_minutes = base_error * context_factor
                    
                    record = ETAAccuracyRecord(
                        record_id=f"ETA-{route_id}-{int(record_time.timestamp())}",
                        bus_id=random.choice(buses),
                        route_id=route_id,
                        stop_id=f"STOP-{random.randint(1, 20)}",
                        predicted_eta=record_time + timedelta(minutes=random.randint(5, 45)),
                        actual_arrival=record_time + timedelta(minutes=random.randint(5, 45)) + timedelta(minutes=error_minutes),
                        prediction_made_time=record_time - timedelta(minutes=random.randint(15, 30)),
                        error_minutes=abs(error_minutes),
                        context={
                            "traffic_level": random.uniform(0.1, 1.0),
                            "weather": random.choice(["clear", "rain", "fog"]),
                            "day_of_week": record_time.weekday(),
                            "hour": record_time.hour
                        },
                        confidence_score=max(0.3, 1.0 - abs(error_minutes) / 10)
                    )
                    eta_records.append(record)
            
            self.eta_records[route_id] = eta_records
        
        # Generate delay records
        for route_id in routes:
            delay_records = []
            
            for days_ago in range(7):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 2-8 delay records per day
                for delay_num in range(random.randint(2, 8)):
                    delay_time = date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    delay_minutes = random.expovariate(1/5)  # Exponential distribution for delays
                    if delay_minutes < 2:  # Minimum significant delay
                        continue
                    
                    delay_reason = random.choice([
                        "heavy_traffic", "weather", "mechanical_issue", 
                        "passenger_incident", "road_closure", "signal_failure"
                    ])
                    
                    record = DelayRecord(
                        delay_id=f"DELAY-{route_id}-{int(delay_time.timestamp())}",
                        bus_id=random.choice(buses),
                        route_id=route_id,
                        scheduled_time=delay_time,
                        actual_time=delay_time + timedelta(minutes=delay_minutes),
                        delay_minutes=delay_minutes,
                        delay_reason=delay_reason,
                        affected_stops=[f"STOP-{i}" for i in range(random.randint(1, 5))],
                        passenger_impact=random.randint(10, 100),
                        recovery_time=delay_time + timedelta(minutes=delay_minutes + random.uniform(5, 30))
                    )
                    delay_records.append(record)
            
            self.delay_records[route_id] = delay_records
        
        # Generate route efficiency metrics
        for route_id in routes:
            efficiency_metrics = []
            
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Simulate daily efficiency metrics
                total_trips = random.randint(20, 50)
                on_time_trips = int(total_trips * random.uniform(0.7, 0.95))
                average_delay = random.expovariate(1/3)  # Average delay in minutes
                
                metrics = RouteEfficiencyMetrics(
                    route_id=route_id,
                    date=date,
                    total_trips=total_trips,
                    on_time_trips=on_time_trips,
                    average_delay=average_delay,
                    total_distance=random.uniform(200, 800),  # km
                    total_time=random.uniform(8, 16),  # hours
                    average_speed=random.uniform(25, 45),  # km/h
                    fuel_consumed=random.uniform(100, 400),  # liters
                    passengers_carried=random.randint(500, 2000),
                    revenue_generated=random.uniform(1000, 5000),
                    cost_incurred=random.uniform(800, 3000)
                )
                efficiency_metrics.append(metrics)
            
            self.route_efficiency[route_id] = efficiency_metrics
    
    def calculate_eta_accuracy(self, route_id: Optional[str] = None, 
                             time_period: int = 7) -> Dict[str, Any]:
        """Calculate ETA accuracy metrics"""
        cutoff_time = datetime.now() - timedelta(days=time_period)
        
        all_records = []
        if route_id:
            all_records = [r for r in self.eta_records.get(route_id, []) 
                         if r.actual_arrival >= cutoff_time]
        else:
            for records in self.eta_records.values():
                all_records.extend([r for r in records if r.actual_arrival >= cutoff_time])
        
        if not all_records:
            return {"error": "No ETA data available for the specified period"}
        
        # Calculate accuracy metrics
        errors = [r.error_minutes for r in all_records]
        within_threshold = len([e for e in errors if e <= self.eta_accuracy_threshold])
        
        # By context factors
        traffic_accuracy = {}
        weather_accuracy = {}
        hour_accuracy = {}
        
        for record in all_records:
            traffic = record.context.get("traffic_level", 0.5)
            weather = record.context.get("weather", "clear")
            hour = record.context.get("hour", 12)
            
            if traffic not in traffic_accuracy:
                traffic_accuracy[traffic] = []
            if weather not in weather_accuracy:
                weather_accuracy[weather] = []
            if hour not in hour_accuracy:
                hour_accuracy[hour] = []
            
            traffic_accuracy[traffic].append(record.error_minutes)
            weather_accuracy[weather].append(record.error_minutes)
            hour_accuracy[hour].append(record.error_minutes)
        
        # Calculate averages by context
        for key in list(traffic_accuracy.keys()):
            traffic_accuracy[key] = statistics.mean(traffic_accuracy[key])
        
        for key in list(weather_accuracy.keys()):
            weather_accuracy[key] = statistics.mean(weather_accuracy[key])
        
        for key in list(hour_accuracy.keys()):
            hour_accuracy[key] = statistics.mean(hour_accuracy[key])
        
        return {
            "period_days": time_period,
            "total_predictions": len(all_records),
            "average_error_minutes": statistics.mean(errors),
            "median_error_minutes": statistics.median(errors),
            "within_threshold_percentage": (within_threshold / len(all_records)) * 100,
            "accuracy_distribution": {
                "excellent": len([e for e in errors if e <= 2]) / len(all_records) * 100,
                "good": len([e for e in errors if 2 < e <= 5]) / len(all_records) * 100,
                "fair": len([e for e in errors if 5 < e <= 10]) / len(all_records) * 100,
                "poor": len([e for e in errors if e > 10]) / len(all_errors) * 100
            },
            "accuracy_by_context": {
                "traffic_level": traffic_accuracy,
                "weather": weather_accuracy,
                "hour_of_day": hour_accuracy
            },
            "confidence_correlation": self._calculate_confidence_correlation(all_records)
        }
    
    def _calculate_confidence_correlation(self, records: List[ETAAccuracyRecord]) -> float:
        """Calculate correlation between confidence scores and actual accuracy"""
        if len(records) < 10:
            return 0.0
        
        confidences = [r.confidence_score for r in records]
        accuracies = [1.0 - min(r.error_minutes / 10, 1.0) for r in records]
        
        # Simple correlation calculation
        n = len(records)
        sum_confidence = sum(confidences)
        sum_accuracy = sum(accuracies)
        sum_confidence_sq = sum(c * c for c in confidences)
        sum_accuracy_sq = sum(a * a for a in accuracies)
        sum_products = sum(c * a for c, a in zip(confidences, accuracies))
        
        numerator = n * sum_products - sum_confidence * sum_accuracy
        denominator = ((n * sum_confidence_sq - sum_confidence ** 2) * 
                      (n * sum_accuracy_sq - sum_accuracy ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def analyze_delay_patterns(self, route_id: Optional[str] = None, 
                             time_period: int = 7) -> Dict[str, Any]:
        """Analyze delay patterns and causes"""
        cutoff_time = datetime.now() - timedelta(days=time_period)
        
        all_delays = []
        if route_id:
            all_delays = [d for d in self.delay_records.get(route_id, []) 
                         if d.scheduled_time >= cutoff_time]
        else:
            for records in self.delay_records.values():
                all_delays.extend([d for d in records if d.scheduled_time >= cutoff_time])
        
        if not all_delays:
            return {"error": "No delay data available for the specified period"}
        
        # Delay statistics
        delays = [d.delay_minutes for d in all_delays]
        
        # Delay causes analysis
        cause_analysis = {}
        for delay in all_delays:
            cause = delay.delay_reason
            if cause not in cause_analysis:
                cause_analysis[cause] = []
            cause_analysis[cause].append(delay.delay_minutes)
        
        # Calculate statistics for each cause
        cause_stats = {}
        for cause, delay_list in cause_analysis.items():
            cause_stats[cause] = {
                "count": len(delay_list),
                "average_delay": statistics.mean(delay_list),
                "max_delay": max(delay_list),
                "total_passenger_impact": sum(d.passenger_impact for d in all_delays if d.delay_reason == cause)
            }
        
        # Time-based patterns
        hour_delays = {}
        day_delays = {}
        
        for delay in all_delays:
            hour = delay.scheduled_time.hour
            day = delay.scheduled_time.weekday()
            
            if hour not in hour_delays:
                hour_delays[hour] = []
            if day not in day_delays:
                day_delays[day] = []
            
            hour_delays[hour].append(delay.delay_minutes)
            day_delays[day].append(delay.delay_minutes)
        
        # Calculate averages for time patterns
        hour_pattern = {h: statistics.mean(dlist) for h, dlist in hour_delays.items()}
        day_pattern = {d: statistics.mean(dlist) for d, dlist in day_delays.items()}
        
        # Recovery analysis
        recovery_times = []
        for delay in all_delays:
            if delay.recovery_time:
                recovery_time = (delay.recovery_time - delay.actual_time).total_seconds() / 60
                recovery_times.append(recovery_time)
        
        return {
            "period_days": time_period,
            "total_delays": len(all_delays),
            "delay_statistics": {
                "average_delay": statistics.mean(delays),
                "median_delay": statistics.median(delays),
                "max_delay": max(delays),
                "total_passenger_impact": sum(d.passenger_impact for d in all_delays)
            },
            "delay_causes": cause_stats,
            "time_patterns": {
                "by_hour": hour_pattern,
                "by_day_of_week": day_pattern
            },
            "recovery_analysis": {
                "average_recovery_time_minutes": statistics.mean(recovery_times) if recovery_times else 0,
                "recovery_rate": len(recovery_times) / len(all_delays) * 100
            },
            "delay_distribution": {
                "minor": len([d for d in delays if d <= 5]) / len(delays) * 100,
                "moderate": len([d for d in delays if 5 < d <= 15]) / len(delays) * 100,
                "major": len([d for d in delays if 15 < d <= 30]) / len(delays) * 100,
                "severe": len([d for d in delays if d > 30]) / len(delays) * 100
            }
        }
    
    def calculate_route_efficiency(self, route_id: Optional[str] = None, 
                                 time_period: int = 30) -> Dict[str, Any]:
        """Calculate route efficiency metrics"""
        cutoff_time = datetime.now() - timedelta(days=time_period)
        
        all_metrics = []
        if route_id:
            all_metrics = [m for m in self.route_efficiency.get(route_id, []) 
                         if m.date >= cutoff_time]
        else:
            for metrics in self.route_efficiency.values():
                all_metrics.extend([m for m in metrics if m.date >= cutoff_time])
        
        if not all_metrics:
            return {"error": "No efficiency data available for the specified period"}
        
        # Aggregate metrics
        total_trips = sum(m.total_trips for m in all_metrics)
        on_time_trips = sum(m.on_time_trips for m in all_metrics)
        total_distance = sum(m.total_distance for m in all_metrics)
        total_time = sum(m.total_time for m in all_metrics)
        total_fuel = sum(m.fuel_consumed for m in all_metrics)
        total_passengers = sum(m.passengers_carried for m in all_metrics)
        total_revenue = sum(m.revenue_generated for m in all_metrics)
        total_cost = sum(m.cost_incurred for m in all_metrics)
        
        # Calculate averages
        on_time_rate = (on_time_trips / total_trips) * 100 if total_trips > 0 else 0
        average_speed = (total_distance / total_time) if total_time > 0 else 0
        fuel_efficiency = (total_distance / total_fuel) if total_fuel > 0 else 0  # km/l
        passenger_per_km = (total_passengers / total_distance) if total_distance > 0 else 0
        profit_margin = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
        
        # By route comparison
        route_comparison = {}
        for rid in set(m.route_id for m in all_metrics):
            route_data = [m for m in all_metrics if m.route_id == rid]
            route_trips = sum(m.total_trips for m in route_data)
            route_on_time = sum(m.on_time_trips for m in route_data)
            route_distance = sum(m.total_distance for m in route_data)
            route_fuel = sum(m.fuel_consumed for m in route_data)
            
            route_comparison[rid] = {
                "on_time_rate": (route_on_time / route_trips) * 100 if route_trips > 0 else 0,
                "average_speed": (route_distance / sum(m.total_time for m in route_data)) if sum(m.total_time for m in route_data) > 0 else 0,
                "fuel_efficiency": (route_distance / route_fuel) if route_fuel > 0 else 0,
                "total_trips": route_trips
            }
        
        return {
            "period_days": time_period,
            "overall_metrics": {
                "total_trips": total_trips,
                "on_time_performance_percentage": on_time_rate,
                "average_speed_kmh": average_speed,
                "fuel_efficiency_kmpl": fuel_efficiency,
                "passengers_per_km": passenger_per_km,
                "profit_margin_percentage": profit_margin,
                "total_distance_km": total_distance,
                "total_fuel_consumed_liters": total_fuel,
                "total_passengers": total_passengers,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "net_profit": total_revenue - total_cost
            },
            "route_comparison": route_comparison,
            "efficiency_trends": self._calculate_efficiency_trends(all_metrics)
        }
    
    def _calculate_efficiency_trends(self, metrics: List[RouteEfficiencyMetrics]) -> Dict[str, str]:
        """Calculate efficiency trends over time"""
        if len(metrics) < 7:
            return {"insufficient_data": "Need at least 7 days of data for trend analysis"}
        
        # Sort by date
        sorted_metrics = sorted(metrics, key=lambda m: m.date)
        
        # Split into two halves
        mid_point = len(sorted_metrics) // 2
        early_period = sorted_metrics[:mid_point]
        recent_period = sorted_metrics[mid_point:]
        
        # Calculate averages for each period
        early_on_time = sum(m.on_time_trips for m in early_period) / sum(m.total_trips for m in early_period) * 100
        recent_on_time = sum(m.on_time_trips for m in recent_period) / sum(m.total_trips for m in recent_period) * 100
        
        early_speed = sum(m.total_distance for m in early_period) / sum(m.total_time for m in early_period)
        recent_speed = sum(m.total_distance for m in recent_period) / sum(m.total_time for m in recent_period)
        
        early_efficiency = sum(m.total_distance for m in early_period) / sum(m.fuel_consumed for m in early_period)
        recent_efficiency = sum(m.total_distance for m in recent_period) / sum(m.fuel_consumed for m in recent_period)
        
        # Determine trends
        trends = {}
        
        if recent_on_time > early_on_time + 2:
            trends["on_time_performance"] = "improving"
        elif recent_on_time < early_on_time - 2:
            trends["on_time_performance"] = "declining"
        else:
            trends["on_time_performance"] = "stable"
        
        if recent_speed > early_speed + 1:
            trends["average_speed"] = "improving"
        elif recent_speed < early_speed - 1:
            trends["average_speed"] = "declining"
        else:
            trends["average_speed"] = "stable"
        
        if recent_efficiency > early_efficiency + 0.5:
            trends["fuel_efficiency"] = "improving"
        elif recent_efficiency < early_efficiency - 0.5:
            trends["fuel_efficiency"] = "declining"
        else:
            trends["fuel_efficiency"] = "stable"
        
        return trends
    
    def generate_performance_report(self, report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        current_time = datetime.now()
        
        if report_type == "comprehensive":
            eta_analysis = self.calculate_eta_accuracy(time_period=7)
            delay_analysis = self.analyze_delay_patterns(time_period=7)
            efficiency_analysis = self.calculate_route_efficiency(time_period=30)
            
            # System health score
            health_score = self._calculate_system_health_score(eta_analysis, delay_analysis, efficiency_analysis)
            
            return {
                "report_type": "comprehensive",
                "generated_at": current_time.isoformat(),
                "system_health_score": health_score,
                "eta_accuracy": eta_analysis,
                "delay_patterns": delay_analysis,
                "route_efficiency": efficiency_analysis,
                "recommendations": self._generate_performance_recommendations(eta_analysis, delay_analysis, efficiency_analysis)
            }
        
        elif report_type == "executive_summary":
            # High-level summary for executives
            eta_analysis = self.calculate_eta_accuracy(time_period=7)
            efficiency_analysis = self.calculate_route_efficiency(time_period=30)
            
            return {
                "report_type": "executive_summary",
                "generated_at": current_time.isoformat(),
                "key_metrics": {
                    "eta_accuracy_percentage": eta_analysis.get("within_threshold_percentage", 0),
                    "on_time_performance_percentage": efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0),
                    "average_speed_kmh": efficiency_analysis.get("overall_metrics", {}).get("average_speed_kmh", 0),
                    "fuel_efficiency_kmpl": efficiency_analysis.get("overall_metrics", {}).get("fuel_efficiency_kmpl", 0),
                    "profit_margin_percentage": efficiency_analysis.get("overall_metrics", {}).get("profit_margin_percentage", 0)
                },
                "top_issues": self._identify_top_performance_issues(),
                "quick_recommendations": self._generate_quick_recommendations()
            }
        
        else:
            return {"error": f"Unknown report type: {report_type}"}
    
    def _calculate_system_health_score(self, eta_analysis: Dict, delay_analysis: Dict, 
                                     efficiency_analysis: Dict) -> Dict[str, Any]:
        """Calculate overall system health score"""
        score_components = {}
        
        # ETA accuracy component (30% weight)
        eta_score = eta_analysis.get("within_threshold_percentage", 0) / 100
        score_components["eta_accuracy"] = eta_score * 30
        
        # Delay component (25% weight)
        avg_delay = delay_analysis.get("delay_statistics", {}).get("average_delay", 10)
        delay_score = max(0, 1 - (avg_delay / 20))  # Normalize 0-20 minute delays to 0-1
        score_components["delay_performance"] = delay_score * 25
        
        # On-time performance component (25% weight)
        on_time_score = efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0) / 100
        score_components["on_time_performance"] = on_time_score * 25
        
        # Efficiency component (20% weight)
        speed_score = min(1, efficiency_analysis.get("overall_metrics", {}).get("average_speed_kmh", 30) / 40)
        fuel_score = min(1, efficiency_analysis.get("overall_metrics", {}).get("fuel_efficiency_kmpl", 5) / 8)
        efficiency_score = (speed_score + fuel_score) / 2
        score_components["operational_efficiency"] = efficiency_score * 20
        
        # Calculate total score
        total_score = sum(score_components.values())
        
        # Determine health status
        if total_score >= 85:
            health_status = "excellent"
        elif total_score >= 70:
            health_status = "good"
        elif total_score >= 55:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            "overall_score": round(total_score, 1),
            "health_status": health_status,
            "score_breakdown": score_components,
            "grade": self._get_performance_grade(total_score)
        }
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _identify_top_performance_issues(self) -> List[Dict[str, Any]]:
        """Identify top performance issues"""
        issues = []
        
        eta_analysis = self.calculate_eta_accuracy(time_period=7)
        delay_analysis = self.analyze_delay_patterns(time_period=7)
        efficiency_analysis = self.calculate_route_efficiency(time_period=30)
        
        # Check ETA accuracy
        eta_accuracy = eta_analysis.get("within_threshold_percentage", 0)
        if eta_accuracy < 75:
            issues.append({
                "type": "eta_accuracy",
                "severity": "high" if eta_accuracy < 60 else "medium",
                "description": f"ETA accuracy is only {eta_accuracy:.1f}%",
                "impact": "Passenger dissatisfaction and planning issues"
            })
        
        # Check delays
        avg_delay = delay_analysis.get("delay_statistics", {}).get("average_delay", 0)
        if avg_delay > 8:
            issues.append({
                "type": "excessive_delays",
                "severity": "high" if avg_delay > 12 else "medium",
                "description": f"Average delay is {avg_delay:.1f} minutes",
                "impact": "Service reliability and passenger experience"
            })
        
        # Check on-time performance
        on_time_rate = efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0)
        if on_time_rate < 80:
            issues.append({
                "type": "on_time_performance",
                "severity": "high" if on_time_rate < 70 else "medium",
                "description": f"On-time performance is only {on_time_rate:.1f}%",
                "impact": "Service quality and operational efficiency"
            })
        
        # Check fuel efficiency
        fuel_efficiency = efficiency_analysis.get("overall_metrics", {}).get("fuel_efficiency_kmpl", 0)
        if fuel_efficiency < 4:
            issues.append({
                "type": "fuel_efficiency",
                "severity": "medium",
                "description": f"Fuel efficiency is only {fuel_efficiency:.2f} km/l",
                "impact": "Increased operating costs and environmental impact"
            })
        
        return issues
    
    def _generate_performance_recommendations(self, eta_analysis: Dict, delay_analysis: Dict, 
                                            efficiency_analysis: Dict) -> List[str]:
        """Generate detailed performance recommendations"""
        recommendations = []
        
        # ETA recommendations
        eta_accuracy = eta_analysis.get("within_threshold_percentage", 0)
        if eta_accuracy < 80:
            recommendations.append("Improve ETA prediction algorithms with real-time traffic data integration")
            recommendations.append("Implement machine learning models for better traffic pattern recognition")
        
        # Delay recommendations
        avg_delay = delay_analysis.get("delay_statistics", {}).get("average_delay", 0)
        if avg_delay > 5:
            recommendations.append("Implement proactive delay mitigation strategies")
            recommendations.append("Enhance communication systems for real-time delay notifications")
        
        # Efficiency recommendations
        on_time_rate = efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0)
        if on_time_rate < 85:
            recommendations.append("Optimize scheduling and resource allocation")
            recommendations.append("Review and adjust route timings based on current conditions")
        
        # General recommendations
        recommendations.append("Continue monitoring performance metrics and trends")
        recommendations.append("Implement regular performance review meetings with operational staff")
        
        return recommendations
    
    def _generate_quick_recommendations(self) -> List[str]:
        """Generate quick recommendations for executive summary"""
        return [
            "Focus on improving ETA accuracy for better passenger experience",
            "Address major delay causes through targeted interventions",
            "Optimize route scheduling to improve on-time performance",
            "Monitor fuel efficiency trends for cost optimization"
        ]
    
    def get_performance_trends(self, metric: PerformanceMetric, entity_id: str, 
                             time_period: int = 30) -> Optional[PerformanceTrend]:
        """Get performance trends for a specific metric and entity"""
        # This would analyze historical data to identify trends
        # For now, return a sample trend
        trend_key = f"{metric.value}_{entity_id}"
        
        if trend_key in self.performance_trends:
            return self.performance_trends[trend_key][-1]  # Return most recent trend
        
        # Generate sample trend
        direction = random.choice(list(TrendDirection))
        change_percentage = random.uniform(-15, 15)
        
        trend = PerformanceTrend(
            metric=metric,
            entity_id=entity_id,
            direction=direction,
            change_percentage=change_percentage,
            confidence=random.uniform(0.6, 0.95),
            time_period=f"{time_period}days",
            data_points=[],  # Would be populated with actual data points
            analysis_notes=f"Sample trend analysis for {metric.value}"
        )
        
        return trend
=======
"""
performance_analytics.py
=======================
NEW FILE - Comprehensive Performance Analytics Dashboard
Provides detailed performance analytics, ETA accuracy, delay patterns, and route efficiency

Features:
- ETA accuracy tracking
- Delay pattern analysis
- Route efficiency metrics
- Performance trend analysis
- Comparative analytics
- Predictive insights
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json
import random

class PerformanceMetric(Enum):
    ETA_ACCURACY = "eta_accuracy"
    ON_TIME_PERFORMANCE = "on_time_performance"
    ROUTE_EFFICIENCY = "route_efficiency"
    FUEL_EFFICIENCY = "fuel_efficiency"
    PASSENGER_SATISFACTION = "passenger_satisfaction"
    SERVICE_RELIABILITY = "service_reliability"

class TrendDirection(Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class ETAAccuracyRecord:
    """Record of ETA prediction accuracy"""
    record_id: str
    bus_id: str
    route_id: str
    stop_id: str
    predicted_eta: datetime
    actual_arrival: datetime
    prediction_made_time: datetime
    error_minutes: float
    context: Dict[str, Any]  # Traffic, weather, etc.
    confidence_score: float

@dataclass
class DelayRecord:
    """Record of service delays"""
    delay_id: str
    bus_id: str
    route_id: str
    scheduled_time: datetime
    actual_time: datetime
    delay_minutes: float
    delay_reason: str
    affected_stops: List[str]
    passenger_impact: int
    recovery_time: Optional[datetime] = None

@dataclass
class RouteEfficiencyMetrics:
    """Efficiency metrics for a specific route"""
    route_id: str
    date: datetime
    total_trips: int
    on_time_trips: int
    average_delay: float
    total_distance: float  # km
    total_time: float  # hours
    average_speed: float  # km/h
    fuel_consumed: float  # liters
    passengers_carried: int
    revenue_generated: float
    cost_incurred: float

@dataclass
class PerformanceTrend:
    """Performance trend over time"""
    metric: PerformanceMetric
    entity_id: str  # bus_id, route_id, or system
    direction: TrendDirection
    change_percentage: float
    confidence: float
    time_period: str  # "daily", "weekly", "monthly"
    data_points: List[Tuple[datetime, float]]
    analysis_notes: str = ""

class PerformanceAnalyticsManager:
    """Comprehensive performance analytics system"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.eta_records: Dict[str, List[ETAAccuracyRecord]] = {}  # route_id -> records
        self.delay_records: Dict[str, List[DelayRecord]] = {}  # route_id -> records
        self.route_efficiency: Dict[str, List[RouteEfficiencyMetrics]] = {}  # route_id -> metrics
        self.performance_trends: Dict[str, List[PerformanceTrend]] = {}
        
        # Configuration
        self.eta_accuracy_threshold = 5.0  # minutes
        self.significant_delay_threshold = 10.0  # minutes
        self.trend_analysis_window = timedelta(days=30)
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Create sample performance data for demonstration"""
        routes = ["FR-01", "FR-02", "FR-03A", "FR-04", "FR-05"]
        buses = ["BUS-01", "BUS-02", "BUS-03", "BUS-04", "BUS-05"]
        
        # Generate ETA accuracy records
        for route_id in routes:
            eta_records = []
            
            # Generate records for the last 7 days
            for days_ago in range(7):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 10-20 records per day
                for record_num in range(random.randint(10, 20)):
                    record_time = date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    # Simulate ETA prediction with varying accuracy
                    base_error = random.gauss(0, 3)  # Normal distribution around 0
                    context_factor = random.uniform(0.5, 1.5)  # Context affects accuracy
                    error_minutes = base_error * context_factor
                    
                    record = ETAAccuracyRecord(
                        record_id=f"ETA-{route_id}-{int(record_time.timestamp())}",
                        bus_id=random.choice(buses),
                        route_id=route_id,
                        stop_id=f"STOP-{random.randint(1, 20)}",
                        predicted_eta=record_time + timedelta(minutes=random.randint(5, 45)),
                        actual_arrival=record_time + timedelta(minutes=random.randint(5, 45)) + timedelta(minutes=error_minutes),
                        prediction_made_time=record_time - timedelta(minutes=random.randint(15, 30)),
                        error_minutes=abs(error_minutes),
                        context={
                            "traffic_level": random.uniform(0.1, 1.0),
                            "weather": random.choice(["clear", "rain", "fog"]),
                            "day_of_week": record_time.weekday(),
                            "hour": record_time.hour
                        },
                        confidence_score=max(0.3, 1.0 - abs(error_minutes) / 10)
                    )
                    eta_records.append(record)
            
            self.eta_records[route_id] = eta_records
        
        # Generate delay records
        for route_id in routes:
            delay_records = []
            
            for days_ago in range(7):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 2-8 delay records per day
                for delay_num in range(random.randint(2, 8)):
                    delay_time = date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    delay_minutes = random.expovariate(1/5)  # Exponential distribution for delays
                    if delay_minutes < 2:  # Minimum significant delay
                        continue
                    
                    delay_reason = random.choice([
                        "heavy_traffic", "weather", "mechanical_issue", 
                        "passenger_incident", "road_closure", "signal_failure"
                    ])
                    
                    record = DelayRecord(
                        delay_id=f"DELAY-{route_id}-{int(delay_time.timestamp())}",
                        bus_id=random.choice(buses),
                        route_id=route_id,
                        scheduled_time=delay_time,
                        actual_time=delay_time + timedelta(minutes=delay_minutes),
                        delay_minutes=delay_minutes,
                        delay_reason=delay_reason,
                        affected_stops=[f"STOP-{i}" for i in range(random.randint(1, 5))],
                        passenger_impact=random.randint(10, 100),
                        recovery_time=delay_time + timedelta(minutes=delay_minutes + random.uniform(5, 30))
                    )
                    delay_records.append(record)
            
            self.delay_records[route_id] = delay_records
        
        # Generate route efficiency metrics
        for route_id in routes:
            efficiency_metrics = []
            
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Simulate daily efficiency metrics
                total_trips = random.randint(20, 50)
                on_time_trips = int(total_trips * random.uniform(0.7, 0.95))
                average_delay = random.expovariate(1/3)  # Average delay in minutes
                
                metrics = RouteEfficiencyMetrics(
                    route_id=route_id,
                    date=date,
                    total_trips=total_trips,
                    on_time_trips=on_time_trips,
                    average_delay=average_delay,
                    total_distance=random.uniform(200, 800),  # km
                    total_time=random.uniform(8, 16),  # hours
                    average_speed=random.uniform(25, 45),  # km/h
                    fuel_consumed=random.uniform(100, 400),  # liters
                    passengers_carried=random.randint(500, 2000),
                    revenue_generated=random.uniform(1000, 5000),
                    cost_incurred=random.uniform(800, 3000)
                )
                efficiency_metrics.append(metrics)
            
            self.route_efficiency[route_id] = efficiency_metrics
    
    def calculate_eta_accuracy(self, route_id: Optional[str] = None, 
                             time_period: int = 7) -> Dict[str, Any]:
        """Calculate ETA accuracy metrics"""
        cutoff_time = datetime.now() - timedelta(days=time_period)
        
        all_records = []
        if route_id:
            all_records = [r for r in self.eta_records.get(route_id, []) 
                         if r.actual_arrival >= cutoff_time]
        else:
            for records in self.eta_records.values():
                all_records.extend([r for r in records if r.actual_arrival >= cutoff_time])
        
        if not all_records:
            return {"error": "No ETA data available for the specified period"}
        
        # Calculate accuracy metrics
        errors = [r.error_minutes for r in all_records]
        within_threshold = len([e for e in errors if e <= self.eta_accuracy_threshold])
        
        # By context factors
        traffic_accuracy = {}
        weather_accuracy = {}
        hour_accuracy = {}
        
        for record in all_records:
            traffic = record.context.get("traffic_level", 0.5)
            weather = record.context.get("weather", "clear")
            hour = record.context.get("hour", 12)
            
            if traffic not in traffic_accuracy:
                traffic_accuracy[traffic] = []
            if weather not in weather_accuracy:
                weather_accuracy[weather] = []
            if hour not in hour_accuracy:
                hour_accuracy[hour] = []
            
            traffic_accuracy[traffic].append(record.error_minutes)
            weather_accuracy[weather].append(record.error_minutes)
            hour_accuracy[hour].append(record.error_minutes)
        
        # Calculate averages by context
        for key in list(traffic_accuracy.keys()):
            traffic_accuracy[key] = statistics.mean(traffic_accuracy[key])
        
        for key in list(weather_accuracy.keys()):
            weather_accuracy[key] = statistics.mean(weather_accuracy[key])
        
        for key in list(hour_accuracy.keys()):
            hour_accuracy[key] = statistics.mean(hour_accuracy[key])
        
        return {
            "period_days": time_period,
            "total_predictions": len(all_records),
            "average_error_minutes": statistics.mean(errors),
            "median_error_minutes": statistics.median(errors),
            "within_threshold_percentage": (within_threshold / len(all_records)) * 100,
            "accuracy_distribution": {
                "excellent": len([e for e in errors if e <= 2]) / len(all_records) * 100,
                "good": len([e for e in errors if 2 < e <= 5]) / len(all_records) * 100,
                "fair": len([e for e in errors if 5 < e <= 10]) / len(all_records) * 100,
                "poor": len([e for e in errors if e > 10]) / len(all_errors) * 100
            },
            "accuracy_by_context": {
                "traffic_level": traffic_accuracy,
                "weather": weather_accuracy,
                "hour_of_day": hour_accuracy
            },
            "confidence_correlation": self._calculate_confidence_correlation(all_records)
        }
    
    def _calculate_confidence_correlation(self, records: List[ETAAccuracyRecord]) -> float:
        """Calculate correlation between confidence scores and actual accuracy"""
        if len(records) < 10:
            return 0.0
        
        confidences = [r.confidence_score for r in records]
        accuracies = [1.0 - min(r.error_minutes / 10, 1.0) for r in records]
        
        # Simple correlation calculation
        n = len(records)
        sum_confidence = sum(confidences)
        sum_accuracy = sum(accuracies)
        sum_confidence_sq = sum(c * c for c in confidences)
        sum_accuracy_sq = sum(a * a for a in accuracies)
        sum_products = sum(c * a for c, a in zip(confidences, accuracies))
        
        numerator = n * sum_products - sum_confidence * sum_accuracy
        denominator = ((n * sum_confidence_sq - sum_confidence ** 2) * 
                      (n * sum_accuracy_sq - sum_accuracy ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def analyze_delay_patterns(self, route_id: Optional[str] = None, 
                             time_period: int = 7) -> Dict[str, Any]:
        """Analyze delay patterns and causes"""
        cutoff_time = datetime.now() - timedelta(days=time_period)
        
        all_delays = []
        if route_id:
            all_delays = [d for d in self.delay_records.get(route_id, []) 
                         if d.scheduled_time >= cutoff_time]
        else:
            for records in self.delay_records.values():
                all_delays.extend([d for d in records if d.scheduled_time >= cutoff_time])
        
        if not all_delays:
            return {"error": "No delay data available for the specified period"}
        
        # Delay statistics
        delays = [d.delay_minutes for d in all_delays]
        
        # Delay causes analysis
        cause_analysis = {}
        for delay in all_delays:
            cause = delay.delay_reason
            if cause not in cause_analysis:
                cause_analysis[cause] = []
            cause_analysis[cause].append(delay.delay_minutes)
        
        # Calculate statistics for each cause
        cause_stats = {}
        for cause, delay_list in cause_analysis.items():
            cause_stats[cause] = {
                "count": len(delay_list),
                "average_delay": statistics.mean(delay_list),
                "max_delay": max(delay_list),
                "total_passenger_impact": sum(d.passenger_impact for d in all_delays if d.delay_reason == cause)
            }
        
        # Time-based patterns
        hour_delays = {}
        day_delays = {}
        
        for delay in all_delays:
            hour = delay.scheduled_time.hour
            day = delay.scheduled_time.weekday()
            
            if hour not in hour_delays:
                hour_delays[hour] = []
            if day not in day_delays:
                day_delays[day] = []
            
            hour_delays[hour].append(delay.delay_minutes)
            day_delays[day].append(delay.delay_minutes)
        
        # Calculate averages for time patterns
        hour_pattern = {h: statistics.mean(dlist) for h, dlist in hour_delays.items()}
        day_pattern = {d: statistics.mean(dlist) for d, dlist in day_delays.items()}
        
        # Recovery analysis
        recovery_times = []
        for delay in all_delays:
            if delay.recovery_time:
                recovery_time = (delay.recovery_time - delay.actual_time).total_seconds() / 60
                recovery_times.append(recovery_time)
        
        return {
            "period_days": time_period,
            "total_delays": len(all_delays),
            "delay_statistics": {
                "average_delay": statistics.mean(delays),
                "median_delay": statistics.median(delays),
                "max_delay": max(delays),
                "total_passenger_impact": sum(d.passenger_impact for d in all_delays)
            },
            "delay_causes": cause_stats,
            "time_patterns": {
                "by_hour": hour_pattern,
                "by_day_of_week": day_pattern
            },
            "recovery_analysis": {
                "average_recovery_time_minutes": statistics.mean(recovery_times) if recovery_times else 0,
                "recovery_rate": len(recovery_times) / len(all_delays) * 100
            },
            "delay_distribution": {
                "minor": len([d for d in delays if d <= 5]) / len(delays) * 100,
                "moderate": len([d for d in delays if 5 < d <= 15]) / len(delays) * 100,
                "major": len([d for d in delays if 15 < d <= 30]) / len(delays) * 100,
                "severe": len([d for d in delays if d > 30]) / len(delays) * 100
            }
        }
    
    def calculate_route_efficiency(self, route_id: Optional[str] = None, 
                                 time_period: int = 30) -> Dict[str, Any]:
        """Calculate route efficiency metrics"""
        cutoff_time = datetime.now() - timedelta(days=time_period)
        
        all_metrics = []
        if route_id:
            all_metrics = [m for m in self.route_efficiency.get(route_id, []) 
                         if m.date >= cutoff_time]
        else:
            for metrics in self.route_efficiency.values():
                all_metrics.extend([m for m in metrics if m.date >= cutoff_time])
        
        if not all_metrics:
            return {"error": "No efficiency data available for the specified period"}
        
        # Aggregate metrics
        total_trips = sum(m.total_trips for m in all_metrics)
        on_time_trips = sum(m.on_time_trips for m in all_metrics)
        total_distance = sum(m.total_distance for m in all_metrics)
        total_time = sum(m.total_time for m in all_metrics)
        total_fuel = sum(m.fuel_consumed for m in all_metrics)
        total_passengers = sum(m.passengers_carried for m in all_metrics)
        total_revenue = sum(m.revenue_generated for m in all_metrics)
        total_cost = sum(m.cost_incurred for m in all_metrics)
        
        # Calculate averages
        on_time_rate = (on_time_trips / total_trips) * 100 if total_trips > 0 else 0
        average_speed = (total_distance / total_time) if total_time > 0 else 0
        fuel_efficiency = (total_distance / total_fuel) if total_fuel > 0 else 0  # km/l
        passenger_per_km = (total_passengers / total_distance) if total_distance > 0 else 0
        profit_margin = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
        
        # By route comparison
        route_comparison = {}
        for rid in set(m.route_id for m in all_metrics):
            route_data = [m for m in all_metrics if m.route_id == rid]
            route_trips = sum(m.total_trips for m in route_data)
            route_on_time = sum(m.on_time_trips for m in route_data)
            route_distance = sum(m.total_distance for m in route_data)
            route_fuel = sum(m.fuel_consumed for m in route_data)
            
            route_comparison[rid] = {
                "on_time_rate": (route_on_time / route_trips) * 100 if route_trips > 0 else 0,
                "average_speed": (route_distance / sum(m.total_time for m in route_data)) if sum(m.total_time for m in route_data) > 0 else 0,
                "fuel_efficiency": (route_distance / route_fuel) if route_fuel > 0 else 0,
                "total_trips": route_trips
            }
        
        return {
            "period_days": time_period,
            "overall_metrics": {
                "total_trips": total_trips,
                "on_time_performance_percentage": on_time_rate,
                "average_speed_kmh": average_speed,
                "fuel_efficiency_kmpl": fuel_efficiency,
                "passengers_per_km": passenger_per_km,
                "profit_margin_percentage": profit_margin,
                "total_distance_km": total_distance,
                "total_fuel_consumed_liters": total_fuel,
                "total_passengers": total_passengers,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "net_profit": total_revenue - total_cost
            },
            "route_comparison": route_comparison,
            "efficiency_trends": self._calculate_efficiency_trends(all_metrics)
        }
    
    def _calculate_efficiency_trends(self, metrics: List[RouteEfficiencyMetrics]) -> Dict[str, str]:
        """Calculate efficiency trends over time"""
        if len(metrics) < 7:
            return {"insufficient_data": "Need at least 7 days of data for trend analysis"}
        
        # Sort by date
        sorted_metrics = sorted(metrics, key=lambda m: m.date)
        
        # Split into two halves
        mid_point = len(sorted_metrics) // 2
        early_period = sorted_metrics[:mid_point]
        recent_period = sorted_metrics[mid_point:]
        
        # Calculate averages for each period
        early_on_time = sum(m.on_time_trips for m in early_period) / sum(m.total_trips for m in early_period) * 100
        recent_on_time = sum(m.on_time_trips for m in recent_period) / sum(m.total_trips for m in recent_period) * 100
        
        early_speed = sum(m.total_distance for m in early_period) / sum(m.total_time for m in early_period)
        recent_speed = sum(m.total_distance for m in recent_period) / sum(m.total_time for m in recent_period)
        
        early_efficiency = sum(m.total_distance for m in early_period) / sum(m.fuel_consumed for m in early_period)
        recent_efficiency = sum(m.total_distance for m in recent_period) / sum(m.fuel_consumed for m in recent_period)
        
        # Determine trends
        trends = {}
        
        if recent_on_time > early_on_time + 2:
            trends["on_time_performance"] = "improving"
        elif recent_on_time < early_on_time - 2:
            trends["on_time_performance"] = "declining"
        else:
            trends["on_time_performance"] = "stable"
        
        if recent_speed > early_speed + 1:
            trends["average_speed"] = "improving"
        elif recent_speed < early_speed - 1:
            trends["average_speed"] = "declining"
        else:
            trends["average_speed"] = "stable"
        
        if recent_efficiency > early_efficiency + 0.5:
            trends["fuel_efficiency"] = "improving"
        elif recent_efficiency < early_efficiency - 0.5:
            trends["fuel_efficiency"] = "declining"
        else:
            trends["fuel_efficiency"] = "stable"
        
        return trends
    
    def generate_performance_report(self, report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        current_time = datetime.now()
        
        if report_type == "comprehensive":
            eta_analysis = self.calculate_eta_accuracy(time_period=7)
            delay_analysis = self.analyze_delay_patterns(time_period=7)
            efficiency_analysis = self.calculate_route_efficiency(time_period=30)
            
            # System health score
            health_score = self._calculate_system_health_score(eta_analysis, delay_analysis, efficiency_analysis)
            
            return {
                "report_type": "comprehensive",
                "generated_at": current_time.isoformat(),
                "system_health_score": health_score,
                "eta_accuracy": eta_analysis,
                "delay_patterns": delay_analysis,
                "route_efficiency": efficiency_analysis,
                "recommendations": self._generate_performance_recommendations(eta_analysis, delay_analysis, efficiency_analysis)
            }
        
        elif report_type == "executive_summary":
            # High-level summary for executives
            eta_analysis = self.calculate_eta_accuracy(time_period=7)
            efficiency_analysis = self.calculate_route_efficiency(time_period=30)
            
            return {
                "report_type": "executive_summary",
                "generated_at": current_time.isoformat(),
                "key_metrics": {
                    "eta_accuracy_percentage": eta_analysis.get("within_threshold_percentage", 0),
                    "on_time_performance_percentage": efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0),
                    "average_speed_kmh": efficiency_analysis.get("overall_metrics", {}).get("average_speed_kmh", 0),
                    "fuel_efficiency_kmpl": efficiency_analysis.get("overall_metrics", {}).get("fuel_efficiency_kmpl", 0),
                    "profit_margin_percentage": efficiency_analysis.get("overall_metrics", {}).get("profit_margin_percentage", 0)
                },
                "top_issues": self._identify_top_performance_issues(),
                "quick_recommendations": self._generate_quick_recommendations()
            }
        
        else:
            return {"error": f"Unknown report type: {report_type}"}
    
    def _calculate_system_health_score(self, eta_analysis: Dict, delay_analysis: Dict, 
                                     efficiency_analysis: Dict) -> Dict[str, Any]:
        """Calculate overall system health score"""
        score_components = {}
        
        # ETA accuracy component (30% weight)
        eta_score = eta_analysis.get("within_threshold_percentage", 0) / 100
        score_components["eta_accuracy"] = eta_score * 30
        
        # Delay component (25% weight)
        avg_delay = delay_analysis.get("delay_statistics", {}).get("average_delay", 10)
        delay_score = max(0, 1 - (avg_delay / 20))  # Normalize 0-20 minute delays to 0-1
        score_components["delay_performance"] = delay_score * 25
        
        # On-time performance component (25% weight)
        on_time_score = efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0) / 100
        score_components["on_time_performance"] = on_time_score * 25
        
        # Efficiency component (20% weight)
        speed_score = min(1, efficiency_analysis.get("overall_metrics", {}).get("average_speed_kmh", 30) / 40)
        fuel_score = min(1, efficiency_analysis.get("overall_metrics", {}).get("fuel_efficiency_kmpl", 5) / 8)
        efficiency_score = (speed_score + fuel_score) / 2
        score_components["operational_efficiency"] = efficiency_score * 20
        
        # Calculate total score
        total_score = sum(score_components.values())
        
        # Determine health status
        if total_score >= 85:
            health_status = "excellent"
        elif total_score >= 70:
            health_status = "good"
        elif total_score >= 55:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            "overall_score": round(total_score, 1),
            "health_status": health_status,
            "score_breakdown": score_components,
            "grade": self._get_performance_grade(total_score)
        }
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _identify_top_performance_issues(self) -> List[Dict[str, Any]]:
        """Identify top performance issues"""
        issues = []
        
        eta_analysis = self.calculate_eta_accuracy(time_period=7)
        delay_analysis = self.analyze_delay_patterns(time_period=7)
        efficiency_analysis = self.calculate_route_efficiency(time_period=30)
        
        # Check ETA accuracy
        eta_accuracy = eta_analysis.get("within_threshold_percentage", 0)
        if eta_accuracy < 75:
            issues.append({
                "type": "eta_accuracy",
                "severity": "high" if eta_accuracy < 60 else "medium",
                "description": f"ETA accuracy is only {eta_accuracy:.1f}%",
                "impact": "Passenger dissatisfaction and planning issues"
            })
        
        # Check delays
        avg_delay = delay_analysis.get("delay_statistics", {}).get("average_delay", 0)
        if avg_delay > 8:
            issues.append({
                "type": "excessive_delays",
                "severity": "high" if avg_delay > 12 else "medium",
                "description": f"Average delay is {avg_delay:.1f} minutes",
                "impact": "Service reliability and passenger experience"
            })
        
        # Check on-time performance
        on_time_rate = efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0)
        if on_time_rate < 80:
            issues.append({
                "type": "on_time_performance",
                "severity": "high" if on_time_rate < 70 else "medium",
                "description": f"On-time performance is only {on_time_rate:.1f}%",
                "impact": "Service quality and operational efficiency"
            })
        
        # Check fuel efficiency
        fuel_efficiency = efficiency_analysis.get("overall_metrics", {}).get("fuel_efficiency_kmpl", 0)
        if fuel_efficiency < 4:
            issues.append({
                "type": "fuel_efficiency",
                "severity": "medium",
                "description": f"Fuel efficiency is only {fuel_efficiency:.2f} km/l",
                "impact": "Increased operating costs and environmental impact"
            })
        
        return issues
    
    def _generate_performance_recommendations(self, eta_analysis: Dict, delay_analysis: Dict, 
                                            efficiency_analysis: Dict) -> List[str]:
        """Generate detailed performance recommendations"""
        recommendations = []
        
        # ETA recommendations
        eta_accuracy = eta_analysis.get("within_threshold_percentage", 0)
        if eta_accuracy < 80:
            recommendations.append("Improve ETA prediction algorithms with real-time traffic data integration")
            recommendations.append("Implement machine learning models for better traffic pattern recognition")
        
        # Delay recommendations
        avg_delay = delay_analysis.get("delay_statistics", {}).get("average_delay", 0)
        if avg_delay > 5:
            recommendations.append("Implement proactive delay mitigation strategies")
            recommendations.append("Enhance communication systems for real-time delay notifications")
        
        # Efficiency recommendations
        on_time_rate = efficiency_analysis.get("overall_metrics", {}).get("on_time_performance_percentage", 0)
        if on_time_rate < 85:
            recommendations.append("Optimize scheduling and resource allocation")
            recommendations.append("Review and adjust route timings based on current conditions")
        
        # General recommendations
        recommendations.append("Continue monitoring performance metrics and trends")
        recommendations.append("Implement regular performance review meetings with operational staff")
        
        return recommendations
    
    def _generate_quick_recommendations(self) -> List[str]:
        """Generate quick recommendations for executive summary"""
        return [
            "Focus on improving ETA accuracy for better passenger experience",
            "Address major delay causes through targeted interventions",
            "Optimize route scheduling to improve on-time performance",
            "Monitor fuel efficiency trends for cost optimization"
        ]
    
    def get_performance_trends(self, metric: PerformanceMetric, entity_id: str, 
                             time_period: int = 30) -> Optional[PerformanceTrend]:
        """Get performance trends for a specific metric and entity"""
        # This would analyze historical data to identify trends
        # For now, return a sample trend
        trend_key = f"{metric.value}_{entity_id}"
        
        if trend_key in self.performance_trends:
            return self.performance_trends[trend_key][-1]  # Return most recent trend
        
        # Generate sample trend
        direction = random.choice(list(TrendDirection))
        change_percentage = random.uniform(-15, 15)
        
        trend = PerformanceTrend(
            metric=metric,
            entity_id=entity_id,
            direction=direction,
            change_percentage=change_percentage,
            confidence=random.uniform(0.6, 0.95),
            time_period=f"{time_period}days",
            data_points=[],  # Would be populated with actual data points
            analysis_notes=f"Sample trend analysis for {metric.value}"
        )
        
        return trend
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
