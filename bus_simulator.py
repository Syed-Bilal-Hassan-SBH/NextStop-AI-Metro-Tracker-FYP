<<<<<<< HEAD
# Enhanced bus_simulator.py - PRESERVING ALL ORIGINAL FUNCTIONALITY + Adding Traffic & ETA

import math
import time
import threading
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
from dataclasses import asdict
from geopy.distance import geodesic
from models import Route, Bus
from database_manager import DatabaseManager
import json
from datetime import datetime

def serialize_for_json(obj):
    """Recursively convert datetime objects to ISO strings for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj

class TrafficSegment:
    """NEW: Represents a traffic segment between two stops"""
    def __init__(self, start_stop, end_stop, route_id):
        self.start_stop = start_stop
        self.end_stop = end_stop
        self.route_id = route_id
        self.segment_id = f"{route_id}_{start_stop.name}_{end_stop.name}"
        self.distance = geodesic(
            (start_stop.latitude, start_stop.longitude),
            (end_stop.latitude, end_stop.longitude)
        ).kilometers
        
        self.current_traffic_level = random.uniform(0.3, 1.2)
        self.base_speed_limit = 40  # km/h
        self.last_updated = datetime.now()
        
    def update_traffic_conditions(self):
        """Update traffic conditions based on time and random factors"""
        current_hour = datetime.now().hour
        
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            base_factor = 0.4
        elif 22 <= current_hour or current_hour <= 6:
            base_factor = 1.1
        else:
            base_factor = 0.8
            
        random_change = random.uniform(-0.15, 0.15)
        self.current_traffic_level = max(0.2, min(1.5, 
            base_factor + random_change + random.uniform(-0.1, 0.1)))
        
        if random.random() < 0.03:
            event = random.choice(['accident', 'construction', 'clear_road', 'weather'])
            if event == 'accident':
                self.current_traffic_level = random.uniform(0.1, 0.3)
            elif event == 'construction':
                self.current_traffic_level = random.uniform(0.2, 0.4)
            elif event == 'weather':
                self.current_traffic_level = random.uniform(0.3, 0.6)
            elif event == 'clear_road':
                self.current_traffic_level = random.uniform(1.1, 1.4)
                
        self.last_updated = datetime.now()
    
    def get_effective_speed(self):
        return self.base_speed_limit * self.current_traffic_level
    
    def get_traffic_color(self):
        if self.current_traffic_level <= 0.3:
            return "#DC3545"  # Red - Heavy traffic
        elif self.current_traffic_level <= 0.6:
            return "#FFC107"  # Yellow - Moderate traffic
        elif self.current_traffic_level <= 0.9:
            return "#28A745"  # Green - Light traffic
        else:
            return "#007CBA"  # Blue - Very light traffic
    
    def get_traffic_description(self):
        if self.current_traffic_level <= 0.3:
            return "Heavy Traffic"
        elif self.current_traffic_level <= 0.6:
            return "Moderate Traffic"
        elif self.current_traffic_level <= 0.9:
            return "Light Traffic"
        else:
            return "Free Flow"

class AIETAPredictor:
    """NEW: AI-based ETA prediction system"""
    def __init__(self):
        self.historical_data = {}
        self.learning_rate = 0.1
        self.weights = {
            'distance': 1.0,
            'traffic': 0.8,
            'time_of_day': 0.6,
            'stops': 0.4,
            'historical': 0.7
        }
        
    def predict_segment_time(self, traffic_segment, current_time=None):
        if current_time is None:
            current_time = datetime.now()
            
        base_time = (traffic_segment.distance / traffic_segment.get_effective_speed()) * 60
        
        hour = current_time.hour
        time_factor = 1.0
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            time_factor = 1.3
        elif 22 <= hour or hour <= 6:
            time_factor = 0.8
            
        predicted_time = base_time * time_factor
        predicted_time *= (1 + random.uniform(-0.1, 0.1))
        
        return max(0.5, predicted_time)
    
    def predict_eta_to_stops(self, bus, route, traffic_segments):
        current_time = datetime.now()
        etas = {}
        cumulative_time = 0
        
        current_stop_index = bus.next_stop_index
        direction = bus.direction
        
        if direction == 'reverse':
            stop_indices = list(range(current_stop_index, -1, -1))
        else:
            stop_indices = list(range(current_stop_index, len(route.stops)))
        
        for i, stop_index in enumerate(stop_indices):
            if i == 0:
                continue
                
            prev_index = stop_indices[i-1]
            curr_index = stop_index
            
            segment_key = f"{route.route_id}_{prev_index}_{curr_index}"
            if segment_key in traffic_segments:
                segment = traffic_segments[segment_key]
                segment_time = self.predict_segment_time(segment, current_time)
                cumulative_time += segment_time
                
                if i < len(stop_indices) - 1:
                    dwell_time = 0.5 + random.uniform(0, 0.5)
                    cumulative_time += dwell_time
                    
            eta_datetime = current_time + timedelta(minutes=cumulative_time)
            etas[stop_index] = {
                'stop_name': route.stops[stop_index].name,
                'eta_minutes': cumulative_time,
                'eta_datetime': eta_datetime,
                'confidence': random.uniform(0.6, 0.9)  # Simplified confidence
            }
            
        return etas

# ORIGINAL CLASS WITH ENHANCEMENTS ADDED
class EnhancedMultiRouteBusSimulator:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.routes = {}
        self.buses = {}  # All buses (running in background)
        self.simulation_running = False
        self.active_routes = set()  # Only controls visibility, not simulation
        self.background_routes = set()  # Routes running in background
        
        # NEW: Traffic and ETA systems (ADDED without removing original features)
        self.traffic_segments = {}
        self.eta_predictor = AIETAPredictor()
        self.traffic_update_interval = 30
        self.last_traffic_update = datetime.now()
        
        # ORIGINAL: Route colors (PRESERVED)
        self.route_colors = {
            'FR-01': '#007cba',  # Blue
            'FR-02': '#dc3545',  # Red
            'FR-03A': '#28a745', # Green
            'FR-03B': '#17a2b8', # Cyan
            'FR-04': '#ffc107',  # Yellow
            'FR-04A': '#fd7e14', # Orange
            'FR-05': '#6f42c1',  # Purple
            'FR-06': '#e83e8c',  # Pink
            'FR-07': '#20c997',  # Teal
            'FR-08A': '#6c757d', # Gray
            'FR-08B': '#343a40', # Dark
            'FR-08C': '#495057', # Dark Gray
            'FR-09': '#fd7e14', # Orange variant
            'FR-10': '#20c997', # Teal variant
            'FR-11': '#e83e8c', # Pink variant
            'FR-12': '#6f42c1', # Purple variant
            'FR-13': '#dc3545', # Red variant
            'FR-14': '#28a745', # Green variant
            'FR-14A': '#17a2b8',# Cyan variant
            'FR-15': '#ffc107'  # Yellow variant
        }
        
        # ORIGINAL: Enhanced scheduling system (PRESERVED)
        self.route_schedules = {}  # Track next departure times
        self.max_buses_per_route = 10  # Maximum buses per route
        self.departure_interval = 10  # Seconds between departures
        self.bus_counters = {}  # Counter for bus numbering
        
        # ORIGINAL: Load and initialize everything (PRESERVED ORDER)
        self.load_all_routes()
        self.initialize_traffic_system()  # NEW: Added traffic system
        self.initialize_scheduling_system()
        self.initialize_background_simulation()
    
    # ORIGINAL METHOD: Preserved exactly
    def load_all_routes(self):
        """Load all route data from database"""
        all_routes = self.db_manager.get_all_routes()
        
        for route_info in all_routes:
            route_id = route_info['route_id']
            stops = self.db_manager.get_route_stops(route_id)
            
            if stops:  # Only create route if it has stops
                route = Route(
                    route_id=route_id,
                    name=route_info['name'],
                    source=route_info['source'],
                    destination=route_info['destination'],
                    stops=stops
                )
                
                # Calculate total distance
                total_distance = 0.0
                for i in range(len(stops) - 1):
                    current = (stops[i].latitude, stops[i].longitude)
                    next_stop = (stops[i + 1].latitude, stops[i + 1].longitude)
                    total_distance += geodesic(current, next_stop).kilometers
                
                route.total_distance = total_distance
                self.routes[route_id] = route
                print(f"✅ Loaded route {route_id}: {len(stops)} stops, {total_distance:.2f} km")
    
    # NEW METHOD: Added traffic system initialization
    def initialize_traffic_system(self):
        """Initialize the traffic monitoring system"""
        print("🚦 Initializing traffic monitoring system...")
        
        for route_id, route in self.routes.items():
            for i in range(len(route.stops) - 1):
                start_stop = route.stops[i]
                end_stop = route.stops[i + 1]
                
                segment_forward = TrafficSegment(start_stop, end_stop, route_id)
                segment_key_forward = f"{route_id}_{i}_{i+1}"
                self.traffic_segments[segment_key_forward] = segment_forward
                
                segment_reverse = TrafficSegment(end_stop, start_stop, route_id)
                segment_key_reverse = f"{route_id}_{i+1}_{i}"
                self.traffic_segments[segment_key_reverse] = segment_reverse
        
        print(f"✅ Traffic system initialized with {len(self.traffic_segments)} segments")
    
    # NEW METHODS: Traffic management
    def update_traffic_conditions(self):
        current_time = datetime.now()
        if (current_time - self.last_traffic_update).seconds < self.traffic_update_interval:
            return
            
        for segment in self.traffic_segments.values():
            segment.update_traffic_conditions()
            
        self.last_traffic_update = current_time
    
    def get_traffic_data_for_frontend(self):
        traffic_data = {}
        
        for segment_id, segment in self.traffic_segments.items():
            traffic_data[segment_id] = {
                'segment_id': segment_id,
                'route_id': segment.route_id,
                'start_lat': segment.start_stop.latitude,
                'start_lng': segment.start_stop.longitude,
                'end_lat': segment.end_stop.latitude,
                'end_lng': segment.end_stop.longitude,
                'traffic_level': segment.current_traffic_level,
                'traffic_color': segment.get_traffic_color(),
                'traffic_description': segment.get_traffic_description(),
                'effective_speed': segment.get_effective_speed(),
                'distance': segment.distance,
                'last_updated': segment.last_updated.isoformat()
            }
        
        return traffic_data
    
    def get_all_bus_etas(self):
        all_etas = {}
        
        for bus_id, bus in self.buses.items():
            if bus.route_id in self.active_routes:
                route = self.routes.get(bus.route_id)
                if route:
                    etas = self.eta_predictor.predict_eta_to_stops(bus, route, self.traffic_segments)
                    if etas:
                        all_etas[bus_id] = etas
                        
        return all_etas
    
    # ORIGINAL METHOD: Preserved exactly
    def initialize_scheduling_system(self):
        """Initialize the enhanced scheduling system for all routes"""
        print("📅 Initializing enhanced scheduling system...")
        
        current_time = datetime.now()
        
        for route_id in self.routes.keys():
            # Initialize schedule for each route with bidirectional tracking
            self.route_schedules[route_id] = {
                'next_forward_departure': current_time + timedelta(seconds=random.randint(0, 30)),
                'next_reverse_departure': current_time + timedelta(seconds=random.randint(5, 35)),  # Offset reverse
                'forward_buses_count': 0,
                'reverse_buses_count': 0,
                'total_buses_count': 0,
                'active': False  # Will be set to True when route is activated
            }
            self.bus_counters[route_id] = 0
            
        print(f"✅ Scheduling system initialized for {len(self.routes)} routes")
    
    # ORIGINAL METHOD: Preserved exactly
    def initialize_background_simulation(self):
        """Initialize a minimal background simulation (fewer buses initially)"""
        print("🔄 Initializing background simulation...")
        
        # Start with just 1 bus per route for background activity
        for route_id, route in self.routes.items():
            self.create_new_bus(route_id, direction='forward', is_initial=True)
            self.background_routes.add(route_id)
        
        print(f"✅ Background simulation initialized with {len(self.buses)} buses")
    
    # ORIGINAL METHOD: Preserved exactly
    def create_new_bus(self, route_id: str, direction: str = 'forward', is_initial: bool = False) -> str:
        """Create a new bus for the specified route and direction"""
        if route_id not in self.routes:
            return None

        route = self.routes[route_id]
        self.bus_counters[route_id] += 1
        bus_number = self.bus_counters[route_id]

        direction_code = 'F' if direction == 'forward' else 'R'
        bus_id = f"{route_id}-{direction_code}-{bus_number:03d}"

        # Always start at the terminal stop
        if direction == 'forward':
            start_index = 0
            next_stop_index = 1
        else:
            start_index = len(route.stops) - 1
            next_stop_index = start_index - 1

        start_stop = route.stops[start_index]

        bus = Bus(
            bus_id=bus_id,
            route_id=route_id,
            current_lat=start_stop.latitude,
            current_lng=start_stop.longitude,
            speed=0.0,
            status='stopped_at_station' if not is_initial else 'moving',
            next_stop_index=next_stop_index,
            last_update=datetime.now(),
            direction=direction
        )
        
        # Initialize enhanced properties
        bus.base_speed = random.uniform(25, 40)
        bus.target_speed = bus.base_speed
        bus.traffic_factor = random.uniform(0.8, 1.2)
        bus.departure_number = bus_number - 1  # For tracking
        bus.departure_time = datetime.now()
        
        # If starting at station, initialize stop sequence
        if not is_initial:
            bus.is_at_stop = True
            bus.stop_start_time = datetime.now()
            bus.stop_duration = random.randint(10, 30)  # Initial boarding time

        self.buses[bus_id] = bus

        terminal_name = route.source if direction == 'forward' else route.destination
        destination_name = route.destination if direction == 'forward' else route.source
        print(f"🚌 Created {direction} bus {bus_id} at {terminal_name} → {destination_name}")
        print(f"📍 Bus {bus_id} initial coords: {start_stop.latitude}, {start_stop.longitude}")
        return bus_id

    def add_extra_bus(self, route_id: str):
        """Manually add an extra bus to a route (Deploy Extra Service)"""
        if route_id not in self.routes:
            return False, "Route not found"
        
        # Create a new bus in forward direction
        bus_id = self.create_new_bus(route_id, direction='forward')
        
        if bus_id:
            return True, f"Extra bus {bus_id} deployed successfully on {route_id}"
        else:
            return False, "Failed to create bus"
    
    # ORIGINAL METHODS: All scheduling and bus management preserved exactly
    def schedule_next_departure(self, route_id: str, direction: str):
        """Schedule the next bus departure for a route in specified direction"""
        if route_id not in self.route_schedules:
            return
        
        schedule = self.route_schedules[route_id]
        
        # Only schedule if route is active and under bus limit
        if schedule['active'] and schedule['total_buses_count'] < self.max_buses_per_route:
            
            # Schedule next departure based on direction
            next_time = datetime.now() + timedelta(seconds=self.departure_interval)
            
            if direction == 'forward':
                schedule['next_forward_departure'] = next_time
            else:
                schedule['next_reverse_departure'] = next_time
            
            route = self.routes[route_id]
            terminal = route.source if direction == 'forward' else route.destination
            print(f"📅 Next {direction} {route_id} departure scheduled for {next_time.strftime('%H:%M:%S')} from {terminal}")
    
    def process_scheduled_departures(self):
        """Process scheduled departures from both terminals with alternating pattern"""
        current_time = datetime.now()
        
        for route_id, schedule in self.route_schedules.items():
            if not schedule['active'] or route_id not in self.active_routes:
                continue
            
            route = self.routes[route_id]
            
            # Check forward direction departures
            if (schedule['total_buses_count'] < self.max_buses_per_route and 
                current_time >= schedule['next_forward_departure']):
                
                # Create forward bus from source
                bus_id = self.create_new_bus(route_id, direction='forward')
                if bus_id:
                    schedule['forward_buses_count'] += 1
                    schedule['total_buses_count'] += 1
                    self.schedule_next_departure(route_id, 'forward')
                    
                    print(f"🚌 Forward departure: Bus {bus_id} from {route.source} → {route.destination}")
            
            # Check reverse direction departures (independent scheduling)
            if (schedule['total_buses_count'] < self.max_buses_per_route and 
                current_time >= schedule['next_reverse_departure']):
                
                # Create reverse bus from destination
                bus_id = self.create_new_bus(route_id, direction='reverse')
                if bus_id:
                    schedule['reverse_buses_count'] += 1
                    schedule['total_buses_count'] += 1
                    self.schedule_next_departure(route_id, 'reverse')
                    
                    print(f"🚌 Reverse departure: Bus {bus_id} from {route.destination} → {route.source}")
    
    def handle_bus_completion(self, bus: Bus):
        """Handle bus when it completes the route (continue in same direction or turn around)"""
        route = self.routes[bus.route_id]
        
        if bus.direction == 'forward' and bus.next_stop_index >= len(route.stops):
            # Reached destination, start return journey
            bus.direction = 'reverse'
            bus.next_stop_index = len(route.stops) - 2  # Second to last stop
            
            # ✅ FIX: Set bus position to the last stop (destination terminal)
            terminal_stop = route.stops[-1]
            bus.current_lat = terminal_stop.latitude
            bus.current_lng = terminal_stop.longitude
            
            bus.status = 'stopped_at_station'
            bus.is_at_stop = True
            bus.stop_start_time = datetime.now()
            bus.stop_duration = random.randint(30, 60)  # Longer stop at terminal
            
            print(f"🔄 Bus {bus.bus_id} reached {route.destination}, starting return journey")
            
        elif bus.direction == 'reverse' and bus.next_stop_index < 0:
            # Reached source again, start new forward journey
            bus.direction = 'forward'
            bus.next_stop_index = 1
            
            # ✅ FIX: Set bus position to the first stop (source terminal)
            terminal_stop = route.stops[0]
            bus.current_lat = terminal_stop.latitude
            bus.current_lng = terminal_stop.longitude
            
            bus.status = 'stopped_at_station'
            bus.is_at_stop = True
            bus.stop_start_time = datetime.now()
            bus.stop_duration = random.randint(30, 60)  # Longer stop at terminal
            
            print(f"🔄 Bus {bus.bus_id} returned to {route.source}, starting new journey")
        
    # ORIGINAL METHOD: Preserved with minor enhancement for traffic
    def calculate_next_position(self, bus: Bus) -> Tuple[float, float]:
        """Calculate next GPS position with enhanced bidirectional movement"""
        route = self.routes[bus.route_id]
        
        # Handle route completion and direction changes
        self.handle_bus_completion(bus)
        
        # Get target stop based on direction
        if bus.direction == 'forward':
            if bus.next_stop_index >= len(route.stops):
                bus.next_stop_index = len(route.stops) - 1
        else:  # reverse
            if bus.next_stop_index < 0:
                bus.next_stop_index = 0
        
        target_stop = route.stops[bus.next_stop_index]
        
        current_pos = (bus.current_lat, bus.current_lng)
        target_pos = (target_stop.latitude, target_stop.longitude)
        
        # Calculate distance to target
        distance_to_target = geodesic(current_pos, target_pos).meters
        
        # Check if bus is currently at a stop
        if bus.is_at_stop:
            if bus.should_leave_stop():
                bus.leave_stop()
                return bus.current_lat, bus.current_lng
            else:
                # Bus is still at stop, don't move
                return bus.current_lat, bus.current_lng
        
        # Check if bus should stop at the target stop
        if distance_to_target < 50:  # 50 meters - arrived at stop
            bus.current_lat = target_stop.latitude
            bus.current_lng = target_stop.longitude
            bus.start_stop_sequence()
            
            # Prepare for next stop based on direction
            if bus.direction == 'forward':
                bus.next_stop_index += 1
            else:  # reverse
                bus.next_stop_index -= 1
            
            return bus.current_lat, bus.current_lng
        
        # Update speed based on distance to stop
        bus.update_speed_for_approach(distance_to_target)
        
        # Calculate movement step
        time_step = 3  # seconds
        speed_ms = bus.speed * 1000 / 3600  # convert km/h to m/s
        step_distance = speed_ms * time_step
        
        # Don't overshoot the target
        if step_distance > distance_to_target:
            step_distance = distance_to_target
        
        # Calculate bearing to target
        lat1, lng1 = math.radians(bus.current_lat), math.radians(bus.current_lng)
        lat2, lng2 = math.radians(target_stop.latitude), math.radians(target_stop.longitude)
        
        d_lng = lng2 - lng1
        y = math.sin(d_lng) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lng)
        bearing = math.atan2(y, x)
        
        # Calculate new position
        R = 6371000  # Earth's radius in meters
        lat1_rad = math.radians(bus.current_lat)
        lng1_rad = math.radians(bus.current_lng)
        
        new_lat = math.asin(
            math.sin(lat1_rad) * math.cos(step_distance / R) +
            math.cos(lat1_rad) * math.sin(step_distance / R) * math.cos(bearing)
        )
        
        new_lng = lng1_rad + math.atan2(
            math.sin(bearing) * math.sin(step_distance / R) * math.cos(lat1_rad),
            math.cos(step_distance / R) - math.sin(lat1_rad) * math.sin(new_lat)
        )
        
        return math.degrees(new_lat), math.degrees(new_lng)
    
    # MODIFIED: Enhanced with traffic awareness but preserves original behavior
    def update_bus_position(self, bus: Bus):
        """Update single bus position with enhanced behavior"""
        # NEW: Update traffic conditions periodically
        self.update_traffic_conditions()
        
        # Update traffic factor periodically
        if random.random() < 0.05:  # 5% chance per update
            bus.update_traffic_conditions()
        
        # Don't move if bus is at stop
        if bus.is_at_stop:
            # ENFORCEMENT: Force exact terminal coordinates if stopped at station
            if bus.status == 'stopped_at_station':
                route = self.routes[bus.route_id]
                terminal_stop = route.stops[0] if bus.direction == 'forward' else route.stops[-1]
                bus.current_lat = terminal_stop.latitude
                bus.current_lng = terminal_stop.longitude

            if not bus.should_leave_stop():
                bus.last_update = datetime.now()
                return
        
        # Calculate new position
        new_lat, new_lng = self.calculate_next_position(bus)
        bus.current_lat = new_lat
        bus.current_lng = new_lng
        bus.last_update = datetime.now()
        
        # Save to database (only if route is active to reduce DB load)
        if bus.route_id in self.active_routes:
            self.db_manager.save_bus(bus)
    
    # ORIGINAL METHOD: Preserved exactly
    def get_available_routes(self) -> List[Dict]:
        """Get list of available routes for frontend selection"""
        return [
            {
                'route_id': route.route_id,
                'name': route.name,
                'source': route.source,
                'destination': route.destination,
                'total_distance': route.total_distance,
                'stops_count': len(route.stops),
                'color': self.route_colors.get(route.route_id, '#007cba'),
                'active': route.route_id in self.active_routes,
                'background_buses': len([b for b in self.buses.values() if b.route_id == route.route_id]),
                'scheduled_buses': self.route_schedules.get(route.route_id, {}).get('total_buses_count', 0)
            }
            for route in self.routes.values()
        ]
    
    # ORIGINAL METHOD: Preserved exactly
    def activate_route_with_bidirectional_service(self, route_id: str, num_buses: int = 10):
        """Enhanced activate_route method that immediately starts buses from both terminals"""
        if route_id not in self.routes:
            print(f"❌ Route {route_id} not found")
            return False
        
        if route_id in self.active_routes:
            print(f"⚠️ Route {route_id} already active")
            return True
        
        route = self.routes[route_id]
        
        # Activate the route
        self.active_routes.add(route_id)
        
        # Initialize/update scheduling for bidirectional service
        current_time = datetime.now()
        self.route_schedules[route_id] = {
            'active': True,
            'total_buses_count': 0,
            'forward_buses_count': 0,
            'reverse_buses_count': 0,
            'next_forward_departure': current_time + timedelta(seconds=5),  # First forward bus in 5 seconds
            'next_reverse_departure': current_time + timedelta(seconds=10), # First reverse bus in 10 seconds
        }
        
        # Immediately create initial buses from both terminals for instant service
        max_buses = min(num_buses, self.max_buses_per_route)
        initial_buses_per_direction = min(2, max_buses // 2)  # Start with 1-2 buses per direction
        
        created_buses = []
        
        # Create initial forward direction bus from source
        for i in range(initial_buses_per_direction):
            bus_id = self.create_new_bus(route_id, direction='forward')
            if bus_id:
                bus = self.buses[bus_id]
                bus.stop_duration = random.randint(5, 15) + (i * 5)  # Stagger departures
                created_buses.append(bus_id)
                self.route_schedules[route_id]['forward_buses_count'] += 1
                self.route_schedules[route_id]['total_buses_count'] += 1
        
        # Create initial reverse direction bus from destination  
        for i in range(initial_buses_per_direction):
            bus_id = self.create_new_bus(route_id, direction='reverse')
            if bus_id:
                bus = self.buses[bus_id]
                bus.stop_duration = random.randint(5, 15) + (i * 5)  # Stagger departures
                created_buses.append(bus_id)
                self.route_schedules[route_id]['reverse_buses_count'] += 1
                self.route_schedules[route_id]['total_buses_count'] += 1
        
        print(f"✅ Activated route {route_id} with bidirectional service:")
        print(f"   • {initial_buses_per_direction} buses starting from {route.source} (forward)")
        print(f"   • {initial_buses_per_direction} buses starting from {route.destination} (reverse)")
        print(f"   • Additional buses will depart from both terminals every {self.departure_interval} seconds")
        print(f"   • Maximum buses scheduled: {max_buses}")
        
        return True
    
    # Use this method as the main activate_route method
    def activate_route(self, route_id: str, num_buses: int = 10):
        """Main route activation method with bidirectional service"""
        return self.activate_route_with_bidirectional_service(route_id, num_buses)
    
    # ORIGINAL METHOD: Preserved exactly  
    def deactivate_route(self, route_id: str):
        """Deactivate a route (buses continue in background)"""
        if route_id not in self.active_routes:
            print(f"⚠️ Route {route_id} not active")
            return
        
        # Deactivate the route
        self.active_routes.remove(route_id)
        
        # Stop scheduling new departures
        if route_id in self.route_schedules:
            self.route_schedules[route_id]['active'] = False
        
        # Count buses that will continue in background
        background_buses = [b for b in self.buses.values() if b.route_id == route_id]
        
        print(f"✅ Deactivated route {route_id} ({len(background_buses)} buses continue in background)")
    
    # ORIGINAL METHOD: Preserved exactly
    def start_simulation(self):
        """Start the enhanced simulation with bidirectional scheduling"""
        self.simulation_running = True
        
        def simulation_loop():
            print("🔄 Starting enhanced bidirectional simulation loop with scheduling...")
            update_counter = 0
            
            while self.simulation_running:
                try:
                    # Process scheduled departures from both terminals
                    self.process_scheduled_departures()
                    
                    # Update all buses
                    for bus in list(self.buses.values()):  # Use list() to avoid modification during iteration
                        self.update_bus_position(bus)
                    
                    update_counter += 1
                    if update_counter % 20 == 0:  # Log every minute
                        active_buses = len([b for b in self.buses.values() if b.route_id in self.active_routes])
                        background_buses = len(self.buses) - active_buses
                        scheduled_routes = len([r for r in self.route_schedules.values() if r['active']])
                        
                        # Count forward and reverse buses
                        forward_count = len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'forward'])
                        reverse_count = len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'reverse'])
                        
                        print(f"🚌 Enhanced bidirectional simulation update #{update_counter}: "
                              f"{active_buses} visible buses ({forward_count} forward, {reverse_count} reverse), "
                              f"{background_buses} background buses, {scheduled_routes} routes with active scheduling")
                    
                    time.sleep(3)  # Update every 3 seconds
                    
                except Exception as e:
                    print(f"❌ Error in simulation loop: {e}")
                    time.sleep(1)
            
            print("🛑 Enhanced bidirectional simulation loop stopped")
        
        simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
        simulation_thread.start()
        print("🚌 Enhanced bidirectional multi-route bus simulation with scheduling started!")
    
    # ORIGINAL METHOD: Preserved exactly
    def stop_simulation(self):
        """Stop the bus simulation"""
        self.simulation_running = False
        print("🛑 Enhanced bidirectional multi-route bus simulation stopped!")
    
    # ORIGINAL METHOD: Preserved exactly
    def get_bidirectional_statistics(self, route_id: str) -> Dict:
        """Get statistics for bidirectional bus service on a specific route"""
        if route_id not in self.routes:
            return {}
        
        route = self.routes[route_id]
        route_buses = [b for b in self.buses.values() if b.route_id == route_id]
        
        forward_buses = [b for b in route_buses if b.direction == 'forward']
        reverse_buses = [b for b in route_buses if b.direction == 'reverse']
        
        # Get schedule information
        schedule = self.route_schedules.get(route_id, {})
        
        return {
            'route_id': route_id,
            'route_name': route.name,
            'total_buses': len(route_buses),
            'forward_direction': {
                'count': len(forward_buses),
                'terminal': route.source,
                'destination': route.destination,
                'buses_at_stops': len([b for b in forward_buses if b.is_at_stop]),
                'average_speed': sum(b.speed for b in forward_buses) / len(forward_buses) if forward_buses else 0,
                'scheduled_count': schedule.get('forward_buses_count', 0)
            },
            'reverse_direction': {
                'count': len(reverse_buses), 
                'terminal': route.destination,
                'destination': route.source,
                'buses_at_stops': len([b for b in reverse_buses if b.is_at_stop]),
                'average_speed': sum(b.speed for b in reverse_buses) / len(reverse_buses) if reverse_buses else 0,
                'scheduled_count': schedule.get('reverse_buses_count', 0)
            },
            'service_balance': {
                'forward_percentage': (len(forward_buses) / len(route_buses) * 100) if route_buses else 0,
                'reverse_percentage': (len(reverse_buses) / len(route_buses) * 100) if route_buses else 0,
                'total_scheduled': schedule.get('total_buses_count', 0)
            },
            'scheduling_info': {
                'departure_interval': self.departure_interval,
                'max_buses': self.max_buses_per_route,
                'next_forward': schedule.get('next_forward_departure').isoformat() if schedule.get('next_forward_departure') else None,  # ✅ Add .isoformat()
                'next_reverse': schedule.get('next_reverse_departure').isoformat() if schedule.get('next_reverse_departure') else None   # ✅ Add .isoformat()
            }
        }
    
    # ORIGINAL METHOD: Enhanced with traffic and ETA data
    def get_simulation_data_with_bidirectional_info(self) -> Dict:
        """Enhanced simulation data with bidirectional service information"""
        # Get existing simulation data
        data = self.get_simulation_data()  # Your existing method
        
        # NEW: Add traffic and ETA data
        data['traffic_segments'] = self.get_traffic_data_for_frontend()
        data['bus_etas'] = self.get_all_bus_etas()
        
        # Add bidirectional statistics for active routes
        bidirectional_stats = {}
        for route_id in self.active_routes:
            bidirectional_stats[route_id] = self.get_bidirectional_statistics(route_id)
        
        # Add to existing data
        data['bidirectional_service'] = bidirectional_stats
        data['service_summary'] = {
            'total_terminals_served': len(self.active_routes) * 2,  # Each route serves 2 terminals
            'bidirectional_routes': len(self.active_routes),
            'forward_buses': len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'forward']),
            'reverse_buses': len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'reverse'])
        }
        
        # NEW: Add traffic statistics
        if self.traffic_segments:
            all_traffic_levels = [s.current_traffic_level for s in self.traffic_segments.values()]
            data['traffic_statistics'] = {
                'total_segments': len(self.traffic_segments),
                'average_traffic_level': sum(all_traffic_levels) / len(all_traffic_levels) if all_traffic_levels else 1.0,
                'heavy_traffic_segments': len([l for l in all_traffic_levels if l <= 0.3]),
                'moderate_traffic_segments': len([l for l in all_traffic_levels if 0.3 < l <= 0.6]),
                'light_traffic_segments': len([l for l in all_traffic_levels if l > 0.6]),
                'last_traffic_update': self.last_traffic_update.isoformat()
            }
        
        return data
    
    # ORIGINAL METHOD: Preserved exactly (your original get_simulation_data)
    def get_simulation_data(self) -> Dict:
        """Get current simulation state for active (visible) routes only"""
        buses_data = []
        for bus in self.buses.values():
            if bus.route_id in self.active_routes:
                bus_dict = asdict(bus)
                bus_dict['last_update'] = bus.last_update.isoformat()
                
                # ✅ Convert stop_start_time
                if hasattr(bus, 'stop_start_time') and bus.stop_start_time:
                    bus_dict['stop_start_time'] = bus.stop_start_time.isoformat()
                else:
                    bus_dict['stop_start_time'] = None
                
                # ✅ Convert departure_time
                if hasattr(bus, 'departure_time') and bus.departure_time:
                    bus_dict['departure_time'] = bus.departure_time.isoformat()
                else:
                    bus_dict['departure_time'] = None
                
                # ✅ FIX: Get ETAs and convert ALL datetime objects in them
                etas = self.eta_predictor.predict_eta_to_stops(bus, self.routes[bus.route_id], self.traffic_segments)
                
                # Convert datetime objects in ETAs to ISO strings
                etas_serializable = {}
                for stop_idx, eta_data in etas.items():
                    etas_serializable[stop_idx] = {
                        'stop_name': eta_data['stop_name'],
                        'eta_minutes': eta_data['eta_minutes'],
                        'eta_datetime': eta_data['eta_datetime'].isoformat(),  # ← Convert to string!
                        'confidence': eta_data['confidence']
                    }
                bus_dict['etas'] = etas_serializable
                
                # Get dynamic color based on status
                status_color = bus.get_status_color() if hasattr(bus, 'get_status_color') else None
                if status_color:
                    bus_dict['color'] = status_color
                else:
                    bus_dict['color'] = self.route_colors.get(bus.route_id, '#007cba')
                
                # Add detailed status
                bus_dict['detailed_status'] = bus.get_detailed_status() if hasattr(bus, 'get_detailed_status') else bus.status
                
                buses_data.append(bus_dict)
        
        # Convert routes to JSON-serializable format - only for active routes
        routes_data = {}
        for route_id, route in self.routes.items():
            if route_id in self.active_routes:
                routes_data[route_id] = {
                    'route_id': route.route_id,
                    'name': route.name,
                    'source': route.source,
                    'destination': route.destination,
                    'total_distance': route.total_distance,
                    'color': self.route_colors.get(route_id, '#007cba'),
                    'stops': [asdict(stop) for stop in route.stops]
                }
        
        # Add scheduling information
        scheduling_data = {}
        for route_id, schedule in self.route_schedules.items():
            if route_id in self.active_routes:
                scheduling_data[route_id] = {
                    'active': schedule['active'],
                    'total_buses_count': schedule.get('total_buses_count', 0),
                    'forward_buses_count': schedule.get('forward_buses_count', 0),
                    'reverse_buses_count': schedule.get('reverse_buses_count', 0),
                    'max_buses': self.max_buses_per_route,
                    'departure_interval': self.departure_interval,
                    'next_forward_departure': schedule.get('next_forward_departure', '').isoformat() if schedule.get('next_forward_departure') else None,
                    'next_reverse_departure': schedule.get('next_reverse_departure', '').isoformat() if schedule.get('next_reverse_departure') else None
                }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'buses': buses_data,
            'routes': routes_data,
            'available_routes': self.get_available_routes(),
            'active_routes': list(self.active_routes),
            'total_background_buses': len(self.buses),
            'visible_buses': len(buses_data),
            'scheduling': scheduling_data,
            'total_stops': sum(len(route.stops) for route in self.routes.values() if route.route_id in self.active_routes)
        }
    
    # ORIGINAL METHOD: Enhanced with traffic information
    def get_route_statistics(self) -> Dict:
        """Get enhanced statistics about all routes and buses"""
        stats = {
            'total_routes': len(self.routes),
            'active_routes': len(self.active_routes),
            'total_buses': len(self.buses),
            'buses_by_status': {},
            'routes_detail': {},
            'scheduling_stats': {
                'routes_with_active_scheduling': len([r for r in self.route_schedules.values() if r.get('active', False)]),
                'total_scheduled_buses': sum(r.get('total_buses_count', 0) for r in self.route_schedules.values()),
                'departure_interval': self.departure_interval,
                'max_buses_per_route': self.max_buses_per_route
            }
        }
        
        # NEW: Add traffic overview
        if self.traffic_segments:
            all_traffic_levels = [s.current_traffic_level for s in self.traffic_segments.values()]
            stats['traffic_overview'] = {
                'total_segments': len(self.traffic_segments),
                'segments_by_traffic_level': {
                    'heavy': len([l for l in all_traffic_levels if l <= 0.3]),
                    'moderate': len([l for l in all_traffic_levels if 0.3 < l <= 0.6]),
                    'light': len([l for l in all_traffic_levels if 0.6 < l <= 0.9]),
                    'free_flow': len([l for l in all_traffic_levels if l > 0.9])
                }
            }
        
        # NEW: Add ETA statistics
        all_etas = self.get_all_bus_etas()
        stats['eta_statistics'] = {
            'buses_with_etas': len(all_etas),
            'average_confidence': 0.7  # Simplified for now
        }
        
        # Count buses by status
        for bus in self.buses.values():
            status = bus.status
            if hasattr(bus, 'is_at_stop') and bus.is_at_stop:
                status = 'at_stop'
            stats['buses_by_status'][status] = stats['buses_by_status'].get(status, 0) + 1
        
        # Enhanced route details with bidirectional information
        for route_id, route in self.routes.items():
            route_buses = [b for b in self.buses.values() if b.route_id == route_id]
            forward_buses = [b for b in route_buses if b.direction == 'forward']
            reverse_buses = [b for b in route_buses if b.direction == 'reverse']
            schedule = self.route_schedules.get(route_id, {})
            
            stats['routes_detail'][route_id] = {
                'name': route.name,
                'active': route_id in self.active_routes,
                'buses_count': len(route_buses),
                'forward_buses': len(forward_buses),
                'reverse_buses': len(reverse_buses),
                'buses_at_stops': len([b for b in route_buses if hasattr(b, 'is_at_stop') and b.is_at_stop]),
                'average_speed': sum(b.speed for b in route_buses) / len(route_buses) if route_buses else 0,
                'scheduled_total_buses': schedule.get('total_buses_count', 0),
                'scheduled_forward_buses': schedule.get('forward_buses_count', 0),
                'scheduled_reverse_buses': schedule.get('reverse_buses_count', 0),
                'scheduling_active': schedule.get('active', False),
                'next_forward_departure': schedule.get('next_forward_departure').isoformat() if schedule.get('next_forward_departure') else None,
                'next_reverse_departure': schedule.get('next_reverse_departure').isoformat() if schedule.get('next_reverse_departure') else None
            }
        
        return stats

# Backward compatibility aliases - PRESERVED
MultiRouteBusSimulator = EnhancedMultiRouteBusSimulator
=======
# Enhanced bus_simulator.py - PRESERVING ALL ORIGINAL FUNCTIONALITY + Adding Traffic & ETA

import math
import time
import threading
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
from dataclasses import asdict
from geopy.distance import geodesic
from models import Route, Bus
from database_manager import DatabaseManager
import json
from datetime import datetime

def serialize_for_json(obj):
    """Recursively convert datetime objects to ISO strings for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj

class TrafficSegment:
    """NEW: Represents a traffic segment between two stops"""
    def __init__(self, start_stop, end_stop, route_id):
        self.start_stop = start_stop
        self.end_stop = end_stop
        self.route_id = route_id
        self.segment_id = f"{route_id}_{start_stop.name}_{end_stop.name}"
        self.distance = geodesic(
            (start_stop.latitude, start_stop.longitude),
            (end_stop.latitude, end_stop.longitude)
        ).kilometers
        
        self.current_traffic_level = random.uniform(0.3, 1.2)
        self.base_speed_limit = 40  # km/h
        self.last_updated = datetime.now()
        
    def update_traffic_conditions(self):
        """Update traffic conditions based on time and random factors"""
        current_hour = datetime.now().hour
        
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            base_factor = 0.4
        elif 22 <= current_hour or current_hour <= 6:
            base_factor = 1.1
        else:
            base_factor = 0.8
            
        random_change = random.uniform(-0.15, 0.15)
        self.current_traffic_level = max(0.2, min(1.5, 
            base_factor + random_change + random.uniform(-0.1, 0.1)))
        
        if random.random() < 0.03:
            event = random.choice(['accident', 'construction', 'clear_road', 'weather'])
            if event == 'accident':
                self.current_traffic_level = random.uniform(0.1, 0.3)
            elif event == 'construction':
                self.current_traffic_level = random.uniform(0.2, 0.4)
            elif event == 'weather':
                self.current_traffic_level = random.uniform(0.3, 0.6)
            elif event == 'clear_road':
                self.current_traffic_level = random.uniform(1.1, 1.4)
                
        self.last_updated = datetime.now()
    
    def get_effective_speed(self):
        return self.base_speed_limit * self.current_traffic_level
    
    def get_traffic_color(self):
        if self.current_traffic_level <= 0.3:
            return "#DC3545"  # Red - Heavy traffic
        elif self.current_traffic_level <= 0.6:
            return "#FFC107"  # Yellow - Moderate traffic
        elif self.current_traffic_level <= 0.9:
            return "#28A745"  # Green - Light traffic
        else:
            return "#007CBA"  # Blue - Very light traffic
    
    def get_traffic_description(self):
        if self.current_traffic_level <= 0.3:
            return "Heavy Traffic"
        elif self.current_traffic_level <= 0.6:
            return "Moderate Traffic"
        elif self.current_traffic_level <= 0.9:
            return "Light Traffic"
        else:
            return "Free Flow"

class AIETAPredictor:
    """NEW: AI-based ETA prediction system"""
    def __init__(self):
        self.historical_data = {}
        self.learning_rate = 0.1
        self.weights = {
            'distance': 1.0,
            'traffic': 0.8,
            'time_of_day': 0.6,
            'stops': 0.4,
            'historical': 0.7
        }
        
    def predict_segment_time(self, traffic_segment, current_time=None):
        if current_time is None:
            current_time = datetime.now()
            
        base_time = (traffic_segment.distance / traffic_segment.get_effective_speed()) * 60
        
        hour = current_time.hour
        time_factor = 1.0
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            time_factor = 1.3
        elif 22 <= hour or hour <= 6:
            time_factor = 0.8
            
        predicted_time = base_time * time_factor
        predicted_time *= (1 + random.uniform(-0.1, 0.1))
        
        return max(0.5, predicted_time)
    
    def predict_eta_to_stops(self, bus, route, traffic_segments):
        current_time = datetime.now()
        etas = {}
        cumulative_time = 0
        
        current_stop_index = bus.next_stop_index
        direction = bus.direction
        
        if direction == 'reverse':
            stop_indices = list(range(current_stop_index, -1, -1))
        else:
            stop_indices = list(range(current_stop_index, len(route.stops)))
        
        for i, stop_index in enumerate(stop_indices):
            if i == 0:
                continue
                
            prev_index = stop_indices[i-1]
            curr_index = stop_index
            
            segment_key = f"{route.route_id}_{prev_index}_{curr_index}"
            if segment_key in traffic_segments:
                segment = traffic_segments[segment_key]
                segment_time = self.predict_segment_time(segment, current_time)
                cumulative_time += segment_time
                
                if i < len(stop_indices) - 1:
                    dwell_time = 0.5 + random.uniform(0, 0.5)
                    cumulative_time += dwell_time
                    
            eta_datetime = current_time + timedelta(minutes=cumulative_time)
            etas[stop_index] = {
                'stop_name': route.stops[stop_index].name,
                'eta_minutes': cumulative_time,
                'eta_datetime': eta_datetime,
                'confidence': random.uniform(0.6, 0.9)  # Simplified confidence
            }
            
        return etas

# ORIGINAL CLASS WITH ENHANCEMENTS ADDED
class EnhancedMultiRouteBusSimulator:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.routes = {}
        self.buses = {}  # All buses (running in background)
        self.simulation_running = False
        self.active_routes = set()  # Only controls visibility, not simulation
        self.background_routes = set()  # Routes running in background
        
        # NEW: Traffic and ETA systems (ADDED without removing original features)
        self.traffic_segments = {}
        self.eta_predictor = AIETAPredictor()
        self.traffic_update_interval = 30
        self.last_traffic_update = datetime.now()
        
        # ORIGINAL: Route colors (PRESERVED)
        self.route_colors = {
            'FR-01': '#007cba',  # Blue
            'FR-02': '#dc3545',  # Red
            'FR-03A': '#28a745', # Green
            'FR-03B': '#17a2b8', # Cyan
            'FR-04': '#ffc107',  # Yellow
            'FR-04A': '#fd7e14', # Orange
            'FR-05': '#6f42c1',  # Purple
            'FR-06': '#e83e8c',  # Pink
            'FR-07': '#20c997',  # Teal
            'FR-08A': '#6c757d', # Gray
            'FR-08B': '#343a40', # Dark
            'FR-08C': '#495057', # Dark Gray
            'FR-09': '#fd7e14', # Orange variant
            'FR-10': '#20c997', # Teal variant
            'FR-11': '#e83e8c', # Pink variant
            'FR-12': '#6f42c1', # Purple variant
            'FR-13': '#dc3545', # Red variant
            'FR-14': '#28a745', # Green variant
            'FR-14A': '#17a2b8',# Cyan variant
            'FR-15': '#ffc107'  # Yellow variant
        }
        
        # ORIGINAL: Enhanced scheduling system (PRESERVED)
        self.route_schedules = {}  # Track next departure times
        self.max_buses_per_route = 10  # Maximum buses per route
        self.departure_interval = 10  # Seconds between departures
        self.bus_counters = {}  # Counter for bus numbering
        
        # ORIGINAL: Load and initialize everything (PRESERVED ORDER)
        self.load_all_routes()
        self.initialize_traffic_system()  # NEW: Added traffic system
        self.initialize_scheduling_system()
        self.initialize_background_simulation()
    
    # ORIGINAL METHOD: Preserved exactly
    def load_all_routes(self):
        """Load all route data from database"""
        all_routes = self.db_manager.get_all_routes()
        
        for route_info in all_routes:
            route_id = route_info['route_id']
            stops = self.db_manager.get_route_stops(route_id)
            
            if stops:  # Only create route if it has stops
                route = Route(
                    route_id=route_id,
                    name=route_info['name'],
                    source=route_info['source'],
                    destination=route_info['destination'],
                    stops=stops
                )
                
                # Calculate total distance
                total_distance = 0.0
                for i in range(len(stops) - 1):
                    current = (stops[i].latitude, stops[i].longitude)
                    next_stop = (stops[i + 1].latitude, stops[i + 1].longitude)
                    total_distance += geodesic(current, next_stop).kilometers
                
                route.total_distance = total_distance
                self.routes[route_id] = route
                print(f"✅ Loaded route {route_id}: {len(stops)} stops, {total_distance:.2f} km")
    
    # NEW METHOD: Added traffic system initialization
    def initialize_traffic_system(self):
        """Initialize the traffic monitoring system"""
        print("🚦 Initializing traffic monitoring system...")
        
        for route_id, route in self.routes.items():
            for i in range(len(route.stops) - 1):
                start_stop = route.stops[i]
                end_stop = route.stops[i + 1]
                
                segment_forward = TrafficSegment(start_stop, end_stop, route_id)
                segment_key_forward = f"{route_id}_{i}_{i+1}"
                self.traffic_segments[segment_key_forward] = segment_forward
                
                segment_reverse = TrafficSegment(end_stop, start_stop, route_id)
                segment_key_reverse = f"{route_id}_{i+1}_{i}"
                self.traffic_segments[segment_key_reverse] = segment_reverse
        
        print(f"✅ Traffic system initialized with {len(self.traffic_segments)} segments")
    
    # NEW METHODS: Traffic management
    def update_traffic_conditions(self):
        current_time = datetime.now()
        if (current_time - self.last_traffic_update).seconds < self.traffic_update_interval:
            return
            
        for segment in self.traffic_segments.values():
            segment.update_traffic_conditions()
            
        self.last_traffic_update = current_time
    
    def get_traffic_data_for_frontend(self):
        traffic_data = {}
        
        for segment_id, segment in self.traffic_segments.items():
            traffic_data[segment_id] = {
                'segment_id': segment_id,
                'route_id': segment.route_id,
                'start_lat': segment.start_stop.latitude,
                'start_lng': segment.start_stop.longitude,
                'end_lat': segment.end_stop.latitude,
                'end_lng': segment.end_stop.longitude,
                'traffic_level': segment.current_traffic_level,
                'traffic_color': segment.get_traffic_color(),
                'traffic_description': segment.get_traffic_description(),
                'effective_speed': segment.get_effective_speed(),
                'distance': segment.distance,
                'last_updated': segment.last_updated.isoformat()
            }
        
        return traffic_data
    
    def get_all_bus_etas(self):
        all_etas = {}
        
        for bus_id, bus in self.buses.items():
            if bus.route_id in self.active_routes:
                route = self.routes.get(bus.route_id)
                if route:
                    etas = self.eta_predictor.predict_eta_to_stops(bus, route, self.traffic_segments)
                    if etas:
                        all_etas[bus_id] = etas
                        
        return all_etas
    
    # ORIGINAL METHOD: Preserved exactly
    def initialize_scheduling_system(self):
        """Initialize the enhanced scheduling system for all routes"""
        print("📅 Initializing enhanced scheduling system...")
        
        current_time = datetime.now()
        
        for route_id in self.routes.keys():
            # Initialize schedule for each route with bidirectional tracking
            self.route_schedules[route_id] = {
                'next_forward_departure': current_time + timedelta(seconds=random.randint(0, 30)),
                'next_reverse_departure': current_time + timedelta(seconds=random.randint(5, 35)),  # Offset reverse
                'forward_buses_count': 0,
                'reverse_buses_count': 0,
                'total_buses_count': 0,
                'active': False  # Will be set to True when route is activated
            }
            self.bus_counters[route_id] = 0
            
        print(f"✅ Scheduling system initialized for {len(self.routes)} routes")
    
    # ORIGINAL METHOD: Preserved exactly
    def initialize_background_simulation(self):
        """Initialize a minimal background simulation (fewer buses initially)"""
        print("🔄 Initializing background simulation...")
        
        # Start with just 1 bus per route for background activity
        for route_id, route in self.routes.items():
            self.create_new_bus(route_id, direction='forward', is_initial=True)
            self.background_routes.add(route_id)
        
        print(f"✅ Background simulation initialized with {len(self.buses)} buses")
    
    # ORIGINAL METHOD: Preserved exactly
    def create_new_bus(self, route_id: str, direction: str = 'forward', is_initial: bool = False) -> str:
        """Create a new bus for the specified route and direction"""
        if route_id not in self.routes:
            return None

        route = self.routes[route_id]
        self.bus_counters[route_id] += 1
        bus_number = self.bus_counters[route_id]

        direction_code = 'F' if direction == 'forward' else 'R'
        bus_id = f"{route_id}-{direction_code}-{bus_number:03d}"

        # Always start at the terminal stop
        if direction == 'forward':
            start_index = 0
            next_stop_index = 1
        else:
            start_index = len(route.stops) - 1
            next_stop_index = start_index - 1

        start_stop = route.stops[start_index]

        bus = Bus(
            bus_id=bus_id,
            route_id=route_id,
            current_lat=start_stop.latitude,
            current_lng=start_stop.longitude,
            speed=0.0,
            status='stopped_at_station' if not is_initial else 'moving',
            next_stop_index=next_stop_index,
            last_update=datetime.now(),
            direction=direction
        )
        
        # Initialize enhanced properties
        bus.base_speed = random.uniform(25, 40)
        bus.target_speed = bus.base_speed
        bus.traffic_factor = random.uniform(0.8, 1.2)
        bus.departure_number = bus_number - 1  # For tracking
        bus.departure_time = datetime.now()
        
        # If starting at station, initialize stop sequence
        if not is_initial:
            bus.is_at_stop = True
            bus.stop_start_time = datetime.now()
            bus.stop_duration = random.randint(10, 30)  # Initial boarding time

        self.buses[bus_id] = bus

        terminal_name = route.source if direction == 'forward' else route.destination
        destination_name = route.destination if direction == 'forward' else route.source
        print(f"🚌 Created {direction} bus {bus_id} at {terminal_name} → {destination_name}")
        print(f"📍 Bus {bus_id} initial coords: {start_stop.latitude}, {start_stop.longitude}")
        return bus_id

    def add_extra_bus(self, route_id: str):
        """Manually add an extra bus to a route (Deploy Extra Service)"""
        if route_id not in self.routes:
            return False, "Route not found"
        
        # Create a new bus in forward direction
        bus_id = self.create_new_bus(route_id, direction='forward')
        
        if bus_id:
            return True, f"Extra bus {bus_id} deployed successfully on {route_id}"
        else:
            return False, "Failed to create bus"
    
    # ORIGINAL METHODS: All scheduling and bus management preserved exactly
    def schedule_next_departure(self, route_id: str, direction: str):
        """Schedule the next bus departure for a route in specified direction"""
        if route_id not in self.route_schedules:
            return
        
        schedule = self.route_schedules[route_id]
        
        # Only schedule if route is active and under bus limit
        if schedule['active'] and schedule['total_buses_count'] < self.max_buses_per_route:
            
            # Schedule next departure based on direction
            next_time = datetime.now() + timedelta(seconds=self.departure_interval)
            
            if direction == 'forward':
                schedule['next_forward_departure'] = next_time
            else:
                schedule['next_reverse_departure'] = next_time
            
            route = self.routes[route_id]
            terminal = route.source if direction == 'forward' else route.destination
            print(f"📅 Next {direction} {route_id} departure scheduled for {next_time.strftime('%H:%M:%S')} from {terminal}")
    
    def process_scheduled_departures(self):
        """Process scheduled departures from both terminals with alternating pattern"""
        current_time = datetime.now()
        
        for route_id, schedule in self.route_schedules.items():
            if not schedule['active'] or route_id not in self.active_routes:
                continue
            
            route = self.routes[route_id]
            
            # Check forward direction departures
            if (schedule['total_buses_count'] < self.max_buses_per_route and 
                current_time >= schedule['next_forward_departure']):
                
                # Create forward bus from source
                bus_id = self.create_new_bus(route_id, direction='forward')
                if bus_id:
                    schedule['forward_buses_count'] += 1
                    schedule['total_buses_count'] += 1
                    self.schedule_next_departure(route_id, 'forward')
                    
                    print(f"🚌 Forward departure: Bus {bus_id} from {route.source} → {route.destination}")
            
            # Check reverse direction departures (independent scheduling)
            if (schedule['total_buses_count'] < self.max_buses_per_route and 
                current_time >= schedule['next_reverse_departure']):
                
                # Create reverse bus from destination
                bus_id = self.create_new_bus(route_id, direction='reverse')
                if bus_id:
                    schedule['reverse_buses_count'] += 1
                    schedule['total_buses_count'] += 1
                    self.schedule_next_departure(route_id, 'reverse')
                    
                    print(f"🚌 Reverse departure: Bus {bus_id} from {route.destination} → {route.source}")
    
    def handle_bus_completion(self, bus: Bus):
        """Handle bus when it completes the route (continue in same direction or turn around)"""
        route = self.routes[bus.route_id]
        
        if bus.direction == 'forward' and bus.next_stop_index >= len(route.stops):
            # Reached destination, start return journey
            bus.direction = 'reverse'
            bus.next_stop_index = len(route.stops) - 2  # Second to last stop
            
            # ✅ FIX: Set bus position to the last stop (destination terminal)
            terminal_stop = route.stops[-1]
            bus.current_lat = terminal_stop.latitude
            bus.current_lng = terminal_stop.longitude
            
            bus.status = 'stopped_at_station'
            bus.is_at_stop = True
            bus.stop_start_time = datetime.now()
            bus.stop_duration = random.randint(30, 60)  # Longer stop at terminal
            
            print(f"🔄 Bus {bus.bus_id} reached {route.destination}, starting return journey")
            
        elif bus.direction == 'reverse' and bus.next_stop_index < 0:
            # Reached source again, start new forward journey
            bus.direction = 'forward'
            bus.next_stop_index = 1
            
            # ✅ FIX: Set bus position to the first stop (source terminal)
            terminal_stop = route.stops[0]
            bus.current_lat = terminal_stop.latitude
            bus.current_lng = terminal_stop.longitude
            
            bus.status = 'stopped_at_station'
            bus.is_at_stop = True
            bus.stop_start_time = datetime.now()
            bus.stop_duration = random.randint(30, 60)  # Longer stop at terminal
            
            print(f"🔄 Bus {bus.bus_id} returned to {route.source}, starting new journey")
        
    # ORIGINAL METHOD: Preserved with minor enhancement for traffic
    def calculate_next_position(self, bus: Bus) -> Tuple[float, float]:
        """Calculate next GPS position with enhanced bidirectional movement"""
        route = self.routes[bus.route_id]
        
        # Handle route completion and direction changes
        self.handle_bus_completion(bus)
        
        # Get target stop based on direction
        if bus.direction == 'forward':
            if bus.next_stop_index >= len(route.stops):
                bus.next_stop_index = len(route.stops) - 1
        else:  # reverse
            if bus.next_stop_index < 0:
                bus.next_stop_index = 0
        
        target_stop = route.stops[bus.next_stop_index]
        
        current_pos = (bus.current_lat, bus.current_lng)
        target_pos = (target_stop.latitude, target_stop.longitude)
        
        # Calculate distance to target
        distance_to_target = geodesic(current_pos, target_pos).meters
        
        # Check if bus is currently at a stop
        if bus.is_at_stop:
            if bus.should_leave_stop():
                bus.leave_stop()
                return bus.current_lat, bus.current_lng
            else:
                # Bus is still at stop, don't move
                return bus.current_lat, bus.current_lng
        
        # Check if bus should stop at the target stop
        if distance_to_target < 50:  # 50 meters - arrived at stop
            bus.current_lat = target_stop.latitude
            bus.current_lng = target_stop.longitude
            bus.start_stop_sequence()
            
            # Prepare for next stop based on direction
            if bus.direction == 'forward':
                bus.next_stop_index += 1
            else:  # reverse
                bus.next_stop_index -= 1
            
            return bus.current_lat, bus.current_lng
        
        # Update speed based on distance to stop
        bus.update_speed_for_approach(distance_to_target)
        
        # Calculate movement step
        time_step = 3  # seconds
        speed_ms = bus.speed * 1000 / 3600  # convert km/h to m/s
        step_distance = speed_ms * time_step
        
        # Don't overshoot the target
        if step_distance > distance_to_target:
            step_distance = distance_to_target
        
        # Calculate bearing to target
        lat1, lng1 = math.radians(bus.current_lat), math.radians(bus.current_lng)
        lat2, lng2 = math.radians(target_stop.latitude), math.radians(target_stop.longitude)
        
        d_lng = lng2 - lng1
        y = math.sin(d_lng) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lng)
        bearing = math.atan2(y, x)
        
        # Calculate new position
        R = 6371000  # Earth's radius in meters
        lat1_rad = math.radians(bus.current_lat)
        lng1_rad = math.radians(bus.current_lng)
        
        new_lat = math.asin(
            math.sin(lat1_rad) * math.cos(step_distance / R) +
            math.cos(lat1_rad) * math.sin(step_distance / R) * math.cos(bearing)
        )
        
        new_lng = lng1_rad + math.atan2(
            math.sin(bearing) * math.sin(step_distance / R) * math.cos(lat1_rad),
            math.cos(step_distance / R) - math.sin(lat1_rad) * math.sin(new_lat)
        )
        
        return math.degrees(new_lat), math.degrees(new_lng)
    
    # MODIFIED: Enhanced with traffic awareness but preserves original behavior
    def update_bus_position(self, bus: Bus):
        """Update single bus position with enhanced behavior"""
        # NEW: Update traffic conditions periodically
        self.update_traffic_conditions()
        
        # Update traffic factor periodically
        if random.random() < 0.05:  # 5% chance per update
            bus.update_traffic_conditions()
        
        # Don't move if bus is at stop
        if bus.is_at_stop:
            # ENFORCEMENT: Force exact terminal coordinates if stopped at station
            if bus.status == 'stopped_at_station':
                route = self.routes[bus.route_id]
                terminal_stop = route.stops[0] if bus.direction == 'forward' else route.stops[-1]
                bus.current_lat = terminal_stop.latitude
                bus.current_lng = terminal_stop.longitude

            if not bus.should_leave_stop():
                bus.last_update = datetime.now()
                return
        
        # Calculate new position
        new_lat, new_lng = self.calculate_next_position(bus)
        bus.current_lat = new_lat
        bus.current_lng = new_lng
        bus.last_update = datetime.now()
        
        # Save to database (only if route is active to reduce DB load)
        if bus.route_id in self.active_routes:
            self.db_manager.save_bus(bus)
    
    # ORIGINAL METHOD: Preserved exactly
    def get_available_routes(self) -> List[Dict]:
        """Get list of available routes for frontend selection"""
        return [
            {
                'route_id': route.route_id,
                'name': route.name,
                'source': route.source,
                'destination': route.destination,
                'total_distance': route.total_distance,
                'stops_count': len(route.stops),
                'color': self.route_colors.get(route.route_id, '#007cba'),
                'active': route.route_id in self.active_routes,
                'background_buses': len([b for b in self.buses.values() if b.route_id == route.route_id]),
                'scheduled_buses': self.route_schedules.get(route.route_id, {}).get('total_buses_count', 0)
            }
            for route in self.routes.values()
        ]
    
    # ORIGINAL METHOD: Preserved exactly
    def activate_route_with_bidirectional_service(self, route_id: str, num_buses: int = 10):
        """Enhanced activate_route method that immediately starts buses from both terminals"""
        if route_id not in self.routes:
            print(f"❌ Route {route_id} not found")
            return False
        
        if route_id in self.active_routes:
            print(f"⚠️ Route {route_id} already active")
            return True
        
        route = self.routes[route_id]
        
        # Activate the route
        self.active_routes.add(route_id)
        
        # Initialize/update scheduling for bidirectional service
        current_time = datetime.now()
        self.route_schedules[route_id] = {
            'active': True,
            'total_buses_count': 0,
            'forward_buses_count': 0,
            'reverse_buses_count': 0,
            'next_forward_departure': current_time + timedelta(seconds=5),  # First forward bus in 5 seconds
            'next_reverse_departure': current_time + timedelta(seconds=10), # First reverse bus in 10 seconds
        }
        
        # Immediately create initial buses from both terminals for instant service
        max_buses = min(num_buses, self.max_buses_per_route)
        initial_buses_per_direction = min(2, max_buses // 2)  # Start with 1-2 buses per direction
        
        created_buses = []
        
        # Create initial forward direction bus from source
        for i in range(initial_buses_per_direction):
            bus_id = self.create_new_bus(route_id, direction='forward')
            if bus_id:
                bus = self.buses[bus_id]
                bus.stop_duration = random.randint(5, 15) + (i * 5)  # Stagger departures
                created_buses.append(bus_id)
                self.route_schedules[route_id]['forward_buses_count'] += 1
                self.route_schedules[route_id]['total_buses_count'] += 1
        
        # Create initial reverse direction bus from destination  
        for i in range(initial_buses_per_direction):
            bus_id = self.create_new_bus(route_id, direction='reverse')
            if bus_id:
                bus = self.buses[bus_id]
                bus.stop_duration = random.randint(5, 15) + (i * 5)  # Stagger departures
                created_buses.append(bus_id)
                self.route_schedules[route_id]['reverse_buses_count'] += 1
                self.route_schedules[route_id]['total_buses_count'] += 1
        
        print(f"✅ Activated route {route_id} with bidirectional service:")
        print(f"   • {initial_buses_per_direction} buses starting from {route.source} (forward)")
        print(f"   • {initial_buses_per_direction} buses starting from {route.destination} (reverse)")
        print(f"   • Additional buses will depart from both terminals every {self.departure_interval} seconds")
        print(f"   • Maximum buses scheduled: {max_buses}")
        
        return True
    
    # Use this method as the main activate_route method
    def activate_route(self, route_id: str, num_buses: int = 10):
        """Main route activation method with bidirectional service"""
        return self.activate_route_with_bidirectional_service(route_id, num_buses)
    
    # ORIGINAL METHOD: Preserved exactly  
    def deactivate_route(self, route_id: str):
        """Deactivate a route (buses continue in background)"""
        if route_id not in self.active_routes:
            print(f"⚠️ Route {route_id} not active")
            return
        
        # Deactivate the route
        self.active_routes.remove(route_id)
        
        # Stop scheduling new departures
        if route_id in self.route_schedules:
            self.route_schedules[route_id]['active'] = False
        
        # Count buses that will continue in background
        background_buses = [b for b in self.buses.values() if b.route_id == route_id]
        
        print(f"✅ Deactivated route {route_id} ({len(background_buses)} buses continue in background)")
    
    # ORIGINAL METHOD: Preserved exactly
    def start_simulation(self):
        """Start the enhanced simulation with bidirectional scheduling"""
        self.simulation_running = True
        
        def simulation_loop():
            print("🔄 Starting enhanced bidirectional simulation loop with scheduling...")
            update_counter = 0
            
            while self.simulation_running:
                try:
                    # Process scheduled departures from both terminals
                    self.process_scheduled_departures()
                    
                    # Update all buses
                    for bus in list(self.buses.values()):  # Use list() to avoid modification during iteration
                        self.update_bus_position(bus)
                    
                    update_counter += 1
                    if update_counter % 20 == 0:  # Log every minute
                        active_buses = len([b for b in self.buses.values() if b.route_id in self.active_routes])
                        background_buses = len(self.buses) - active_buses
                        scheduled_routes = len([r for r in self.route_schedules.values() if r['active']])
                        
                        # Count forward and reverse buses
                        forward_count = len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'forward'])
                        reverse_count = len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'reverse'])
                        
                        print(f"🚌 Enhanced bidirectional simulation update #{update_counter}: "
                              f"{active_buses} visible buses ({forward_count} forward, {reverse_count} reverse), "
                              f"{background_buses} background buses, {scheduled_routes} routes with active scheduling")
                    
                    time.sleep(3)  # Update every 3 seconds
                    
                except Exception as e:
                    print(f"❌ Error in simulation loop: {e}")
                    time.sleep(1)
            
            print("🛑 Enhanced bidirectional simulation loop stopped")
        
        simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
        simulation_thread.start()
        print("🚌 Enhanced bidirectional multi-route bus simulation with scheduling started!")
    
    # ORIGINAL METHOD: Preserved exactly
    def stop_simulation(self):
        """Stop the bus simulation"""
        self.simulation_running = False
        print("🛑 Enhanced bidirectional multi-route bus simulation stopped!")
    
    # ORIGINAL METHOD: Preserved exactly
    def get_bidirectional_statistics(self, route_id: str) -> Dict:
        """Get statistics for bidirectional bus service on a specific route"""
        if route_id not in self.routes:
            return {}
        
        route = self.routes[route_id]
        route_buses = [b for b in self.buses.values() if b.route_id == route_id]
        
        forward_buses = [b for b in route_buses if b.direction == 'forward']
        reverse_buses = [b for b in route_buses if b.direction == 'reverse']
        
        # Get schedule information
        schedule = self.route_schedules.get(route_id, {})
        
        return {
            'route_id': route_id,
            'route_name': route.name,
            'total_buses': len(route_buses),
            'forward_direction': {
                'count': len(forward_buses),
                'terminal': route.source,
                'destination': route.destination,
                'buses_at_stops': len([b for b in forward_buses if b.is_at_stop]),
                'average_speed': sum(b.speed for b in forward_buses) / len(forward_buses) if forward_buses else 0,
                'scheduled_count': schedule.get('forward_buses_count', 0)
            },
            'reverse_direction': {
                'count': len(reverse_buses), 
                'terminal': route.destination,
                'destination': route.source,
                'buses_at_stops': len([b for b in reverse_buses if b.is_at_stop]),
                'average_speed': sum(b.speed for b in reverse_buses) / len(reverse_buses) if reverse_buses else 0,
                'scheduled_count': schedule.get('reverse_buses_count', 0)
            },
            'service_balance': {
                'forward_percentage': (len(forward_buses) / len(route_buses) * 100) if route_buses else 0,
                'reverse_percentage': (len(reverse_buses) / len(route_buses) * 100) if route_buses else 0,
                'total_scheduled': schedule.get('total_buses_count', 0)
            },
            'scheduling_info': {
                'departure_interval': self.departure_interval,
                'max_buses': self.max_buses_per_route,
                'next_forward': schedule.get('next_forward_departure').isoformat() if schedule.get('next_forward_departure') else None,  # ✅ Add .isoformat()
                'next_reverse': schedule.get('next_reverse_departure').isoformat() if schedule.get('next_reverse_departure') else None   # ✅ Add .isoformat()
            }
        }
    
    # ORIGINAL METHOD: Enhanced with traffic and ETA data
    def get_simulation_data_with_bidirectional_info(self) -> Dict:
        """Enhanced simulation data with bidirectional service information"""
        # Get existing simulation data
        data = self.get_simulation_data()  # Your existing method
        
        # NEW: Add traffic and ETA data
        data['traffic_segments'] = self.get_traffic_data_for_frontend()
        data['bus_etas'] = self.get_all_bus_etas()
        
        # Add bidirectional statistics for active routes
        bidirectional_stats = {}
        for route_id in self.active_routes:
            bidirectional_stats[route_id] = self.get_bidirectional_statistics(route_id)
        
        # Add to existing data
        data['bidirectional_service'] = bidirectional_stats
        data['service_summary'] = {
            'total_terminals_served': len(self.active_routes) * 2,  # Each route serves 2 terminals
            'bidirectional_routes': len(self.active_routes),
            'forward_buses': len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'forward']),
            'reverse_buses': len([b for b in self.buses.values() if b.route_id in self.active_routes and b.direction == 'reverse'])
        }
        
        # NEW: Add traffic statistics
        if self.traffic_segments:
            all_traffic_levels = [s.current_traffic_level for s in self.traffic_segments.values()]
            data['traffic_statistics'] = {
                'total_segments': len(self.traffic_segments),
                'average_traffic_level': sum(all_traffic_levels) / len(all_traffic_levels) if all_traffic_levels else 1.0,
                'heavy_traffic_segments': len([l for l in all_traffic_levels if l <= 0.3]),
                'moderate_traffic_segments': len([l for l in all_traffic_levels if 0.3 < l <= 0.6]),
                'light_traffic_segments': len([l for l in all_traffic_levels if l > 0.6]),
                'last_traffic_update': self.last_traffic_update.isoformat()
            }
        
        return data
    
    # ORIGINAL METHOD: Preserved exactly (your original get_simulation_data)
    def get_simulation_data(self) -> Dict:
        """Get current simulation state for active (visible) routes only"""
        buses_data = []
        for bus in self.buses.values():
            if bus.route_id in self.active_routes:
                bus_dict = asdict(bus)
                bus_dict['last_update'] = bus.last_update.isoformat()
                
                # ✅ Convert stop_start_time
                if hasattr(bus, 'stop_start_time') and bus.stop_start_time:
                    bus_dict['stop_start_time'] = bus.stop_start_time.isoformat()
                else:
                    bus_dict['stop_start_time'] = None
                
                # ✅ Convert departure_time
                if hasattr(bus, 'departure_time') and bus.departure_time:
                    bus_dict['departure_time'] = bus.departure_time.isoformat()
                else:
                    bus_dict['departure_time'] = None
                
                # ✅ FIX: Get ETAs and convert ALL datetime objects in them
                etas = self.eta_predictor.predict_eta_to_stops(bus, self.routes[bus.route_id], self.traffic_segments)
                
                # Convert datetime objects in ETAs to ISO strings
                etas_serializable = {}
                for stop_idx, eta_data in etas.items():
                    etas_serializable[stop_idx] = {
                        'stop_name': eta_data['stop_name'],
                        'eta_minutes': eta_data['eta_minutes'],
                        'eta_datetime': eta_data['eta_datetime'].isoformat(),  # ← Convert to string!
                        'confidence': eta_data['confidence']
                    }
                bus_dict['etas'] = etas_serializable
                
                # Get dynamic color based on status
                status_color = bus.get_status_color() if hasattr(bus, 'get_status_color') else None
                if status_color:
                    bus_dict['color'] = status_color
                else:
                    bus_dict['color'] = self.route_colors.get(bus.route_id, '#007cba')
                
                # Add detailed status
                bus_dict['detailed_status'] = bus.get_detailed_status() if hasattr(bus, 'get_detailed_status') else bus.status
                
                buses_data.append(bus_dict)
        
        # Convert routes to JSON-serializable format - only for active routes
        routes_data = {}
        for route_id, route in self.routes.items():
            if route_id in self.active_routes:
                routes_data[route_id] = {
                    'route_id': route.route_id,
                    'name': route.name,
                    'source': route.source,
                    'destination': route.destination,
                    'total_distance': route.total_distance,
                    'color': self.route_colors.get(route_id, '#007cba'),
                    'stops': [asdict(stop) for stop in route.stops]
                }
        
        # Add scheduling information
        scheduling_data = {}
        for route_id, schedule in self.route_schedules.items():
            if route_id in self.active_routes:
                scheduling_data[route_id] = {
                    'active': schedule['active'],
                    'total_buses_count': schedule.get('total_buses_count', 0),
                    'forward_buses_count': schedule.get('forward_buses_count', 0),
                    'reverse_buses_count': schedule.get('reverse_buses_count', 0),
                    'max_buses': self.max_buses_per_route,
                    'departure_interval': self.departure_interval,
                    'next_forward_departure': schedule.get('next_forward_departure', '').isoformat() if schedule.get('next_forward_departure') else None,
                    'next_reverse_departure': schedule.get('next_reverse_departure', '').isoformat() if schedule.get('next_reverse_departure') else None
                }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'buses': buses_data,
            'routes': routes_data,
            'available_routes': self.get_available_routes(),
            'active_routes': list(self.active_routes),
            'total_background_buses': len(self.buses),
            'visible_buses': len(buses_data),
            'scheduling': scheduling_data,
            'total_stops': sum(len(route.stops) for route in self.routes.values() if route.route_id in self.active_routes)
        }
    
    # ORIGINAL METHOD: Enhanced with traffic information
    def get_route_statistics(self) -> Dict:
        """Get enhanced statistics about all routes and buses"""
        stats = {
            'total_routes': len(self.routes),
            'active_routes': len(self.active_routes),
            'total_buses': len(self.buses),
            'buses_by_status': {},
            'routes_detail': {},
            'scheduling_stats': {
                'routes_with_active_scheduling': len([r for r in self.route_schedules.values() if r.get('active', False)]),
                'total_scheduled_buses': sum(r.get('total_buses_count', 0) for r in self.route_schedules.values()),
                'departure_interval': self.departure_interval,
                'max_buses_per_route': self.max_buses_per_route
            }
        }
        
        # NEW: Add traffic overview
        if self.traffic_segments:
            all_traffic_levels = [s.current_traffic_level for s in self.traffic_segments.values()]
            stats['traffic_overview'] = {
                'total_segments': len(self.traffic_segments),
                'segments_by_traffic_level': {
                    'heavy': len([l for l in all_traffic_levels if l <= 0.3]),
                    'moderate': len([l for l in all_traffic_levels if 0.3 < l <= 0.6]),
                    'light': len([l for l in all_traffic_levels if 0.6 < l <= 0.9]),
                    'free_flow': len([l for l in all_traffic_levels if l > 0.9])
                }
            }
        
        # NEW: Add ETA statistics
        all_etas = self.get_all_bus_etas()
        stats['eta_statistics'] = {
            'buses_with_etas': len(all_etas),
            'average_confidence': 0.7  # Simplified for now
        }
        
        # Count buses by status
        for bus in self.buses.values():
            status = bus.status
            if hasattr(bus, 'is_at_stop') and bus.is_at_stop:
                status = 'at_stop'
            stats['buses_by_status'][status] = stats['buses_by_status'].get(status, 0) + 1
        
        # Enhanced route details with bidirectional information
        for route_id, route in self.routes.items():
            route_buses = [b for b in self.buses.values() if b.route_id == route_id]
            forward_buses = [b for b in route_buses if b.direction == 'forward']
            reverse_buses = [b for b in route_buses if b.direction == 'reverse']
            schedule = self.route_schedules.get(route_id, {})
            
            stats['routes_detail'][route_id] = {
                'name': route.name,
                'active': route_id in self.active_routes,
                'buses_count': len(route_buses),
                'forward_buses': len(forward_buses),
                'reverse_buses': len(reverse_buses),
                'buses_at_stops': len([b for b in route_buses if hasattr(b, 'is_at_stop') and b.is_at_stop]),
                'average_speed': sum(b.speed for b in route_buses) / len(route_buses) if route_buses else 0,
                'scheduled_total_buses': schedule.get('total_buses_count', 0),
                'scheduled_forward_buses': schedule.get('forward_buses_count', 0),
                'scheduled_reverse_buses': schedule.get('reverse_buses_count', 0),
                'scheduling_active': schedule.get('active', False),
                'next_forward_departure': schedule.get('next_forward_departure').isoformat() if schedule.get('next_forward_departure') else None,
                'next_reverse_departure': schedule.get('next_reverse_departure').isoformat() if schedule.get('next_reverse_departure') else None
            }
        
        return stats

# Backward compatibility aliases - PRESERVED
MultiRouteBusSimulator = EnhancedMultiRouteBusSimulator
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
BusSimulator = EnhancedMultiRouteBusSimulator