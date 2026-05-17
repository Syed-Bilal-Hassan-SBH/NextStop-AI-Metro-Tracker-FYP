<<<<<<< HEAD
import folium
from bus_simulator import BusSimulator

class MapVisualizer:
    def __init__(self, simulator: BusSimulator):
        self.simulator = simulator
    
    def generate_map(self) -> str:
        """Generate HTML map with bus positions"""
        # Center map on Islamabad
        m = folium.Map(location=[33.65, 73.05], zoom_start=12)
        
        # Add route polyline
        route = self.simulator.routes['FR-01']
        route_coords = [(stop.latitude, stop.longitude) for stop in route.stops]
        
        folium.PolyLine(
            route_coords,
            color='blue',
            weight=5,
            opacity=0.8,
            popup='Metro FR-01 Route'
        ).add_to(m)
        
        # Add stops
        for i, stop in enumerate(route.stops):
            folium.Marker(
                [stop.latitude, stop.longitude],
                popup=f"{stop.name} (Stop {i+1})",
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
        
        # Add buses
        for bus in self.simulator.buses.values():
            color = 'red' if bus.status == 'delayed' else 'blue'
            folium.Marker(
                [bus.current_lat, bus.current_lng],
                popup=f"Bus {bus.bus_id}<br>Speed: {bus.speed:.1f} km/h<br>Status: {bus.status}",
                icon=folium.Icon(color=color, icon='bus', prefix='fa')
            ).add_to(m)
        
=======
import folium
from bus_simulator import BusSimulator

class MapVisualizer:
    def __init__(self, simulator: BusSimulator):
        self.simulator = simulator
    
    def generate_map(self) -> str:
        """Generate HTML map with bus positions"""
        # Center map on Islamabad
        m = folium.Map(location=[33.65, 73.05], zoom_start=12)
        
        # Add route polyline
        route = self.simulator.routes['FR-01']
        route_coords = [(stop.latitude, stop.longitude) for stop in route.stops]
        
        folium.PolyLine(
            route_coords,
            color='blue',
            weight=5,
            opacity=0.8,
            popup='Metro FR-01 Route'
        ).add_to(m)
        
        # Add stops
        for i, stop in enumerate(route.stops):
            folium.Marker(
                [stop.latitude, stop.longitude],
                popup=f"{stop.name} (Stop {i+1})",
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
        
        # Add buses
        for bus in self.simulator.buses.values():
            color = 'red' if bus.status == 'delayed' else 'blue'
            folium.Marker(
                [bus.current_lat, bus.current_lng],
                popup=f"Bus {bus.bus_id}<br>Speed: {bus.speed:.1f} km/h<br>Status: {bus.status}",
                icon=folium.Icon(color=color, icon='bus', prefix='fa')
            ).add_to(m)
        
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
        return m._repr_html_()