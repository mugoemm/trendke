import api from './videoApi';

// Auth API
export const authApi = {
  // Signup
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },

  // Login
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Get user profile
  getUserProfile: async (userId) => {
    const response = await api.get(`/auth/user/${userId}`);
    return response.data;
  },

  // Forgot password
  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  // Reset password
  resetPassword: async (token, new_password) => {
    const response = await api.post('/auth/reset-password', { token, new_password });
    return response.data;
  },

  // Resend verification email
  resendVerification: async () => {
    const response = await api.post('/auth/resend-verification');
    return response.data;
  },

  // Verify email
  verifyEmail: async (token) => {
    const response = await api.post('/auth/verify-email', { token });
    return response.data;
  },

  // Toggle 2FA
  toggle2FA: async (enable) => {
    const response = await api.post('/auth/2fa/enable', { enable });
    return response.data;
  },

  // Send 2FA code
  send2FACode: async (email) => {
    const response = await api.post('/auth/2fa/send-code', { email });
    return response.data;
  },

  // Verify 2FA code
  verify2FA: async (email, code) => {
    const response = await api.post('/auth/2fa/verify', { email, code });
    return response.data;
  },
};

// Export individual functions for convenience
export const signup = authApi.signup;
export const login = authApi.login;
export const getCurrentUser = authApi.getCurrentUser;
export const getUserProfile = authApi.getUserProfile;
export const forgotPassword = authApi.forgotPassword;
export const resetPassword = authApi.resetPassword;
export const resendVerification = authApi.resendVerification;
export const verifyEmail = authApi.verifyEmail;
export const toggle2FA = authApi.toggle2FA;
export const send2FACode = authApi.send2FACode;
export const verify2FA = authApi.verify2FA;

export default authApi;
