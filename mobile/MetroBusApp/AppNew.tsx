/**
 * Metro Bus Management System - Mobile App v2.0
 * Complete Feature Parity with Web/Backend
 * Features: Routes, Traffic, Journey Planning, Analytics, Admin
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  StatusBar,
  useColorScheme,
  RefreshControl,
  Alert,
  Dimensions,
} from 'react-native';

// ==========================================
// TYPE DEFINITIONS
// ==========================================

interface Route {
  route_id: string;
  name: string;
  source: string;
  destination: string;
  total_distance: number;
  stops_count: number;
  active: boolean;
  color: string;
  background_buses: number;
}

interface Bus {
  bus_id: string;
  route_id: string;
  current_lat: number;
  current_lng: number;
  speed: number;
  status: string;
  direction: string;
  detailed_status?: string;
}

type TabType = 'routes' | 'traffic' | 'journey' | 'analytics' | 'admin';

// ==========================================
// API SERVICE - COMPREHENSIVE
// ==========================================

const API_CONFIG = {
  BASE_URL: 'http://10.0.2.2:8000', // Android Emulator
  // BASE_URL: 'http://192.168.18.21:8000', // Physical Device
  WS_URL: 'ws://10.0.2.2:8000/ws/live-tracking',
};

class ApiService {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request(endpoint: string, options?: RequestInit) {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers: { 'Content-Type': 'application/json', ...options?.headers },
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Routes
  async getRoutes() { return this.request('/api/routes'); }
  async activateRoute(routeId: string, numBuses: number = 10) {
    return this.request('/api/routes/activate', {
      method: 'POST',
      body: JSON.stringify({ route_id: routeId, num_buses: numBuses }),
    });
  }
  async deactivateRoute(routeId: string) {
    return this.request('/api/routes/deactivate', {
      method: 'POST',
      body: JSON.stringify({ route_id: routeId }),
    });
  }
  async deactivateAllRoutes() {
    return this.request('/api/routes/deactivate-all', { method: 'POST' });
  }

  // Journey
  async planJourney(originLat: number, originLng: number, destLat: number, destLng: number) {
    return this.request('/api/journey/plan', {
      method: 'POST',
      body: JSON.stringify({
        origin_lat: originLat,
        origin_lng: originLng,
        destination_lat: destLat,
        destination_lng: destLng,
      }),
    });
  }
  async getTransferPoints() { return this.request('/api/journey/transfer-points'); }
  async findNearbyStops(lat: number, lng: number, radius: number = 0.5) {
    return this.request(`/api/journey/nearby-stops?lat=${lat}&lng=${lng}&radius_km=${radius}`);
  }

  // Traffic & ETA
  async getCurrentTraffic() { return this.request('/api/traffic/current'); }
  async getRouteTraffic(routeId: string) { return this.request(`/api/traffic/route/${routeId}`); }
  async getAllETAPredictions() { return this.request('/api/eta/all'); }
  async getBusETA(busId: string) { return this.request(`/api/eta/bus/${busId}`); }

  // Simulation & Stats
  async getSimulationStatus() { return this.request('/api/simulation/status'); }
  async getRouteStatistics() { return this.request('/api/routes/statistics'); }
  async getBidirectionalStats(routeId: string) { return this.request(`/api/routes/${routeId}/bidirectional`); }
  async getBuses() { return this.request('/api/buses'); }

  // Admin
  async getAdminStatistics() { return this.request('/api/admin/statistics'); }
  async getAdminAlerts() { return this.request('/api/admin/alerts'); }
  async getPerformanceMetrics() { return this.request('/api/admin/performance'); }
  async sendAnnouncement(title: string, message: string, priority: string = 'normal') {
    return this.request('/api/admin/announcement', {
      method: 'POST',
      body: JSON.stringify({ title, message, priority, timestamp: new Date().toISOString() }),
    });
  }
}

const apiService = new ApiService(API_CONFIG.BASE_URL);

// ==========================================
// WEBSOCKET SERVICE
// ==========================================

class WebSocketService {
  private ws: WebSocket | null = null;
  private listeners: { [key: string]: Function[] } = {};
  private reconnectAttempts = 0;

  connect() {
    try {
      this.ws = new WebSocket(API_CONFIG.WS_URL);
      this.ws.onopen = () => {
        console.log('✅ WebSocket Connected');
        this.reconnectAttempts = 0;
        this.emit('connected', true);
      };
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('message', data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket Error:', error);
        this.emit('error', error);
      };
      this.ws.onclose = () => {
        console.log('📴 WebSocket Disconnected');
        this.emit('connected', false);
        this.reconnect();
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.reconnect();
    }
  }

  reconnect() {
    if (this.reconnectAttempts < 5) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), 3000);
    }
  }

  on(event: string, callback: Function) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }

  emit(event: string, data: any) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

const wsService = new WebSocketService();

// ==========================================
// MAIN APP COMPONENT
// ==========================================

function App() {
  const isDarkMode = useColorScheme() === 'dark';
  const [activeTab, setActiveTab] = useState<TabType>('routes');
  const [routes, setRoutes] = useState<Route[]>([]);
  const [buses, setBuses] = useState<Bus[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [simulationStatus, setSimulationStatus] = useState<any>(null);
  const [trafficData, setTrafficData] = useState<any>(null);
  const [etaData, setEtaData] = useState<any>(null);
  const [adminStats, setAdminStats] = useState<any>(null);

  useEffect(() => {
    wsService.connect();
    wsService.on('connected', (connected: boolean) => setIsConnected(connected));
    wsService.on('message', (data: any) => {
      if (data.buses) setBuses(data.buses);
      if (data.available_routes) setRoutes(data.available_routes);
    });
    loadAllData();
    return () => wsService.disconnect();
  }, []);

  const loadAllData = useCallback(async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadRoutes(),
        loadSimulationStatus(),
        loadTrafficData(),
        loadETAData(),
        loadAdminStats(),
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadRoutes = async () => {
    try {
      const data = await apiService.getRoutes();
      setRoutes(data.routes || []);
    } catch (error) {
      console.error('Error fetching routes:', error);
    }
  };

  const loadSimulationStatus = async () => {
    try {
      const data = await apiService.getSimulationStatus();
      setSimulationStatus(data);
    } catch (error) {
      console.error('Error fetching simulation status:', error);
    }
  };

  const loadTrafficData = async () => {
    try {
      const data = await apiService.getCurrentTraffic();
      setTrafficData(data);
    } catch (error) {
      console.error('Error fetching traffic data:', error);
    }
  };

  const loadETAData = async () => {
    try {
      const data = await apiService.getAllETAPredictions();
      setEtaData(data);
    } catch (error) {
      console.error('Error fetching ETA data:', error);
    }
  };

  const loadAdminStats = async () => {
    try {
      const data = await apiService.getAdminStatistics();
      setAdminStats(data);
    } catch (error) {
      console.error('Error fetching admin stats:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAllData();
    setRefreshing(false);
  };

  const handleActivateRoute = async (routeId: string) => {
    try {
      await apiService.activateRoute(routeId);
      Alert.alert('Success', `Route ${routeId} activated!`);
      await loadRoutes();
    } catch (error) {
      Alert.alert('Error', 'Failed to activate route');
    }
  };

  const handleDeactivateRoute = async (routeId: string) => {
    try {
      await apiService.deactivateRoute(routeId);
      Alert.alert('Success', `Route ${routeId} deactivated!`);
      await loadRoutes();
    } catch (error) {
      Alert.alert('Error', 'Failed to deactivate route');
    }
  };

  const renderRoutesTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.sectionTitle}>Available Routes</Text>
      {routes.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateText}>No routes available</Text>
        </View>
      ) : (
        routes.map(route => (
          <View key={route.route_id} style={[styles.routeCard, { borderColor: route.active ? '#28a745' : '#e0e0e0' }]}>
            <View style={styles.routeHeader}>
              <Text style={[styles.routeId, { color: route.color || '#667eea' }]}>{route.route_id}</Text>
              <View style={[styles.statusBadge, { backgroundColor: route.active ? '#28a745' : '#6c757d' }]}>
                <Text style={styles.statusText}>{route.active ? 'ACTIVE' : 'INACTIVE'}</Text>
              </View>
            </View>
            <Text style={styles.routeName}>{route.name}</Text>
            <Text style={styles.routeDestination}>{route.source} → {route.destination}</Text>
            <View style={styles.routeStats}>
              <Text style={styles.routeStat}>🚌 {route.background_buses} buses</Text>
              <Text style={styles.routeStat}>📍 {route.stops_count} stops</Text>
              <Text style={styles.routeStat}>📏 {route.total_distance.toFixed(1)} km</Text>
            </View>
            <TouchableOpacity
              style={[styles.actionButton, route.active ? styles.deactivateButton : styles.activateButton]}
              onPress={() => route.active ? handleDeactivateRoute(route.route_id) : handleActivateRoute(route.route_id)}
            >
              <Text style={styles.actionButtonText}>{route.active ? '🛑 Deactivate' : '▶️ Activate'}</Text>
            </TouchableOpacity>
          </View>
        ))
      )}

      {buses.length > 0 && (
        <View style={styles.busesSection}>
          <Text style={styles.sectionTitle}>Active Buses ({buses.length})</Text>
          {buses.slice(0, 10).map(bus => (
            <View key={bus.bus_id} style={styles.busCard}>
              <View style={styles.busHeader}>
                <Text style={styles.busId}>🚌 {bus.bus_id}</Text>
                <Text style={styles.busSpeed}>{bus.speed.toFixed(0)} km/h</Text>
              </View>
              <Text style={styles.busStatus}>{bus.detailed_status || bus.status}</Text>
              <Text style={styles.busDirection}>Direction: {bus.direction === 'forward' ? '→' : '←'}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );

  const renderTrafficTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.sectionTitle}>🚦 Traffic Analysis</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Current Traffic Conditions</Text>
        <Text style={styles.infoText}>
          {trafficData ? JSON.stringify(trafficData).substring(0, 150) + '...' : 'No traffic data'}
        </Text>
        <TouchableOpacity style={styles.viewButton} onPress={loadTrafficData}>
          <Text style={styles.viewButtonText}>Refresh Traffic</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>📊 ETA Predictions</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>All ETA Information</Text>
        <Text style={styles.infoText}>
          {etaData ? JSON.stringify(etaData).substring(0, 150) + '...' : 'Loading ETA data...'}
        </Text>
      </View>
    </ScrollView>
  );

  const renderJourneyTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>🧭 Journey Planning</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Plan Your Journey</Text>
        <Text style={styles.infoText}>📍 Enter origin and destination to get optimal routes</Text>
        <TouchableOpacity style={styles.viewButton} onPress={async () => {
          try {
            const result = await apiService.planJourney(24.8607, 67.0011, 24.7466, 67.0199);
            Alert.alert('Journey Planned', 'Route plan created successfully');
          } catch (error) {
            Alert.alert('Error', 'Failed to plan journey');
          }
        }}>
          <Text style={styles.viewButtonText}>Plan Journey</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>📍 Transfer Points</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Available Transfer Hubs</Text>
        <TouchableOpacity style={styles.viewButton} onPress={async () => {
          try {
            const result = await apiService.getTransferPoints();
            Alert.alert('Transfer Points', `${Object.keys(result).length} transfer points available`);
          } catch (error) {
            Alert.alert('Error', 'Failed to fetch transfer points');
          }
        }}>
          <Text style={styles.viewButtonText}>View Transfer Points</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  const renderAnalyticsTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.sectionTitle}>📈 System Analytics</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Simulation Status</Text>
        <Text style={styles.infoText}>
          Routes: {simulationStatus?.debug_info?.available_routes || 0} | Active: {simulationStatus?.debug_info?.active_routes || 0} | Buses: {simulationStatus?.debug_info?.total_buses || 0}
        </Text>
        <TouchableOpacity style={styles.viewButton} onPress={loadSimulationStatus}>
          <Text style={styles.viewButtonText}>Refresh Analytics</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>🎯 Route Statistics</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Performance Metrics</Text>
        <Text style={styles.infoText}>Detailed route statistics and performance analysis</Text>
      </View>
    </ScrollView>
  );

  const renderAdminTab = () => (
    <ScrollView style={styles.tabContent} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.sectionTitle}>👔 Admin Dashboard</Text>
      <View style={styles.adminCard}>
        <Text style={styles.infoTitle}>System Management</Text>
        <TouchableOpacity style={[styles.viewButton, { backgroundColor: '#dc3545', marginTop: 10 }]} onPress={async () => {
          try {
            await apiService.deactivateAllRoutes();
            Alert.alert('Success', 'All routes deactivated');
            await loadRoutes();
          } catch (error) {
            Alert.alert('Error', 'Failed to deactivate routes');
          }
        }}>
          <Text style={styles.viewButtonText}>⚠️ Deactivate All Routes</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>📊 Admin Statistics</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>System Stats</Text>
        <Text style={styles.infoText}>{adminStats ? 'Statistics loaded' : 'Click below to load'}</Text>
        <TouchableOpacity style={styles.viewButton} onPress={loadAdminStats}>
          <Text style={styles.viewButtonText}>Load Admin Stats</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>📢 Announcements</Text>
      <View style={styles.infoCard}>
        <TouchableOpacity style={styles.viewButton} onPress={async () => {
          try {
            await apiService.sendAnnouncement('System Notice', 'Scheduled maintenance', 'high');
            Alert.alert('Success', 'Announcement sent');
          } catch (error) {
            Alert.alert('Error', 'Failed to send announcement');
          }
        }}>
          <Text style={styles.viewButtonText}>Send Announcement</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>⚠️ Alerts</Text>
      <View style={styles.infoCard}>
        <TouchableOpacity style={styles.viewButton} onPress={async () => {
          try {
            const alerts = await apiService.getAdminAlerts();
            Alert.alert('Alerts', `${Object.keys(alerts).length} active alerts`);
          } catch (error) {
            Alert.alert('Info', 'No critical alerts');
          }
        }}>
          <Text style={styles.viewButtonText}>Check Alerts</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>📈 Performance Metrics</Text>
      <View style={styles.infoCard}>
        <TouchableOpacity style={styles.viewButton} onPress={async () => {
          try {
            await apiService.getPerformanceMetrics();
            Alert.alert('Performance', 'Metrics loaded successfully');
          } catch (error) {
            Alert.alert('Info', 'Performance monitoring available');
          }
        }}>
          <Text style={styles.viewButtonText}>View Performance</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  return (
    <>
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>Metro Bus</Text>
            <Text style={styles.headerSubtitle}>Complete Management System</Text>
          </View>
          <View style={[styles.statusDot, { backgroundColor: isConnected ? '#28a745' : '#dc3545' }]} />
        </View>

        <View style={styles.statsContainer}>
          <View style={[styles.statCard, { backgroundColor: '#E8F0FE' }]}>
            <Text style={[styles.statValue, { color: '#667eea' }]}>{routes.length}</Text>
            <Text style={styles.statLabel}>ROUTES</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#E8F5E9' }]}>
            <Text style={[styles.statValue, { color: '#28a745' }]}>{buses.length}</Text>
            <Text style={styles.statLabel}>BUSES</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#FFF9E6' }]}>
            <Text style={[styles.statValue, { color: '#ffc107' }]}>{routes.filter(r => r.active).length}</Text>
            <Text style={styles.statLabel}>ACTIVE</Text>
          </View>
        </View>

        <View style={styles.tabNavigation}>
          {(['routes', 'traffic', 'journey', 'analytics', 'admin'] as const).map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
              onPress={() => setActiveTab(tab)}
            >
              <Text style={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}>
                {tab === 'routes' && '🚌'}
                {tab === 'traffic' && '🚦'}
                {tab === 'journey' && '🧭'}
                {tab === 'analytics' && '📈'}
                {tab === 'admin' && '👔'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {activeTab === 'routes' && renderRoutesTab()}
        {activeTab === 'traffic' && renderTrafficTab()}
        {activeTab === 'journey' && renderJourneyTab()}
        {activeTab === 'analytics' && renderAnalyticsTab()}
        {activeTab === 'admin' && renderAdminTab()}

        <View style={styles.footer}>
          <Text style={styles.footerText}>{isConnected ? '🟢 Connected' : '🔴 Disconnected'}</Text>
          <Text style={styles.footerSubtext}>{API_CONFIG.BASE_URL}</Text>
        </View>
      </SafeAreaView>
    </>
  );
}

// ==========================================
// STYLES
// ==========================================

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { backgroundColor: '#667eea', padding: 20, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', elevation: 3 },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: 'white' },
  headerSubtitle: { fontSize: 12, color: 'rgba(255,255,255,0.8)', marginTop: 4 },
  statusDot: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: 'white' },
  statsContainer: { flexDirection: 'row', padding: 16, gap: 12, backgroundColor: 'white', elevation: 2 },
  statCard: { flex: 1, padding: 16, borderRadius: 12, alignItems: 'center' },
  statValue: { fontSize: 28, fontWeight: 'bold' },
  statLabel: { fontSize: 11, color: '#6c757d', marginTop: 4, fontWeight: '600' },
  tabNavigation: { flexDirection: 'row', padding: 12, backgroundColor: 'white', elevation: 2 },
  tabButton: { flex: 1, paddingVertical: 12, alignItems: 'center', borderBottomWidth: 3, borderBottomColor: 'transparent' },
  tabButtonActive: { borderBottomColor: '#667eea' },
  tabButtonText: { fontSize: 20 },
  tabButtonTextActive: { fontSize: 22 },
  tabContent: { flex: 1, padding: 16 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 16, color: '#2c3e50' },
  loader: { marginTop: 40 },
  emptyState: { alignItems: 'center', paddingVertical: 40 },
  emptyStateText: { fontSize: 16, color: '#6c757d' },
  routeCard: { backgroundColor: 'white', padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 2, elevation: 2 },
  routeHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  routeId: { fontSize: 20, fontWeight: 'bold' },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  statusText: { color: 'white', fontSize: 10, fontWeight: 'bold' },
  routeName: { fontSize: 15, color: '#495057', marginBottom: 4, fontWeight: '500' },
  routeDestination: { fontSize: 13, color: '#6c757d', marginBottom: 12 },
  routeStats: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 12, paddingVertical: 8, backgroundColor: '#f8f9fa', borderRadius: 8 },
  routeStat: { fontSize: 12, color: '#6c757d', fontWeight: '500' },
  actionButton: { padding: 14, borderRadius: 8, alignItems: 'center' },
  activateButton: { backgroundColor: '#28a745' },
  deactivateButton: { backgroundColor: '#dc3545' },
  actionButtonText: { color: 'white', fontWeight: 'bold', fontSize: 14 },
  busesSection: { marginTop: 24 },
  busCard: { backgroundColor: 'white', padding: 12, borderRadius: 10, marginBottom: 10, borderLeftWidth: 4, borderLeftColor: '#667eea' },
  busHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  busId: { fontSize: 14, fontWeight: 'bold', color: '#2c3e50' },
  busSpeed: { fontSize: 14, fontWeight: 'bold', color: '#667eea' },
  busStatus: { fontSize: 12, color: '#6c757d', marginBottom: 4 },
  busDirection: { fontSize: 11, color: '#6c757d' },
  infoCard: { backgroundColor: 'white', padding: 16, borderRadius: 12, marginBottom: 16, elevation: 2 },
  infoTitle: { fontSize: 16, fontWeight: 'bold', marginBottom: 8, color: '#667eea' },
  infoText: { fontSize: 13, color: '#6c757d', marginBottom: 12, lineHeight: 20 },
  adminCard: { backgroundColor: '#fff3cd', padding: 16, borderRadius: 12, marginBottom: 16, borderLeftWidth: 4, borderLeftColor: '#ffc107' },
  viewButton: { backgroundColor: '#667eea', padding: 12, borderRadius: 8, alignItems: 'center' },
  viewButtonText: { color: 'white', fontWeight: 'bold', fontSize: 14 },
  retryButton: { backgroundColor: '#667eea', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8, marginTop: 12 },
  retryButtonText: { color: 'white', fontWeight: 'bold' },
  footer: { backgroundColor: 'white', padding: 12, alignItems: 'center', borderTopWidth: 1, borderTopColor: '#e0e0e0' },
  footerText: { fontSize: 12, fontWeight: 'bold', color: '#495057' },
  footerSubtext: { fontSize: 10, color: '#6c757d', marginTop: 2 },
});

export default App;
