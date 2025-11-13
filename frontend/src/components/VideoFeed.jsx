import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useInView } from 'react-intersection-observer';
import { getVideoFeed } from '../api/videoApi';
import VideoPlayer from './VideoPlayer';
import { FiRefreshCw } from 'react-icons/fi';
import toast from 'react-hot-toast';

const VideoFeed = ({ initialVideoId }) => {
  const [videos, setVideos] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { ref, inView } = useInView({
    threshold: 0.5,
  });
  const videoRefs = useRef({});

  const fetchVideos = useCallback(async (isRefresh = false) => {
    if ((loading || !hasMore) && !isRefresh) return;

    setLoading(true);
    try {
      const limit = 10;
      const currentPage = isRefresh ? 1 : page;
      const offset = (currentPage - 1) * limit;
      const newVideos = await getVideoFeed(limit, offset);
      
      if (!newVideos || newVideos.length === 0) {
        setHasMore(false);
      } else {
        if (isRefresh) {
          setVideos(newVideos);
          setPage(2);
          setHasMore(true);
        } else {
          setVideos(prev => [...prev, ...newVideos]);
          setPage(prev => prev + 1);
        }
      }
    } catch (error) {
      console.error('Failed to fetch videos:', error);
      toast.error('Failed to load videos');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [page, loading, hasMore]);

  useEffect(() => {
    fetchVideos();
  }, []);

  // Scroll to specific video if initialVideoId is provided
  useEffect(() => {
    if (initialVideoId && videos.length > 0) {
      const videoIndex = videos.findIndex(v => v.id === initialVideoId);
      if (videoIndex !== -1 && videoRefs.current[initialVideoId]) {
        videoRefs.current[initialVideoId].scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    }
  }, [initialVideoId, videos]);

  useEffect(() => {
    if (inView && !loading && hasMore) {
      fetchVideos();
    }
  }, [inView, loading, hasMore]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchVideos(true);
  };

  const handleLikeUpdate = (videoId, newLikeCount, isLiked) => {
    setVideos(prevVideos =>
      prevVideos.map(video =>
        video.id === videoId
          ? { ...video, likes_count: newLikeCount, is_liked: isLiked }
          : video
      )
    );
  };

  if (videos.length === 0 && !loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-950">
        <div className="text-center px-4">
          <div className="w-24 h-24 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-white text-2xl font-bold mb-3">No videos yet</h3>
          <p className="text-gray-400 text-lg mb-6">Be the first to share your creativity!</p>
          <a
            href="/upload"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-xl transition-all"
          >
            <span>Upload Video</span>
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-screen">
      {/* Refresh Button */}
      <button
        onClick={handleRefresh}
        disabled={refreshing}
        className="fixed top-20 right-4 z-40 p-3 bg-black/50 backdrop-blur-sm rounded-full text-white hover:bg-black/70 transition-all disabled:opacity-50"
      >
        <FiRefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
      </button>

      {/* Video Feed */}
      <div className="h-screen overflow-y-scroll snap-y snap-mandatory scrollbar-hide">
        {videos.map((video, index) => (
          <div
            // Fix: Use id+index for unique key to avoid duplicate key warning
            key={`${video.id}-${index}`}
            className="h-screen snap-start snap-always"
            ref={(el) => {
              videoRefs.current[video.id] = el;
              if (index === videos.length - 3) {
                ref(el);
              }
            }}
          >
            {/* Pass video object to VideoPlayer, which uses video.video_url (dynamic, not hardcoded) */}
            <VideoPlayer video={video} onLikeUpdate={handleLikeUpdate} />
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="h-screen flex items-center justify-center bg-gray-950">
            <div className="text-center">
              <div className="relative w-16 h-16 mx-auto mb-4">
                <div className="absolute inset-0 rounded-full border-4 border-pink-500/30"></div>
                <div className="absolute inset-0 rounded-full border-4 border-t-pink-500 border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
              </div>
              <p className="text-gray-400 text-sm">Loading more videos...</p>
            </div>
          </div>
        )}

        {/* End of Feed */}
        {!hasMore && videos.length > 0 && (
          <div className="h-screen flex items-center justify-center bg-gray-950">
            <div className="text-center px-4">
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-white text-xl font-bold mb-2">You're all caught up!</h3>
              <p className="text-gray-400 mb-6">You've seen all the latest videos</p>
              <button
                onClick={handleRefresh}
                className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-xl transition-all"
              >
                Refresh Feed
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoFeed;
