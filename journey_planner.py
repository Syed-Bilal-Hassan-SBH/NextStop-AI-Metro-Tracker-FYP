#!/usr/bin/env python3
"""
Intelligent Connection Builder for Enhanced Metro Bus System
- Multi-route journey planning with optimal transfers
- Real-time scheduling and ETA integration
- Smart transfer point suggestions
- Walk time calculations between stops
"""

import asyncio
import math
import heapq
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from geopy.distance import geodesic
import logging

@dataclass
class TransferPoint:
    """Represents a potential transfer location between routes"""
    stop_id: str
    stop_name: str
    latitude: float
    longitude: float
    routes: List[str] = field(default_factory=list)
    transfer_time_minutes: float = 5.0  # Default walking/waiting time
    accessibility_features: List[str] = field(default_factory=list)

@dataclass
class JourneySegment:
    """Individual segment of a multi-route journey"""
    route_id: str
    route_name: str
    boarding_stop: Dict[str, Any]
    alighting_stop: Dict[str, Any]
    departure_time: datetime
    arrival_time: datetime
    travel_time_minutes: float
    bus_id: Optional[str] = None
    direction: str = "forward"
    confidence: float = 0.8
    fare_cost: float = 0.0
    segment_color: str = "#667eea"

@dataclass
class Journey:
    """Complete multi-route journey plan"""
    origin: Dict[str, Any]
    destination: Dict[str, Any]
    segments: List[JourneySegment]
    total_travel_time: float
    total_walking_time: float
    total_waiting_time: float
    total_fare: float
    departure_time: datetime
    arrival_time: datetime
    transfers_count: int
    confidence_score: float
    journey_id: str
    carbon_footprint: float = 0.0
    accessibility_rating: float = 1.0

class IntelligentConnectionBuilder:
    """
    Advanced journey planning system for multi-route bus networks
    """
    
    def __init__(self, simulator, db_manager):
        self.simulator = simulator
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Journey planning parameters
        self.max_walking_distance_km = 0.5  # 500m max walk between stops
        self.max_transfers = 3
        self.transfer_buffer_minutes = 5  # Minimum connection time
        self.walking_speed_kmh = 4.5  # Average walking speed
        self.base_fare_per_route = 25.0  # Base fare per route segment
        
        # Cache for performance
        self.transfer_points_cache = {}
        self.route_connections_cache = {}
        self.journey_cache = {}
        
        # Initialize transfer points
        self._initialize_transfer_network()
    
    def _initialize_transfer_network(self):
        """Build network of potential transfer points between routes"""
        self.logger.info("Initializing intelligent transfer network...")
        
        if not self.simulator.routes:
            return
        
        transfer_candidates = {}
        
        # Analyze all route intersections
        for route1_id, route1 in self.simulator.routes.items():
            if not route1.stops:
                continue
                
            for route2_id, route2 in self.simulator.routes.items():
                if route1_id >= route2_id or not route2.stops:
                    continue
                
                # Find nearby stops between routes
                for stop1_idx, stop1 in enumerate(route1.stops):
                    for stop2_idx, stop2 in enumerate(route2.stops):
                        distance_km = self._calculate_distance(
                            stop1.latitude, stop1.longitude,
                            stop2.latitude, stop2.longitude
                        )
                        
                        if distance_km <= self.max_walking_distance_km:
                            # Create transfer point
                            transfer_key = f"{stop1.latitude:.4f},{stop1.longitude:.4f}"
                            
                            if transfer_key not in transfer_candidates:
                                transfer_candidates[transfer_key] = TransferPoint(
                                    stop_id=f"transfer_{len(transfer_candidates)}",
                                    stop_name=f"Transfer Hub near {stop1.name}",
                                    latitude=stop1.latitude,
                                    longitude=stop1.longitude,
                                    transfer_time_minutes=max(3, distance_km * 60 / self.walking_speed_kmh * 1000)
                                )
                            
                            # Add routes to this transfer point
                            if route1_id not in transfer_candidates[transfer_key].routes:
                                transfer_candidates[transfer_key].routes.append(route1_id)
                            if route2_id not in transfer_candidates[transfer_key].routes:
                                transfer_candidates[transfer_key].routes.append(route2_id)
        
        self.transfer_points_cache = transfer_candidates
        self.logger.info(f"Identified {len(transfer_candidates)} potential transfer points")
    
    async def plan_journey(self, origin_lat: float, origin_lng: float, 
                      dest_lat: float, dest_lng: float,
                      departure_time: Optional[datetime] = None,
                      preferences: Dict[str, Any] = None) -> List[Journey]:
        """
        Plan optimal multi-route journey with intelligent transfers
        """
        if departure_time is None:
            departure_time = datetime.now()
        
        if preferences is None:
            preferences = {}
        
        self.logger.info(f"Planning journey from ({origin_lat}, {origin_lng}) to ({dest_lat}, {dest_lng})")
        
        # Find nearby stops for origin and destination
        origin_stops = await self._find_nearby_stops(origin_lat, origin_lng, max_stops=5)
        dest_stops = await self._find_nearby_stops(dest_lat, dest_lng, max_stops=5)
        
        self.logger.info(f"Found {len(origin_stops)} origin stops and {len(dest_stops)} destination stops")
        
        if not origin_stops or not dest_stops:
            self.logger.warning("No nearby stops found for origin or destination")
            return []
        
        # Log the stops found for debugging
        self.logger.debug(f"Origin stops: {[s['stop_name'] for s in origin_stops]}")
        self.logger.debug(f"Destination stops: {[s['stop_name'] for s in dest_stops]}")
        
        # Generate journey options using different algorithms
        journey_options = []
        
        # 1. Direct route search
        direct_journeys = await self._find_direct_routes(
            origin_stops, dest_stops, departure_time, preferences
        )
        journey_options.extend(direct_journeys)
        
        # 2. Single transfer search
        single_transfer_journeys = await self._find_single_transfer_routes(
            origin_stops, dest_stops, departure_time, preferences
        )
        journey_options.extend(single_transfer_journeys)
        
        # 3. Multi-transfer search (up to max_transfers)
        if preferences.get('allow_multiple_transfers', True):
            multi_transfer_journeys = await self._find_multi_transfer_routes(
                origin_stops, dest_stops, departure_time, preferences
            )
            journey_options.extend(multi_transfer_journeys)
        
        # Score and rank journey options
        ranked_journeys = self._rank_journey_options(
            journey_options, preferences
        )
        
        # Return top 5 options
        return ranked_journeys[:5]
    
    async def _find_nearby_stops(self, lat: float, lng: float, max_stops: int = 5) -> List[Dict]:
        """Find bus stops near given coordinates"""
        nearby_stops = []
        
        # First, try exact match (for stop-to-stop planning)
        for route_id, route in self.simulator.routes.items():
            if not route.stops:
                continue
                
            for stop_idx, stop in enumerate(route.stops):
                distance_km = self._calculate_distance(lat, lng, stop.latitude, stop.longitude)
                
                # Exact match within 10 meters (likely same stop)
                if distance_km <= 0.01:  # 10 meters
                    nearby_stops.append({
                        'route_id': route_id,
                        'stop_index': stop_idx,
                        'stop_name': stop.name,
                        'latitude': stop.latitude,
                        'longitude': stop.longitude,
                        'distance_km': 0.0,  # Treat as exact match
                        'walk_time_minutes': 0.0,
                        'exact_match': True
                    })
        
        # If we found exact matches, return those
        if nearby_stops:
            return nearby_stops[:max_stops]
        
        # Otherwise, find nearby stops within walking distance
        for route_id, route in self.simulator.routes.items():
            if not route.stops:
                continue
                
            for stop_idx, stop in enumerate(route.stops):
                distance_km = self._calculate_distance(lat, lng, stop.latitude, stop.longitude)
                
                if distance_km <= self.max_walking_distance_km:
                    nearby_stops.append({
                        'route_id': route_id,
                        'stop_index': stop_idx,
                        'stop_name': stop.name,
                        'latitude': stop.latitude,
                        'longitude': stop.longitude,
                        'distance_km': distance_km,
                        'walk_time_minutes': (distance_km * 1000 * 60) / (self.walking_speed_kmh * 1000),
                        'exact_match': False
                    })
        
        # Sort by distance and return closest stops
        nearby_stops.sort(key=lambda x: x['distance_km'])
        return nearby_stops[:max_stops]
    
    async def _find_direct_routes(self, origin_stops: List[Dict], dest_stops: List[Dict],
                            departure_time: datetime, preferences: Dict) -> List[Journey]:
        """Find direct single-route journeys"""
        direct_journeys = []
        
        for origin_stop in origin_stops:
            for dest_stop in dest_stops:
                if origin_stop['route_id'] == dest_stop['route_id']:
                    # Same route - allow both forward and reverse without swapping endpoints
                    journey = await self._create_direct_journey(
                        origin_stop, dest_stop, departure_time, preferences
                    )
                    if journey:
                        direct_journeys.append(journey)
        
        return direct_journeys
    
    async def _create_direct_journey(self, origin_stop: Dict, dest_stop: Dict,
                                   departure_time: datetime, preferences: Dict) -> Optional[Journey]:
        """Create a direct single-route journey"""
        route_id = origin_stop['route_id']
        route = self.simulator.routes.get(route_id)
        
        if not route:
            return None
        
        # Determine direction and ordered indices for timing
        direction = 'forward' if dest_stop['stop_index'] > origin_stop['stop_index'] else 'reverse'
        start_idx = origin_stop['stop_index']
        end_idx = dest_stop['stop_index']
        if direction == 'reverse':
            start_idx, end_idx = dest_stop['stop_index'], origin_stop['stop_index']
        
        # Calculate travel time using ETA predictor if available (indices must be ascending)
        travel_time_minutes = await self._estimate_travel_time(
            route_id, start_idx, end_idx, departure_time
        )
        
        # Get next bus arrival at origin stop
        next_bus_time = await self._get_next_bus_arrival(
            route_id, origin_stop['stop_index'], departure_time, direction
        )
        
        if not next_bus_time:
            return None
        
        arrival_time = next_bus_time + timedelta(minutes=travel_time_minutes)
        
        # Create journey segment
        segment = JourneySegment(
            route_id=route_id,
            route_name=route.name,
            boarding_stop={
                'name': origin_stop.get('stop_name', ''),
                'latitude': origin_stop['latitude'],
                'longitude': origin_stop['longitude'],
                'index': origin_stop['stop_index']
            },
            alighting_stop={
                'name': dest_stop.get('stop_name', ''),
                'latitude': dest_stop['latitude'],
                'longitude': dest_stop['longitude'],
                'index': dest_stop['stop_index']
            },
            departure_time=next_bus_time,
            arrival_time=arrival_time,
            travel_time_minutes=travel_time_minutes,
            direction=direction,
            confidence=0.9,
            fare_cost=self.base_fare_per_route,
            segment_color=self._get_route_color(route_id)
        )
        
        # Calculate walking times
        origin_walk_time = origin_stop['walk_time_minutes']
        dest_walk_time = dest_stop['walk_time_minutes']
        total_walking_time = origin_walk_time + dest_walk_time
        
        # Calculate waiting time
        waiting_time = (next_bus_time - departure_time).total_seconds() / 60
        
        journey = Journey(
            origin={'lat': origin_stop['latitude'], 'lng': origin_stop['longitude']},
            destination={'lat': dest_stop['latitude'], 'lng': dest_stop['longitude']},
            segments=[segment],
            total_travel_time=travel_time_minutes + total_walking_time + waiting_time,
            total_walking_time=total_walking_time,
            total_waiting_time=waiting_time,
            total_fare=self.base_fare_per_route,
            departure_time=departure_time,
            arrival_time=arrival_time + timedelta(minutes=dest_walk_time),
            transfers_count=0,
            confidence_score=0.9,
            journey_id=f"direct_{route_id}_{int(departure_time.timestamp())}",
            carbon_footprint=self._calculate_carbon_footprint([segment])
        )
        
        return journey
    
    async def _find_single_transfer_routes(self, origin_stops: List[Dict], dest_stops: List[Dict],
                                         departure_time: datetime, preferences: Dict) -> List[Journey]:
        """Find journeys with exactly one transfer"""
        transfer_journeys = []
        
        # Use A* algorithm for efficient pathfinding
        for origin_stop in origin_stops:
            for dest_stop in dest_stops:
                if origin_stop['route_id'] == dest_stop['route_id']:
                    continue  # Skip direct routes (handled separately)
                
                # Find transfer points between these routes
                transfer_options = self._find_transfer_points(
                    origin_stop['route_id'], dest_stop['route_id']
                )
                
                for transfer_point in transfer_options:
                    journey = await self._create_transfer_journey(
                        origin_stop, dest_stop, transfer_point, departure_time, preferences
                    )
                    if journey:
                        transfer_journeys.append(journey)
        
        return transfer_journeys
    
    def _find_transfer_points(self, route1_id: str, route2_id: str) -> List[Dict]:
        """Find optimal transfer points between two routes"""
        transfer_options = []
        
        route1 = self.simulator.routes.get(route1_id)
        route2 = self.simulator.routes.get(route2_id)
        
        if not route1 or not route2 or not route1.stops or not route2.stops:
            return []
        
        # Find intersecting or nearby stops
        for stop1_idx, stop1 in enumerate(route1.stops):
            for stop2_idx, stop2 in enumerate(route2.stops):
                distance_km = self._calculate_distance(
                    stop1.latitude, stop1.longitude,
                    stop2.latitude, stop2.longitude
                )
                
                if distance_km <= self.max_walking_distance_km:
                    transfer_time = max(
                        self.transfer_buffer_minutes,
                        distance_km * 60 / self.walking_speed_kmh * 1000
                    )
                    
                    transfer_options.append({
                        'route1_stop_idx': stop1_idx,
                        'route2_stop_idx': stop2_idx,
                        'route1_stop': stop1,
                        'route2_stop': stop2,
                        'transfer_distance_km': distance_km,
                        'transfer_time_minutes': transfer_time,
                        'transfer_quality': self._assess_transfer_quality(stop1, stop2, distance_km)
                    })
        
        # Sort by transfer quality (shorter distance, better facilities)
        transfer_options.sort(key=lambda x: x['transfer_quality'], reverse=True)
        return transfer_options[:3]  # Return top 3 transfer options
    
    def _assess_transfer_quality(self, stop1, stop2, distance_km: float) -> float:
        """Assess the quality of a transfer point (higher = better)"""
        quality_score = 1.0
        
        # Distance penalty
        quality_score -= (distance_km / self.max_walking_distance_km) * 0.3
        
        # Bonus for terminal stops (usually have better facilities)
        if 'terminal' in stop1.name.lower() or 'terminal' in stop2.name.lower():
            quality_score += 0.2
        
        # Bonus for major stops/stations
        if any(keyword in stop1.name.lower() for keyword in ['station', 'center', 'mall', 'hospital']):
            quality_score += 0.1
        
        return max(0.0, min(1.0, quality_score))
    
    async def _create_transfer_journey(self, origin_stop: Dict, dest_stop: Dict,
                                     transfer_point: Dict, departure_time: datetime,
                                     preferences: Dict) -> Optional[Journey]:
        """Create a journey with one transfer"""
        # First segment: origin to transfer point
        first_segment = await self._create_journey_segment(
            origin_stop['route_id'],
            origin_stop['stop_index'],
            transfer_point['route1_stop_idx'],
            departure_time,
            preferences
        )
        
        if not first_segment:
            return None
        
        # Calculate transfer time
        transfer_arrival = first_segment.arrival_time
        transfer_departure = transfer_arrival + timedelta(
            minutes=transfer_point['transfer_time_minutes']
        )
        
        # Second segment: transfer point to destination
        second_segment = await self._create_journey_segment(
            dest_stop['route_id'],
            transfer_point['route2_stop_idx'],
            dest_stop['stop_index'],
            transfer_departure,
            preferences
        )
        
        if not second_segment:
            return None
        
        # Calculate total journey metrics
        segments = [first_segment, second_segment]
        total_travel_time = sum(seg.travel_time_minutes for seg in segments)
        total_walking_time = (origin_stop['walk_time_minutes'] + 
                            dest_stop['walk_time_minutes'] + 
                            transfer_point['transfer_time_minutes'])
        total_waiting_time = ((first_segment.departure_time - departure_time).total_seconds() / 60 +
                            (second_segment.departure_time - transfer_arrival).total_seconds() / 60)
        
        confidence_score = min(seg.confidence for seg in segments) * 0.9  # Reduce confidence for transfers
        
        journey = Journey(
            origin={'lat': origin_stop['latitude'], 'lng': origin_stop['longitude']},
            destination={'lat': dest_stop['latitude'], 'lng': dest_stop['longitude']},
            segments=segments,
            total_travel_time=total_travel_time + total_walking_time + total_waiting_time,
            total_walking_time=total_walking_time,
            total_waiting_time=total_waiting_time,
            total_fare=sum(seg.fare_cost for seg in segments),
            departure_time=departure_time,
            arrival_time=second_segment.arrival_time + timedelta(minutes=dest_stop['walk_time_minutes']),
            transfers_count=1,
            confidence_score=confidence_score,
            journey_id=f"transfer_{first_segment.route_id}_{second_segment.route_id}_{int(departure_time.timestamp())}",
            carbon_footprint=self._calculate_carbon_footprint(segments)
        )
        
        return journey
    
    async def _create_journey_segment(self, route_id: str, origin_idx: int, dest_idx: int,
                                    departure_time: datetime, preferences: Dict) -> Optional[JourneySegment]:
        """Create a single journey segment between two stops on the same route"""
        route = self.simulator.routes.get(route_id)
        if not route or origin_idx == dest_idx:
            return None
        
        # Determine direction and order indices for timing
        direction = 'forward' if dest_idx > origin_idx else 'reverse'
        start_idx = min(origin_idx, dest_idx)
        end_idx = max(origin_idx, dest_idx)
        origin_stop = route.stops[origin_idx]
        dest_stop = route.stops[dest_idx]
        
        # Estimate travel time
        travel_time = await self._estimate_travel_time(route_id, start_idx, end_idx, departure_time)
        
        # Get next bus arrival
        next_bus_time = await self._get_next_bus_arrival(route_id, origin_idx, departure_time, direction)
        if not next_bus_time:
            return None
        
        arrival_time = next_bus_time + timedelta(minutes=travel_time)
        
        return JourneySegment(
            route_id=route_id,
            route_name=route.name,
            boarding_stop={
                'name': origin_stop.name,
                'latitude': origin_stop.latitude,
                'longitude': origin_stop.longitude,
                'index': origin_idx
            },
            alighting_stop={
                'name': dest_stop.name,
                'latitude': dest_stop.latitude,
                'longitude': dest_stop.longitude,
                'index': dest_idx
            },
            departure_time=next_bus_time,
            arrival_time=arrival_time,
            travel_time_minutes=travel_time,
            direction=direction,
            confidence=0.85,
            fare_cost=self.base_fare_per_route,
            segment_color=self._get_route_color(route_id)
        )
    
    async def _find_multi_transfer_routes(self, origin_stops: List[Dict], dest_stops: List[Dict],
                                        departure_time: datetime, preferences: Dict) -> List[Journey]:
        """Find journeys with multiple transfers using Dijkstra's algorithm"""
        # This is a more complex implementation that would use graph algorithms
        # For now, return empty list - can be expanded later
        return []
    
    async def _estimate_travel_time(self, route_id: str, origin_idx: int, dest_idx: int,
                                  departure_time: datetime) -> float:
        """Estimate travel time between stops using ETA predictor"""
        if hasattr(self.simulator, 'eta_predictor') and self.simulator.eta_predictor:
            # Use AI-powered ETA prediction
            route = self.simulator.routes.get(route_id)
            if route and route.stops:
                # Estimate based on distance and current traffic
                total_distance = 0
                for i in range(origin_idx, dest_idx):
                    if i + 1 < len(route.stops):
                        stop1 = route.stops[i]
                        stop2 = route.stops[i + 1]
                        total_distance += self._calculate_distance(
                            stop1.latitude, stop1.longitude,
                            stop2.latitude, stop2.longitude
                        )
                
                # Use traffic-aware speed estimation
                average_speed_kmh = self._get_traffic_aware_speed(route_id, departure_time)
                travel_time_minutes = (total_distance / average_speed_kmh) * 60
                
                # Add stop dwell time
                num_intermediate_stops = dest_idx - origin_idx - 1
                dwell_time_minutes = num_intermediate_stops * 1.5  # 1.5 minutes per stop
                
                return travel_time_minutes + dwell_time_minutes
        
        # Fallback: use simple distance-based estimation
        route = self.simulator.routes.get(route_id)
        if not route or not route.stops:
            return 15.0  # Default 15 minutes
        
        origin_stop = route.stops[origin_idx]
        dest_stop = route.stops[dest_idx]
        distance_km = self._calculate_distance(
            origin_stop.latitude, origin_stop.longitude,
            dest_stop.latitude, dest_stop.longitude
        )
        
        return max(5.0, (distance_km / 25.0) * 60)  # Assume 25 km/h average speed
    
    async def _get_next_bus_arrival(self, route_id: str, stop_idx: int, 
                                  after_time: datetime, direction: str = 'forward') -> Optional[datetime]:
        """Get the next bus arrival time at a specific stop for a direction"""
        # Check if there are active buses on this route and direction
        route_buses = [bus for bus in self.simulator.buses.values() 
                      if bus.route_id == route_id and bus.direction == direction]
        
        if not route_buses:
            # Use scheduled departure (every 10 minutes for enhanced system)
            departure_interval = getattr(self.simulator, 'departure_interval', 10)
            minutes_to_next = departure_interval - (after_time.minute % departure_interval)
            return after_time.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_next)
        
        # Find the next bus that will reach this stop
        for bus in route_buses:
            if not hasattr(bus, 'next_stop_index'):
                continue
            if direction == 'forward' and bus.next_stop_index <= stop_idx:
                # This bus will reach the stop - estimate when
                if hasattr(self.simulator, 'eta_predictor'):
                    # Use ETA predictor for more accurate prediction
                    route = self.simulator.routes.get(route_id)
                    if route:
                        etas = self.simulator.eta_predictor.predict_eta_to_stops(
                            bus, route, self.simulator.traffic_segments or {}
                        )
                        
                        if stop_idx in etas:
                            eta_minutes = etas[stop_idx]['eta_minutes']
                            return after_time + timedelta(minutes=eta_minutes)
            elif direction == 'reverse' and bus.next_stop_index >= stop_idx:
                if hasattr(self.simulator, 'eta_predictor'):
                    route = self.simulator.routes.get(route_id)
                    if route:
                        etas = self.simulator.eta_predictor.predict_eta_to_stops(
                            bus, route, self.simulator.traffic_segments or {}
                        )
                        if stop_idx in etas:
                            eta_minutes = etas[stop_idx]['eta_minutes']
                            return after_time + timedelta(minutes=eta_minutes)
        
        # Fallback: next scheduled departure
        departure_interval = getattr(self.simulator, 'departure_interval', 10)
        return after_time + timedelta(minutes=departure_interval)
    
    def _get_traffic_aware_speed(self, route_id: str, departure_time: datetime) -> float:
        """Get traffic-aware average speed for route"""
        base_speed = 25.0  # Base speed in km/h
        
        if not hasattr(self.simulator, 'traffic_segments'):
            return base_speed
        
        # Calculate weighted average speed based on traffic conditions
        route_segments = [seg for seg in self.simulator.traffic_segments.values() 
                         if getattr(seg, 'route_id', None) == route_id]
        
        if not route_segments:
            return base_speed
        
        total_weight = 0
        weighted_speed_sum = 0
        
        for segment in route_segments:
            weight = getattr(segment, 'distance', 1.0)
            speed = segment.get_effective_speed() if hasattr(segment, 'get_effective_speed') else base_speed
            
            total_weight += weight
            weighted_speed_sum += speed * weight
        
        if total_weight > 0:
            return weighted_speed_sum / total_weight
        
        return base_speed
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        return geodesic((lat1, lng1), (lat2, lng2)).kilometers
    
    def _get_route_color(self, route_id: str) -> str:
        """Get color for route visualization"""
        route_colors = {
            'FR-01': '#007cba', 'FR-02': '#dc3545', 'FR-03A': '#28a745', 'FR-03B': '#17a2b8',
            'FR-04': '#ffc107', 'FR-04A': '#fd7e14', 'FR-05': '#6f42c1', 'FR-06': '#e83e8c',
            'FR-07': '#20c997', 'FR-08A': '#6c757d', 'FR-08B': '#343a40', 'FR-08C': '#495057',
            'FR-09': '#fd7e14', 'FR-10': '#20c997', 'FR-11': '#e83e8c', 'FR-12': '#6f42c1',
            'FR-13': '#dc3545', 'FR-14': '#28a745', 'FR-14A': '#17a2b8', 'FR-15': '#ffc107'
        }
        return route_colors.get(route_id, '#667eea')
    
    def _calculate_carbon_footprint(self, segments: List[JourneySegment]) -> float:
        """Calculate carbon footprint for journey in kg CO2"""
        # Assume 0.05 kg CO2 per km for bus transport
        total_distance = sum(
            self._calculate_distance(
                seg.boarding_stop['latitude'], seg.boarding_stop['longitude'],
                seg.alighting_stop['latitude'], seg.alighting_stop['longitude']
            ) for seg in segments
        )
        return total_distance * 0.05
    
    def _rank_journey_options(self, journeys: List[Journey], preferences: Dict) -> List[Journey]:
        """Rank and sort journey options based on user preferences and quality metrics"""
        if not journeys:
            return []
        
        # Default weights for ranking criteria
        weights = {
            'time': preferences.get('time_weight', 0.4),
            'transfers': preferences.get('transfer_weight', 0.2),
            'walking': preferences.get('walking_weight', 0.15),
            'cost': preferences.get('cost_weight', 0.1),
            'confidence': preferences.get('confidence_weight', 0.1),
            'carbon': preferences.get('carbon_weight', 0.05)
        }
        
        # Normalize metrics for scoring
        min_time = min(j.total_travel_time for j in journeys)
        max_time = max(j.total_travel_time for j in journeys)
        min_cost = min(j.total_fare for j in journeys)
        max_cost = max(j.total_fare for j in journeys)
        
        scored_journeys = []
        
        for journey in journeys:
            score = 0.0
            
            # Time score (lower is better)
            if max_time > min_time:
                time_score = 1.0 - (journey.total_travel_time - min_time) / (max_time - min_time)
            else:
                time_score = 1.0
            score += weights['time'] * time_score
            
            # Transfer score (fewer transfers is better)
            transfer_score = max(0.0, 1.0 - (journey.transfers_count / self.max_transfers))
            score += weights['transfers'] * transfer_score
            
            # Walking score (less walking is better)
            walking_score = max(0.0, 1.0 - (journey.total_walking_time / 30.0))  # 30 min max walk
            score += weights['walking'] * walking_score
            
            # Cost score (lower cost is better)
            if max_cost > min_cost:
                cost_score = 1.0 - (journey.total_fare - min_cost) / (max_cost - min_cost)
            else:
                cost_score = 1.0
            score += weights['cost'] * cost_score
            
            # Confidence score
            score += weights['confidence'] * journey.confidence_score
            
            # Carbon footprint score (lower is better)
            carbon_score = max(0.0, 1.0 - (journey.carbon_footprint / 10.0))  # 10kg max
            score += weights['carbon'] * carbon_score
            
            scored_journeys.append((score, journey))
        
        # Sort by score (highest first)
        scored_journeys.sort(key=lambda x: x[0], reverse=True)
        
        return [journey for score, journey in scored_journeys]
    
    def get_journey_summary(self, journey: Journey) -> Dict[str, Any]:
        """Generate a comprehensive journey summary for API response"""
        return {
            'journey_id': journey.journey_id,
            'summary': {
                'origin': journey.origin,
                'destination': journey.destination,
                'departure_time': journey.departure_time.isoformat(),
                'arrival_time': journey.arrival_time.isoformat(),
                'total_duration_minutes': round(journey.total_travel_time),
                'transfers_required': journey.transfers_count,
                'total_fare': journey.total_fare,
                'confidence_score': round(journey.confidence_score, 2),
                'carbon_footprint_kg': round(journey.carbon_footprint, 3),
                'accessibility_rating': journey.accessibility_rating
            },
            'segments': [
                {
                    'segment_number': idx + 1,
                    'route_id': seg.route_id,
                    'route_name': seg.route_name,
                    'route_color': seg.segment_color,
                    'direction': seg.direction,
                    'boarding_stop': {
                        'name': seg.boarding_stop['name'],
                        'location': [seg.boarding_stop['latitude'], seg.boarding_stop['longitude']],
                        'stop_index': seg.boarding_stop.get('index')
                    },
                    'alighting_stop': {
                        'name': seg.alighting_stop['name'],
                        'location': [seg.alighting_stop['latitude'], seg.alighting_stop['longitude']],
                        'stop_index': seg.alighting_stop.get('index')
                    },
                    'departure_time': seg.departure_time.isoformat(),
                    'arrival_time': seg.arrival_time.isoformat(),
                    'travel_time_minutes': round(seg.travel_time_minutes),
                    'fare_cost': seg.fare_cost,
                    'bus_id': seg.bus_id,
                    'confidence': round(seg.confidence, 2)
                }
                for idx, seg in enumerate(journey.segments)
            ],
            'transfer_points': [
                {
                    'after_segment': idx,
                    'location': [
                        journey.segments[idx].alighting_stop['latitude'],
                        journey.segments[idx].alighting_stop['longitude']
                    ],
                    'from_route': journey.segments[idx].route_id,
                    'to_route': journey.segments[idx + 1].route_id,
                    'transfer_time_minutes': round(
                        (journey.segments[idx + 1].departure_time - 
                         journey.segments[idx].arrival_time).total_seconds() / 60
                    ),
                    'transfer_instructions': self._generate_transfer_instructions(
                        journey.segments[idx], journey.segments[idx + 1]
                    )
                }
                for idx in range(len(journey.segments) - 1)
            ],
            'instructions': self._generate_step_by_step_instructions(journey),
            'alternative_options': {
                'faster_route_available': False,
                'cheaper_route_available': False,
                'fewer_transfers_available': journey.transfers_count > 0
            }
        }
    
    def _generate_transfer_instructions(self, from_segment: JourneySegment, 
                                      to_segment: JourneySegment) -> str:
        """Generate human-readable transfer instructions"""
        from_stop = from_segment.alighting_stop['name']
        to_stop = to_segment.boarding_stop['name']
        
        if from_stop == to_stop:
            return f"Stay at {from_stop} and board the {to_segment.route_id} bus"
        else:
            distance_km = self._calculate_distance(
                from_segment.alighting_stop['latitude'],
                from_segment.alighting_stop['longitude'],
                to_segment.boarding_stop['latitude'],
                to_segment.boarding_stop['longitude']
            )
            walk_time = round((distance_km * 1000 * 60) / (self.walking_speed_kmh * 1000))
            return f"Walk {round(distance_km * 1000)}m ({walk_time} min) from {from_stop} to {to_stop}"
    
    def _generate_step_by_step_instructions(self, journey: Journey) -> List[Dict[str, Any]]:
        """Generate detailed step-by-step journey instructions"""
        instructions = []
        
        # Initial walking instruction
        if journey.segments:
            first_segment = journey.segments[0]
            instructions.append({
                'step': 1,
                'type': 'walk',
                'instruction': f"Walk to {first_segment.boarding_stop['name']}",
                'duration_minutes': 5,  # Estimated
                'location': [
                    first_segment.boarding_stop['latitude'],
                    first_segment.boarding_stop['longitude']
                ]
            })
        
        step_counter = 2
        
        for idx, segment in enumerate(journey.segments):
            # Board bus instruction
            instructions.append({
                'step': step_counter,
                'type': 'board',
                'instruction': f"Board {segment.route_id} bus ({segment.route_name}) at {segment.boarding_stop['name']}",
                'scheduled_time': segment.departure_time.isoformat(),
                'route_color': segment.segment_color,
                'direction': segment.direction,
                'location': [
                    segment.boarding_stop['latitude'],
                    segment.boarding_stop['longitude']
                ]
            })
            step_counter += 1
            
            # Travel instruction
            instructions.append({
                'step': step_counter,
                'type': 'travel',
                'instruction': f"Stay on {segment.route_id} for {round(segment.travel_time_minutes)} minutes",
                'duration_minutes': round(segment.travel_time_minutes),
                'stops_count': abs(segment.alighting_stop.get('index', 0) - segment.boarding_stop.get('index', 0))
            })
            step_counter += 1
            
            # Alight instruction
            instructions.append({
                'step': step_counter,
                'type': 'alight',
                'instruction': f"Get off at {segment.alighting_stop['name']}",
                'scheduled_time': segment.arrival_time.isoformat(),
                'location': [
                    segment.alighting_stop['latitude'],
                    segment.alighting_stop['longitude']
                ]
            })
            step_counter += 1
            
            # Transfer instruction (if not the last segment)
            if idx < len(journey.segments) - 1:
                next_segment = journey.segments[idx + 1]
                transfer_instruction = self._generate_transfer_instructions(segment, next_segment)
                transfer_time = round(
                    (next_segment.departure_time - segment.arrival_time).total_seconds() / 60
                )
                
                instructions.append({
                    'step': step_counter,
                    'type': 'transfer',
                    'instruction': transfer_instruction,
                    'duration_minutes': transfer_time,
                    'from_route': segment.route_id,
                    'to_route': next_segment.route_id
                })
                step_counter += 1
        
        # Final walking instruction
        if journey.segments:
            last_segment = journey.segments[-1]
            instructions.append({
                'step': step_counter,
                'type': 'walk',
                'instruction': f"Walk to your final destination",
                'duration_minutes': 5,  # Estimated
                'from_location': [
                    last_segment.alighting_stop['latitude'],
                    last_segment.alighting_stop['longitude']
                ],
                'to_location': [journey.destination['lat'], journey.destination['lng']]
            })
        
        return instructions
    
    async def get_real_time_journey_updates(self, journey_id: str) -> Dict[str, Any]:
        """Get real-time updates for an active journey"""
        # This would track the user's progress and provide live updates
        # For now, return a template structure
        return {
            'journey_id': journey_id,
            'status': 'active',
            'current_step': 3,
            'delays': {
                'total_delay_minutes': 2,
                'affected_segments': [1],
                'reason': 'Light traffic congestion'
            },
            'live_updates': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Your bus is running 2 minutes late due to traffic',
                    'type': 'delay_notification'
                }
            ],
            'next_action': {
                'type': 'board',
                'route_id': 'FR-01',
                'stop_name': 'Central Station',
                'eta_minutes': 7,
                'confidence': 0.85
            }
        }
    
    def suggest_alternative_routes(self, journey: Journey, issue_type: str = 'delay') -> List[Journey]:
        """Suggest alternative routes when issues occur"""
        # This would re-plan the journey considering current conditions
        # For now, return empty list
        return []