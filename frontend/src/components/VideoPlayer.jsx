import React, { useState, useRef, useEffect } from 'react';
import { FiHeart, FiMessageCircle, FiShare2, FiMoreVertical, FiUserPlus, FiUserCheck, FiVolume2, FiVolumeX } from 'react-icons/fi';
import { FaHeart } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { likeVideo, getComments, addComment } from '../api/videoApi';
import { socialApi } from '../api/socialApi';
import GiftButton from './GiftButton';
import toast from 'react-hot-toast';

const VideoPlayer = ({ video, onLikeUpdate }) => {
  const [isLiked, setIsLiked] = useState(video.is_liked);
  const [likesCount, setLikesCount] = useState(video.likes_count);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFollowing, setIsFollowing] = useState(false);
  const [showLikeAnimation, setShowLikeAnimation] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const videoRef = useRef(null);
  const lastTapRef = useRef(0);
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const isOwnVideo = currentUser.id === video.user_id;

  // Check if following on mount
  useEffect(() => {
    if (!isOwnVideo && currentUser.id) {
      checkFollowingStatus();
    }
  }, [video.user_id]);

  const checkFollowingStatus = async () => {
    try {
      const result = await socialApi.isFollowing(video.user_id);
      setIsFollowing(result.following);
    } catch (error) {
      console.error('Failed to check following status:', error);
    }
  };

  // IntersectionObserver: try to autoplay, but catch NotAllowedError and show overlay if needed
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          if (videoRef.current) {
            videoRef.current.play()
              .then(() => {
                setIsPlaying(true);
                setShowOverlay(false); // Hide overlay if autoplay works
              })
              .catch((err) => {
                // Autoplay failed, show overlay
                setIsPlaying(false);
                setShowOverlay(true);
                // Comment: NotAllowedError is expected if user hasn't interacted
              });
          }
        } else {
          videoRef.current?.pause();
          setIsPlaying(false);
        }
      },
      { threshold: 0.5 }
    );
    if (videoRef.current) {
      observer.observe(videoRef.current);
    }
    return () => observer.disconnect();
  }, []);

  const handleLike = async () => {
    try {
      const response = await likeVideo(video.id);
      setIsLiked(response.liked);
      setLikesCount(response.likes_count);
      onLikeUpdate?.(video.id, response.likes_count, response.liked);
    } catch (error) {
      toast.error('Failed to like video');
    }
  };

  const handleShowComments = async () => {
    if (!showComments) {
      try {
        const response = await getComments(video.id);
        setComments(response);
      } catch (error) {
        toast.error('Failed to load comments');
      }
    }
    setShowComments(!showComments);
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const comment = await addComment(video.id, newComment);
      setComments([comment, ...comments]);
      setNewComment('');
      toast.success('Comment added');
    } catch (error) {
      toast.error('Failed to add comment');
    }
  };

  const handleFollow = async () => {
    try {
      if (isFollowing) {
        await socialApi.unfollowUser(video.user_id);
        setIsFollowing(false);
        toast.success('Unfollowed');
      } else {
        await socialApi.followUser(video.user_id);
        setIsFollowing(true);
        toast.success('Following!');
      }
    } catch (error) {
      toast.error('Failed to update follow status');
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: video.title,
        text: video.description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard');
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted;
      setIsMuted(!isMuted);
    }
  };

  // Overlay state for 'Tap to play' button
  const [showOverlay, setShowOverlay] = useState(false);

  // Double-tap to like (TikTok-style)
  const handleVideoClick = () => {
    const now = Date.now();
    const timeSinceLastTap = now - lastTapRef.current;
    
    // Double tap detected (within 300ms)
    if (timeSinceLastTap < 300 && timeSinceLastTap > 0) {
      // Double tap - trigger like
      if (!isLiked) {
        handleLike();
      }
      // Show heart animation
      setShowLikeAnimation(true);
      setTimeout(() => setShowLikeAnimation(false), 1000);
      lastTapRef.current = 0; // Reset
    } else {
      // Single tap - play/pause
      lastTapRef.current = now;
      if (videoRef.current) {
        if (isPlaying) {
          videoRef.current.pause();
          setIsPlaying(false);
        } else {
          videoRef.current.play()
            .then(() => {
              setIsPlaying(true);
              setShowOverlay(false); // Hide overlay after user taps
            })
            .catch(() => {
              setShowOverlay(true); // Still failed, keep overlay
            });
        }
      }
    }
  };

  return (
    <div className="relative h-full w-full bg-black">
      {/* Video */}
      <video
        ref={videoRef}
        src={video.video_url}
        className="h-full w-full object-contain cursor-pointer"
        loop
        playsInline
        muted={isMuted}
        onClick={handleVideoClick}
      />
      
      {/* Double-tap heart animation */}
      {showLikeAnimation && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-30">
          <FaHeart className="text-white text-9xl animate-ping opacity-80" />
        </div>
      )}
      
      {/* 'Tap to play' overlay if autoplay fails */}
      {showOverlay && (
        <button
          className="absolute inset-0 flex items-center justify-center bg-black/60 z-20 text-white text-xl font-bold"
          style={{ pointerEvents: 'auto' }}
          onClick={handleVideoClick}
        >
          Tap to play
        </button>
      )}

      {/* Video Info Overlay */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
        <div className="flex items-center justify-between mb-3">
          <Link to={`/profile/${video.user_id}`} className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center">
              <span className="text-white font-semibold">
                {video.username?.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="text-white font-semibold">{video.username}</span>
          </Link>
          
          {/* Follow Button */}
          {!isOwnVideo && (
            <button
              onClick={handleFollow}
              className={`px-4 py-1.5 rounded-full font-semibold transition-all ${
                isFollowing
                  ? 'bg-gray-600 text-white'
                  : 'bg-gradient-to-r from-pink-500 to-purple-600 text-white'
              }`}
            >
              {isFollowing ? (
                <div className="flex items-center space-x-1">
                  <FiUserCheck className="w-4 h-4" />
                  <span>Following</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1">
                  <FiUserPlus className="w-4 h-4" />
                  <span>Follow</span>
                </div>
              )}
            </button>
          )}
        </div>

        <h3 className="text-white font-medium mb-2">{video.title}</h3>
        {video.description && (
          <p className="text-gray-300 text-sm mb-2">{video.description}</p>
        )}
        {video.hashtags && video.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {video.hashtags.map((tag, index) => (
              <span key={index} className="text-pink-400 text-sm">
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="absolute right-4 bottom-20 flex flex-col space-y-6">
        {/* Mute/Unmute Button */}
        <button
          onClick={toggleMute}
          className="flex flex-col items-center space-y-1"
        >
          {isMuted ? (
            <FiVolumeX className="text-white" size={32} />
          ) : (
            <FiVolume2 className="text-white" size={32} />
          )}
        </button>

        <button
          onClick={handleLike}
          className="flex flex-col items-center space-y-1"
        >
          {isLiked ? (
            <FaHeart className="text-pink-500" size={32} />
          ) : (
            <FiHeart className="text-white" size={32} />
          )}
          <span className="text-white text-xs">{likesCount}</span>
        </button>

        <button
          onClick={handleShowComments}
          className="flex flex-col items-center space-y-1"
        >
          <FiMessageCircle className="text-white" size={32} />
          <span className="text-white text-xs">{video.comments_count}</span>
        </button>

        <GiftButton receiverId={video.user_id} />

        <button onClick={handleShare} className="flex flex-col items-center space-y-1">
          <FiShare2 className="text-white" size={32} />
          <span className="text-white text-xs">Share</span>
        </button>
      </div>

      {/* Comments Modal */}
      {showComments && (
        <div className="absolute inset-0 bg-black/90 z-50 flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-gray-700">
            <h3 className="text-white text-lg font-semibold">Comments</h3>
            <button onClick={() => setShowComments(false)} className="text-white">
              <FiMoreVertical size={24} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {comments.map((comment) => (
              <div key={comment.id} className="flex space-x-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-sm">
                    {comment.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="text-white text-sm font-semibold">{comment.username}</p>
                  <p className="text-gray-300 text-sm">{comment.content}</p>
                  <p className="text-gray-500 text-xs mt-1">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleAddComment} className="p-4 border-t border-gray-700">
            <div className="flex space-x-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="flex-1 bg-gray-800 text-white rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-semibold hover:opacity-90 transition"
              >
                Post
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;
