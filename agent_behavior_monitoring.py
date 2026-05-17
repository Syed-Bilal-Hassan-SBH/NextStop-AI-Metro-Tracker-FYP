"""
agent_behavior_monitoring.py
===========================
NEW FILE - Agent Behavior Monitoring for Individual Bus Decisions
Tracks and analyzes individual bus agent behavior patterns and decision-making

Features:
- Individual bus decision tracking
- Behavior pattern analysis
- Anomaly detection
- Performance comparison
- Decision optimization recommendations
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
import json

class DecisionType(Enum):
    ROUTE_CHOICE = "route_choice"
    SPEED_ADJUSTMENT = "speed_adjustment bian"
    STOP_SKIPPING = "stop_skipping"
    DETOUR_TAKING = "detour_taking"
    EMERGENCY_RESPONSE = "emergency_response"
    TRAFFIC_AVOIDANCE = "traffic_avoidance"
    SCHEDULE_ADHERENCE = "schedule_adherence"

class BehaviorPattern(Enum):
    CONSERVATIVE = "conservative"  # Follows rules strictly
    AGGRESSIVE = "aggressive"     # Takes risks for efficiency
    ADAPTIVE = "adaptive"         # Adjusts well to conditions
    ERRATIC = "erratic"          # Inconsistent behavior
    OPTIMAL = "optimal"          # Makes best decisions

@dataclass
class BusDecision:
    """Record of a specific decision made by a bus agent"""
    bus_id: str
    decision_id: str
    decision_type: DecisionType
    timestamp: datetime
    location: Tuple[float, float]  # (lat, lng)
    context: Dict[str, Any]  # Traffic, weather, passenger load, etc.
    options_considered: List[Dict[str, Any]]  # Alternative options
    chosen_option: Dict[str, Any]
    outcome: Dict[str, Any]  # Result of the decision
    efficiency_score: float  # 0.0 - 1.0
    safety_score: float     # 0.0 - 1.0
    passenger_satisfaction: float  # 0.0 - 1.0
    reasoning: str = ""

@dataclass
class BehaviorProfile:
    """Behavioral profile for a bus agent"""
    bus_id: str
    total_decisions: int = 0
    decision_types: Dict[DecisionType, int] = field(default_factory=dict)
    behavior_pattern: BehaviorPattern = BehaviorPattern.ADAPTIVE
    average_efficiency: float = 0.0
    average_safety: float = 0.0
    average_passenger_satisfaction: float = 0.0
    anomaly_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Decision distribution
    route_choice_efficiency: float = 0.0
    speed_adjustment_efficiency: float = 0.0
    emergency_response_efficiency: float = 0.0
    traffic_avoidance_efficiency: float = 0.0
    
    # Behavioral metrics
    risk_tolerance: float = 0.5  # 0.0 - 1.0
    adaptability_score: float = 0.5  # 0.0 - 1.0
    consistency_score: float = 0.5  # 0.0 - 1.0
    learning_rate: float = 0.5  # 0.0 - 1.0

@dataclass
class AnomalyAlert:
    """Alert for anomalous behavior"""
    alert_id: str
    bus_id: str
    anomaly_type: str
    severity: str  # low, medium, high, critical
    description: str
    timestamp: datetime
    expected_behavior: str
    actual_behavior: str
    impact_assessment: str
    recommended_action: str
    resolved: bool = False
    resolution_notes: str = ""

class AgentBehaviorMonitor:
    """Comprehensive agent behavior monitoring system"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.decisions: Dict[str, List[BusDecision]] = {}  # bus_id -> decisions
        self.behavior_profiles: Dict[str, BehaviorProfile] = {}
        self.anomaly_alerts: Dict[str, AnomalyAlert] = {}
        
        # Configuration
        self.anomaly_threshold = 2.0  # Standard deviations from norm
        self.min_decisions_for_profile = 10
        self.behavior_analysis_window = timedelta(days=7)
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Create sample decision data for demonstration"""
        sample_buses = ["BUS-01", "BUS-02", "BUS-03", "BUS-04", "BUS-05"]
        
        for bus_id in sample_buses:
            decisions = []
            
            # Generate sample decisions for the last 24 hours
            for hours_ago in range(24):
                timestamp = datetime.now() - timedelta(hours=hours_ago)
                
                # Generate 2-4 decisions per hour
                for decision_num in range(random.randint(2, 4)):
                    decision_time = timestamp + timedelta(minutes=random.randint(0, 59))
                    
                    # Random decision type
                    decision_type = random.choice(list(DecisionType))
                    
                    # Create context
                    context = {
                        "traffic_level": random.uniform(0.1, 1.0),
                        "weather_condition": random.choice(["clear", "rain", "fog", "heavy_rain"]),
                        "passenger_load": random.randint(10, 80),
                        "time_pressure": random.uniform(0.0, 1.0),
                        "fuel_level": random.uniform(0.2, 1.0)
                    }
                    
                    # Simulate decision options and outcome
                    decision = self._create_sample_decision(
                        bus_id, decision_type, decision_time, context
                    )
                    decisions.append(decision)
            
            self.decisions[bus_id] = decisions
            self._update_behavior_profile(bus_id)
    
    def _create_sample_decision(self, bus_id: str, decision_type: DecisionType, 
                              timestamp: datetime, context: Dict[str, Any]) -> BusDecision:
        """Create a sample decision based on type and context"""
        decision_id = f"DEC-{bus_id}-{int(timestamp.timestamp())}"
        
        # Simulate different decision patterns based on bus personality
        bus_personality = getattr(self, f"_get_bus_personality_{bus_id[-2:]}", self._get_bus_personality_default)()
        
        options_considered = []
        chosen_option = {}
        outcome = {}
        efficiency_score = 0.5
        safety_score = 0.5
        passenger_satisfaction = 0.5
        reasoning = ""
        
        if decision_type == DecisionType.SPEED_ADJUSTMENT:
            # Speed adjustment decisions
            base_speed = 35.0  # km/h
            traffic_factor = context["traffic_level"]
            
            options = [
                {"speed": base_speed * 0.8, "risk": "low", "efficiency": "low"},
                {"speed": base_speed, "risk": "medium", "efficiency": "medium"},
                {"speed": base_speed * 1.2, "risk": "high", "efficiency": "high"}
            ]
            
            options_considered = options
            
            # Choose based on personality
            if bus_personality == "aggressive":
                chosen_option = options[2]  # High speed
                efficiency_score = 0.8
                safety_score = 0.3
                reasoning = "Chose higher speed to maintain schedule despite traffic"
            elif bus_personality == "conservative":
                chosen_option = options[0]  # Low speed
                efficiency_score = 0.3
                safety_score = 0.9
                reasoning = "Reduced speed for safety in current conditions"
            else:
                chosen_option = options[1]  # Medium speed
                efficiency_score = 0.6
                safety_score = 0.7
                reasoning = "Balanced speed adjustment for current traffic"
            
            outcome = {
                "time_saved_minutes": random.uniform(-5, 15),
                "fuel_consumed": random.uniform(2, 8),
                "passenger_complaints": random.randint(0, 3)
            }
            
        elif decision_type == DecisionType.TRAFFIC_AVOIDANCE:
            # Traffic avoidance decisions
            options = [
                {"action": "stay_on_route", "extra_time": 15, "risk": "low"},
                {"action": "take_alternative", "extra_time": 5, "risk": "medium"},
                {"action": "aggressive_detour", "extra_time": -2, "risk": "high"}
            ]
            
            options_considered = options
            
            if bus_personality == "aggressive":
                chosen_option = options[2]
                efficiency_score = 0.7
                safety_score = 0.4
                reasoning = "Took aggressive detour to avoid heavy traffic"
            elif bus_personality == "conservative":
                chosen_option = options[0]
                efficiency_score = 0.2
                safety_score = 0.8
                reasoning = "Stayed on planned route despite delays"
            else:
                chosen_option = options[1]
                efficiency_score = 0.6
                safety_score = 0.6
                reasoning = "Took alternative route to balance time and safety"
            
            outcome = {
                "actual_delay": random.uniform(-5, 20),
                "passenger_satisfaction": random.uniform(0.3, 0.9),
                "navigation_complexity": random.uniform(0.1, 0.8)
            }
            
        elif decision_type == DecisionType.EMERGENCY_RESPONSE:
            # Emergency response decisions
            options = [
                {"action": "continue_service", "priority": "schedule"},
                {"action": "stop_and_assist", "priority": "safety"},
                {"action": "call_dispatch", "priority": "protocol"}
            ]
            
            options_considered = options
            chosen_option = options[1]  # Usually choose safety
            efficiency_score = 0.3
            safety_score = 0.9
            passenger_satisfaction = random.uniform(0.7, 1.0)
            reasoning = "Prioritized passenger safety in emergency situation"
            
            outcome = {
                "emergency_resolved": random.choice([True, False]),
                "delay_caused": random.uniform(5, 30),
                "lives_impacted": random.randint(1, 50)
            }
        
        else:
            # Generic decision
            options_considered = [{"option": "A"}, {"option": "B"}, {"option": "C"}]
            chosen_option = {"option": "B"}
            efficiency_score = random.uniform(0.3, 0.8)
            safety_score = random.uniform(0.4, 0.9)
            passenger_satisfaction = random.uniform(0.4, 0.8)
            reasoning = "Standard operational decision"
        
        # Add some randomness to scores
        efficiency_score += random.uniform(-0.1, 0.1)
        safety_score += random.uniform(-0.1, 0.1)
        passenger_satisfaction += random.uniform(-0.1, 0.1)
        
        # Clamp scores to valid range
        efficiency_score = max(0.0, min(1.0, efficiency_score))
        safety_score = max(0.0, min(1.0, safety_score))
        passenger_satisfaction = max(0.0, min(1.0, passenger_satisfaction))
        
        return BusDecision(
            bus_id=bus_id,
            decision_id=decision_id,
            decision_type=decision_type,
            timestamp=timestamp,
            location=(random.uniform(25.0, 25.5), random.uniform(55.0, 55.5)),
            context=context,
            options_considered=options_considered,
            chosen_option=chosen_option,
            outcome=outcome,
            efficiency_score=efficiency_score,
            safety_score=safety_score,
            passenger_satisfaction=passenger_satisfaction,
            reasoning=reasoning
        )
    
    def _get_bus_personality_default(self) -> str:
        """Default bus personality"""
        return "adaptive"
    
    def _get_bus_personality_01(self) -> str:
        return "aggressive"
    
    def _get_bus_personality_02(self) -> str:
        return "conservative"
    
    def _get_bus_personality_03(self) -> str:
        return "adaptive"
    
    def _get_bus_personality_04(self) -> str:
        return "conservative"
    
    def _get_bus_personality_05(self) -> str:
        return "aggressive"
    
    def record_decision(self, decision: BusDecision) -> bool:
        """Record a new decision made by a bus agent"""
        try:
            if decision.bus_id not in self.decisions:
                self.decisions[decision.bus_id] = []
            
            self.decisions[decision.bus_id].append(decision)
            
            # Update behavior profile
            self._update_behavior_profile(decision.bus_id)
            
            # Check for anomalies
            self._check_for_anomalies(decision)
            
            self.logger.info(f"Recorded decision {decision.decision_id} for bus {decision.bus_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording decision: {e}")
            return False
    
    def _update_behavior_profile(self, bus_id: str):
        """Update the behavior profile for a bus"""
        decisions = self.decisions.get(bus_id, [])
        
        if len(decisions) < self.min_decisions_for_profile:
            return
        
        profile = self.behavior_profiles.get(bus_id)
        if not profile:
            profile = BehaviorProfile(bus_id=bus_id)
            self.behavior_profiles[bus_id] = profile
        
        # Update basic metrics
        profile.total_decisions = len(decisions)
        profile.last_updated = datetime.now()
        
        # Calculate average scores
        efficiency_scores = [d.efficiency_score for d in decisions]
        safety_scores = [d.safety_score for d in decisions]
        satisfaction_scores = [d.passenger_satisfaction for d in decisions]
        
        profile.average_efficiency = statistics.mean(efficiency_scores)
        profile.average_safety = statistics.mean(safety_scores)
        profile.average_passenger_satisfaction = statistics.mean(satisfaction_scores)
        
        # Count decision types
        decision_type_counts = {}
        for decision in decisions:
            decision_type_counts[decision.decision_type] = decision_type_counts.get(decision.decision_type, 0) + 1
        profile.decision_types = decision_type_counts
        
        # Calculate decision-type specific efficiencies
        speed_decisions = [d for d in decisions if d.decision_type == DecisionType.SPEED_ADJUSTMENT]
        if speed_decisions:
            profile.speed_adjustment_efficiency = statistics.mean([d.efficiency_score for d in speed_decisions])
        
        traffic_decisions = [d for d in decisions if d.decision_type == DecisionType.TRAFFIC_AVOIDANCE]
        if traffic_decisions:
            profile.traffic_avoidance_efficiency = statistics.mean([d.efficiency_score for d in traffic_decisions])
        
        emergency_decisions = [d for d in decisions if d.decision_type == DecisionType.EMERGENCY_RESPONSE]
        if emergency_decisions:
            profile.emergency_response_efficiency = statistics.mean([d.efficiency_score for d in emergency_decisions])
        
        # Determine behavior pattern
        profile.behavior_pattern = self._classify_behavior_pattern(profile)
        
        # Calculate behavioral metrics
        profile.risk_tolerance = self._calculate_risk_tolerance(decisions)
        profile.adaptability_score = self._calculate_adaptability(decisions)
        profile.consistency_score = self._calculate_consistency(decisions)
        profile.learning_rate = self._calculate_learning_rate(decisions)
    
    def _classify_behavior_pattern(self, profile: BehaviorProfile) -> BehaviorPattern:
        """Classify the behavior pattern based on profile metrics"""
        efficiency = profile.average_efficiency
        safety = profile.average_safety
        consistency = profile.consistency_score
        
        # Use a simple rule-based classification
        if efficiency > 0.8 and safety > 0.8 and consistency > 0.8:
            return BehaviorPattern.OPTIMAL
        elif efficiency > 0.7 and safety < 0.5:
            return BehaviorPattern.AGGRESSIVE
        elif efficiency < 0.5 and safety > 0.8:
            return BehaviorPattern.CONSERVATIVE
        elif consistency < 0.4:
            return BehaviorPattern.ERRATIC
        else:
            return BehaviorPattern.ADAPTIVE
    
    def _calculate_risk_tolerance(self, decisions: List[BusDecision]) -> float:
        """Calculate risk tolerance based on decision patterns"""
        risk_scores = []
        
        for decision in decisions:
            # Higher efficiency with lower safety indicates higher risk tolerance
            risk_score = (decision.efficiency_score - decision.safety_score + 1) / 2
            risk_scores.append(risk_score)
        
        return statistics.mean(risk_scores) if risk_scores else 0.5
    
    def _calculate_adaptability(self, decisions: List[BusDecision]) -> float:
        """Calculate adaptability based on context-aware decisions"""
        adaptability_scores = []
        
        for decision in decisions:
            # Check if decision matches context appropriately
            context = decision.context
            traffic_level = context.get("traffic_level", 0.5)
            
            # High adaptability: adjust speed based on traffic
            if decision.decision_type == DecisionType.SPEED_ADJUSTMENT:
                if traffic_level > 0.7 and decision.chosen_option.get("speed", 35) < 35:
                    adaptability_scores.append(1.0)
                elif traffic_level < 0.3 and decision.chosen_option.get("speed", 35) > 35:
                    adaptability_scores.append(1.0)
                else:
                    adaptability_scores.append(0.5)
            else:
                adaptability_scores.append(0.7)  # Default adaptability
        
        return statistics.mean(adaptability_scores) if adaptability_scores else 0.5
    
    def _calculate_consistency(self, decisions: List[BusDecision]) -> float:
        """Calculate consistency in decision-making"""
        if len(decisions) < 5:
            return 0.5
        
        # Group decisions by type and check consistency
        type_groups = {}
        for decision in decisions:
            if decision.decision_type not in type_groups:
                type_groups[decision.decision_type] = []
            type_groups[decision.decision_type].append(decision.efficiency_score)
        
        consistency_scores = []
        for decision_type, scores in type_groups.items():
            if len(scores) > 1:
                # Lower standard deviation = higher consistency
                std_dev = statistics.stdev(scores)
                consistency = 1.0 - min(std_dev, 1.0)
                consistency_scores.append(consistency)
        
        return statistics.mean(consistency_scores) if consistency_scores else 0.5
    
    def _calculate_learning_rate(self, decisions: List[BusDecision]) -> float:
        """Calculate learning rate based on improvement over time"""
        if len(decisions) < 10:
            return 0.5
        
        # Sort decisions by time
        sorted_decisions = sorted(decisions, key=lambda d: d.timestamp)
        
        # Compare early decisions to recent decisions
        mid_point = len(sorted_decisions) // 2
        early_decisions = sorted_decisions[:mid_point]
        recent_decisions = sorted_decisions[mid_point:]
        
        early_avg = statistics.mean([d.efficiency_score for d in early_decisions])
        recent_avg = statistics.mean([d.efficiency_score for d in recent_decisions])
        
        # Learning rate is the improvement
        learning = (recent_avg - early_avg + 1) / 2  # Normalize to 0-1
        return max(0.0, min(1.0, learning))
    
    def _check_for_anomalies(self, decision: BusDecision):
        """Check if a decision represents anomalous behavior"""
        profile = self.behavior_profiles.get(decision.bus_id)
        if not profile or profile.total_decisions < self.min_decisions_for_profile:
            return
        
        # Check for efficiency anomaly
        efficiency_deviation = abs(decision.efficiency_score - profile.average_efficiency)
        if efficiency_deviation > self.anomaly_threshold * 0.3:  # 30% deviation
            self._create_anomaly_alert(
                decision.bus_id,
                "efficiency_anomaly",
                "high" if efficiency_deviation > 0.5 else "medium",
                f"Bus {decision.bus_id} made a decision with unusual efficiency score",
                decision
            )
        
        # Check for safety anomaly
        safety_deviation = abs(decision.safety_score - profile.average_safety)
        if safety_deviation > self.anomaly_threshold * 0.3 and decision.safety_score < 0.3:
            self._create_anomaly_alert(
                decision.bus_id,
                "safety_concern",
                "high",
                f"Bus {decision.bus_id} made an unusually unsafe decision",
                decision
            )
        
        # Check for pattern deviation
        if profile.behavior_pattern == BehaviorPattern.CONSERVATIVE and decision.efficiency_score > 0.8:
            self._create_anomaly_alert(
                decision.bus_id,
                "behavior_change",
                "medium",
                f"Conservative bus {decision.bus_id} made an aggressive decision",
                decision
            )
    
    def _create_anomaly_alert(self, bus_id: str, anomaly_type: str, severity: str, 
                             description: str, decision: BusDecision):
        """Create an anomaly alert"""
        alert_id = f"ALERT-{bus_id}-{int(datetime.now().timestamp())}"
        
        alert = AnomalyAlert(
            alert_id=alert_id,
            bus_id=bus_id,
            anomaly_type=anomaly_type,
            severity=severity,
            description=description,
            timestamp=datetime.now(),
            expected_behavior=f"Typical behavior for {self.behavior_profiles.get(bus_id, BehaviorProfile()).behavior_pattern.value} agent",
            actual_behavior=decision.reasoning,
            impact_assessment=self._assess_impact(decision),
            recommended_action=self._get_recommended_action(anomaly_type, severity)
        )
        
        self.anomaly_alerts[alert_id] = alert
        self.logger.warning(f"Anomaly detected: {description}")
    
    def _assess_impact(self, decision: BusDecision) -> str:
        """Assess the impact of a decision"""
        if decision.efficiency_score < 0.3 and decision.safety_score < 0.3:
            return "High negative impact on both efficiency and safety"
        elif decision.safety_score < 0.3:
            return "Significant safety risk to passengers and vehicle"
        elif decision.efficiency_score < 0.3:
            return "Significant efficiency impact causing delays"
        elif decision.passenger_satisfaction < 0.3:
            return "Negative passenger experience impact"
        else:
            return "Minor operational impact"
    
    def _get_recommended_action(self, anomaly_type: str, severity: str) -> str:
        """Get recommended action for anomaly"""
        if severity == "critical":
            return "Immediate supervisor review and possible remote intervention"
        elif severity == "high":
            return "Schedule detailed performance review and additional training"
        elif anomaly_type == "safety_concern":
            return "Mandatory safety briefing and route reassignment pending review"
        elif anomaly_type == "efficiency_anomaly":
            return "Monitor future decisions and provide coaching if pattern continues"
        else:
            return "Continue monitoring and document for trend analysis"
    
    def get_bus_behavior_analysis(self, bus_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive behavior analysis for a specific bus"""
        decisions = self.decisions.get(bus_id, [])
        profile = self.behavior_profiles.get(bus_id)
        
        if not decisions or not profile:
            return None
        
        # Recent decisions (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_decisions = [d for d in decisions if d.timestamp >= recent_cutoff]
        
        # Decision type breakdown
        decision_breakdown = {}
        for decision_type, count in profile.decision_types.items():
            type_decisions = [d for d in decisions if d.decision_type == decision_type]
            if type_decisions:
                decision_breakdown[decision_type.value] = {
                    "count": count,
                    "avg_efficiency": statistics.mean([d.efficiency_score for d in type_decisions]),
                    "avg_safety": statistics.mean([d.safety_score for d in type_decisions]),
                    "recent_count": len([d for d in recent_decisions if d.decision_type == decision_type])
                }
        
        # Recent anomalies
        recent_anomalies = [a for a in self.anomaly_alerts.values() 
                          if a.bus_id == bus_id and a.timestamp >= recent_cutoff]
        
        # Performance trends
        if len(decisions) >= 20:
            # Compare first half to second half
            sorted_decisions = sorted(decisions, key=lambda d: d.timestamp)
            mid_point = len(sorted_decisions) // 2
            
            early_efficiency = statistics.mean([d.efficiency_score for d in sorted_decisions[:mid_point]])
            recent_efficiency = statistics.mean([d.efficiency_score for d in sorted_decisions[mid_point:]])
            
            efficiency_trend = "improving" if recent_efficiency > early_efficiency else "declining"
            efficiency_change = ((recent_efficiency - early_efficiency) / early_efficiency) * 100
        else:
            efficiency_trend = "insufficient_data"
            efficiency_change = 0.0
        
        return {
            "bus_id": bus_id,
            "profile": {
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
            },
            "decision_breakdown": decision_breakdown,
            "recent_activity": {
                "decisions_last_24h": len(recent_decisions),
                "anomalies_last_24h": len(recent_anomalies),
                "avg_efficiency_recent": statistics.mean([d.efficiency_score for d in recent_decisions]) if recent_decisions else 0.0
            },
            "performance_trends": {
                "efficiency_trend": efficiency_trend,
                "efficiency_change_percentage": efficiency_change
            },
            "recent_anomalies": [
                {
                    "alert_id": a.alert_id,
                    "type": a.anomaly_type,
                    "severity": a.severity,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in recent_anomalies[-5:]  # Last 5 anomalies
            ],
            "recommendations": self._generate_bus_recommendations(profile, recent_anomalies)
        }
    
    def _generate_bus_recommendations(self, profile: BehaviorProfile, recent_anomalies: List[AnomalyAlert]) -> List[str]:
        """Generate recommendations for bus improvement"""
        recommendations = []
        
        if profile.average_efficiency < 0.5:
            recommendations.append("Consider additional route optimization training")
        
        if profile.average_safety < 0.6:
            recommendations.append("Schedule safety protocol refresher course")
        
        if profile.consistency_score < 0.4:
            recommendations.append("Review decision-making guidelines for consistency")
        
        if profile.learning_rate < 0.3:
            recommendations.append("Provide adaptive decision-making coaching")
        
        if len(recent_anomalies) > 2:
            recommendations.append("Increase supervision frequency due to recent anomalies")
        
        if profile.behavior_pattern == BehaviorPattern.ERRATIC:
            recommendations.append("Consider temporary reassignment to less complex routes")
        
        if profile.risk_tolerance > 0.8:
            recommendations.append("Counsel on balancing efficiency with safety")
        
        if not recommendations:
            recommendations.append("Continue current performance - meeting expectations")
        
        return recommendations
    
    def get_fleet_behavior_overview(self) -> Dict[str, Any]:
        """Get fleet-wide behavior overview"""
        total_buses = len(self.behavior_profiles)
        if total_buses == 0:
            return {"error": "No behavior data available"}
        
        # Aggregate statistics
        all_profiles = list(self.behavior_profiles.values())
        
        # Behavior pattern distribution
        pattern_counts = {}
        for pattern in BehaviorPattern:
            count = len([p for p in all_profiles if p.behavior_pattern == pattern])
            pattern_counts[pattern.value] = count
        
        # Performance metrics
        avg_efficiency = statistics.mean([p.average_efficiency for p in all_profiles])
        avg_safety = statistics.mean([p.average_safety for p in all_profiles])
        avg_satisfaction = statistics.mean([p.average_passenger_satisfaction for p in all_profiles])
        
        # Behavioral metrics
        avg_risk_tolerance = statistics.mean([p.risk_tolerance for p in all_profiles])
        avg_adaptability = statistics.mean([p.adaptability_score for p in all_profiles])
        avg_consistency = statistics.mean([p.consistency_score for p in all_profiles])
        
        # Recent anomalies
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_anomalies = [a for a in self.anomaly_alerts.values() if a.timestamp >= recent_cutoff]
        
        # Top and bottom performers
        sorted_by_efficiency = sorted(all_profiles, key=lambda p: p.average_efficiency)
        top_performers = [p.bus_id for p in sorted_by_efficiency[-3:]]
        bottom_performers = [p.bus_id for p in sorted_by_efficiency[:3]]
        
        return {
            "total_buses_monitored": total_buses,
            "behavior_pattern_distribution": pattern_counts,
            "fleet_performance": {
                "average_efficiency": avg_efficiency,
                "average_safety": avg_safety,
                "average_passenger_satisfaction": avg_satisfaction
            },
            "behavioral_metrics": {
                "average_risk_tolerance": avg_risk_tolerance,
                "average_adaptability": avg_adaptability,
                "average_consistency": avg_consistency
            },
            "recent_anomalies": {
                "last_24h": len(recent_anomalies),
                "by_severity": {
                    "critical": len([a for a in recent_anomalies if a.severity == "critical"]),
                    "high": len([a for a in recent_anomalies if a.severity == "high"]),
                    "medium": len([a for a in recent_anomalies if a.severity == "medium"]),
                    "low": len([a for a in recent_anomalies if a.severity == "low"])
                }
            },
            "performance_rankings": {
                "top_performers": top_performers,
                "bottom_performers": bottom_performers
            },
            "total_decisions_recorded": sum(p.total_decisions for p in all_profiles),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def resolve_anomaly(self, alert_id: str, resolution_notes: str) -> bool:
        """Resolve an anomaly alert"""
        alert = self.anomaly_alerts.get(alert_id)
        if not alert:
            return False
        
        alert.resolved = True
        alert.resolution_notes = resolution_notes
        
        # Update anomaly count in profile
        profile = self.behavior_profiles.get(alert.bus_id)
        if profile:
            profile.anomaly_count = max(0, profile.anomaly_count - 1)
        
        self.logger.info(f"Resolved anomaly {alert_id} for bus {alert.bus_id}")
        return True
