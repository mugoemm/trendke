import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiTrendingUp, FiMusic, FiSmile, FiZap, FiHeart, FiFilm } from 'react-icons/fi';
import { getTrendingVideos } from '../api/videoApi';
import toast from 'react-hot-toast';

const categories = [
  { id: 'trending', name: 'Trending', icon: <FiTrendingUp className="w-5 h-5" />, color: 'from-pink-500 to-rose-500' },
  { id: 'music', name: 'Music', icon: <FiMusic className="w-5 h-5" />, color: 'from-purple-500 to-indigo-500' },
  { id: 'comedy', name: 'Comedy', icon: <FiSmile className="w-5 h-5" />, color: 'from-amber-500 to-orange-500' },
  { id: 'entertainment', name: 'Entertainment', icon: <FiZap className="w-5 h-5" />, color: 'from-cyan-500 to-blue-500' },
  { id: 'lifestyle', name: 'Lifestyle', icon: <FiHeart className="w-5 h-5" />, color: 'from-red-500 to-pink-500' },
  { id: 'sports', name: 'Sports', icon: <FiFilm className="w-5 h-5" />, color: 'from-green-500 to-emerald-500' },
];

const Explore = () => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState('trending');
  const [trendingVideos, setTrendingVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrendingVideos();
  }, []);

  const loadTrendingVideos = async () => {
    try {
      setLoading(true);
      const videos = await getTrendingVideos(20);
      setTrendingVideos(videos);
    } catch (error) {
      console.error('Failed to load trending videos:', error);
      toast.error('Failed to load trending videos');
    } finally {
      setLoading(false);
    }
  };

  const handleVideoClick = (videoId) => {
    navigate('/', { state: { videoId } });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 pt-20 pb-24 md:pb-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Explore
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Discover trending content and explore categories
          </p>
        </div>

        {/* Category Tabs */}
        <div className="flex overflow-x-auto gap-3 mb-8 pb-2 scrollbar-hide">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold whitespace-nowrap transition-all ${
                activeCategory === category.id
                  ? `bg-gradient-to-r ${category.color} text-white shadow-lg scale-105`
                  : 'bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-800 hover:border-pink-500 dark:hover:border-pink-500'
              }`}
            >
              {category.icon}
              <span>{category.name}</span>
            </button>
          ))}
        </div>

        {/* Content Grid */}
        {loading ? (
          <div className="bg-white dark:bg-gray-900 rounded-2xl p-12 text-center border border-gray-200 dark:border-gray-800">
            <div className="relative w-16 h-16 mx-auto mb-4">
              <div className="absolute inset-0 rounded-full border-4 border-pink-500/30"></div>
              <div className="absolute inset-0 rounded-full border-4 border-t-pink-500 border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
            </div>
            <p className="text-gray-600 dark:text-gray-400">Loading trending videos...</p>
          </div>
        ) : trendingVideos.length === 0 ? (
          <div className="bg-white dark:bg-gray-900 rounded-2xl p-12 text-center border border-gray-200 dark:border-gray-800">
            <div className="w-24 h-24 bg-gradient-to-br from-pink-100 to-purple-100 dark:from-pink-900/20 dark:to-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiTrendingUp className="w-12 h-12 text-pink-500" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              No Trending Videos Yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
              Trending videos will appear here as more content is created and engaged with!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {trendingVideos.map((video, index) => (
              <div
                key={video.id}
                onClick={() => handleVideoClick(video.id)}
                className="group cursor-pointer"
              >
                <div className="relative aspect-[9/16] bg-gray-800 rounded-lg overflow-hidden">
                  {video.thumbnail_url ? (
                    <img
                      src={video.thumbnail_url}
                      alt={video.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-pink-500/20 to-purple-500/20">
                      <span className="text-4xl">🎥</span>
                    </div>
                  )}
                  {/* Rank Badge */}
                  {index < 3 && (
                    <div className={`absolute top-2 left-2 w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                      index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : 'bg-orange-600'
                    }`}>
                      {index + 1}
                    </div>
                  )}
                  {/* Play Icon Overlay */}
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
                    <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center">
                      <svg className="w-8 h-8 text-gray-900 ml-1" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                      </svg>
                    </div>
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/90 to-transparent">
                    <p className="text-white text-sm font-semibold truncate">{video.title}</p>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-white/80 text-xs">@{video.username}</span>
                      <span className="text-white/80 text-xs flex items-center">
                        <FiHeart className="w-3 h-3 mr-1" />
                        {video.likes_count}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Trending Hashtags */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Trending Hashtags
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['#trending', '#viral', '#foryou', '#dance', '#music', '#comedy', '#challenge', '#lifestyle'].map((tag) => (
              <div
                key={tag}
                className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-800 hover:border-pink-500 dark:hover:border-pink-500 cursor-pointer transition-all group"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-pink-500 font-bold text-lg">{tag}</span>
                  <FiTrendingUp className="w-5 h-5 text-pink-500 group-hover:scale-125 transition-transform" />
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {Math.floor(Math.random() * 100)}M views
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Suggested Creators */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Suggested Creators
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 hover:shadow-xl transition-all"
              >
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-500 to-purple-600"></div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 dark:text-white">Creator {i}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">@creator{i}</p>
                  </div>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Creating amazing content for you to enjoy
                </p>
                <button className="w-full px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all">
                  Follow
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Explore;
