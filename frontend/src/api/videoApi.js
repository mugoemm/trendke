import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Video API
export const videoApi = {
  // Get video feed
  getFeed: async (limit = 20, offset = 0) => {
    const response = await api.get(`/videos/feed?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  // Get trending videos
  getTrending: async (limit = 20) => {
    const response = await api.get(`/videos/trending/videos?limit=${limit}`);
    return response.data;
  },

  // Get video details
  getVideoDetails: async (videoId) => {
    const response = await api.get(`/videos/${videoId}`);
    return response.data;
  },

  // Upload video
  uploadVideo: async (formData) => {
    const response = await api.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Like video
  likeVideo: async (videoId) => {
    const response = await api.post(`/videos/${videoId}/like`);
    return response.data;
  },

  // Get comments
  getComments: async (videoId, limit = 50) => {
    const response = await api.get(`/videos/${videoId}/comments?limit=${limit}`);
    return response.data;
  },

  // Add comment
  addComment: async (videoId, content) => {
    const response = await api.post(`/videos/${videoId}/comment`, {
      content: content,
    });
    return response.data;
  },
};

// Export individual functions for convenience
export const uploadVideo = videoApi.uploadVideo;
export const getVideoFeed = videoApi.getFeed;
export const getTrendingVideos = videoApi.getTrending;
export const getVideoById = videoApi.getVideoDetails;
export const likeVideo = videoApi.likeVideo;
export const getComments = videoApi.getComments;
export const addComment = videoApi.addComment;

export default api;
