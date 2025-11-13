import api from './videoApi';

// Social API - Follow/Unfollow features
export const socialApi = {
  // Follow a user
  followUser: async (userId) => {
    const response = await api.post(`/social/follow/${userId}`);
    return response.data;
  },

  // Unfollow a user
  unfollowUser: async (userId) => {
    const response = await api.delete(`/social/unfollow/${userId}`);
    return response.data;
  },

  // Check if following a user
  isFollowing: async (userId) => {
    const response = await api.get(`/social/is-following/${userId}`);
    return response.data;
  },

  // Get user's followers
  getFollowers: async (userId, limit = 50, offset = 0) => {
    const response = await api.get(`/social/followers/${userId}?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  // Get users someone is following
  getFollowing: async (userId, limit = 50, offset = 0) => {
    const response = await api.get(`/social/following/${userId}?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  // Get feed from followed users
  getFollowingFeed: async (limit = 20, offset = 0) => {
    const response = await api.get(`/social/feed/following?limit=${limit}&offset=${offset}`);
    return response.data;
  }
};

export default socialApi;
