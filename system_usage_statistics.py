<<<<<<< HEAD
"""
system_usage_statistics.py
==========================
NEW FILE - System Usage Statistics and Commuter Behavior Insights
Provides comprehensive system usage analytics and commuter behavior patterns

Features:
- System usage metrics
- Commuter behavior analysis
- Peak usage patterns
- Route popularity analysis
- User demographics insights
- Service utilization trends
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json
import random

class UserCategory(Enum):
    REGULAR_COMMUTER = "regular_commuter"
    OCCASIONAL_USER = "occasional_user"
    TOURIST = "tourist"
    STUDENT = "student"
    SENIOR_CITIZEN = "senior_citizen"
    BUSINESS_TRAVELER = "business_traveler"

class TripPurpose(Enum):
    WORK_COMMUTE = "work_commute"
    EDUCATION = "education"
    SHOPPING = "shopping"
    LEISURE = "leisure"
    MEDICAL = "medical"
    SOCIAL = "social"
    OTHER = "other"

@dataclass
class UserActivityRecord:
    """Record of user activity"""
    user_id: str
    activity_type: str  # login, trip_planning, booking, feedback
    timestamp: datetime
    session_duration: Optional[float] = None  # minutes
    device_type: str = "web"  # web, mobile, kiosk
    location: Optional[Tuple[float, float]] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TripRecord:
    """Record of a user trip"""
    trip_id: str
    user_id: str
    route_id: str
    start_stop: str
    end_stop: str
    start_time: datetime
    end_time: datetime
    trip_duration: float  # minutes
    distance: float  # km
    fare_paid: float
    payment_method: str
    user_category: UserCategory
    trip_purpose: TripPurpose
    passengers_count: int = 1
    satisfaction_score: Optional[float] = None

@dataclass
class RouteUsageMetrics:
    """Usage metrics for a specific route"""
    route_id: str
    date: datetime
    total_trips: int
    unique_users: int
    total_revenue: float
    average_occupancy: float  # 0.0 - 1.0
    peak_hour_usage: Dict[int, int]  # hour -> trip count
    user_demographics: Dict[UserCategory, int]
    popular_segments: List[Tuple[str, str, int]]  # (start_stop, end_stop, count)
    average_trip_duration: float
    revenue_per_trip: float

@dataclass
class Comm
    """Commuter behavior pattern"""
    pattern_id: str
    user_id: str
    pattern_type: str  # daily, weekly, seasonal
    consistency_score: float  # 0  # hour -> frequency
    preferred_routes: List[str]
    preferred_times: List[int]  # hours
    trip_frequency: float  # trips per week
    average_trip_distance: float
    loyalty_score: float  # 0.0 - 1.0

class SystemUsageAnalytics:
    """Comprehensive system usage and commuter behavior analytics"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.user_activities: Dict[str, List[UserActivityRecord]] = {}  # user_id -> activities
        self.trip_records: Dict[str, List[TripRecord]] = {}  # route_id -> trips
        self.route_usage_metrics: Dict[str, List[RouteUsageMetrics]] = {}  # route_id -> metrics
        self.commuter_patterns: Dict[str, CommuterPattern]一些 = {}  # user_id -> pattern
        
        # Configuration
        self.analysis_window = timedelta(days=30)
        self.peak_hour_threshold = 100  # trips per hour to consider peak
        self.loyalty_threshold = 10  # trips to be considered loyal
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Create sample usage data for demonstration"""
        routes = ["FR-01", "FR-02", "FR-03A", "FR-04", "FR-05"]
        user_categories = list(UserCategory)
        trip_purposes = list(TripPurpose)
        
        # Generate user activities
        for user_num in range(1000):  # 1000 users
            user_id = f"USER-{user_num:04d}"
            activities = []
            
            # Generate activities for the last 30 days
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 1-5 activities per day
                for activity_num in range(random.randint(1, 5)):
                    activity_time = date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    activity_type = random.choice(["login", "trip_planning", "booking", "feedback"])
                    session_duration = random.uniform(1, 30) if activity_type != "login" else None
                    
                    activity = UserActivityRecord(
                        user_id=user_id,
                        activity_type=activity_type,
                        timestamp=activity_time,
                        session_duration=session_duration,
                        device_type=random.choice(["web", "mobile", "kiosk"]),
                        location=(random.uniform(25.0, 25.5), random.uniform(55.0, 55.5)),
                        context={
                            "browser": random.choice(["chrome", "firefox", "safari"]),
                            "os": random.choice(["windows", "mac", "android", "ios"])
                        }
                    )
                    activities.append(activity)
            
            self.user_activities[user_id] = activities
        
        # Generate trip records
        for route_id in routes:
            trips = []
            
            # Generate trips for the last 30 days
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 50-200 trips per day
                for trip_num in range(random.randint(50, 200)):
                    trip_time = date + timedelta(
                        hours=random.randint(5, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    user_id = f"USER-{random.randint(1, 999):04d}"
                    
                    trip = TripRecord(
                        trip_id=f"TRIP-{route_id}-{int(trip_time.timestamp())}",
                        user_id=user_id,
                        route_id=route_id,
                        start_stop=f"STOP-{random.randint(1, 20)}",
                        end_stop=f"STOP-{random.randint(1, 20)}",
                        start_time=trip_time,
                        end_time=trip_time + timedelta(minutes=random.randint(15, 90)),
                        trip_duration=random.uniform(15, 90),
                        distance=random.uniform(5, 25),
                        fare_paid=random.uniform(2, 15),
                        payment_method=random.choice(["card", "cash", "mobile", "subscription"]),
                        user_category=random.choice(user_categories
                       /linker(1,水里
                        trip_purpose.
                        passengers_count=random.randint(1, 4),
                        satisfaction_score=random.uniform(3.0, 5.0) if random.random() > 0.3 else None
                    )
                    trips.append(trip)
            
            self.trip_records[route_id] = trips
        
        # Generate route usage metrics
        for route_id in routes:
            metrics = []
            
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                route_trips = self.trip_records.get(route_id, [])
                day_trips = [t for t in route_trips if t.start_time.date() == date.date()]
                
                if not day_trips:
                    continue
                
                # Calculate metrics
                total_trips = len(day_trips)
                unique_users = len(set(t.user_id for t in day_trips))
                total_revenue = sum(t.fare_paid for t in day_trips)
                
                # Peak hour usage
                peak_hour_usage = {}
                for trip in day_trips:
                    hour = trip.start_time.hour
                    peak_hour_usage[hour] = peak_hour_usage.get(hour, 0) + 1
                
                # User demographics接收
                user_demographics = {}
                for trip in集中
                    user_demographics[trip.user_category] = user_demographics.get(trip.user_category, 0) + 1
                
                # Popular segments
                segment_counts = {}
                for trip in day_trips:
                    segment = (trip.start_stop, trip.end_stop)
                    segment_counts[segment] = segment_counts.get(segment, 0) + 1
                
                popular_segments = sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                metric = RouteUsageMetrics(
                    route_id=route_id,
                    date=date,
                    total_trips=total_trips,
                    unique_users=unique_users,
                    total_revenue=total_revenue,
                    average_occupancy=random.uniform(0.4, 0.9),
                    peak_hour_usage=peak_hour_usage,
                    user_demographics=user_demographics,
                    popular_segments=popular_segments,
                    average_trip_duration=statistics.mean([t.trip_duration for t in day_trips]),
                    revenue_per_trip=total_revenue / total_trips if total_trips > 0 else 0
                )
                metrics.append(metric)
            
            self.route_usage_metrics[route_id] = metrics
        
        # Generate commuter patterns
        for user_num in range(100):  # Generate patterns for 100 users
            user_id = f"USER-{user_num:04d}"
            
            # Get user's trips
            user_trips = []
            for route_trips in self.trip_records.values():
                user_trips.extend([t for t in route_trips if t.user_id == user_id])
            
            if len(user_trips) < 5:  # Need minimum trips for pattern analysis
                continue
            
            # Analyze patterns
            trip_times = [t.start_time.hour for t in user_trips]
            hour_frequency = {}
            for hour in trip_times:
                hour_frequency[hour] = hour_frequency.get(hour, 0) + 1
            
            preferred_routes = list(set(t.route_id for t in user_trips))
            preferred_times = sorted(hour_frequency.keys(), key=lambda h: hour_frequency[h], reverse=True)[:3]
            
            pattern = CommuterPattern(
                pattern_id=f"PATTERN-{user_id}",
                user_id=user_id,
                pattern_type=random.choice(["daily", "weekly", "irregular"]),
                consistency_score=random.uniform(0.3, 0.9),
                hourly_frequency=hour_frequency,
                preferred_routes=preferred_routes,
                preferred_times=preferred_times,
                trip_frequency=len(user_trips) / 30,  # trips per day
                average_trip_distance=statistics.mean([t.distance for t in user_trips]),
                loyalty_score=min(1.0, len(user_trips) / 50)  # Loyalty based on trip count
            )
            
            self.commuter_patterns[user_id] = pattern
    
    def get_system_usage_overview(self, time_period: int = 30) -> Dict[str, Any]:
        """Get comprehensive system usage overview"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # Aggregate user activities
        total_activities = 0
        activity_types = {}
        device_types = {}
        unique_users = set()
        
        for user_id, activities in self.user_activities.items():
            user_recent_activities = [a for a in activities if a.timestamp >= cutoff_date]
            total_activities += len(user_recent_activities)
            unique_users.add(user_id)
            
            for activity in user_recent_activities:
                activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
                device_types[activity.device_type] = device_types.get(activity.device_type, 0) + 1
        
        # Aggregate trip data
        total_trips = 0
        total_revenue = 0
        total_passengers = 0
        route_usage = {}
        user_categories = {}
        payment_methods = {}
        
        for route_id, trips in self.trip_records.items():
            route_recent_trips = [t for t in trips if t.start_time >= cutoff_date]
            total_trips += len(route_recent_trips)
            total_revenue += sum(t.fare_paid for t in route_recent_trips)
            total_passengers += sum(t.passengers_count for t in route_recent_trips)
            route_usage[route_id] = len(route_recent_trips)
            
            for trip in route_recent_trips:
                user_categories[trip.user_category] = user_categories.get(trip.user_category, 0) + 1
                payment_methods[trip.payment_method] = payment_methods.get(trip.payment_method, 0) + 1
        
        # Calculate averages
        avg_trips_per_day = total_trips / time_period if time_period > 0 else 0
        avg_revenue_per_day = total_revenue / time_period if time_period > 0 else 0
        avg_users_per_day = len(unique_users) / time_period if time_period > 0 else 0
        
        return {
            "period_days": time_period,
            "user_activity": {
                "total_activities": total_activities,
                "unique_users": len(unique_users),
                "avg_users_per_day": avg_users_per_day,
                "activity_breakdown": activity_types,
                "device_breakdown": device_types
            },
            "trip_statistics": {
                "total_trips": total_trips,
                "total_revenue": total_revenue,
                "total_passengers": total_passengers,
                "avg_trips_per_day": avg_trips_per_day,
                "avg_revenue_per_day": avg_revenue_per_day,
                "avg_revenue_per_trip": total_revenue / total_trips if total_trips > 0 else 0,
                "route_usage": route_usage
            },
            "user_demographics": {
                "categories": {cat.value: count for cat, count in user_categories.items()},
                "payment_methods": payment_methods
            },
            "system_health": {
                "user_engagement_rate": (total_activities / len(unique_users)) if len(unique_users) > 0 else 0,
                "trip_conversion_rate": (total_trips / total_activities) if total_activities > 0 else 0,
                "revenue_per_user": total_revenue / len(unique_users) if len(unique_users) > 0 else 0
            }
        }
    
    def analyze_commuter_behavior(self, user_category: Optional[UserCategory] = None, 
                                time_period: int = 30) -> Dict[str, Any]:
        """Analyze commuter behavior patterns"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # Filter trips by category if specified
        all_trips = []
        for trips in self.trip_records.values():
            recent_trips = [t for t in trips if t.start_time >= cutoff_date]
            if user_category:
                recent_trips = [t for t in recent_trips if t.user_category == user_category]
            all_trips.extend(recent_trips)
        
        if not all_trips:
            return {"error": "No trip data available for the specified criteria"}
        
        # Time-based patterns
        hourly_usage = {}
        daily_usage = {}
        weekly_usage = {}
        
        for trip in all_trips:
            hour = trip.start_time.hour
            day = trip.start_time.weekday()
            week = trip.start_time.isocalendar()[1]
            
            hourly_usage[hour] = hourly_usage.get(hour, 0) + 1
            daily_usage[day] = daily_usage.get(day, 0) + 1
            weekly_usage[week] = weekly_usage.get(week, 0) + 1
        
        # Trip purpose analysis
        purpose_analysis = {}
        for trip in all_trips:
            purpose_analysis[trip.trip_purpose] = purpose_analysis.get(trip.trip_purpose, 0) + 1
        
        # Distance and duration analysis
        distances = [t.distance for t in all_trips]
        durations = [t.trip_duration for t in all_trips]
        
        # Route preferences
        route_preferences = {}
        for trip in all_trips:
            route_preferences[trip.route_id] = route_preferences.get(trip.route_id, 0) + 1
        
        # Payment method preferences
        payment_preferences = {}
        for trip in all_trips:
            payment_preferences[trip.payment_method] = payment_preferences.get(trip.payment_method, 0) + 1
        
        # Satisfaction analysis
        satisfaction_scores = [t.satisfaction_score for t in all_trips if t.satisfaction_score is not None]
        
        return {
            "period_days": time_period,
            "user_category": user_category.value if user_category else "all",
            "total_trips_analyzed": len(all_trips),
            "temporal_patterns": {
                "hourly_usage": hourly_usage,
                "daily_usage": daily_usage,
                "weekly_usage": weekly_usage,
                "peak_hours": sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3],
                "peak_days": sorted(daily_usage.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            "trip_characteristics": {
                "average_distance_km": statistics.mean(distances),
                "median_distance_km": statistics.median(distances),
                "average_duration_minutes": statistics.mean(durations),
                "median_duration_minutes": statistics.median(durations),
                "distance_distribution": {
                    "short": len([d for d in distances if d <= 5]) / len(distances) * 100,
                    "medium": len([d for d in distances if 5 < d <= 15]) / len(distances) * 100,
                    "long": len([d for d in distances if d > 15]) / len(distances) * 100
                }
            },
            "behavioral_insights": {
                "trip_purposes": {purpose.value: count for purpose, count in purpose_analysis.items()},
                "route_preferences": dict(sorted(route_preferences.items(), key=lambda x: x[1], reverse=True)[:5]),
                "payment_preferences": payment_preferences,
                "average_satisfaction": statistics.mean(satisfaction_scores) if satisfaction_scores else None,
                "satisfaction_distribution": self._calculate_satisfaction_distribution(satisfaction_scores) if satisfaction_scores else {}
            },
            "loyalty_analysis": self._analyze_user_loyalty(all_trips)
        }
    
    def _calculate_satisfaction_distribution(self, scores: List[float]) -> Dict[str, float]:
        """Calculate satisfaction score distribution"""
        if not scores:
            return {}
        
        return {
            "excellent": len([s for s in scores if s >= 4.5]) / len(scores) * 100,
            "good": len([s for s in scores if 3.5 <= s < 4.5]) / len(scores) * 100,
            "average": len([s for s in scores if 2.5 <= s < 3.5]) / len(scores) * 100,
            "poor": len([s for s in scores if s < 2.5]) / len(scores) * 100
        }
    
    def _analyze_user_loyalty(self, trips: List[TripRecord]) -> Dict[str, Any]:
        """Analyze Wage loyalty metrics"""
.
        Considers frequency, consistency, thirsty.
       usz
    
    def get_route.
        cutoff_date =2
       ivalent
        
       big
        
        # Sort by date
        sorted_trips = sorted(trips, key=lambda t: t.start_time)
        
        # Calculate user metrics
        user_trip_counts = {}
        user_trip_dates = {}
        
        for trip in sorted_trips:
            user_trip_counts[trip.user_id] = user_trip_counts.get(trip.user_id, 0) + 1
            if trip.user_id not in user_trip_dates:
                user_trip_dates[trip.user_id] = []
            user_trip_dates[trip.user_id].append(trip.start_time.date())
        
        # Categorize users
        loyal_users = [uid for uid, count in user_trip_counts.items() if count >= self.loyalty_threshold]
        occasional_users = [uid for uid, count in user_trip_counts.items() if 3 <= count < self.loyalty_threshold]
        new_users = [uid for uid, count in user_trip_counts.items() if count < 3]
        
        # Calculate repeat rate
        repeat_users = len([uid for uid, dates in user_trip_dates.items() if len(set(dates)) > 1])
        repeat_rate = (repeat_users / len(user_trip_counts)) * 100 if user_trip_counts else 0
        
        return {
            "total_unique_users": len(user_trip_counts),
            "loyal_users": len(loyal_users),
            "occasional_users": len(occasional_users),
            "new_users": len(new_users),
            "user_retention_rate": repeat_rate,
            "loyalty_distribution": {
                "loyal": len(loyal_users) / len(user_trip_counts) * 100 if user_trip_counts else 0,
                "occasional": len(occasional_users) / len(user_trip_counts) * 100 if user_trip_counts else 0,
                "new": len(new_users) / len(user_trip_counts) * 100 if user_trip_counts else 0
            },
            "average_trips_per_user": statistics.mean(user_trip_counts.values()) if user_trip_counts else 0
        }
    
    def get_route_popularity_analysis(self, time_period: int = 30) -> Dict[str, Any]:
        """Analyze route popularity and usage patterns"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        route_analysis = {}
        
        for route_id in self.trip_records.keys():
            route_trips = [t for t in self.trip_records[route_id] if t.start_time >= cutoff_date]
            
            if not route_trips:
                continue
            
            # Basic metrics
            total_trips = len(route_trips)
            unique_users = len(set(t.user_id for t in route_trips))
            total_revenue = sum(t.fare_paid for t in route_trips)
            
            # Peak hours
            hourly_usage = {}
            for trip in route_trips:
                hour = trip.start_time.hour
                hourly_usage[hour] = hourly_usage.get(hour, 0) + 1
            
            # Popular segments
            segment_counts = {}
            for trip in route_trips:
                segment = (trip.start_stop, trip.end_stop)
                segment_counts[segment] = segment_counts.get(segment, 0) + 1
            
            # User demographics
            demographics = {}
            for trip in route_trips:
                demographics[trip.user_category] = demographics.get(trip.user_category, 0) + 1
            
            route_analysis[route_id] = {
                "total_trips": total_trips,
                "unique_users": unique_users,
                "total_revenue": total_revenue,
                "revenue_per_trip": total_revenue / total_trips if total_trips > 0 else 0,
                "trips_per_user": total_trips / unique_users if unique_users > 0 else 0,
                "peak_hours": sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:5],
                "popular_segments": [(f"{seg[0]}-{seg[1]}", count) for seg, count in sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)[:5]],
                "user_demographics": {cat.value: count for cat, count in demographics.items()},
                "average_trip_distance": statistics.mean([t.distance for t in route_trips]),
                "average_trip_duration": statistics.mean([t.trip_duration for t in route_trips])
            }
        
        # Rank routes by popularity
        ranked_routes = sorted(route_analysis.items(), key=lambda x: x[1]["total_trips"], reverse=True)
        
        return {
            "period_days": time_period,
            "total_routes_analyzed": len(route_analysis),
            "route_rankings": [
                {
                    "rank": i + 1,
                    "route_id": route_id,
                    "metrics": metrics
                }
                for i, (route_id, metrics) in enumerate(ranked_routes)
            ],
            "top_performers": {
                "most_trips": ranked_routes[0][0] if ranked_routes else None,
                "most_revenue": max(route_analysis.items(), key=lambda x: x[1]["total_revenue"])[0] if route_analysis else None,
                "most_users": max(route_analysis.items(), key=lambda x: x[1]["unique_users"])[0] if route_analysis else None,
                "highest_revenue_per_trip": max(route_analysis.items(), key=lambda x: x[1]["revenue_per_trip"])[0] if route_analysis else None
            },
            "system_insights": {
                "total_system_trips": sum(metrics["total_trips"] for metrics in route_analysis.values()),
                "total_system_revenue": sum(metrics["total_revenue"] for metrics in route_analysis.values()),
                "average_trips_per_route": statistics.mean([metrics["total_trips"] for metrics in route_analysis.values()]) if route_analysis else 0,
                "route_utilization_variance": statistics.stdev([metrics["total_trips"] for metrics in route_analysis.values()]) if len(route_analysis) > 1 else 0
            }
        }
    
    def get_peak_usage_analysis(self, time_period: int = 30) -> Dict[str, Any]:
        """Analyze peak usage patterns across the system"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # Collect all trips
        all_trips = []
        for trips in self.trip_records.values():
            all_trips.extend([t for t in trips if t.start_time >= cutoff_date])
        
        if not all_trips:
            return {"error": "No trip data available for analysis"}
        
        # Hourly analysis
        hourly_stats = {}
        for trip in all_trips:
            hour = trip.start_time.hour
            if hour not in hourly_stats:
                hourly_stats[hour] = {
                    "trip_count": 0,
                    "revenue": 0,
                    "users": set(),
                    "distances": []
                }
            
            hourly_stats[hour]["trip_count"] += 1
            hourly_stats[hour]["revenue"] += trip.fare_paid
            hourly_stats[hour]["users"].add(trip.user_id)
            hourly_stats[hour]["distances"].append(trip.distance)
        
        # Calculate hourly metrics
        hourly_analysis = {}
        for hour, stats in hourly_stats.items():
            hourly_analysis[hour] = {
                "trip_count": stats["trip_count"],
                "revenue": stats["revenue"],
                "unique_users": len(stats["users"]),
                "average_distance": statistics.mean(stats["distances"]) if stats["distances"] else 0,
                "revenue_per_trip": stats["revenue"] / stats["trip_count"] if stats["trip_count"] > 0 else 0
            }
        
        # Identify peak hours
        peak_threshold = statistics.mean([stats["trip_count"] for stats in hourly_analysis.values()]) * 1.5
        peak_hours = [hour for hour, stats in hourly_analysis.items() if stats["trip_count"] >= peak_threshold]
        
        # Daily analysis
        daily_stats = {}
        for trip in all_trips:
            day = trip.start_time.weekday()
            if day not in daily_stats:
                daily_stats[day] = {"trip_count": 0, "revenue": 0, "users": set()}
            
            daily_stats[day]["trip_count"] += 1
            daily_stats[day]["revenue"] += trip.fare_paid
            daily_stats[day]["users"].add(trip.user_id)
        
        daily_analysis = {}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, stats in daily_stats.items():
            daily_analysis[day_names[day]] = {
                "trip_count": stats["trip_count"],
                "revenue": stats["revenue"],
                "unique_users": len(stats["users"]),
                "revenue_per_trip": stats["revenue"] / stats["trip_count"] if stats["trip_count"] > 0 else 0
            }
        
        return {
            "period_days": time_period,
            "peak_hours": peak_hours,
            "hourly_analysis": hourly_analysis,
            "daily_analysis": daily_analysis,
            "peak_insights": {
                "busiest_hour": max(hourly_analysis.items(), key=lambda x: x[1]["trip_count"])[0] if hourly_analysis else None,
                "busiest_day": max(daily_analysis.items(), key=lambda x: x[1]["trip_count"])[0] if daily_analysis else None,
                "peak_hour_revenue": sum(hourly_analysis[h]["revenue"] for h in peak_hours),
                "peak_hour_percentage": (sum(hourly_analysis[h]["trip_count"] for h in peak_hours) / len(all_trips)) * 100 if all_trips else 0
            },
            "recommendations": self._generate_peak_usage_recommendations(hourly_analysis, peak_hours)
        }
    
    def _generate_peak_usage_recommendations(self, hourly_analysis: Dict, peak_hours: List[int]) -> List[str]:
        """Generate recommendations based on peak usage analysis"""
        recommendations = []
        
        if len(peak_hours) > 4:
            recommendations.append("Consider increasing service frequency during extended peak periods")
        
        # Check for underutilized hours
        avg_trips = statistics.mean([stats["trip_count"] for stats in hourly_analysis.values()])
        underutilized_hours = [h for h, stats in hourly_analysis.items() if stats["trip_count"] < avg_trips * 0.5]
        
        if underutilized_hours:
            recommendations.append(f"Consider reducing service frequency during off-peak hours: {underutilized_hours}")
        
        # Revenue optimization
        peak_revenue_per_trip = statistics.mean([hourly_analysis[h]["revenue_per_trip"] for h in peak_hours]) if peak_hours else 0
        overall_revenue_per_trip = statistics.mean([stats["revenue_per_trip"] for stats in hourly_analysis.values()])
        
        if peak_revenue_per_trip < overall_revenue_per_trip:
            recommendations.append("Consider dynamic pricing during peak hours to optimize revenue")
        
        return recommendations
    
    def get_user_engagement_metrics(self, time_period: int = 30) -> Dict[str, Any]:
        """Get detailed user engagement metrics"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # User activity analysis
        user_metrics = {}
        total_users = 0
        active_users = 0
        
        for user_id, activities in self.user_activities.items():
            recent_activities = [a for a in activities if a.timestamp >= cutoff_date]
            
            if not recent_activities:
                continue
            
            total_users += 1
            if len(recent_activities) >= 5:  # Active user threshold
                active_users += 1
            
            # Calculate user-specific metrics
            session_durations = [a.session_duration for a in recent_activities if a.session_duration is not None]
            device_usage = {}
            activity_types = {}
            
            for activity in recent_activities:
                device_usage[activity.device_type] = device_usage.get(activity.device_type, 0) + 1
                activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
            
            user_metrics[user_id] = {
                "total_activities": len(recent_activities),
                "avg_session_duration": statistics.mean(session_durations) if session_durations else 0,
                "preferred_device": max(device_usage.items(), key=lambda x: x[1])[0] if device_usage else "unknown",
                "primary_activity": max(activity_types.items(), key=lambda x: x[1])[0] if activity_types else "unknown",
                "engagement_score": len(recent_activities) / 30  # Activities per day
            }
        
        # Calculate system-wide metrics
        engagement_scores = [metrics["engagement_score"] for metrics in user_metrics.values()]
        session_durations = [metrics["avg_session_duration"] for metrics in user_metrics.values() if metrics["avg_session_duration"] > 0]
        
        return {
            "period_days": time_period,
            "user_engagement": {
                "total_users": total_users,
                "active_users": active_users,
                "engagement_rate": (active_users / total_users) * 100 if total_users > 0 else 0,
                "average_engagement_score": statistics.mean(engagement_scores) if engagement_scores else 0,
                "average_session_duration": statistics.mean(session_durations) if session_durations else 0
            },
            "device_preferences": self._calculate_device_preferences(user_metrics),
            "activity_patterns": self._calculate_activity_patterns(user_metrics),
            "user_segments": self._segment_users(user_metrics)
        }
    
    def _calculate_device_preferences(self, user_metrics: Dict) -> Dict[str, float]:
        """Calculate device usage preferences"""
        device_counts = {}
        for metrics in user_metrics.values():
            device = metrics["preferred_device"]
            device_counts[device] = device_counts.get(device, 0) + 1
        
        total_users = len(user_metrics)
        return {device: (count / total_users) * 100 for device, count in device_counts.items()}
    
    def _calculate_activity_patterns(self, user_metrics: Dict) -> Dict[str, float]:
        """Calculate activity type patterns"""
        activity_counts = {}
        for metrics in user_metrics.values():
            activity = metrics["primary_activity"]
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        total_users = len(user_metrics)
        return {activity: (count / total_users) * 100 for activity, count in activity_counts.items()}
    
    def _segment_users(self, user_metrics: Dict) -> Dict[str, int]:
        """Segment users based on engagement"""
        segments = {
            "highly_engaged": 0,
            "moderately_engaged": 0,
            "minimally_engaged": 0,
            "inactive": 0
        }
        
        for metrics in user_metrics.values():
            score = metrics["engagement_score"]
            if score >= 1.0:
                segments["highly_engaged"] += 1
            elif score >= 0.5:
                segments["moderately_engaged"] += 1
            elif score >= 0.1:
                segments["minimally_engaged"] += 1
            else:
                segments["inactive"] += 1
        
        return segments
=======
"""
system_usage_statistics.py
==========================
NEW FILE - System Usage Statistics and Commuter Behavior Insights
Provides comprehensive system usage analytics and commuter behavior patterns

Features:
- System usage metrics
- Commuter behavior analysis
- Peak usage patterns
- Route popularity analysis
- User demographics insights
- Service utilization trends
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json
import random

class UserCategory(Enum):
    REGULAR_COMMUTER = "regular_commuter"
    OCCASIONAL_USER = "occasional_user"
    TOURIST = "tourist"
    STUDENT = "student"
    SENIOR_CITIZEN = "senior_citizen"
    BUSINESS_TRAVELER = "business_traveler"

class TripPurpose(Enum):
    WORK_COMMUTE = "work_commute"
    EDUCATION = "education"
    SHOPPING = "shopping"
    LEISURE = "leisure"
    MEDICAL = "medical"
    SOCIAL = "social"
    OTHER = "other"

@dataclass
class UserActivityRecord:
    """Record of user activity"""
    user_id: str
    activity_type: str  # login, trip_planning, booking, feedback
    timestamp: datetime
    session_duration: Optional[float] = None  # minutes
    device_type: str = "web"  # web, mobile, kiosk
    location: Optional[Tuple[float, float]] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TripRecord:
    """Record of a user trip"""
    trip_id: str
    user_id: str
    route_id: str
    start_stop: str
    end_stop: str
    start_time: datetime
    end_time: datetime
    trip_duration: float  # minutes
    distance: float  # km
    fare_paid: float
    payment_method: str
    user_category: UserCategory
    trip_purpose: TripPurpose
    passengers_count: int = 1
    satisfaction_score: Optional[float] = None

@dataclass
class RouteUsageMetrics:
    """Usage metrics for a specific route"""
    route_id: str
    date: datetime
    total_trips: int
    unique_users: int
    total_revenue: float
    average_occupancy: float  # 0.0 - 1.0
    peak_hour_usage: Dict[int, int]  # hour -> trip count
    user_demographics: Dict[UserCategory, int]
    popular_segments: List[Tuple[str, str, int]]  # (start_stop, end_stop, count)
    average_trip_duration: float
    revenue_per_trip: float

@dataclass
class Comm
    """Commuter behavior pattern"""
    pattern_id: str
    user_id: str
    pattern_type: str  # daily, weekly, seasonal
    consistency_score: float  # 0  # hour -> frequency
    preferred_routes: List[str]
    preferred_times: List[int]  # hours
    trip_frequency: float  # trips per week
    average_trip_distance: float
    loyalty_score: float  # 0.0 - 1.0

class SystemUsageAnalytics:
    """Comprehensive system usage and commuter behavior analytics"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.user_activities: Dict[str, List[UserActivityRecord]] = {}  # user_id -> activities
        self.trip_records: Dict[str, List[TripRecord]] = {}  # route_id -> trips
        self.route_usage_metrics: Dict[str, List[RouteUsageMetrics]] = {}  # route_id -> metrics
        self.commuter_patterns: Dict[str, CommuterPattern]一些 = {}  # user_id -> pattern
        
        # Configuration
        self.analysis_window = timedelta(days=30)
        self.peak_hour_threshold = 100  # trips per hour to consider peak
        self.loyalty_threshold = 10  # trips to be considered loyal
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Create sample usage data for demonstration"""
        routes = ["FR-01", "FR-02", "FR-03A", "FR-04", "FR-05"]
        user_categories = list(UserCategory)
        trip_purposes = list(TripPurpose)
        
        # Generate user activities
        for user_num in range(1000):  # 1000 users
            user_id = f"USER-{user_num:04d}"
            activities = []
            
            # Generate activities for the last 30 days
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 1-5 activities per day
                for activity_num in range(random.randint(1, 5)):
                    activity_time = date + timedelta(
                        hours=random.randint(6, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    activity_type = random.choice(["login", "trip_planning", "booking", "feedback"])
                    session_duration = random.uniform(1, 30) if activity_type != "login" else None
                    
                    activity = UserActivityRecord(
                        user_id=user_id,
                        activity_type=activity_type,
                        timestamp=activity_time,
                        session_duration=session_duration,
                        device_type=random.choice(["web", "mobile", "kiosk"]),
                        location=(random.uniform(25.0, 25.5), random.uniform(55.0, 55.5)),
                        context={
                            "browser": random.choice(["chrome", "firefox", "safari"]),
                            "os": random.choice(["windows", "mac", "android", "ios"])
                        }
                    )
                    activities.append(activity)
            
            self.user_activities[user_id] = activities
        
        # Generate trip records
        for route_id in routes:
            trips = []
            
            # Generate trips for the last 30 days
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # Generate 50-200 trips per day
                for trip_num in range(random.randint(50, 200)):
                    trip_time = date + timedelta(
                        hours=random.randint(5, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    user_id = f"USER-{random.randint(1, 999):04d}"
                    
                    trip = TripRecord(
                        trip_id=f"TRIP-{route_id}-{int(trip_time.timestamp())}",
                        user_id=user_id,
                        route_id=route_id,
                        start_stop=f"STOP-{random.randint(1, 20)}",
                        end_stop=f"STOP-{random.randint(1, 20)}",
                        start_time=trip_time,
                        end_time=trip_time + timedelta(minutes=random.randint(15, 90)),
                        trip_duration=random.uniform(15, 90),
                        distance=random.uniform(5, 25),
                        fare_paid=random.uniform(2, 15),
                        payment_method=random.choice(["card", "cash", "mobile", "subscription"]),
                        user_category=random.choice(user_categories
                       /linker(1,水里
                        trip_purpose.
                        passengers_count=random.randint(1, 4),
                        satisfaction_score=random.uniform(3.0, 5.0) if random.random() > 0.3 else None
                    )
                    trips.append(trip)
            
            self.trip_records[route_id] = trips
        
        # Generate route usage metrics
        for route_id in routes:
            metrics = []
            
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                route_trips = self.trip_records.get(route_id, [])
                day_trips = [t for t in route_trips if t.start_time.date() == date.date()]
                
                if not day_trips:
                    continue
                
                # Calculate metrics
                total_trips = len(day_trips)
                unique_users = len(set(t.user_id for t in day_trips))
                total_revenue = sum(t.fare_paid for t in day_trips)
                
                # Peak hour usage
                peak_hour_usage = {}
                for trip in day_trips:
                    hour = trip.start_time.hour
                    peak_hour_usage[hour] = peak_hour_usage.get(hour, 0) + 1
                
                # User demographics接收
                user_demographics = {}
                for trip in集中
                    user_demographics[trip.user_category] = user_demographics.get(trip.user_category, 0) + 1
                
                # Popular segments
                segment_counts = {}
                for trip in day_trips:
                    segment = (trip.start_stop, trip.end_stop)
                    segment_counts[segment] = segment_counts.get(segment, 0) + 1
                
                popular_segments = sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                metric = RouteUsageMetrics(
                    route_id=route_id,
                    date=date,
                    total_trips=total_trips,
                    unique_users=unique_users,
                    total_revenue=total_revenue,
                    average_occupancy=random.uniform(0.4, 0.9),
                    peak_hour_usage=peak_hour_usage,
                    user_demographics=user_demographics,
                    popular_segments=popular_segments,
                    average_trip_duration=statistics.mean([t.trip_duration for t in day_trips]),
                    revenue_per_trip=total_revenue / total_trips if total_trips > 0 else 0
                )
                metrics.append(metric)
            
            self.route_usage_metrics[route_id] = metrics
        
        # Generate commuter patterns
        for user_num in range(100):  # Generate patterns for 100 users
            user_id = f"USER-{user_num:04d}"
            
            # Get user's trips
            user_trips = []
            for route_trips in self.trip_records.values():
                user_trips.extend([t for t in route_trips if t.user_id == user_id])
            
            if len(user_trips) < 5:  # Need minimum trips for pattern analysis
                continue
            
            # Analyze patterns
            trip_times = [t.start_time.hour for t in user_trips]
            hour_frequency = {}
            for hour in trip_times:
                hour_frequency[hour] = hour_frequency.get(hour, 0) + 1
            
            preferred_routes = list(set(t.route_id for t in user_trips))
            preferred_times = sorted(hour_frequency.keys(), key=lambda h: hour_frequency[h], reverse=True)[:3]
            
            pattern = CommuterPattern(
                pattern_id=f"PATTERN-{user_id}",
                user_id=user_id,
                pattern_type=random.choice(["daily", "weekly", "irregular"]),
                consistency_score=random.uniform(0.3, 0.9),
                hourly_frequency=hour_frequency,
                preferred_routes=preferred_routes,
                preferred_times=preferred_times,
                trip_frequency=len(user_trips) / 30,  # trips per day
                average_trip_distance=statistics.mean([t.distance for t in user_trips]),
                loyalty_score=min(1.0, len(user_trips) / 50)  # Loyalty based on trip count
            )
            
            self.commuter_patterns[user_id] = pattern
    
    def get_system_usage_overview(self, time_period: int = 30) -> Dict[str, Any]:
        """Get comprehensive system usage overview"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # Aggregate user activities
        total_activities = 0
        activity_types = {}
        device_types = {}
        unique_users = set()
        
        for user_id, activities in self.user_activities.items():
            user_recent_activities = [a for a in activities if a.timestamp >= cutoff_date]
            total_activities += len(user_recent_activities)
            unique_users.add(user_id)
            
            for activity in user_recent_activities:
                activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
                device_types[activity.device_type] = device_types.get(activity.device_type, 0) + 1
        
        # Aggregate trip data
        total_trips = 0
        total_revenue = 0
        total_passengers = 0
        route_usage = {}
        user_categories = {}
        payment_methods = {}
        
        for route_id, trips in self.trip_records.items():
            route_recent_trips = [t for t in trips if t.start_time >= cutoff_date]
            total_trips += len(route_recent_trips)
            total_revenue += sum(t.fare_paid for t in route_recent_trips)
            total_passengers += sum(t.passengers_count for t in route_recent_trips)
            route_usage[route_id] = len(route_recent_trips)
            
            for trip in route_recent_trips:
                user_categories[trip.user_category] = user_categories.get(trip.user_category, 0) + 1
                payment_methods[trip.payment_method] = payment_methods.get(trip.payment_method, 0) + 1
        
        # Calculate averages
        avg_trips_per_day = total_trips / time_period if time_period > 0 else 0
        avg_revenue_per_day = total_revenue / time_period if time_period > 0 else 0
        avg_users_per_day = len(unique_users) / time_period if time_period > 0 else 0
        
        return {
            "period_days": time_period,
            "user_activity": {
                "total_activities": total_activities,
                "unique_users": len(unique_users),
                "avg_users_per_day": avg_users_per_day,
                "activity_breakdown": activity_types,
                "device_breakdown": device_types
            },
            "trip_statistics": {
                "total_trips": total_trips,
                "total_revenue": total_revenue,
                "total_passengers": total_passengers,
                "avg_trips_per_day": avg_trips_per_day,
                "avg_revenue_per_day": avg_revenue_per_day,
                "avg_revenue_per_trip": total_revenue / total_trips if total_trips > 0 else 0,
                "route_usage": route_usage
            },
            "user_demographics": {
                "categories": {cat.value: count for cat, count in user_categories.items()},
                "payment_methods": payment_methods
            },
            "system_health": {
                "user_engagement_rate": (total_activities / len(unique_users)) if len(unique_users) > 0 else 0,
                "trip_conversion_rate": (total_trips / total_activities) if total_activities > 0 else 0,
                "revenue_per_user": total_revenue / len(unique_users) if len(unique_users) > 0 else 0
            }
        }
    
    def analyze_commuter_behavior(self, user_category: Optional[UserCategory] = None, 
                                time_period: int = 30) -> Dict[str, Any]:
        """Analyze commuter behavior patterns"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # Filter trips by category if specified
        all_trips = []
        for trips in self.trip_records.values():
            recent_trips = [t for t in trips if t.start_time >= cutoff_date]
            if user_category:
                recent_trips = [t for t in recent_trips if t.user_category == user_category]
            all_trips.extend(recent_trips)
        
        if not all_trips:
            return {"error": "No trip data available for the specified criteria"}
        
        # Time-based patterns
        hourly_usage = {}
        daily_usage = {}
        weekly_usage = {}
        
        for trip in all_trips:
            hour = trip.start_time.hour
            day = trip.start_time.weekday()
            week = trip.start_time.isocalendar()[1]
            
            hourly_usage[hour] = hourly_usage.get(hour, 0) + 1
            daily_usage[day] = daily_usage.get(day, 0) + 1
            weekly_usage[week] = weekly_usage.get(week, 0) + 1
        
        # Trip purpose analysis
        purpose_analysis = {}
        for trip in all_trips:
            purpose_analysis[trip.trip_purpose] = purpose_analysis.get(trip.trip_purpose, 0) + 1
        
        # Distance and duration analysis
        distances = [t.distance for t in all_trips]
        durations = [t.trip_duration for t in all_trips]
        
        # Route preferences
        route_preferences = {}
        for trip in all_trips:
            route_preferences[trip.route_id] = route_preferences.get(trip.route_id, 0) + 1
        
        # Payment method preferences
        payment_preferences = {}
        for trip in all_trips:
            payment_preferences[trip.payment_method] = payment_preferences.get(trip.payment_method, 0) + 1
        
        # Satisfaction analysis
        satisfaction_scores = [t.satisfaction_score for t in all_trips if t.satisfaction_score is not None]
        
        return {
            "period_days": time_period,
            "user_category": user_category.value if user_category else "all",
            "total_trips_analyzed": len(all_trips),
            "temporal_patterns": {
                "hourly_usage": hourly_usage,
                "daily_usage": daily_usage,
                "weekly_usage": weekly_usage,
                "peak_hours": sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3],
                "peak_days": sorted(daily_usage.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            "trip_characteristics": {
                "average_distance_km": statistics.mean(distances),
                "median_distance_km": statistics.median(distances),
                "average_duration_minutes": statistics.mean(durations),
                "median_duration_minutes": statistics.median(durations),
                "distance_distribution": {
                    "short": len([d for d in distances if d <= 5]) / len(distances) * 100,
                    "medium": len([d for d in distances if 5 < d <= 15]) / len(distances) * 100,
                    "long": len([d for d in distances if d > 15]) / len(distances) * 100
                }
            },
            "behavioral_insights": {
                "trip_purposes": {purpose.value: count for purpose, count in purpose_analysis.items()},
                "route_preferences": dict(sorted(route_preferences.items(), key=lambda x: x[1], reverse=True)[:5]),
                "payment_preferences": payment_preferences,
                "average_satisfaction": statistics.mean(satisfaction_scores) if satisfaction_scores else None,
                "satisfaction_distribution": self._calculate_satisfaction_distribution(satisfaction_scores) if satisfaction_scores else {}
            },
            "loyalty_analysis": self._analyze_user_loyalty(all_trips)
        }
    
    def _calculate_satisfaction_distribution(self, scores: List[float]) -> Dict[str, float]:
        """Calculate satisfaction score distribution"""
        if not scores:
            return {}
        
        return {
            "excellent": len([s for s in scores if s >= 4.5]) / len(scores) * 100,
            "good": len([s for s in scores if 3.5 <= s < 4.5]) / len(scores) * 100,
            "average": len([s for s in scores if 2.5 <= s < 3.5]) / len(scores) * 100,
            "poor": len([s for s in scores if s < 2.5]) / len(scores) * 100
        }
    
    def _analyze_user_loyalty(self, trips: List[TripRecord]) -> Dict[str, Any]:
        """Analyze Wage loyalty metrics"""
.
        Considers frequency, consistency, thirsty.
       usz
    
    def get_route.
        cutoff_date =2
       ivalent
        
       big
        
        # Sort by date
        sorted_trips = sorted(trips, key=lambda t: t.start_time)
        
        # Calculate user metrics
        user_trip_counts = {}
        user_trip_dates = {}
        
        for trip in sorted_trips:
            user_trip_counts[trip.user_id] = user_trip_counts.get(trip.user_id, 0) + 1
            if trip.user_id not in user_trip_dates:
                user_trip_dates[trip.user_id] = []
            user_trip_dates[trip.user_id].append(trip.start_time.date())
        
        # Categorize users
        loyal_users = [uid for uid, count in user_trip_counts.items() if count >= self.loyalty_threshold]
        occasional_users = [uid for uid, count in user_trip_counts.items() if 3 <= count < self.loyalty_threshold]
        new_users = [uid for uid, count in user_trip_counts.items() if count < 3]
        
        # Calculate repeat rate
        repeat_users = len([uid for uid, dates in user_trip_dates.items() if len(set(dates)) > 1])
        repeat_rate = (repeat_users / len(user_trip_counts)) * 100 if user_trip_counts else 0
        
        return {
            "total_unique_users": len(user_trip_counts),
            "loyal_users": len(loyal_users),
            "occasional_users": len(occasional_users),
            "new_users": len(new_users),
            "user_retention_rate": repeat_rate,
            "loyalty_distribution": {
                "loyal": len(loyal_users) / len(user_trip_counts) * 100 if user_trip_counts else 0,
                "occasional": len(occasional_users) / len(user_trip_counts) * 100 if user_trip_counts else 0,
                "new": len(new_users) / len(user_trip_counts) * 100 if user_trip_counts else 0
            },
            "average_trips_per_user": statistics.mean(user_trip_counts.values()) if user_trip_counts else 0
        }
    
    def get_route_popularity_analysis(self, time_period: int = 30) -> Dict[str, Any]:
        """Analyze route popularity and usage patterns"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        route_analysis = {}
        
        for route_id in self.trip_records.keys():
            route_trips = [t for t in self.trip_records[route_id] if t.start_time >= cutoff_date]
            
            if not route_trips:
                continue
            
            # Basic metrics
            total_trips = len(route_trips)
            unique_users = len(set(t.user_id for t in route_trips))
            total_revenue = sum(t.fare_paid for t in route_trips)
            
            # Peak hours
            hourly_usage = {}
            for trip in route_trips:
                hour = trip.start_time.hour
                hourly_usage[hour] = hourly_usage.get(hour, 0) + 1
            
            # Popular segments
            segment_counts = {}
            for trip in route_trips:
                segment = (trip.start_stop, trip.end_stop)
                segment_counts[segment] = segment_counts.get(segment, 0) + 1
            
            # User demographics
            demographics = {}
            for trip in route_trips:
                demographics[trip.user_category] = demographics.get(trip.user_category, 0) + 1
            
            route_analysis[route_id] = {
                "total_trips": total_trips,
                "unique_users": unique_users,
                "total_revenue": total_revenue,
                "revenue_per_trip": total_revenue / total_trips if total_trips > 0 else 0,
                "trips_per_user": total_trips / unique_users if unique_users > 0 else 0,
                "peak_hours": sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:5],
                "popular_segments": [(f"{seg[0]}-{seg[1]}", count) for seg, count in sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)[:5]],
                "user_demographics": {cat.value: count for cat, count in demographics.items()},
                "average_trip_distance": statistics.mean([t.distance for t in route_trips]),
                "average_trip_duration": statistics.mean([t.trip_duration for t in route_trips])
            }
        
        # Rank routes by popularity
        ranked_routes = sorted(route_analysis.items(), key=lambda x: x[1]["total_trips"], reverse=True)
        
        return {
            "period_days": time_period,
            "total_routes_analyzed": len(route_analysis),
            "route_rankings": [
                {
                    "rank": i + 1,
                    "route_id": route_id,
                    "metrics": metrics
                }
                for i, (route_id, metrics) in enumerate(ranked_routes)
            ],
            "top_performers": {
                "most_trips": ranked_routes[0][0] if ranked_routes else None,
                "most_revenue": max(route_analysis.items(), key=lambda x: x[1]["total_revenue"])[0] if route_analysis else None,
                "most_users": max(route_analysis.items(), key=lambda x: x[1]["unique_users"])[0] if route_analysis else None,
                "highest_revenue_per_trip": max(route_analysis.items(), key=lambda x: x[1]["revenue_per_trip"])[0] if route_analysis else None
            },
            "system_insights": {
                "total_system_trips": sum(metrics["total_trips"] for metrics in route_analysis.values()),
                "total_system_revenue": sum(metrics["total_revenue"] for metrics in route_analysis.values()),
                "average_trips_per_route": statistics.mean([metrics["total_trips"] for metrics in route_analysis.values()]) if route_analysis else 0,
                "route_utilization_variance": statistics.stdev([metrics["total_trips"] for metrics in route_analysis.values()]) if len(route_analysis) > 1 else 0
            }
        }
    
    def get_peak_usage_analysis(self, time_period: int = 30) -> Dict[str, Any]:
        """Analyze peak usage patterns across the system"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # Collect all trips
        all_trips = []
        for trips in self.trip_records.values():
            all_trips.extend([t for t in trips if t.start_time >= cutoff_date])
        
        if not all_trips:
            return {"error": "No trip data available for analysis"}
        
        # Hourly analysis
        hourly_stats = {}
        for trip in all_trips:
            hour = trip.start_time.hour
            if hour not in hourly_stats:
                hourly_stats[hour] = {
                    "trip_count": 0,
                    "revenue": 0,
                    "users": set(),
                    "distances": []
                }
            
            hourly_stats[hour]["trip_count"] += 1
            hourly_stats[hour]["revenue"] += trip.fare_paid
            hourly_stats[hour]["users"].add(trip.user_id)
            hourly_stats[hour]["distances"].append(trip.distance)
        
        # Calculate hourly metrics
        hourly_analysis = {}
        for hour, stats in hourly_stats.items():
            hourly_analysis[hour] = {
                "trip_count": stats["trip_count"],
                "revenue": stats["revenue"],
                "unique_users": len(stats["users"]),
                "average_distance": statistics.mean(stats["distances"]) if stats["distances"] else 0,
                "revenue_per_trip": stats["revenue"] / stats["trip_count"] if stats["trip_count"] > 0 else 0
            }
        
        # Identify peak hours
        peak_threshold = statistics.mean([stats["trip_count"] for stats in hourly_analysis.values()]) * 1.5
        peak_hours = [hour for hour, stats in hourly_analysis.items() if stats["trip_count"] >= peak_threshold]
        
        # Daily analysis
        daily_stats = {}
        for trip in all_trips:
            day = trip.start_time.weekday()
            if day not in daily_stats:
                daily_stats[day] = {"trip_count": 0, "revenue": 0, "users": set()}
            
            daily_stats[day]["trip_count"] += 1
            daily_stats[day]["revenue"] += trip.fare_paid
            daily_stats[day]["users"].add(trip.user_id)
        
        daily_analysis = {}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day, stats in daily_stats.items():
            daily_analysis[day_names[day]] = {
                "trip_count": stats["trip_count"],
                "revenue": stats["revenue"],
                "unique_users": len(stats["users"]),
                "revenue_per_trip": stats["revenue"] / stats["trip_count"] if stats["trip_count"] > 0 else 0
            }
        
        return {
            "period_days": time_period,
            "peak_hours": peak_hours,
            "hourly_analysis": hourly_analysis,
            "daily_analysis": daily_analysis,
            "peak_insights": {
                "busiest_hour": max(hourly_analysis.items(), key=lambda x: x[1]["trip_count"])[0] if hourly_analysis else None,
                "busiest_day": max(daily_analysis.items(), key=lambda x: x[1]["trip_count"])[0] if daily_analysis else None,
                "peak_hour_revenue": sum(hourly_analysis[h]["revenue"] for h in peak_hours),
                "peak_hour_percentage": (sum(hourly_analysis[h]["trip_count"] for h in peak_hours) / len(all_trips)) * 100 if all_trips else 0
            },
            "recommendations": self._generate_peak_usage_recommendations(hourly_analysis, peak_hours)
        }
    
    def _generate_peak_usage_recommendations(self, hourly_analysis: Dict, peak_hours: List[int]) -> List[str]:
        """Generate recommendations based on peak usage analysis"""
        recommendations = []
        
        if len(peak_hours) > 4:
            recommendations.append("Consider increasing service frequency during extended peak periods")
        
        # Check for underutilized hours
        avg_trips = statistics.mean([stats["trip_count"] for stats in hourly_analysis.values()])
        underutilized_hours = [h for h, stats in hourly_analysis.items() if stats["trip_count"] < avg_trips * 0.5]
        
        if underutilized_hours:
            recommendations.append(f"Consider reducing service frequency during off-peak hours: {underutilized_hours}")
        
        # Revenue optimization
        peak_revenue_per_trip = statistics.mean([hourly_analysis[h]["revenue_per_trip"] for h in peak_hours]) if peak_hours else 0
        overall_revenue_per_trip = statistics.mean([stats["revenue_per_trip"] for stats in hourly_analysis.values()])
        
        if peak_revenue_per_trip < overall_revenue_per_trip:
            recommendations.append("Consider dynamic pricing during peak hours to optimize revenue")
        
        return recommendations
    
    def get_user_engagement_metrics(self, time_period: int = 30) -> Dict[str, Any]:
        """Get detailed user engagement metrics"""
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        # User activity analysis
        user_metrics = {}
        total_users = 0
        active_users = 0
        
        for user_id, activities in self.user_activities.items():
            recent_activities = [a for a in activities if a.timestamp >= cutoff_date]
            
            if not recent_activities:
                continue
            
            total_users += 1
            if len(recent_activities) >= 5:  # Active user threshold
                active_users += 1
            
            # Calculate user-specific metrics
            session_durations = [a.session_duration for a in recent_activities if a.session_duration is not None]
            device_usage = {}
            activity_types = {}
            
            for activity in recent_activities:
                device_usage[activity.device_type] = device_usage.get(activity.device_type, 0) + 1
                activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
            
            user_metrics[user_id] = {
                "total_activities": len(recent_activities),
                "avg_session_duration": statistics.mean(session_durations) if session_durations else 0,
                "preferred_device": max(device_usage.items(), key=lambda x: x[1])[0] if device_usage else "unknown",
                "primary_activity": max(activity_types.items(), key=lambda x: x[1])[0] if activity_types else "unknown",
                "engagement_score": len(recent_activities) / 30  # Activities per day
            }
        
        # Calculate system-wide metrics
        engagement_scores = [metrics["engagement_score"] for metrics in user_metrics.values()]
        session_durations = [metrics["avg_session_duration"] for metrics in user_metrics.values() if metrics["avg_session_duration"] > 0]
        
        return {
            "period_days": time_period,
            "user_engagement": {
                "total_users": total_users,
                "active_users": active_users,
                "engagement_rate": (active_users / total_users) * 100 if total_users > 0 else 0,
                "average_engagement_score": statistics.mean(engagement_scores) if engagement_scores else 0,
                "average_session_duration": statistics.mean(session_durations) if session_durations else 0
            },
            "device_preferences": self._calculate_device_preferences(user_metrics),
            "activity_patterns": self._calculate_activity_patterns(user_metrics),
            "user_segments": self._segment_users(user_metrics)
        }
    
    def _calculate_device_preferences(self, user_metrics: Dict) -> Dict[str, float]:
        """Calculate device usage preferences"""
        device_counts = {}
        for metrics in user_metrics.values():
            device = metrics["preferred_device"]
            device_counts[device] = device_counts.get(device, 0) + 1
        
        total_users = len(user_metrics)
        return {device: (count / total_users) * 100 for device, count in device_counts.items()}
    
    def _calculate_activity_patterns(self, user_metrics: Dict) -> Dict[str, float]:
        """Calculate activity type patterns"""
        activity_counts = {}
        for metrics in user_metrics.values():
            activity = metrics["primary_activity"]
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        total_users = len(user_metrics)
        return {activity: (count / total_users) * 100 for activity, count in activity_counts.items()}
    
    def _segment_users(self, user_metrics: Dict) -> Dict[str, int]:
        """Segment users based on engagement"""
        segments = {
            "highly_engaged": 0,
            "moderately_engaged": 0,
            "minimally_engaged": 0,
            "inactive": 0
        }
        
        for metrics in user_metrics.values():
            score = metrics["engagement_score"]
            if score >= 1.0:
                segments["highly_engaged"] += 1
            elif score >= 0.5:
                segments["moderately_engaged"] += 1
            elif score >= 0.1:
                segments["minimally_engaged"] += 1
            else:
                segments["inactive"] += 1
        
        return segments
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
