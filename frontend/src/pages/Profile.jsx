import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authApi } from '../api/authApi';
import { videoApi } from '../api/videoApi';
import { giftsApi } from '../api/giftsApi';
import { FaCoins } from 'react-icons/fa';
import toast from 'react-hot-toast';

const Profile = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [videos, setVideos] = useState([]);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const isOwnProfile = !userId || userId === currentUser.id;

  useEffect(() => {
    loadProfile();
    loadUserVideos();
    if (isOwnProfile) {
      loadBalance();
    }
  }, [userId]);

  const loadProfile = async () => {
    try {
      const data = userId 
        ? await authApi.getUserProfile(userId)
        : await authApi.getCurrentUser();
      setProfile(data);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const loadUserVideos = async () => {
    try {
      const allVideos = await videoApi.getFeed(100, 0);
      const userVideos = allVideos.filter(v => 
        v.user_id === (userId || currentUser.id)
      );
      setVideos(userVideos);
    } catch (error) {
      console.error('Failed to load videos:', error);
    }
  };

  const loadBalance = async () => {
    try {
      const data = await giftsApi.getBalance();
      setBalance(data);
    } catch (error) {
      console.error('Failed to load balance:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <p className="text-white">Profile not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 pb-20">
      {/* Profile header */}
      <div className="bg-gray-800 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-start space-x-6">
            <img
              src={profile.avatar_url || 'https://via.placeholder.com/120'}
              alt={profile.username}
              className="w-24 h-24 rounded-full"
            />
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-white">{profile.username}</h1>
              {profile.full_name && (
                <p className="text-white/60">{profile.full_name}</p>
              )}
              {profile.bio && (
                <p className="text-white/80 mt-2">{profile.bio}</p>
              )}

              <div className="flex items-center space-x-6 mt-4">
                <div>
                  <p className="text-white font-bold">{videos.length}</p>
                  <p className="text-white/60 text-sm">Videos</p>
                </div>
                <div>
                  <p className="text-white font-bold">{profile.followers_count}</p>
                  <p className="text-white/60 text-sm">Followers</p>
                </div>
                <div>
                  <p className="text-white font-bold">{profile.following_count}</p>
                  <p className="text-white/60 text-sm">Following</p>
                </div>
              </div>

              {isOwnProfile && (
                <div className="flex items-center space-x-4 mt-4">
                  {balance && (
                    <div className="bg-gray-700 px-4 py-2 rounded-lg flex items-center space-x-2">
                      <FaCoins className="text-yellow-400" />
                      <span className="text-white font-semibold">{balance.coin_balance} coins</span>
                    </div>
                  )}
                  {profile.role === 'creator' && balance && (
                    <div className="bg-green-600 px-4 py-2 rounded-lg">
                      <span className="text-white font-semibold">
                        ${balance.total_earnings.toFixed(2)} earned
                      </span>
                    </div>
                  )}
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                  >
                    Dashboard
                  </button>
                  <button
                    onClick={handleLogout}
                    className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Videos grid */}
      <div className="max-w-6xl mx-auto p-6">
        <h2 className="text-xl font-bold text-white mb-4">Videos</h2>
        <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
          {videos.map((video) => (
            <div
              key={video.id}
              onClick={() => navigate('/', { state: { videoId: video.id } })}
              className="aspect-[9/16] bg-gray-800 rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity relative group"
            >
              {video.thumbnail_url ? (
                <img
                  src={video.thumbnail_url}
                  alt={video.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <span className="text-4xl">🎥</span>
                </div>
              )}
              {/* Play icon overlay */}
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
                <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-900 ml-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                  </svg>
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent">
                <p className="text-white text-xs truncate">{video.title}</p>
                <p className="text-white/60 text-xs">
                  {video.views_count} views
                </p>
              </div>
            </div>
          ))}
        </div>

        {videos.length === 0 && (
          <p className="text-white/60 text-center py-12">No videos yet</p>
        )}
      </div>
    </div>
  );
};

export default Profile;
