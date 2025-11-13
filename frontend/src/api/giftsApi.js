import api from './videoApi';

// Gifts API
export const giftsApi = {
  // Get gift types
  getGiftTypes: async () => {
    const response = await api.get('/gifts/types');
    return response.data;
  },

  // Send gift
  sendGift: async (giftData) => {
    const response = await api.post('/gifts/send', giftData);
    return response.data;
  },

  // Get user balance
  getBalance: async (userId = null) => {
    const url = userId ? `/gifts/balance/${userId}` : '/gifts/balance';
    const response = await api.get(url);
    return response.data;
  },

  // Get leaderboard
  getLeaderboard: async (limit = 50) => {
    const response = await api.get(`/gifts/leaderboard?limit=${limit}`);
    return response.data;
  },

  // Get gift history
  getGiftHistory: async (limit = 50) => {
    const response = await api.get(`/gifts/history?limit=${limit}`);
    return response.data;
  },
};

// Payments API
export const paymentsApi = {
  // Get coin packages
  getPackages: async () => {
    const response = await api.get('/payments/packages');
    return response.data;
  },

  // Initiate purchase
  initiatePurchase: async (purchaseData) => {
    const response = await api.post('/payments/purchase/initiate', purchaseData);
    return response.data;
  },

  // Get payment history
  getPaymentHistory: async (limit = 50) => {
    const response = await api.get(`/payments/history?limit=${limit}`);
    return response.data;
  },
};

// Export individual functions for convenience
export const getGiftTypes = giftsApi.getGiftTypes;
export const sendGift = giftsApi.sendGift;
export const getBalance = giftsApi.getBalance;
export const getLeaderboard = giftsApi.getLeaderboard;
export const getGiftHistory = giftsApi.getGiftHistory;

export default giftsApi;
