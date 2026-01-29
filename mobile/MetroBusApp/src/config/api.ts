export const API_CONFIG = {
  BASE_URL: 'http://192.168.18.21:8000',  // Updated for physical device on same network
  WS_URL: 'ws://192.168.18.21:8000/ws/live-tracking',  // Updated WebSocket URL
  ENDPOINTS: {
    // Routes
    ROUTES: '/api/routes',
    BUSES: '/api/buses',
    ACTIVATE_ROUTE: '/api/routes/activate',
    
    // Journey Planning
    JOURNEY_PLAN: '/api/journey/plan',
    JOURNEY_QUICK_PLAN: '/api/journey/quick-plan',
    NEARBY_STOPS: '/api/journey/nearby-stops',
    TRANSFER_POINTS: '/api/journey/transfer-points',
    
    // Traffic & ETA
    TRAFFIC_CURRENT: '/api/traffic/current',
    TRAFFIC_ROUTE: '/api/traffic/route',
    ETA_ALL: '/api/eta/all',
    ETA_BUS: '/api/eta/bus',
    
    // Statistics & Analytics
    SIMULATION_STATUS: '/api/simulation/status',
    ROUTE_STATISTICS: '/api/routes/statistics',
    ROUTE_BIDIRECTIONAL: '/api/routes',
    
    // Admin Features
    ADMIN_STATISTICS: '/api/admin/statistics',
    ADMIN_ALERTS: '/api/admin/alerts',
    ADMIN_PERFORMANCE: '/api/admin/performance',
    ADMIN_ANNOUNCEMENT: '/api/admin/announcement',
  }
};

