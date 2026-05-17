import axios from 'axios';
import { API_CONFIG } from '../config/api';

class ApiService {
  private api;

  constructor() {
    this.api = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // ====== ROUTE MANAGEMENT ======
  async getRoutes() {
    try {
      const response = await this.api.get(API_CONFIG.ENDPOINTS.ROUTES);
      return response.data;
    } catch (error) {
      console.error('Error fetching routes:', error);
      throw error;
    }
  }

  async activateRoute(routeId: string, numBuses: number = 10) {
    try {
      const response = await this.api.post(API_CONFIG.ENDPOINTS.ACTIVATE_ROUTE, {
        route_id: routeId,
        num_buses: numBuses,
      });
      return response.data;
    } catch (error) {
      console.error('Error activating route:', error);
      throw error;
    }
  }

  async deactivateRoute(routeId: string) {
    try {
      const response = await this.api.post(`${API_CONFIG.BASE_URL}/api/routes/deactivate`, {
        route_id: routeId,
      });
      return response.data;
    } catch (error) {
      console.error('Error deactivating route:', error);
      throw error;
    }
  }

  async deactivateAllRoutes() {
    try {
      const response = await this.api.post(`${API_CONFIG.BASE_URL}/api/routes/deactivate-all`);
      return response.data;
    } catch (error) {
      console.error('Error deactivating all routes:', error);
      throw error;
    }
  }

  // ====== JOURNEY PLANNING ======
  async planJourney(originLat: number, originLng: number, destLat: number, destLng: number, preferences?: any) {
    try {
      const response = await this.api.post(API_CONFIG.ENDPOINTS.JOURNEY_PLAN, {
        origin_lat: originLat,
        origin_lng: originLng,
        destination_lat: destLat,
        destination_lng: destLng,
        preferences: preferences || {
          time_weight: 0.4,
          transfer_weight: 0.3,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error planning journey:', error);
      throw error;
    }
  }

  async quickJourneyPlan(originLat: number, originLng: number, destLat: number, destLng: number) {
    try {
      const response = await this.api.post(`${API_CONFIG.BASE_URL}/api/journey/quick-plan`, {
        origin_lat: originLat,
        origin_lng: originLng,
        destination_lat: destLat,
        destination_lng: destLng,
      });
      return response.data;
    } catch (error) {
      console.error('Error in quick journey plan:', error);
      throw error;
    }
  }

  async getJourneyUpdates(journeyId: string) {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/journey/${journeyId}/updates`);
      return response.data;
    } catch (error) {
      console.error('Error getting journey updates:', error);
      throw error;
    }
  }

  async getTransferPoints() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/journey/transfer-points`);
      return response.data;
    } catch (error) {
      console.error('Error fetching transfer points:', error);
      throw error;
    }
  }

  async findNearbyStops(lat: number, lng: number, radiusKm: number = 0.5) {
    try {
      const response = await this.api.get(
        `${API_CONFIG.ENDPOINTS.NEARBY_STOPS}?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`
      );
      return response.data;
    } catch (error) {
      console.error('Error finding nearby stops:', error);
      throw error;
    }
  }

  // ====== TRAFFIC & ETA ======
  async getCurrentTraffic() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/traffic/current`);
      return response.data;
    } catch (error) {
      console.error('Error fetching traffic data:', error);
      throw error;
    }
  }

  async getRouteTraffic(routeId: string) {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/traffic/route/${routeId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching route traffic:', error);
      throw error;
    }
  }

  async getAllETAPredictions() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/eta/all`);
      return response.data;
    } catch (error) {
      console.error('Error fetching ETA predictions:', error);
      throw error;
    }
  }

  async getBusETA(busId: string) {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/eta/bus/${busId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching bus ETA:', error);
      throw error;
    }
  }

  // ====== SIMULATION & STATISTICS ======
  async getSimulationStatus() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/simulation/status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching simulation status:', error);
      throw error;
    }
  }

  async getRouteStatistics(routeId?: string) {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/routes/statistics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching route statistics:', error);
      throw error;
    }
  }

  async getBidirectionalStats(routeId: string) {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/routes/${routeId}/bidirectional`);
      return response.data;
    } catch (error) {
      console.error('Error fetching bidirectional stats:', error);
      throw error;
    }
  }

  async getBuses() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/buses`);
      return response.data;
    } catch (error) {
      console.error('Error fetching buses:', error);
      throw error;
    }
  }

  // ====== ADMIN FEATURES ======
  async getAdminStatistics() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/admin/statistics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching admin statistics:', error);
      throw error;
    }
  }

  async getAdminAlerts() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/admin/alerts`);
      return response.data;
    } catch (error) {
      console.error('Error fetching admin alerts:', error);
      throw error;
    }
  }

  async getPerformanceMetrics() {
    try {
      const response = await this.api.get(`${API_CONFIG.BASE_URL}/api/admin/performance`);
      return response.data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      throw error;
    }
  }

  async sendAnnouncement(title: string, message: string, priority: string = 'normal') {
    try {
      const response = await this.api.post(`${API_CONFIG.BASE_URL}/api/admin/announcement`, {
        title,
        message,
        priority,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error('Error sending announcement:', error);
      throw error;
    }
  }
}

export default new ApiService();