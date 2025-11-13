import api from './videoApi';

// Live API
export const liveApi = {
  // Start live session
  startLive: async (sessionData) => {
    const response = await api.post('/live/start', sessionData);
    return response.data;
  },

  // Join live session
  joinLive: async (sessionId) => {
    const response = await api.post('/live/join', { session_id: sessionId });
    return response.data;
  },

  // End live session
  endLive: async (sessionId) => {
    const response = await api.post(`/live/${sessionId}/end`);
    return response.data;
  },

  // Get active sessions
  getActiveSessions: async () => {
    const response = await api.get('/live/list?status=active');
    return response.data;
  },

  // Get session details
  getSessionDetails: async (sessionId) => {
    const response = await api.get(`/live/${sessionId}`);
    return response.data;
  },
};

// Export individual functions for convenience
export const startLive = liveApi.startLive;
export const joinLive = liveApi.joinLive;
export const endLive = liveApi.endLive;
export const getActiveSessions = liveApi.getActiveSessions;
export const getSessionDetails = liveApi.getSessionDetails;

export default liveApi;
