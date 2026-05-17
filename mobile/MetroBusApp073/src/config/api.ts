export const API_CONFIG = {
  // Android Emulator: use 10.0.2.2 to reach host machine localhost
  BASE_URL: 'http://10.0.2.2:8000',
  WS_URL: 'ws://10.0.2.2:8000/ws/live-tracking',
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

    // Metro AI Assistant (Groq backend — same as web)
    CHAT_SESSIONS: '/api/chat/sessions',
    chatMessagesPath: (sessionId: string) =>
      `/api/chat/sessions/${encodeURIComponent(sessionId)}/messages`,
    chatStreamPath: (sessionId: string) =>
      `/api/chat/sessions/${encodeURIComponent(sessionId)}/messages/stream`,
  },
};
