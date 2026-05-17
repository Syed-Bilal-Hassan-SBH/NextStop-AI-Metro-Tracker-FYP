<<<<<<< HEAD
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import random

@dataclass
class Stop:
    name: str
    latitude: float
    longitude: float  
    stop_id: int = None
    # NEW: Enhanced fields for ETA predictions (optional)
    average_dwell_time: float = 30.0  # seconds
    passenger_boarding_factor: float = 1.0  # multiplier for rush hours
    historical_delays: List[float] = field(default_factory=list)  # past delay data

@dataclass
class Route:
    route_id: str
    name: str
    source: str
    destination: str
    stops: List[Stop]
    total_distance: float = 0.0
    # NEW: Enhanced fields for traffic analysis (optional)
    average_traffic_level: float = 1.0
    historical_travel_times: Dict[str, List[float]] = field(default_factory=dict)
    peak_hour_factor: float = 1.3  # traffic multiplier during peak hours

@dataclass
class Bus:
    bus_id: str
    route_id: str
    current_lat: float
    current_lng: float
    speed: float  # km/h
    status: str  # 'moving', 'at_stop', 'delayed', 'stopped_at_station'
    next_stop_index: int
    last_update: datetime
    direction: str = 'forward'  # 'forward' or 'reverse'
    
    # ORIGINAL: Enhanced fields for realistic behavior (preserved)
    is_at_stop: bool = False
    stop_start_time: Optional[datetime] = None
    stop_duration: int = field(default_factory=lambda: random.randint(15, 45))
    target_speed: float = field(default_factory=lambda: random.uniform(25, 40))
    base_speed: float = field(default_factory=lambda: random.uniform(25, 40))
    acceleration: float = 2.0  # km/h per second
    deceleration: float = 3.0  # km/h per second
    stop_approach_distance: float = 200.0  # meters
    traffic_factor: float = field(default_factory=lambda: random.uniform(0.7, 1.3))
    passenger_boarding_time: int = field(default_factory=lambda: random.randint(10, 30))
    
    # NEW: Optional fields for traffic awareness and ETA tracking
    current_segment_id: Optional[str] = None
    segment_start_time: Optional[datetime] = None
    traffic_delay_accumulated: float = 0.0  # minutes of delay due to traffic
    predicted_etas: Dict[int, Dict] = field(default_factory=dict)  # stop_index -> ETA info
    confidence_score: float = 0.6  # prediction confidence (0-1)
    historical_performance: List[Dict] = field(default_factory=list)  # past trip data
    
    # NEW: Enhanced traffic-responsive fields (optional)
    adaptive_speed_enabled: bool = True
    traffic_response_sensitivity: float = 0.8  # how much bus responds to traffic (0-1)
    emergency_mode: bool = False  # for handling severe traffic/incidents
    route_deviation_allowed: bool = False  # future: alternative routing
    
    def __post_init__(self):
        """Set initial values after object creation - PRESERVED from original"""
        if not hasattr(self, 'base_speed') or self.base_speed == 0:
            self.base_speed = random.uniform(25, 40)
        if not hasattr(self, 'target_speed') or self.target_speed == 0:
            self.target_speed = self.base_speed
        if not hasattr(self, 'traffic_factor') or self.traffic_factor == 0:
            self.traffic_factor = random.uniform(0.7, 1.3)
    
    # ENHANCED: Improved traffic conditions with safety checks
    def update_traffic_conditions(self):
        """Enhanced traffic condition updates with learning"""
        # Store previous conditions for learning
        previous_factor = getattr(self, 'traffic_factor', 1.0)
        
        # Gradual change in traffic conditions
        change = random.uniform(-0.1, 0.1)
        self.traffic_factor = max(0.3, min(1.5, previous_factor + change))
        
        # Time-based traffic patterns
        hour = datetime.now().hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            base_factor = 0.6  # Heavier traffic
        elif 22 <= hour or hour <= 6:  # Night hours  
            base_factor = 1.1  # Lighter traffic
        else:
            base_factor = 0.9  # Normal traffic
            
        # Apply time-based adjustment with sensitivity
        time_influence = 0.3  # How much time affects traffic
        self.traffic_factor = (self.traffic_factor * (1 - time_influence) + 
                              base_factor * time_influence)
        
        # Update target speed based on traffic and responsiveness
        if getattr(self, 'adaptive_speed_enabled', True):
            speed_adjustment = self.traffic_factor * getattr(self, 'traffic_response_sensitivity', 0.8)
            self.target_speed = self.base_speed * speed_adjustment
        else:
            self.target_speed = self.base_speed * self.traffic_factor
        
        # Random traffic events with enhanced realism
        if random.random() < 0.05:  # 5% chance per update
            event = random.choice(['heavy_traffic', 'accident', 'construction', 
                                 'clear_road', 'weather', 'special_event'])
            self._handle_traffic_event(event)
        
        # Accumulate traffic delay (NEW feature)
        if hasattr(self, 'traffic_delay_accumulated'):
            if self.traffic_factor < 0.8:  # Slower than 80% of normal speed
                delay_minutes = (0.8 - self.traffic_factor) * 0.5  # Proportional delay
                self.traffic_delay_accumulated += delay_minutes
        
        # Update confidence based on traffic stability (NEW feature)
        if hasattr(self, 'confidence_score'):
            factor_change = abs(self.traffic_factor - previous_factor)
            if factor_change > 0.2:  # Significant change
                self.confidence_score = max(0.3, self.confidence_score - 0.1)
            else:  # Stable conditions
                self.confidence_score = min(0.9, self.confidence_score + 0.05)
    
    # NEW: Traffic event handling
    def _handle_traffic_event(self, event_type: str):
        """Handle specific traffic events"""
        event_impacts = {
            'heavy_traffic': (0.3, 0.5, 'Heavy traffic detected'),
            'accident': (0.2, 0.4, 'Traffic accident ahead'),
            'construction': (0.4, 0.6, 'Construction zone'),
            'clear_road': (1.1, 1.4, 'Clear road conditions'),
            'weather': (0.3, 0.7, 'Weather affecting traffic'),
            'special_event': (0.2, 0.8, 'Special event traffic')
        }
        
        if event_type in event_impacts:
            min_factor, max_factor, description = event_impacts[event_type]
            self.traffic_factor = random.uniform(min_factor, max_factor)
            
            # Set emergency mode for severe conditions
            if hasattr(self, 'emergency_mode'):
                if self.traffic_factor <= 0.3:
                    self.emergency_mode = True
                    self.status = 'delayed'
                else:
                    self.emergency_mode = False
                    if self.status == 'delayed' and self.traffic_factor > 0.6:
                        self.status = 'moving'
    
    # ENHANCED: Improved stop sequence with ETA learning
    def start_stop_sequence(self):
        """Enhanced stop sequence with ETA learning"""
        self.is_at_stop = True
        self.stop_start_time = datetime.now()
        self.status = 'stopped_at_station'
        self.speed = 0.0
        
        # Calculate dwell time based on multiple factors
        hour = datetime.now().hour
        base_duration = self.stop_duration
        
        # Rush hour adjustment
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            base_duration = int(base_duration * 1.8)  # More passengers
        elif 22 <= hour or hour <= 6:
            base_duration = int(base_duration * 0.7)  # Fewer passengers
        
        # Traffic-based adjustment (more delay = longer stops due to passenger backlog)
        if hasattr(self, 'traffic_delay_accumulated') and self.traffic_delay_accumulated > 2:
            base_duration = int(base_duration * 1.3)
        
        # Emergency mode adjustment
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            base_duration = int(base_duration * 0.8)  # Faster boarding to catch up
        
        # Add passenger boarding time with variability
        total_duration = base_duration + self.passenger_boarding_time + random.randint(0, 10)
        self.stop_duration = max(5, total_duration)  # Minimum 5 seconds
        
        # Record stop data for ETA learning (NEW)
        if hasattr(self, 'historical_performance'):
            self._record_stop_data()
    
    # NEW: Record stop data for machine learning
    def _record_stop_data(self):
        """Record stop data for machine learning"""
        if not hasattr(self, 'historical_performance'):
            self.historical_performance = []
            
        stop_data = {
            'timestamp': datetime.now(),
            'stop_index': self.next_stop_index,
            'planned_duration': self.stop_duration,
            'traffic_factor': self.traffic_factor,
            'accumulated_delay': getattr(self, 'traffic_delay_accumulated', 0),
            'emergency_mode': getattr(self, 'emergency_mode', False),
            'hour_of_day': datetime.now().hour
        }
        
        # Keep last 50 stop records for learning
        if len(self.historical_performance) >= 50:
            self.historical_performance.pop(0)
        self.historical_performance.append(stop_data)
    
    # ENHANCED: Improved stop departure logic
    def should_leave_stop(self) -> bool:
        """Enhanced stop departure logic"""
        if not self.is_at_stop or not self.stop_start_time:
            return True
        
        elapsed = (datetime.now() - self.stop_start_time).total_seconds()
        
        # Base condition
        if elapsed >= self.stop_duration:
            return True
        
        # Emergency mode: leave early if severely delayed
        if hasattr(self, 'emergency_mode') and self.emergency_mode and elapsed >= (self.stop_duration * 0.7):
            return True
        
        # Smart departure: leave early if traffic ahead is clear and we're behind schedule
        if (hasattr(self, 'traffic_delay_accumulated') and 
            self.traffic_delay_accumulated > 3 and  # More than 3 min delayed
            self.traffic_factor > 1.0 and  # Clear traffic ahead
            elapsed >= (self.stop_duration * 0.8)):  # At least 80% of planned time
            return True
        
        return False
    
    def leave_stop(self):
        """Enhanced stop departure with learning"""
        actual_duration = (datetime.now() - self.stop_start_time).total_seconds()
        
        # Record actual vs planned duration for learning (NEW)
        if hasattr(self, 'historical_performance') and self.historical_performance:
            self.historical_performance[-1]['actual_duration'] = actual_duration
            accuracy = abs(actual_duration - self.stop_duration) / self.stop_duration
            self.historical_performance[-1]['duration_accuracy'] = 1.0 - min(1.0, accuracy)
        
        self.is_at_stop = False
        self.stop_start_time = None
        self.status = 'moving'
        
        # Reset for next stop with learning-based adjustment
        historical_avg = self._get_historical_stop_average()
        if historical_avg > 0:
            # Adjust future predictions based on historical data
            self.stop_duration = int((self.stop_duration + historical_avg) / 2)
        else:
            self.stop_duration = random.randint(15, 45)
            
        self.passenger_boarding_time = random.randint(10, 30)
        
        # Update traffic conditions when leaving stop
        self.update_traffic_conditions()
    
    # NEW: Historical analysis methods
    def _get_historical_stop_average(self) -> float:
        """Calculate historical average stop duration"""
        if not hasattr(self, 'historical_performance') or not self.historical_performance:
            return 0
        
        durations = [record.get('actual_duration', 0) 
                    for record in self.historical_performance[-10:]  # Last 10 stops
                    if 'actual_duration' in record]
        
        return sum(durations) / len(durations) if durations else 0
    
    # ENHANCED: Improved speed adjustment with traffic awareness
    def update_speed_for_approach(self, distance_to_stop: float):
        """Enhanced speed adjustment with traffic awareness"""
        if distance_to_stop <= self.stop_approach_distance:
            # Calculate deceleration based on traffic conditions
            if self.traffic_factor <= 0.5:  # Heavy traffic
                # More gradual deceleration in traffic
                decel_factor = distance_to_stop / (self.stop_approach_distance * 1.5)
                min_approach_speed = 3.0
            else:
                # Normal deceleration
                decel_factor = distance_to_stop / self.stop_approach_distance
                min_approach_speed = 5.0
            
            approach_speed = max(min_approach_speed, self.target_speed * decel_factor)
            self.speed = approach_speed
        else:
            # Gradually adjust to target speed with traffic consideration
            speed_diff = self.target_speed - self.speed
            
            # Adjust acceleration/deceleration based on traffic
            if self.traffic_factor <= 0.5:  # Heavy traffic
                accel_rate = self.acceleration * 0.5  # Slower acceleration
                decel_rate = self.deceleration * 0.7  # More gradual deceleration
            else:
                accel_rate = self.acceleration
                decel_rate = self.deceleration
            
            if abs(speed_diff) > 0.1:
                if speed_diff > 0:
                    self.speed = min(self.target_speed, self.speed + accel_rate)
                else:
                    self.speed = max(self.target_speed, self.speed - decel_rate)
            else:
                self.speed = self.target_speed
        
        # Emergency speed limits
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            self.speed = min(self.speed, 15.0)  # Max 15 km/h in emergency
    
    # NEW: Enhanced status methods for better UI feedback
    def get_status_color(self) -> str:
        """Enhanced status color with traffic awareness"""
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            return '#8B0000'  # Dark red for emergency
        elif self.is_at_stop or self.status == 'stopped_at_station':
            return '#FFA500'  # Orange for stopped
        elif self.status == 'delayed' or (hasattr(self, 'traffic_delay_accumulated') and self.traffic_delay_accumulated > 5):
            return '#DC3545'  # Red for delayed
        elif self.traffic_factor <= 0.3:
            return '#FF4444'  # Bright red for heavy traffic
        elif self.traffic_factor <= 0.6:
            return '#FF8800'  # Orange for moderate traffic
        elif self.speed < 10:
            return '#FFB366'  # Light orange for slow speed
        else:
            return None  # Use default route color
    
    def get_detailed_status(self) -> str:
        """Enhanced status description with traffic and delay info"""
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            return f"Emergency Mode - Severe Delay ({delay_info:.1f}min)"
        elif self.is_at_stop:
            remaining = max(0, self.stop_duration - (datetime.now() - self.stop_start_time).total_seconds())
            return f"At Stop ({remaining:.0f}s remaining)"
        elif self.status == 'delayed':
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            return f"Delayed ({delay_info:.1f}min) - Traffic: {self.traffic_factor:.2f}x"
        elif self.traffic_factor <= 0.3:
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            return f"Heavy Traffic ({self.speed:.1f} km/h) - Delay: {delay_info:.1f}min"
        elif self.traffic_factor <= 0.6:
            return f"Moderate Traffic ({self.speed:.1f} km/h)"
        elif self.speed < 5:
            return "Approaching Stop"
        else:
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            delay_text = f" - {delay_info:.1f}min delayed" if delay_info > 1 else ""
            return f"Moving ({self.speed:.1f} km/h){delay_text}"
    
    # NEW: ETA prediction methods
    def update_eta_prediction(self, stop_index: int, eta_info: Dict):
        """Update ETA prediction for a specific stop"""
        if not hasattr(self, 'predicted_etas'):
            self.predicted_etas = {}
            
        self.predicted_etas[stop_index] = {
            'eta_minutes': eta_info.get('eta_minutes', 0),
            'eta_datetime': eta_info.get('eta_datetime'),
            'confidence': eta_info.get('confidence', 0.6),
            'predicted_at': datetime.now(),
            'factors': eta_info.get('factors', [])
        }
    
    def get_eta_accuracy_score(self) -> float:
        """Calculate ETA prediction accuracy based on historical performance"""
        if not hasattr(self, 'historical_performance') or not self.historical_performance:
            return 0.6  # Default confidence
        
        recent_predictions = [record for record in self.historical_performance[-20:] 
                            if 'duration_accuracy' in record]
        
        if not recent_predictions:
            return 0.6
        
        avg_accuracy = sum(record['duration_accuracy'] for record in recent_predictions) / len(recent_predictions)
        return max(0.3, min(0.95, avg_accuracy))
    
    def reset_delay_tracking(self):
        """Reset accumulated delay tracking (e.g., at terminals)"""
        if hasattr(self, 'traffic_delay_accumulated'):
            self.traffic_delay_accumulated = 0.0
        if hasattr(self, 'emergency_mode'):
            self.emergency_mode = False
        if self.status == 'delayed':
=======
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import random

@dataclass
class Stop:
    name: str
    latitude: float
    longitude: float  
    stop_id: int = None
    # NEW: Enhanced fields for ETA predictions (optional)
    average_dwell_time: float = 30.0  # seconds
    passenger_boarding_factor: float = 1.0  # multiplier for rush hours
    historical_delays: List[float] = field(default_factory=list)  # past delay data

@dataclass
class Route:
    route_id: str
    name: str
    source: str
    destination: str
    stops: List[Stop]
    total_distance: float = 0.0
    # NEW: Enhanced fields for traffic analysis (optional)
    average_traffic_level: float = 1.0
    historical_travel_times: Dict[str, List[float]] = field(default_factory=dict)
    peak_hour_factor: float = 1.3  # traffic multiplier during peak hours

@dataclass
class Bus:
    bus_id: str
    route_id: str
    current_lat: float
    current_lng: float
    speed: float  # km/h
    status: str  # 'moving', 'at_stop', 'delayed', 'stopped_at_station'
    next_stop_index: int
    last_update: datetime
    direction: str = 'forward'  # 'forward' or 'reverse'
    
    # ORIGINAL: Enhanced fields for realistic behavior (preserved)
    is_at_stop: bool = False
    stop_start_time: Optional[datetime] = None
    stop_duration: int = field(default_factory=lambda: random.randint(15, 45))
    target_speed: float = field(default_factory=lambda: random.uniform(25, 40))
    base_speed: float = field(default_factory=lambda: random.uniform(25, 40))
    acceleration: float = 2.0  # km/h per second
    deceleration: float = 3.0  # km/h per second
    stop_approach_distance: float = 200.0  # meters
    traffic_factor: float = field(default_factory=lambda: random.uniform(0.7, 1.3))
    passenger_boarding_time: int = field(default_factory=lambda: random.randint(10, 30))
    
    # NEW: Optional fields for traffic awareness and ETA tracking
    current_segment_id: Optional[str] = None
    segment_start_time: Optional[datetime] = None
    traffic_delay_accumulated: float = 0.0  # minutes of delay due to traffic
    predicted_etas: Dict[int, Dict] = field(default_factory=dict)  # stop_index -> ETA info
    confidence_score: float = 0.6  # prediction confidence (0-1)
    historical_performance: List[Dict] = field(default_factory=list)  # past trip data
    
    # NEW: Enhanced traffic-responsive fields (optional)
    adaptive_speed_enabled: bool = True
    traffic_response_sensitivity: float = 0.8  # how much bus responds to traffic (0-1)
    emergency_mode: bool = False  # for handling severe traffic/incidents
    route_deviation_allowed: bool = False  # future: alternative routing
    
    def __post_init__(self):
        """Set initial values after object creation - PRESERVED from original"""
        if not hasattr(self, 'base_speed') or self.base_speed == 0:
            self.base_speed = random.uniform(25, 40)
        if not hasattr(self, 'target_speed') or self.target_speed == 0:
            self.target_speed = self.base_speed
        if not hasattr(self, 'traffic_factor') or self.traffic_factor == 0:
            self.traffic_factor = random.uniform(0.7, 1.3)
    
    # ENHANCED: Improved traffic conditions with safety checks
    def update_traffic_conditions(self):
        """Enhanced traffic condition updates with learning"""
        # Store previous conditions for learning
        previous_factor = getattr(self, 'traffic_factor', 1.0)
        
        # Gradual change in traffic conditions
        change = random.uniform(-0.1, 0.1)
        self.traffic_factor = max(0.3, min(1.5, previous_factor + change))
        
        # Time-based traffic patterns
        hour = datetime.now().hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            base_factor = 0.6  # Heavier traffic
        elif 22 <= hour or hour <= 6:  # Night hours  
            base_factor = 1.1  # Lighter traffic
        else:
            base_factor = 0.9  # Normal traffic
            
        # Apply time-based adjustment with sensitivity
        time_influence = 0.3  # How much time affects traffic
        self.traffic_factor = (self.traffic_factor * (1 - time_influence) + 
                              base_factor * time_influence)
        
        # Update target speed based on traffic and responsiveness
        if getattr(self, 'adaptive_speed_enabled', True):
            speed_adjustment = self.traffic_factor * getattr(self, 'traffic_response_sensitivity', 0.8)
            self.target_speed = self.base_speed * speed_adjustment
        else:
            self.target_speed = self.base_speed * self.traffic_factor
        
        # Random traffic events with enhanced realism
        if random.random() < 0.05:  # 5% chance per update
            event = random.choice(['heavy_traffic', 'accident', 'construction', 
                                 'clear_road', 'weather', 'special_event'])
            self._handle_traffic_event(event)
        
        # Accumulate traffic delay (NEW feature)
        if hasattr(self, 'traffic_delay_accumulated'):
            if self.traffic_factor < 0.8:  # Slower than 80% of normal speed
                delay_minutes = (0.8 - self.traffic_factor) * 0.5  # Proportional delay
                self.traffic_delay_accumulated += delay_minutes
        
        # Update confidence based on traffic stability (NEW feature)
        if hasattr(self, 'confidence_score'):
            factor_change = abs(self.traffic_factor - previous_factor)
            if factor_change > 0.2:  # Significant change
                self.confidence_score = max(0.3, self.confidence_score - 0.1)
            else:  # Stable conditions
                self.confidence_score = min(0.9, self.confidence_score + 0.05)
    
    # NEW: Traffic event handling
    def _handle_traffic_event(self, event_type: str):
        """Handle specific traffic events"""
        event_impacts = {
            'heavy_traffic': (0.3, 0.5, 'Heavy traffic detected'),
            'accident': (0.2, 0.4, 'Traffic accident ahead'),
            'construction': (0.4, 0.6, 'Construction zone'),
            'clear_road': (1.1, 1.4, 'Clear road conditions'),
            'weather': (0.3, 0.7, 'Weather affecting traffic'),
            'special_event': (0.2, 0.8, 'Special event traffic')
        }
        
        if event_type in event_impacts:
            min_factor, max_factor, description = event_impacts[event_type]
            self.traffic_factor = random.uniform(min_factor, max_factor)
            
            # Set emergency mode for severe conditions
            if hasattr(self, 'emergency_mode'):
                if self.traffic_factor <= 0.3:
                    self.emergency_mode = True
                    self.status = 'delayed'
                else:
                    self.emergency_mode = False
                    if self.status == 'delayed' and self.traffic_factor > 0.6:
                        self.status = 'moving'
    
    # ENHANCED: Improved stop sequence with ETA learning
    def start_stop_sequence(self):
        """Enhanced stop sequence with ETA learning"""
        self.is_at_stop = True
        self.stop_start_time = datetime.now()
        self.status = 'stopped_at_station'
        self.speed = 0.0
        
        # Calculate dwell time based on multiple factors
        hour = datetime.now().hour
        base_duration = self.stop_duration
        
        # Rush hour adjustment
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            base_duration = int(base_duration * 1.8)  # More passengers
        elif 22 <= hour or hour <= 6:
            base_duration = int(base_duration * 0.7)  # Fewer passengers
        
        # Traffic-based adjustment (more delay = longer stops due to passenger backlog)
        if hasattr(self, 'traffic_delay_accumulated') and self.traffic_delay_accumulated > 2:
            base_duration = int(base_duration * 1.3)
        
        # Emergency mode adjustment
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            base_duration = int(base_duration * 0.8)  # Faster boarding to catch up
        
        # Add passenger boarding time with variability
        total_duration = base_duration + self.passenger_boarding_time + random.randint(0, 10)
        self.stop_duration = max(5, total_duration)  # Minimum 5 seconds
        
        # Record stop data for ETA learning (NEW)
        if hasattr(self, 'historical_performance'):
            self._record_stop_data()
    
    # NEW: Record stop data for machine learning
    def _record_stop_data(self):
        """Record stop data for machine learning"""
        if not hasattr(self, 'historical_performance'):
            self.historical_performance = []
            
        stop_data = {
            'timestamp': datetime.now(),
            'stop_index': self.next_stop_index,
            'planned_duration': self.stop_duration,
            'traffic_factor': self.traffic_factor,
            'accumulated_delay': getattr(self, 'traffic_delay_accumulated', 0),
            'emergency_mode': getattr(self, 'emergency_mode', False),
            'hour_of_day': datetime.now().hour
        }
        
        # Keep last 50 stop records for learning
        if len(self.historical_performance) >= 50:
            self.historical_performance.pop(0)
        self.historical_performance.append(stop_data)
    
    # ENHANCED: Improved stop departure logic
    def should_leave_stop(self) -> bool:
        """Enhanced stop departure logic"""
        if not self.is_at_stop or not self.stop_start_time:
            return True
        
        elapsed = (datetime.now() - self.stop_start_time).total_seconds()
        
        # Base condition
        if elapsed >= self.stop_duration:
            return True
        
        # Emergency mode: leave early if severely delayed
        if hasattr(self, 'emergency_mode') and self.emergency_mode and elapsed >= (self.stop_duration * 0.7):
            return True
        
        # Smart departure: leave early if traffic ahead is clear and we're behind schedule
        if (hasattr(self, 'traffic_delay_accumulated') and 
            self.traffic_delay_accumulated > 3 and  # More than 3 min delayed
            self.traffic_factor > 1.0 and  # Clear traffic ahead
            elapsed >= (self.stop_duration * 0.8)):  # At least 80% of planned time
            return True
        
        return False
    
    def leave_stop(self):
        """Enhanced stop departure with learning"""
        actual_duration = (datetime.now() - self.stop_start_time).total_seconds()
        
        # Record actual vs planned duration for learning (NEW)
        if hasattr(self, 'historical_performance') and self.historical_performance:
            self.historical_performance[-1]['actual_duration'] = actual_duration
            accuracy = abs(actual_duration - self.stop_duration) / self.stop_duration
            self.historical_performance[-1]['duration_accuracy'] = 1.0 - min(1.0, accuracy)
        
        self.is_at_stop = False
        self.stop_start_time = None
        self.status = 'moving'
        
        # Reset for next stop with learning-based adjustment
        historical_avg = self._get_historical_stop_average()
        if historical_avg > 0:
            # Adjust future predictions based on historical data
            self.stop_duration = int((self.stop_duration + historical_avg) / 2)
        else:
            self.stop_duration = random.randint(15, 45)
            
        self.passenger_boarding_time = random.randint(10, 30)
        
        # Update traffic conditions when leaving stop
        self.update_traffic_conditions()
    
    # NEW: Historical analysis methods
    def _get_historical_stop_average(self) -> float:
        """Calculate historical average stop duration"""
        if not hasattr(self, 'historical_performance') or not self.historical_performance:
            return 0
        
        durations = [record.get('actual_duration', 0) 
                    for record in self.historical_performance[-10:]  # Last 10 stops
                    if 'actual_duration' in record]
        
        return sum(durations) / len(durations) if durations else 0
    
    # ENHANCED: Improved speed adjustment with traffic awareness
    def update_speed_for_approach(self, distance_to_stop: float):
        """Enhanced speed adjustment with traffic awareness"""
        if distance_to_stop <= self.stop_approach_distance:
            # Calculate deceleration based on traffic conditions
            if self.traffic_factor <= 0.5:  # Heavy traffic
                # More gradual deceleration in traffic
                decel_factor = distance_to_stop / (self.stop_approach_distance * 1.5)
                min_approach_speed = 3.0
            else:
                # Normal deceleration
                decel_factor = distance_to_stop / self.stop_approach_distance
                min_approach_speed = 5.0
            
            approach_speed = max(min_approach_speed, self.target_speed * decel_factor)
            self.speed = approach_speed
        else:
            # Gradually adjust to target speed with traffic consideration
            speed_diff = self.target_speed - self.speed
            
            # Adjust acceleration/deceleration based on traffic
            if self.traffic_factor <= 0.5:  # Heavy traffic
                accel_rate = self.acceleration * 0.5  # Slower acceleration
                decel_rate = self.deceleration * 0.7  # More gradual deceleration
            else:
                accel_rate = self.acceleration
                decel_rate = self.deceleration
            
            if abs(speed_diff) > 0.1:
                if speed_diff > 0:
                    self.speed = min(self.target_speed, self.speed + accel_rate)
                else:
                    self.speed = max(self.target_speed, self.speed - decel_rate)
            else:
                self.speed = self.target_speed
        
        # Emergency speed limits
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            self.speed = min(self.speed, 15.0)  # Max 15 km/h in emergency
    
    # NEW: Enhanced status methods for better UI feedback
    def get_status_color(self) -> str:
        """Enhanced status color with traffic awareness"""
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            return '#8B0000'  # Dark red for emergency
        elif self.is_at_stop or self.status == 'stopped_at_station':
            return '#FFA500'  # Orange for stopped
        elif self.status == 'delayed' or (hasattr(self, 'traffic_delay_accumulated') and self.traffic_delay_accumulated > 5):
            return '#DC3545'  # Red for delayed
        elif self.traffic_factor <= 0.3:
            return '#FF4444'  # Bright red for heavy traffic
        elif self.traffic_factor <= 0.6:
            return '#FF8800'  # Orange for moderate traffic
        elif self.speed < 10:
            return '#FFB366'  # Light orange for slow speed
        else:
            return None  # Use default route color
    
    def get_detailed_status(self) -> str:
        """Enhanced status description with traffic and delay info"""
        if hasattr(self, 'emergency_mode') and self.emergency_mode:
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            return f"Emergency Mode - Severe Delay ({delay_info:.1f}min)"
        elif self.is_at_stop:
            remaining = max(0, self.stop_duration - (datetime.now() - self.stop_start_time).total_seconds())
            return f"At Stop ({remaining:.0f}s remaining)"
        elif self.status == 'delayed':
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            return f"Delayed ({delay_info:.1f}min) - Traffic: {self.traffic_factor:.2f}x"
        elif self.traffic_factor <= 0.3:
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            return f"Heavy Traffic ({self.speed:.1f} km/h) - Delay: {delay_info:.1f}min"
        elif self.traffic_factor <= 0.6:
            return f"Moderate Traffic ({self.speed:.1f} km/h)"
        elif self.speed < 5:
            return "Approaching Stop"
        else:
            delay_info = getattr(self, 'traffic_delay_accumulated', 0)
            delay_text = f" - {delay_info:.1f}min delayed" if delay_info > 1 else ""
            return f"Moving ({self.speed:.1f} km/h){delay_text}"
    
    # NEW: ETA prediction methods
    def update_eta_prediction(self, stop_index: int, eta_info: Dict):
        """Update ETA prediction for a specific stop"""
        if not hasattr(self, 'predicted_etas'):
            self.predicted_etas = {}
            
        self.predicted_etas[stop_index] = {
            'eta_minutes': eta_info.get('eta_minutes', 0),
            'eta_datetime': eta_info.get('eta_datetime'),
            'confidence': eta_info.get('confidence', 0.6),
            'predicted_at': datetime.now(),
            'factors': eta_info.get('factors', [])
        }
    
    def get_eta_accuracy_score(self) -> float:
        """Calculate ETA prediction accuracy based on historical performance"""
        if not hasattr(self, 'historical_performance') or not self.historical_performance:
            return 0.6  # Default confidence
        
        recent_predictions = [record for record in self.historical_performance[-20:] 
                            if 'duration_accuracy' in record]
        
        if not recent_predictions:
            return 0.6
        
        avg_accuracy = sum(record['duration_accuracy'] for record in recent_predictions) / len(recent_predictions)
        return max(0.3, min(0.95, avg_accuracy))
    
    def reset_delay_tracking(self):
        """Reset accumulated delay tracking (e.g., at terminals)"""
        if hasattr(self, 'traffic_delay_accumulated'):
            self.traffic_delay_accumulated = 0.0
        if hasattr(self, 'emergency_mode'):
            self.emergency_mode = False
        if self.status == 'delayed':
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
            self.status = 'moving'