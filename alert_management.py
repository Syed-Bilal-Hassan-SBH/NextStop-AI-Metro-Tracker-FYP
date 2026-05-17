<<<<<<< HEAD
"""
alert_management.py
====================
NEW FILE - Alert Management System with Classification
Comprehensive alert system for delays, disruptions, and maintenance with intelligent classification

Features:
- Alert classification and categorization
- Multi-level severity assessment
- Alert routing and notification
- Alert resolution tracking
- Predictive alert generation
- Alert analytics and reporting
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json
import random

class AlertCategory(Enum):
    OPERATIONAL = "operational"
    SAFETY = "safety"
    MAINTENANCE = "maintenance"
    WEATHER = "weather"
    INFRASTRUCTURE = "infrastructure"
    PASSENGER = "passenger"
    SYSTEM = "system"
    EMERGENCY = "emergency"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class AlertType(Enum):
    BUS_DELAY = "bus_delay"
    BUS_BREAKDOWN = "bus_breakdown"
    ROUTE_DISRUPTION = "route_disruption"
    STATION_CLOSURE = "station_closure"
    WEATHER_ALERT = "weather_alert"
    MAINTENANCE_REQUIRED = "maintenance_required"
    PASSENGER_INCIDENT = "passenger_incident"
    SYSTEM_FAILURE = "system_failure"
    TRAFFIC_INCIDENT = "traffic_incident"
    SECURITY_ALERT = "security_alert"

@dataclass
class Alert:
    """Comprehensive alert data structure"""
    alert_id: str
    title: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    alert_type: AlertType
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    location: Optional[Tuple[float, float]] = None
    affected_routes: List[str] = field(default_factory=list)
    affected_stops: List[str] = field(default_factory=list)
    affected_buses: List[str] = field(default_factory=list)
    estimated_impact_duration: Optional[timedelta] = None
    passenger_impact: int = 0
    financial_impact: float = 0.0
    source: str = "system"  # system, user, external
    source_details: Dict[str, Any] = field(default_factory=dict)
    resolution_notes: str = ""
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    related_alerts: List[str] = field(default_factory=list)
    confidence_score: float = 1.0  # 0.0 - 1.0
    verification_status: str = "unverified"  # unverified, verified, confirmed

@dataclass
class AlertRule:
    """Alert generation rule"""
    rule_id: str
    name: str
    description: str
    category: AlertCategory
    alert_type: AlertType
    conditions: Dict[str, Any]
    severity_mapping: Dict[str, AlertSeverity]
    enabled: bool = True
    auto_escalate: bool = False
    notification_channels: List[str] = field(default_factory=list)
    cooldown_period: timedelta = field(default_factory=lambda: timedelta(minutes=5))

@dataclass
class AlertEscalation:
    """Alert escalation policy"""
    escalation_id: str
    name: str
    conditions: Dict[str, Any]
    escalation_actions: List[Dict[str, Any]]
    time_thresholds: List[Tuple[timedelta, str]]  # (time, action)

class AlertManager:
    """Comprehensive alert management system"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.escalation_policies: Dict[str, AlertEscalation] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.auto_classify_enabled = True
        self.auto_escalate_enabled = True
        self.duplicate_detection_window = timedelta(minutes=30)
        self.max_alerts_per_hour = 100
        
        # Initialize with sample data
        self._initialize_sample_alerts()
        self._initialize_alert_rules()
        self._initialize_escalation_policies()
    
    def _initialize_sample_alerts(self):
        """Create sample alerts for demonstration"""
        current_time = datetime.now()
        
        # Generate sample alerts for the last 24 hours
        for hours_ago in range(24):
            alert_time = current_time - timedelta(hours=hours_ago)
            
            # Generate 1-3 alerts per hour
            for alert_num in range(random.randint(1, 3)):
                alert_type = random.choice(list(AlertType))
                category = self._get_category_for_type(alert_type)
                severity = random.choice(list(AlertSeverity))
                
                alert = Alert(
                    alert_id=f"ALERT-{int(alert_time.timestamp())}-{alert_num}",
                    title=self._generate_alert_title(alert_type),
                    description=self._generate_alert_description(alert_type),
                    category=category,
                    severity=severity,
                    alert_type=alert_type,
                    status=random.choice([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS, AlertStatus.RESOLVED]),
                    created_at=alert_time,
                    updated_at=alert_time + timedelta(minutes=random.randint(0, 60)),
                    location=(random.uniform(25.0, 25.5), random.uniform(55.0, 55.5)),
                    affected_routes=random.sample(["FR-01", "FR-02", "FR-03A", "FR-04", "FR-05"], random.randint(1, 2)),
                    affected_stops=[f"STOP-{random.randint(1, 20)}" for _ in range(random.randint(1, 3))],
                    affected_buses=[f"BUS-{random.randint(1, 10):02d}" for _ in range(random.randint(1, 2))],
                    estimated_impact_duration=timedelta(minutes=random.randint(15, 180)),
                    passenger_impact=random.randint(5, 200),
                    financial_impact=random.uniform(50, 1000),
                    source=random.choice(["system", "user", "external"]),
                    confidence_score=random.uniform(0.7, 1.0),
                    verification_status=random.choice(["unverified", "verified", "confirmed"])
                )
                
                # Set resolution for resolved alerts
                if alert.status == AlertStatus.RESOLVED:
                    alert.resolved_at = alert.updated_at + timedelta(minutes=random.randint(10, 120))
                    alert.resolution_notes = random.choice([
                        "Issue resolved by maintenance team",
                        "Traffic cleared, service restored",
                        "Passenger incident handled",
                        "System restart completed",
                        "Weather conditions improved"
                    ])
                
                self.alerts[alert.alert_id] = alert
    
    def _get_category_for_type(self, alert_type: AlertType) -> AlertCategory:
        """Map alert type to category"""
        mapping = {
            AlertType.BUS_DELAY: AlertCategory.OPERATIONAL,
            AlertType.BUS_BREAKDOWN: AlertCategory.MAINTENANCE,
            AlertType.ROUTE_DISRUPTION: AlertCategory.OPERATIONAL,
            AlertType.STATION_CLOSURE: AlertCategory.INFRASTRUCTURE,
            AlertType.WEATHER_ALERT: AlertCategory.WEATHER,
            AlertType.MAINTENANCE_REQUIRED: AlertCategory.MAINTENANCE,
            AlertType.PASSENGER_INCIDENT: AlertCategory.PASSENGER,
            AlertType.SYSTEM_FAILURE: AlertCategory.SYSTEM,
            AlertType.TRAFFIC_INCIDENT: AlertCategory.OPERATIONAL,
            AlertType.SECURITY_ALERT: AlertCategory.SAFETY
        }
        return mapping.get(alert_type, AlertCategory.OPERATIONAL)
    
    def _generate_alert_title(self, alert_type: AlertType) -> str:
        """Generate alert title based on type"""
        titles = {
            AlertType.BUS_DELAY: "Bus Service Delay",
            AlertType.BUS_BREAKDOWN: "Bus Breakdown Reported",
            AlertType.ROUTE_DISRUPTION: "Route Service Disruption",
            AlertType.STATION_CLOSURE: "Station Closure",
            AlertType.WEATHER_ALERT: "Severe Weather Warning",
            AlertType.MAINTENANCE_REQUIRED: "Maintenance Required",
            AlertType.PASSENGER_INCIDENT: "Passenger Incident",
            AlertType.SYSTEM_FAILURE: "System Failure",
            AlertType.TRAFFIC_INCIDENT: "Traffic Incident",
            AlertType.SECURITY_ALERT: "Security Alert"
        }
        return titles.get(alert_type, "System Alert")
    
    def _generate_alert_description(self, alert_type: AlertType) -> str:
        """Generate alert description based on type"""
        descriptions = {
            AlertType.BUS_DELAY: "Bus experiencing significant delay on route",
            AlertType.BUS_BREAKDOWN: "Bus has broken down and requires assistance",
            AlertType.ROUTE_DISRUPTION: "Route service disrupted due to external factors",
            AlertType.STATION_CLOSURE: "Station temporarily closed for maintenance",
            AlertType.WEATHER_ALERT: "Adverse weather conditions affecting service",
            AlertType.MAINTENANCE_REQUIRED: "Equipment maintenance required",
            AlertType.PASSENGER_INCIDENT: "Passenger incident reported on board",
            AlertType.SYSTEM_FAILURE: "Critical system failure detected",
            AlertType.TRAFFIC_INCIDENT: "Traffic incident affecting bus operations",
            AlertType.SECURITY_ALERT: "Security concern identified"
        }
        return descriptions.get(alert_type, "System alert generated")
    
    def _initialize_alert_rules(self):
        """Initialize alert generation rules"""
        rules = [
            AlertRule(
                rule_id="RULE-001",
                name="Bus Delay Threshold",
                description="Generate alert when bus delay exceeds threshold",
                category=AlertCategory.OPERATIONAL,
                alert_type=AlertType.BUS_DELAY,
                conditions={
                    "delay_minutes": 15,
                    "min_confidence": 0.7
                },
                severity_mapping={
                    "15-30": AlertSeverity.MEDIUM,
                    "30-60": AlertSeverity.HIGH,
                    "60+": AlertSeverity.CRITICAL
                },
                notification_channels=["email", "sms", "dashboard"]
            ),
            AlertRule(
                rule_id="RULE-002",
                name="System Health Check",
                description="Monitor system health and generate alerts",
                category=AlertCategory.SYSTEM,
                alert_type=AlertType.SYSTEM_FAILURE,
                conditions={
                    "cpu_usage": 90,
                    "memory_usage": 85,
                    "error_rate": 5
                },
                severity_mapping={
                    "warning": AlertSeverity.MEDIUM,
                    "critical": AlertSeverity.CRITICAL
                },
                auto_escalate=True,
                notification_channels=["email", "dashboard"]
            ),
            AlertRule(
                rule_id="RULE-003",
                name="Weather Monitoring",
                description="Monitor weather conditions and generate alerts",
                category=AlertCategory.WEATHER,
                alert_type=AlertType.WEATHER_ALERT,
                conditions={
                    "wind_speed": 50,
                    "visibility": 100,
                    "precipitation": "heavy"
                },
                severity_mapping={
                    "moderate": AlertSeverity.MEDIUM,
                    "severe": AlertSeverity.HIGH,
                    "extreme": AlertSeverity.CRITICAL
                },
                notification_channels=["email", "sms", "dashboard"]
            )
        ]
        
        for rule in rules:
            self.alert_rules[rule.rule_id] = rule
    
    def _initialize_escalation_policies(self):
        """Initialize alert escalation policies"""
        policies = [
            AlertEscalation(
                escalation_id="ESC-001",
                name="Critical Alert Escalation",
                conditions={"severity": "critical"},
                escalation_actions=[
                    {"action": "notify_manager", "delay": 0},
                    {"action": "notify_director", "delay": 15},
                    {"action": "emergency_response", "delay": 30}
                ],
                time_thresholds=[
                    (timedelta(minutes=5), "notify_supervisor"),
                    (timedelta(minutes=15), "notify_manager"),
                    (timedelta(minutes=30), "notify_director")
                ]
            ),
            AlertEscalation(
                escalation_id="ESC-002",
                name="High Priority Alert",
                conditions={"severity": "high"},
                escalation_actions=[
                    {"action": "notify_supervisor", "delay": 0},
                    {"action": "notify_manager", "delay": 30}
                ],
                time_thresholds=[
                    (timedelta(minutes=15), "notify_supervisor"),
                    (timedelta(minutes=45), "notify_manager")
                ]
            )
        ]
        
        for policy in policies:
            self.escalation_policies[policy.escalation_id] = policy
    
    def create_alert(self, title: str, description: str, alert_type: AlertType, 
                    severity: AlertSeverity, location: Optional[Tuple[float, float]] = None,
                    affected_routes: List[str] = None, affected_stops: List[str] = None,
                    affected_buses: List[str] = None, source: str = "system",
                    source_details: Dict[str, Any] = None) -> Alert:
        """Create a new alert"""
        alert_id = f"ALERT-{int(datetime.now().timestamp())}"
        
        # Auto-classify if enabled
        category = self._get_category_for_type(alert_type)
        
        # Check for duplicates
        if self._is_duplicate_alert(alert_type, location, affected_routes):
            self.logger.warning(f"Duplicate alert detected, skipping creation")
            return None
        
        alert = Alert(
            alert_id=alert_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            alert_type=alert_type,
            status=AlertStatus.NEW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            location=location,
            affected_routes=affected_routes or [],
            affected_stops=affected_stops or [],
            affected_buses=affected_buses or [],
            source=source,
            source_details=source_details or {},
            confidence_score=self._calculate_confidence(alert_type, source_details),
            verification_status="unverified"
        )
        
        self.alerts[alert_id] = alert
        
        # Auto-escalate if enabled and conditions met
        if self.auto_escalate_enabled:
            self._check_escalation(alert)
        
        # Log alert creation
        self.alert_history.append({
            "action": "created",
            "alert_id": alert_id,
            "timestamp": datetime.now(),
            "details": {"severity": severity.value, "type": alert_type.value}
        })
        
        self.logger.info(f"Alert created: {alert_id} - {title}")
        return alert
    
    def _is_duplicate_alert(self, alert_type: AlertType, location: Optional[Tuple[float, float]], 
                           affected_routes: List[str]) -> bool:
        """Check if alert is a duplicate of recent alert"""
        cutoff_time = datetime.now() - self.duplicate_detection_window
        
        for alert in self.alerts.values():
            if (alert.created_at >= cutoff_time and 
                alert.alert_type == alert_type and
                alert.status not in [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE]):
                
                # Check location proximity
                if location and alert.location:
                    distance = ((location[0] - alert.location[0])**2 + 
                              (location[1] - alert.location[1])**2)**0.5
                    if distance < 0.01:  # Very close location
                        return True
                
                # Check route overlap
                if set(affected_routes or []) & set(alert.affected_routes):
                    return True
        
        return False
    
    def _calculate_confidence(self, alert_type: AlertType, source_details: Dict[str, Any]) -> float:
        """Calculate confidence score for alert"""
        base_confidence = 0.8
        
        # Adjust based on source
        source = source_details.get("source", "system")
        if source == "system":
            base_confidence += 0.1
        elif source == "user":
            base_confidence -= 0.1
        
        # Adjust based on data quality
        data_quality = source_details.get("data_quality", 0.8)
        base_confidence *= data_quality
        
        # Adjust based on alert type reliability
        type_reliability = {
            AlertType.BUS_DELAY: 0.9,
            AlertType.BUS_BREAKDOWN: 0.95,
            AlertType.WEATHER_ALERT: 0.85,
            AlertType.SYSTEM_FAILURE: 0.9,
            AlertType.PASSENGER_INCIDENT: 0.7
        }
        
        reliability = type_reliability.get(alert_type, 0.8)
        base_confidence *= reliability
        
        return max(0.1, min(1.0, base_confidence))
    
    def _check_escalation(self, alert: Alert):
        """Check if alert should be escalated"""
        for policy in self.escalation_policies.values():
            if self._matches_escalation_conditions(alert, policy):
                self._escalate_alert(alert, policy)
    
    def _matches_escalation_conditions(self, alert: Alert, policy: AlertEscalation) -> bool:
        """Check if alert matches escalation policy conditions"""
        conditions = policy.conditions
        
        # Check severity
        if "severity" in conditions:
            if conditions["severity"] == "critical" and alert.severity != AlertSeverity.CRITICAL:
                return False
            elif conditions["severity"] == "high" and alert.severity not in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                return False
        
        return True
    
    def _escalate_alert(self, alert: Alert, policy: AlertEscalation):
        """Escalate alert according to policy"""
        for time_threshold, action in policy.time_thresholds:
            if datetime.now() - alert.created_at >= time_threshold:
                self._execute_escalation_action(alert, action)
    
    def _execute_escalation_action(self, alert: Alert, action: str):
        """Execute escalation action"""
        if action == "notify_supervisor":
            self._send_notification(alert, "supervisor")
        elif action == "notify_manager":
            self._send_notification(alert, "manager")
        elif action == "notify_director":
            self._send_notification(alert, "director")
        elif action == "emergency_response":
            self._initiate_emergency_response(alert)
        
        self.logger.info(f"Alert {alert.alert_id} escalated: {action}")
    
    def _send_notification(self, alert: Alert, recipient: str):
        """Send notification to recipient"""
        # In a real system, this would send email, SMS, push notification, etc.
        notification = {
            "alert_id": alert.alert_id,
            "recipient": recipient,
            "message": f"Alert: {alert.title} - {alert.description}",
            "severity": alert.severity.value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log notification
        self.alert_history.append({
            "action": "notification_sent",
            "alert_id": alert.alert_id,
            "timestamp": datetime.now(),
            "details": notification
        })
    
    def _initiate_emergency_response(self, alert: Alert):
        """Initiate emergency response procedures"""
        emergency_response = {
            "alert_id": alert.alert_id,
            "response_team": "emergency",
            "action": "response_initiated",
            "timestamp": datetime.now().isoformat()
        }
        
        # Log emergency response
        self.alert_history.append({
            "action": "emergency_response",
            "alert_id": alert.alert_id,
            "timestamp": datetime.now(),
            "details": emergency_response
        })
    
    def update_alert_status(self, alert_id: str, status: AlertStatus, 
                           assigned_to: Optional[str] = None, 
                           resolution_notes: Optional[str] = None,
                           updated_by: str = "system") -> bool:
        """Update alert status"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        old_status = alert.status
        alert.status = status
        alert.updated_at = datetime.now()
        
        if assigned_to:
            alert.assigned_to = assigned_to
        
        if resolution_notes:
            alert.resolution_notes = resolution_notes
        
        if status == AlertStatus.RESOLVED:
            alert.resolved_at = datetime.now()
            alert.resolved_by = updated_by
        
        # Log status change
        self.alert_history.append({
            "action": "status_updated",
            "alert_id": alert_id,
            "timestamp": datetime.now(),
            "details": {
                "old_status": old_status.value,
                "new_status": status.value,
                "updated_by": updated_by
            }
        })
        
        self.logger.info(f"Alert {alert_id} status updated to {status.value}")
        return True
    
    def get_alerts(self, status: Optional[AlertStatus] = None, 
                  severity: Optional[AlertSeverity] = None,
                  category: Optional[AlertCategory] = None,
                  time_period: Optional[int] = None) -> List[Alert]:
        """Get alerts with optional filtering"""
        alerts = list(self.alerts.values())
        
        # Filter by time period
        if time_period:
            cutoff_time = datetime.now() - timedelta(hours=time_period)
            alerts = [a for a in alerts if a.created_at >= cutoff_time]
        
        # Filter by status
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Filter by category
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        # Sort by creation time (most recent first)
        alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        return alerts
    
    def get_alert_statistics(self, time_period: int = 24) -> Dict[str, Any]:
        """Get alert statistics for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=time_period)
        recent_alerts = [a for a in self.alerts.values() if a.created_at >= cutoff_time]
        
        if not recent_alerts:
            return {"error": "No alerts in specified time period"}
        
        # Count by status
        status_counts = {}
        for alert in recent_alerts:
            status_counts[alert.status.value] = status_counts.get(alert.status.value, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for alert in recent_alerts:
            severity_counts[alert.severity.value] = severity_counts.get(alert.severity.value, 0) + 1
        
        # Count by category
        category_counts = {}
        for alert in recent_alerts:
            category_counts[alert.category.value] = category_counts.get(alert.category.value, 0) + 1
        
        # Count by type
        type_counts = {}
        for alert in recent_alerts:
            type_counts[alert.alert_type.value] = type_counts.get(alert.alert_type.value, 0) + 1
        
        # Resolution metrics
        resolved_alerts = [a for a in recent_alerts if a.status == AlertStatus.RESOLVED]
        resolution_times = []
        for alert in resolved_alerts:
            if alert.resolved_at:
                resolution_time = (alert.resolved_at - alert.created_at).total_seconds() / 60  # minutes
                resolution_times.append(resolution_time)
        
        avg_resolution_time = statistics.mean(resolution_times) if resolution_times else 0
        
        # Impact metrics
        total_passenger_impact = sum(a.passenger_impact for a in recent_alerts)
        total_financial_impact = sum(a.financial_impact for a in recent_alerts)
        
        return {
            "period_hours": time_period,
            "total_alerts": len(recent_alerts),
            "status_breakdown": status_counts,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "type_breakdown": type_counts,
            "resolution_metrics": {
                "resolved_count": len(resolved_alerts),
                "resolution_rate": (len(resolved_alerts) / len(recent_alerts)) * 100 if recent_alerts else 0,
                "average_resolution_time_minutes": avg_resolution_time
            },
            "impact_metrics": {
                "total_passenger_impact": total_passenger_impact,
                "total_financial_impact": total_financial_impact,
                "average_passenger_impact": total_passenger_impact / len(recent_alerts) if recent_alerts else 0,
                "average_financial_impact": total_financial_impact / len(recent_alerts) if recent_alerts else 0
            },
            "active_alerts": len([a for a in recent_alerts if a.status in [AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS]]),
            "critical_alerts": len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL and a.status != AlertStatus.RESOLVED])
        }
    
    def get_alert_analytics(self, time_period: int = 168) -> Dict[str, Any]:  # Default 1 week
        """Get comprehensive alert analytics"""
        cutoff_time = datetime.now() - timedelta(hours=time_period)
        recent_alerts = [a for a in self.alerts.values() if a.created_at >= cutoff_time]
        
        if not recent_alerts:
            return {"error": "No alerts in specified time period"}
        
        # Time-based analysis
        hourly_distribution = {}
        daily_distribution = {}
        
        for alert in recent_alerts:
            hour = alert.created_at.hour
            day = alert.created_at.weekday()
            
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            daily_distribution[day] = daily_distribution.get(day, 0) + 1
        
        # Trend analysis
        alert_trend = self._calculate_alert_trend(recent_alerts)
        
        # Top alert types
        type_frequency = {}
        for alert in recent_alerts:
            type_frequency[alert.alert_type.value] = type_frequency.get(alert.alert_type.value, 0) + 1
        
        top_alert_types = sorted(type_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Resolution performance by category
        category_resolution = {}
        for alert in recent_alerts:
            category = alert.category.value
            if category not in category_resolution:
                category_resolution[category] = {"total": 0, "resolved": 0, "avg_time": []}
            
            category_resolution[category]["total"] += 1
            if alert.status == AlertStatus.RESOLVED and alert.resolved_at:
                category_resolution[category]["resolved"] += 1
                resolution_time = (alert.resolved_at - alert.created_at).total_seconds() / 60
                category_resolution[category]["avg_time"].append(resolution_time)
        
        # Calculate averages
        for category in category_resolution:
            times = category_resolution[category]["avg_time"]
            category_resolution[category]["avg_resolution_time"] = statistics.mean(times) if times else 0
            category_resolution[category]["resolution_rate"] = (category_resolution[category]["resolved"] / category_resolution[category]["total"]) * 100
        
        return {
            "period_hours": time_period,
            "total_alerts": len(recent_alerts),
            "temporal_analysis": {
                "hourly_distribution": hourly_distribution,
                "daily_distribution": daily_distribution,
                "peak_hours": sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3],
                "peak_days": sorted(daily_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            "trend_analysis": alert_trend,
            "top_alert_types": top_alert_types,
            "category_performance": category_resolution,
            "recommendations": self._generate_alert_recommendations(recent_alerts)
        }
    
    def _calculate_alert_trend(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Calculate alert trends over time"""
        if len(alerts) < 10:
            return {"insufficient_data": "Need at least 10 alerts for trend analysis"}
        
        # Sort by creation time
        sorted_alerts = sorted(alerts, key=lambda a: a.created_at)
        
        # Split into two halves
        mid_point = len(sorted_alerts) // 2
        early_period = sorted_alerts[:mid_point]
        recent_period = sorted_alerts[mid_point:]
        
        # Calculate alert rates
        early_duration = (early_period[-1].created_at - early_period[0].created_at).total_seconds() / 3600
        recent_duration = (recent_period[-1].created_at - recent_period[0].created_at).total_seconds() / 3600
        
        early_rate = len(early_period) / early_duration if early_duration > 0 else 0
        recent_rate = len(recent_period) / recent_duration if recent_duration > 0 else 0
        
        # Determine trend
        if recent_rate > early_rate * 1.2:
            trend = "increasing"
        elif recent_rate < early_rate * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"
        
        change_percentage = ((recent_rate - early_rate) / early_rate) * 100 if early_rate > 0 else 0
        
        return {
            "trend": trend,
            "change_percentage": change_percentage,
            "early_rate_per_hour": early_rate,
            "recent_rate_per_hour": recent_rate
        }
    
    def _generate_alert_recommendations(self, alerts: List[Alert]) -> List[str]:
        """Generate recommendations based on alert patterns"""
        recommendations = []
        
        # Check for high volume of critical alerts
        critical_count = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        if critical_count > len(alerts) * 0.2:
            recommendations.append("High volume of critical alerts - review system reliability and preventive maintenance")
        
        # Check for slow resolution times
        resolved_alerts = [a for a in alerts if a.status == AlertStatus.RESOLVED and a.resolved_at]
        if resolved_alerts:
            avg_resolution_time = statistics.mean([(a.resolved_at - a.created_at).total_seconds() / 60 for a in resolved_alerts])
            if avg_resolution_time > 120:  # 2 hours
                recommendations.append("Alert resolution times are above target - consider improving response procedures")
        
        # Check for common alert types
        type_counts = {}
        for alert in alerts:
            type_counts[alert.alert_type.value] = type_counts.get(alert.alert_type.value, 0) + 1
        
        most_common_type = max(type_counts.items(), key=lambda x: x[1]) if type_counts else None
        if most_common_type and most_common_type[1] > len(alerts) * 0.3:
            recommendations.append(f"High frequency of {most_common_type[0]} alerts - investigate root cause and preventive measures")
        
        # Check for unverified alerts
        unverified_count = len([a for a in alerts if a.verification_status == "unverified"])
        if unverified_count > len(alerts) * 0.5:
            recommendations.append("Many alerts remain unverified - improve alert verification processes")
        
        if not recommendations:
            recommendations.append("Alert patterns are within normal parameters - continue current monitoring")
        
        return recommendations
    
    def get_alert_details(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return None
        
        # Get related alerts
        related_alerts = []
        for related_id in alert.related_alerts:
            if related_id in self.alerts:
                related_alerts.append({
                    "alert_id": related_id,
                    "title": self.alerts[related_id].title,
                    "status": self.alerts[related_id].status.value,
                    "severity": self.alerts[related_id].severity.value
                })
        
        # Get alert history
        alert_history = [h for h in self.alert_history if h["alert_id"] == alert_id]
        
        return {
            "alert": {
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
                "estimated_impact_duration": str(alert.estimated_impact_duration) if alert.estimated_impact_duration else None,
                "passenger_impact": alert.passenger_impact,
                "financial_impact": alert.financial_impact,
                "source": alert.source,
                "confidence_score": alert.confidence_score,
                "verification_status": alert.verification_status,
                "assigned_to": alert.assigned_to,
                "resolution_notes": alert.resolution_notes,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "resolved_by": alert.resolved_by,
                "tags": alert.tags
            },
            "related_alerts": related_alerts,
            "history": alert_history,
            "escalation_actions": self._get_alert_escalation_actions(alert)
        }
    
    def _get_alert_escalation_actions(self, alert: Alert) -> List[Dict[str, Any]]:
        """Get escalation actions for alert"""
        actions = []
        
        for policy in self.escalation_policies.values():
            if self._matches_escalation_conditions(alert, policy):
                for time_threshold, action in policy.time_thresholds:
                    if datetime.now() - alert.created_at >= time_threshold:
                        actions.append({
                            "action": action,
                            "threshold": str(time_threshold),
                            "executed": True,
                            "executed_at": alert.created_at + time_threshold
                        })
                    else:
                        actions.append({
                            "action": action,
                            "threshold": str(time_threshold),
                            "executed": False,
                            "scheduled_for": alert.created_at + time_threshold
                        })
        
        return actions
=======
"""
alert_management.py
====================
NEW FILE - Alert Management System with Classification
Comprehensive alert system for delays, disruptions, and maintenance with intelligent classification

Features:
- Alert classification and categorization
- Multi-level severity assessment
- Alert routing and notification
- Alert resolution tracking
- Predictive alert generation
- Alert analytics and reporting
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json
import random

class AlertCategory(Enum):
    OPERATIONAL = "operational"
    SAFETY = "safety"
    MAINTENANCE = "maintenance"
    WEATHER = "weather"
    INFRASTRUCTURE = "infrastructure"
    PASSENGER = "passenger"
    SYSTEM = "system"
    EMERGENCY = "emergency"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class AlertType(Enum):
    BUS_DELAY = "bus_delay"
    BUS_BREAKDOWN = "bus_breakdown"
    ROUTE_DISRUPTION = "route_disruption"
    STATION_CLOSURE = "station_closure"
    WEATHER_ALERT = "weather_alert"
    MAINTENANCE_REQUIRED = "maintenance_required"
    PASSENGER_INCIDENT = "passenger_incident"
    SYSTEM_FAILURE = "system_failure"
    TRAFFIC_INCIDENT = "traffic_incident"
    SECURITY_ALERT = "security_alert"

@dataclass
class Alert:
    """Comprehensive alert data structure"""
    alert_id: str
    title: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    alert_type: AlertType
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    location: Optional[Tuple[float, float]] = None
    affected_routes: List[str] = field(default_factory=list)
    affected_stops: List[str] = field(default_factory=list)
    affected_buses: List[str] = field(default_factory=list)
    estimated_impact_duration: Optional[timedelta] = None
    passenger_impact: int = 0
    financial_impact: float = 0.0
    source: str = "system"  # system, user, external
    source_details: Dict[str, Any] = field(default_factory=dict)
    resolution_notes: str = ""
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    related_alerts: List[str] = field(default_factory=list)
    confidence_score: float = 1.0  # 0.0 - 1.0
    verification_status: str = "unverified"  # unverified, verified, confirmed

@dataclass
class AlertRule:
    """Alert generation rule"""
    rule_id: str
    name: str
    description: str
    category: AlertCategory
    alert_type: AlertType
    conditions: Dict[str, Any]
    severity_mapping: Dict[str, AlertSeverity]
    enabled: bool = True
    auto_escalate: bool = False
    notification_channels: List[str] = field(default_factory=list)
    cooldown_period: timedelta = field(default_factory=lambda: timedelta(minutes=5))

@dataclass
class AlertEscalation:
    """Alert escalation policy"""
    escalation_id: str
    name: str
    conditions: Dict[str, Any]
    escalation_actions: List[Dict[str, Any]]
    time_thresholds: List[Tuple[timedelta, str]]  # (time, action)

class AlertManager:
    """Comprehensive alert management system"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.escalation_policies: Dict[str, AlertEscalation] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.auto_classify_enabled = True
        self.auto_escalate_enabled = True
        self.duplicate_detection_window = timedelta(minutes=30)
        self.max_alerts_per_hour = 100
        
        # Initialize with sample data
        self._initialize_sample_alerts()
        self._initialize_alert_rules()
        self._initialize_escalation_policies()
    
    def _initialize_sample_alerts(self):
        """Create sample alerts for demonstration"""
        current_time = datetime.now()
        
        # Generate sample alerts for the last 24 hours
        for hours_ago in range(24):
            alert_time = current_time - timedelta(hours=hours_ago)
            
            # Generate 1-3 alerts per hour
            for alert_num in range(random.randint(1, 3)):
                alert_type = random.choice(list(AlertType))
                category = self._get_category_for_type(alert_type)
                severity = random.choice(list(AlertSeverity))
                
                alert = Alert(
                    alert_id=f"ALERT-{int(alert_time.timestamp())}-{alert_num}",
                    title=self._generate_alert_title(alert_type),
                    description=self._generate_alert_description(alert_type),
                    category=category,
                    severity=severity,
                    alert_type=alert_type,
                    status=random.choice([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS, AlertStatus.RESOLVED]),
                    created_at=alert_time,
                    updated_at=alert_time + timedelta(minutes=random.randint(0, 60)),
                    location=(random.uniform(25.0, 25.5), random.uniform(55.0, 55.5)),
                    affected_routes=random.sample(["FR-01", "FR-02", "FR-03A", "FR-04", "FR-05"], random.randint(1, 2)),
                    affected_stops=[f"STOP-{random.randint(1, 20)}" for _ in range(random.randint(1, 3))],
                    affected_buses=[f"BUS-{random.randint(1, 10):02d}" for _ in range(random.randint(1, 2))],
                    estimated_impact_duration=timedelta(minutes=random.randint(15, 180)),
                    passenger_impact=random.randint(5, 200),
                    financial_impact=random.uniform(50, 1000),
                    source=random.choice(["system", "user", "external"]),
                    confidence_score=random.uniform(0.7, 1.0),
                    verification_status=random.choice(["unverified", "verified", "confirmed"])
                )
                
                # Set resolution for resolved alerts
                if alert.status == AlertStatus.RESOLVED:
                    alert.resolved_at = alert.updated_at + timedelta(minutes=random.randint(10, 120))
                    alert.resolution_notes = random.choice([
                        "Issue resolved by maintenance team",
                        "Traffic cleared, service restored",
                        "Passenger incident handled",
                        "System restart completed",
                        "Weather conditions improved"
                    ])
                
                self.alerts[alert.alert_id] = alert
    
    def _get_category_for_type(self, alert_type: AlertType) -> AlertCategory:
        """Map alert type to category"""
        mapping = {
            AlertType.BUS_DELAY: AlertCategory.OPERATIONAL,
            AlertType.BUS_BREAKDOWN: AlertCategory.MAINTENANCE,
            AlertType.ROUTE_DISRUPTION: AlertCategory.OPERATIONAL,
            AlertType.STATION_CLOSURE: AlertCategory.INFRASTRUCTURE,
            AlertType.WEATHER_ALERT: AlertCategory.WEATHER,
            AlertType.MAINTENANCE_REQUIRED: AlertCategory.MAINTENANCE,
            AlertType.PASSENGER_INCIDENT: AlertCategory.PASSENGER,
            AlertType.SYSTEM_FAILURE: AlertCategory.SYSTEM,
            AlertType.TRAFFIC_INCIDENT: AlertCategory.OPERATIONAL,
            AlertType.SECURITY_ALERT: AlertCategory.SAFETY
        }
        return mapping.get(alert_type, AlertCategory.OPERATIONAL)
    
    def _generate_alert_title(self, alert_type: AlertType) -> str:
        """Generate alert title based on type"""
        titles = {
            AlertType.BUS_DELAY: "Bus Service Delay",
            AlertType.BUS_BREAKDOWN: "Bus Breakdown Reported",
            AlertType.ROUTE_DISRUPTION: "Route Service Disruption",
            AlertType.STATION_CLOSURE: "Station Closure",
            AlertType.WEATHER_ALERT: "Severe Weather Warning",
            AlertType.MAINTENANCE_REQUIRED: "Maintenance Required",
            AlertType.PASSENGER_INCIDENT: "Passenger Incident",
            AlertType.SYSTEM_FAILURE: "System Failure",
            AlertType.TRAFFIC_INCIDENT: "Traffic Incident",
            AlertType.SECURITY_ALERT: "Security Alert"
        }
        return titles.get(alert_type, "System Alert")
    
    def _generate_alert_description(self, alert_type: AlertType) -> str:
        """Generate alert description based on type"""
        descriptions = {
            AlertType.BUS_DELAY: "Bus experiencing significant delay on route",
            AlertType.BUS_BREAKDOWN: "Bus has broken down and requires assistance",
            AlertType.ROUTE_DISRUPTION: "Route service disrupted due to external factors",
            AlertType.STATION_CLOSURE: "Station temporarily closed for maintenance",
            AlertType.WEATHER_ALERT: "Adverse weather conditions affecting service",
            AlertType.MAINTENANCE_REQUIRED: "Equipment maintenance required",
            AlertType.PASSENGER_INCIDENT: "Passenger incident reported on board",
            AlertType.SYSTEM_FAILURE: "Critical system failure detected",
            AlertType.TRAFFIC_INCIDENT: "Traffic incident affecting bus operations",
            AlertType.SECURITY_ALERT: "Security concern identified"
        }
        return descriptions.get(alert_type, "System alert generated")
    
    def _initialize_alert_rules(self):
        """Initialize alert generation rules"""
        rules = [
            AlertRule(
                rule_id="RULE-001",
                name="Bus Delay Threshold",
                description="Generate alert when bus delay exceeds threshold",
                category=AlertCategory.OPERATIONAL,
                alert_type=AlertType.BUS_DELAY,
                conditions={
                    "delay_minutes": 15,
                    "min_confidence": 0.7
                },
                severity_mapping={
                    "15-30": AlertSeverity.MEDIUM,
                    "30-60": AlertSeverity.HIGH,
                    "60+": AlertSeverity.CRITICAL
                },
                notification_channels=["email", "sms", "dashboard"]
            ),
            AlertRule(
                rule_id="RULE-002",
                name="System Health Check",
                description="Monitor system health and generate alerts",
                category=AlertCategory.SYSTEM,
                alert_type=AlertType.SYSTEM_FAILURE,
                conditions={
                    "cpu_usage": 90,
                    "memory_usage": 85,
                    "error_rate": 5
                },
                severity_mapping={
                    "warning": AlertSeverity.MEDIUM,
                    "critical": AlertSeverity.CRITICAL
                },
                auto_escalate=True,
                notification_channels=["email", "dashboard"]
            ),
            AlertRule(
                rule_id="RULE-003",
                name="Weather Monitoring",
                description="Monitor weather conditions and generate alerts",
                category=AlertCategory.WEATHER,
                alert_type=AlertType.WEATHER_ALERT,
                conditions={
                    "wind_speed": 50,
                    "visibility": 100,
                    "precipitation": "heavy"
                },
                severity_mapping={
                    "moderate": AlertSeverity.MEDIUM,
                    "severe": AlertSeverity.HIGH,
                    "extreme": AlertSeverity.CRITICAL
                },
                notification_channels=["email", "sms", "dashboard"]
            )
        ]
        
        for rule in rules:
            self.alert_rules[rule.rule_id] = rule
    
    def _initialize_escalation_policies(self):
        """Initialize alert escalation policies"""
        policies = [
            AlertEscalation(
                escalation_id="ESC-001",
                name="Critical Alert Escalation",
                conditions={"severity": "critical"},
                escalation_actions=[
                    {"action": "notify_manager", "delay": 0},
                    {"action": "notify_director", "delay": 15},
                    {"action": "emergency_response", "delay": 30}
                ],
                time_thresholds=[
                    (timedelta(minutes=5), "notify_supervisor"),
                    (timedelta(minutes=15), "notify_manager"),
                    (timedelta(minutes=30), "notify_director")
                ]
            ),
            AlertEscalation(
                escalation_id="ESC-002",
                name="High Priority Alert",
                conditions={"severity": "high"},
                escalation_actions=[
                    {"action": "notify_supervisor", "delay": 0},
                    {"action": "notify_manager", "delay": 30}
                ],
                time_thresholds=[
                    (timedelta(minutes=15), "notify_supervisor"),
                    (timedelta(minutes=45), "notify_manager")
                ]
            )
        ]
        
        for policy in policies:
            self.escalation_policies[policy.escalation_id] = policy
    
    def create_alert(self, title: str, description: str, alert_type: AlertType, 
                    severity: AlertSeverity, location: Optional[Tuple[float, float]] = None,
                    affected_routes: List[str] = None, affected_stops: List[str] = None,
                    affected_buses: List[str] = None, source: str = "system",
                    source_details: Dict[str, Any] = None) -> Alert:
        """Create a new alert"""
        alert_id = f"ALERT-{int(datetime.now().timestamp())}"
        
        # Auto-classify if enabled
        category = self._get_category_for_type(alert_type)
        
        # Check for duplicates
        if self._is_duplicate_alert(alert_type, location, affected_routes):
            self.logger.warning(f"Duplicate alert detected, skipping creation")
            return None
        
        alert = Alert(
            alert_id=alert_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            alert_type=alert_type,
            status=AlertStatus.NEW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            location=location,
            affected_routes=affected_routes or [],
            affected_stops=affected_stops or [],
            affected_buses=affected_buses or [],
            source=source,
            source_details=source_details or {},
            confidence_score=self._calculate_confidence(alert_type, source_details),
            verification_status="unverified"
        )
        
        self.alerts[alert_id] = alert
        
        # Auto-escalate if enabled and conditions met
        if self.auto_escalate_enabled:
            self._check_escalation(alert)
        
        # Log alert creation
        self.alert_history.append({
            "action": "created",
            "alert_id": alert_id,
            "timestamp": datetime.now(),
            "details": {"severity": severity.value, "type": alert_type.value}
        })
        
        self.logger.info(f"Alert created: {alert_id} - {title}")
        return alert
    
    def _is_duplicate_alert(self, alert_type: AlertType, location: Optional[Tuple[float, float]], 
                           affected_routes: List[str]) -> bool:
        """Check if alert is a duplicate of recent alert"""
        cutoff_time = datetime.now() - self.duplicate_detection_window
        
        for alert in self.alerts.values():
            if (alert.created_at >= cutoff_time and 
                alert.alert_type == alert_type and
                alert.status not in [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE]):
                
                # Check location proximity
                if location and alert.location:
                    distance = ((location[0] - alert.location[0])**2 + 
                              (location[1] - alert.location[1])**2)**0.5
                    if distance < 0.01:  # Very close location
                        return True
                
                # Check route overlap
                if set(affected_routes or []) & set(alert.affected_routes):
                    return True
        
        return False
    
    def _calculate_confidence(self, alert_type: AlertType, source_details: Dict[str, Any]) -> float:
        """Calculate confidence score for alert"""
        base_confidence = 0.8
        
        # Adjust based on source
        source = source_details.get("source", "system")
        if source == "system":
            base_confidence += 0.1
        elif source == "user":
            base_confidence -= 0.1
        
        # Adjust based on data quality
        data_quality = source_details.get("data_quality", 0.8)
        base_confidence *= data_quality
        
        # Adjust based on alert type reliability
        type_reliability = {
            AlertType.BUS_DELAY: 0.9,
            AlertType.BUS_BREAKDOWN: 0.95,
            AlertType.WEATHER_ALERT: 0.85,
            AlertType.SYSTEM_FAILURE: 0.9,
            AlertType.PASSENGER_INCIDENT: 0.7
        }
        
        reliability = type_reliability.get(alert_type, 0.8)
        base_confidence *= reliability
        
        return max(0.1, min(1.0, base_confidence))
    
    def _check_escalation(self, alert: Alert):
        """Check if alert should be escalated"""
        for policy in self.escalation_policies.values():
            if self._matches_escalation_conditions(alert, policy):
                self._escalate_alert(alert, policy)
    
    def _matches_escalation_conditions(self, alert: Alert, policy: AlertEscalation) -> bool:
        """Check if alert matches escalation policy conditions"""
        conditions = policy.conditions
        
        # Check severity
        if "severity" in conditions:
            if conditions["severity"] == "critical" and alert.severity != AlertSeverity.CRITICAL:
                return False
            elif conditions["severity"] == "high" and alert.severity not in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                return False
        
        return True
    
    def _escalate_alert(self, alert: Alert, policy: AlertEscalation):
        """Escalate alert according to policy"""
        for time_threshold, action in policy.time_thresholds:
            if datetime.now() - alert.created_at >= time_threshold:
                self._execute_escalation_action(alert, action)
    
    def _execute_escalation_action(self, alert: Alert, action: str):
        """Execute escalation action"""
        if action == "notify_supervisor":
            self._send_notification(alert, "supervisor")
        elif action == "notify_manager":
            self._send_notification(alert, "manager")
        elif action == "notify_director":
            self._send_notification(alert, "director")
        elif action == "emergency_response":
            self._initiate_emergency_response(alert)
        
        self.logger.info(f"Alert {alert.alert_id} escalated: {action}")
    
    def _send_notification(self, alert: Alert, recipient: str):
        """Send notification to recipient"""
        # In a real system, this would send email, SMS, push notification, etc.
        notification = {
            "alert_id": alert.alert_id,
            "recipient": recipient,
            "message": f"Alert: {alert.title} - {alert.description}",
            "severity": alert.severity.value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log notification
        self.alert_history.append({
            "action": "notification_sent",
            "alert_id": alert.alert_id,
            "timestamp": datetime.now(),
            "details": notification
        })
    
    def _initiate_emergency_response(self, alert: Alert):
        """Initiate emergency response procedures"""
        emergency_response = {
            "alert_id": alert.alert_id,
            "response_team": "emergency",
            "action": "response_initiated",
            "timestamp": datetime.now().isoformat()
        }
        
        # Log emergency response
        self.alert_history.append({
            "action": "emergency_response",
            "alert_id": alert.alert_id,
            "timestamp": datetime.now(),
            "details": emergency_response
        })
    
    def update_alert_status(self, alert_id: str, status: AlertStatus, 
                           assigned_to: Optional[str] = None, 
                           resolution_notes: Optional[str] = None,
                           updated_by: str = "system") -> bool:
        """Update alert status"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        old_status = alert.status
        alert.status = status
        alert.updated_at = datetime.now()
        
        if assigned_to:
            alert.assigned_to = assigned_to
        
        if resolution_notes:
            alert.resolution_notes = resolution_notes
        
        if status == AlertStatus.RESOLVED:
            alert.resolved_at = datetime.now()
            alert.resolved_by = updated_by
        
        # Log status change
        self.alert_history.append({
            "action": "status_updated",
            "alert_id": alert_id,
            "timestamp": datetime.now(),
            "details": {
                "old_status": old_status.value,
                "new_status": status.value,
                "updated_by": updated_by
            }
        })
        
        self.logger.info(f"Alert {alert_id} status updated to {status.value}")
        return True
    
    def get_alerts(self, status: Optional[AlertStatus] = None, 
                  severity: Optional[AlertSeverity] = None,
                  category: Optional[AlertCategory] = None,
                  time_period: Optional[int] = None) -> List[Alert]:
        """Get alerts with optional filtering"""
        alerts = list(self.alerts.values())
        
        # Filter by time period
        if time_period:
            cutoff_time = datetime.now() - timedelta(hours=time_period)
            alerts = [a for a in alerts if a.created_at >= cutoff_time]
        
        # Filter by status
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Filter by category
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        # Sort by creation time (most recent first)
        alerts.sort(key=lambda a: a.created_at, reverse=True)
        
        return alerts
    
    def get_alert_statistics(self, time_period: int = 24) -> Dict[str, Any]:
        """Get alert statistics for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=time_period)
        recent_alerts = [a for a in self.alerts.values() if a.created_at >= cutoff_time]
        
        if not recent_alerts:
            return {"error": "No alerts in specified time period"}
        
        # Count by status
        status_counts = {}
        for alert in recent_alerts:
            status_counts[alert.status.value] = status_counts.get(alert.status.value, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for alert in recent_alerts:
            severity_counts[alert.severity.value] = severity_counts.get(alert.severity.value, 0) + 1
        
        # Count by category
        category_counts = {}
        for alert in recent_alerts:
            category_counts[alert.category.value] = category_counts.get(alert.category.value, 0) + 1
        
        # Count by type
        type_counts = {}
        for alert in recent_alerts:
            type_counts[alert.alert_type.value] = type_counts.get(alert.alert_type.value, 0) + 1
        
        # Resolution metrics
        resolved_alerts = [a for a in recent_alerts if a.status == AlertStatus.RESOLVED]
        resolution_times = []
        for alert in resolved_alerts:
            if alert.resolved_at:
                resolution_time = (alert.resolved_at - alert.created_at).total_seconds() / 60  # minutes
                resolution_times.append(resolution_time)
        
        avg_resolution_time = statistics.mean(resolution_times) if resolution_times else 0
        
        # Impact metrics
        total_passenger_impact = sum(a.passenger_impact for a in recent_alerts)
        total_financial_impact = sum(a.financial_impact for a in recent_alerts)
        
        return {
            "period_hours": time_period,
            "total_alerts": len(recent_alerts),
            "status_breakdown": status_counts,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "type_breakdown": type_counts,
            "resolution_metrics": {
                "resolved_count": len(resolved_alerts),
                "resolution_rate": (len(resolved_alerts) / len(recent_alerts)) * 100 if recent_alerts else 0,
                "average_resolution_time_minutes": avg_resolution_time
            },
            "impact_metrics": {
                "total_passenger_impact": total_passenger_impact,
                "total_financial_impact": total_financial_impact,
                "average_passenger_impact": total_passenger_impact / len(recent_alerts) if recent_alerts else 0,
                "average_financial_impact": total_financial_impact / len(recent_alerts) if recent_alerts else 0
            },
            "active_alerts": len([a for a in recent_alerts if a.status in [AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS]]),
            "critical_alerts": len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL and a.status != AlertStatus.RESOLVED])
        }
    
    def get_alert_analytics(self, time_period: int = 168) -> Dict[str, Any]:  # Default 1 week
        """Get comprehensive alert analytics"""
        cutoff_time = datetime.now() - timedelta(hours=time_period)
        recent_alerts = [a for a in self.alerts.values() if a.created_at >= cutoff_time]
        
        if not recent_alerts:
            return {"error": "No alerts in specified time period"}
        
        # Time-based analysis
        hourly_distribution = {}
        daily_distribution = {}
        
        for alert in recent_alerts:
            hour = alert.created_at.hour
            day = alert.created_at.weekday()
            
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            daily_distribution[day] = daily_distribution.get(day, 0) + 1
        
        # Trend analysis
        alert_trend = self._calculate_alert_trend(recent_alerts)
        
        # Top alert types
        type_frequency = {}
        for alert in recent_alerts:
            type_frequency[alert.alert_type.value] = type_frequency.get(alert.alert_type.value, 0) + 1
        
        top_alert_types = sorted(type_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Resolution performance by category
        category_resolution = {}
        for alert in recent_alerts:
            category = alert.category.value
            if category not in category_resolution:
                category_resolution[category] = {"total": 0, "resolved": 0, "avg_time": []}
            
            category_resolution[category]["total"] += 1
            if alert.status == AlertStatus.RESOLVED and alert.resolved_at:
                category_resolution[category]["resolved"] += 1
                resolution_time = (alert.resolved_at - alert.created_at).total_seconds() / 60
                category_resolution[category]["avg_time"].append(resolution_time)
        
        # Calculate averages
        for category in category_resolution:
            times = category_resolution[category]["avg_time"]
            category_resolution[category]["avg_resolution_time"] = statistics.mean(times) if times else 0
            category_resolution[category]["resolution_rate"] = (category_resolution[category]["resolved"] / category_resolution[category]["total"]) * 100
        
        return {
            "period_hours": time_period,
            "total_alerts": len(recent_alerts),
            "temporal_analysis": {
                "hourly_distribution": hourly_distribution,
                "daily_distribution": daily_distribution,
                "peak_hours": sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3],
                "peak_days": sorted(daily_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            "trend_analysis": alert_trend,
            "top_alert_types": top_alert_types,
            "category_performance": category_resolution,
            "recommendations": self._generate_alert_recommendations(recent_alerts)
        }
    
    def _calculate_alert_trend(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Calculate alert trends over time"""
        if len(alerts) < 10:
            return {"insufficient_data": "Need at least 10 alerts for trend analysis"}
        
        # Sort by creation time
        sorted_alerts = sorted(alerts, key=lambda a: a.created_at)
        
        # Split into two halves
        mid_point = len(sorted_alerts) // 2
        early_period = sorted_alerts[:mid_point]
        recent_period = sorted_alerts[mid_point:]
        
        # Calculate alert rates
        early_duration = (early_period[-1].created_at - early_period[0].created_at).total_seconds() / 3600
        recent_duration = (recent_period[-1].created_at - recent_period[0].created_at).total_seconds() / 3600
        
        early_rate = len(early_period) / early_duration if early_duration > 0 else 0
        recent_rate = len(recent_period) / recent_duration if recent_duration > 0 else 0
        
        # Determine trend
        if recent_rate > early_rate * 1.2:
            trend = "increasing"
        elif recent_rate < early_rate * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"
        
        change_percentage = ((recent_rate - early_rate) / early_rate) * 100 if early_rate > 0 else 0
        
        return {
            "trend": trend,
            "change_percentage": change_percentage,
            "early_rate_per_hour": early_rate,
            "recent_rate_per_hour": recent_rate
        }
    
    def _generate_alert_recommendations(self, alerts: List[Alert]) -> List[str]:
        """Generate recommendations based on alert patterns"""
        recommendations = []
        
        # Check for high volume of critical alerts
        critical_count = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        if critical_count > len(alerts) * 0.2:
            recommendations.append("High volume of critical alerts - review system reliability and preventive maintenance")
        
        # Check for slow resolution times
        resolved_alerts = [a for a in alerts if a.status == AlertStatus.RESOLVED and a.resolved_at]
        if resolved_alerts:
            avg_resolution_time = statistics.mean([(a.resolved_at - a.created_at).total_seconds() / 60 for a in resolved_alerts])
            if avg_resolution_time > 120:  # 2 hours
                recommendations.append("Alert resolution times are above target - consider improving response procedures")
        
        # Check for common alert types
        type_counts = {}
        for alert in alerts:
            type_counts[alert.alert_type.value] = type_counts.get(alert.alert_type.value, 0) + 1
        
        most_common_type = max(type_counts.items(), key=lambda x: x[1]) if type_counts else None
        if most_common_type and most_common_type[1] > len(alerts) * 0.3:
            recommendations.append(f"High frequency of {most_common_type[0]} alerts - investigate root cause and preventive measures")
        
        # Check for unverified alerts
        unverified_count = len([a for a in alerts if a.verification_status == "unverified"])
        if unverified_count > len(alerts) * 0.5:
            recommendations.append("Many alerts remain unverified - improve alert verification processes")
        
        if not recommendations:
            recommendations.append("Alert patterns are within normal parameters - continue current monitoring")
        
        return recommendations
    
    def get_alert_details(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific alert"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return None
        
        # Get related alerts
        related_alerts = []
        for related_id in alert.related_alerts:
            if related_id in self.alerts:
                related_alerts.append({
                    "alert_id": related_id,
                    "title": self.alerts[related_id].title,
                    "status": self.alerts[related_id].status.value,
                    "severity": self.alerts[related_id].severity.value
                })
        
        # Get alert history
        alert_history = [h for h in self.alert_history if h["alert_id"] == alert_id]
        
        return {
            "alert": {
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
                "estimated_impact_duration": str(alert.estimated_impact_duration) if alert.estimated_impact_duration else None,
                "passenger_impact": alert.passenger_impact,
                "financial_impact": alert.financial_impact,
                "source": alert.source,
                "confidence_score": alert.confidence_score,
                "verification_status": alert.verification_status,
                "assigned_to": alert.assigned_to,
                "resolution_notes": alert.resolution_notes,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "resolved_by": alert.resolved_by,
                "tags": alert.tags
            },
            "related_alerts": related_alerts,
            "history": alert_history,
            "escalation_actions": self._get_alert_escalation_actions(alert)
        }
    
    def _get_alert_escalation_actions(self, alert: Alert) -> List[Dict[str, Any]]:
        """Get escalation actions for alert"""
        actions = []
        
        for policy in self.escalation_policies.values():
            if self._matches_escalation_conditions(alert, policy):
                for time_threshold, action in policy.time_thresholds:
                    if datetime.now() - alert.created_at >= time_threshold:
                        actions.append({
                            "action": action,
                            "threshold": str(time_threshold),
                            "executed": True,
                            "executed_at": alert.created_at + time_threshold
                        })
                    else:
                        actions.append({
                            "action": action,
                            "threshold": str(time_threshold),
                            "executed": False,
                            "scheduled_for": alert.created_at + time_threshold
                        })
        
        return actions
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
