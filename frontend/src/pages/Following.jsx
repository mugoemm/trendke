import React, { useState, useEffect } from 'react';
import { FiHeart, FiRefreshCw } from 'react-icons/fi';
import { socialApi } from '../api/socialApi';
import VideoPlayer from '../components/VideoPlayer';
import toast from 'react-hot-toast';

const Following = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadFollowingFeed();
  }, []);

  const loadFollowingFeed = async () => {
    try {
      setLoading(true);
      const data = await socialApi.getFollowingFeed(50, 0);
      setVideos(data);
    } catch (error) {
      console.error('Failed to load following feed:', error);
      toast.error('Failed to load videos from followed creators');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadFollowingFeed();
    setRefreshing(false);
    toast.success('Feed refreshed!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 rounded-full border-4 border-pink-500/30"></div>
            <div className="absolute inset-0 rounded-full border-4 border-t-pink-500 border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Loading following feed...</p>
        </div>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 pt-20 pb-24 md:pb-8">
        <div className="max-w-2xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-pink-500 to-purple-600 rounded-2xl mb-4">
              <FiHeart className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Following
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Videos from creators you follow
            </p>
          </div>

          {/* Empty State */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl p-12 text-center border border-gray-200 dark:border-gray-800">
            <div className="w-24 h-24 bg-gradient-to-br from-pink-100 to-purple-100 dark:from-pink-900/20 dark:to-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiHeart className="w-12 h-12 text-pink-500" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              No followed creators yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-sm mx-auto">
              Start following creators to see their latest videos here. Your personalized feed awaits!
            </p>
            <a
              href="/"
              className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
            >
              <span>Discover Creators</span>
            </a>
          </div>

          {/* Feature Info */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-800">
              <div className="text-2xl mb-2">🎬</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Latest Content</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">See new videos as they're uploaded</p>
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-800">
              <div className="text-2xl mb-2">🔔</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Notifications</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Get notified about new uploads</p>
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-800">
              <div className="text-2xl mb-2">⭐</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Personalized</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Your unique feed of favorites</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show videos in vertical feed format
  return (
    <div className="relative h-screen bg-black">
      {/* Refresh Button */}
      <button
        onClick={handleRefresh}
        disabled={refreshing}
        className="fixed top-20 right-4 z-40 p-3 bg-black/50 backdrop-blur-sm rounded-full text-white hover:bg-black/70 transition-all disabled:opacity-50"
      >
        <FiRefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
      </button>

      {/* Following Feed Badge */}
      <div className="fixed top-20 left-4 z-40 px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 rounded-full">
        <div className="flex items-center space-x-2">
          <FiHeart className="w-4 h-4 text-white" />
          <span className="text-white font-semibold text-sm">Following</span>
        </div>
      </div>

      {/* Vertical Video Feed */}
      <div className="h-screen overflow-y-scroll snap-y snap-mandatory scrollbar-hide">
        {videos.map((video, index) => (
          <div
            key={`${video.id}-${index}`}
            className="h-screen snap-start snap-always"
          >
            <VideoPlayer video={video} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Following;
