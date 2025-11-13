/**
 * Performance utilities for video handling
 */

/**
 * Preload next videos for smooth scrolling
 * @param {Array} videos - Array of video objects
 * @param {number} currentIndex - Current video index
 * @param {number} preloadCount - Number of videos to preload
 */
export const preloadVideos = (videos, currentIndex, preloadCount = 2) => {
  const videosToPreload = videos.slice(
    currentIndex + 1,
    currentIndex + 1 + preloadCount
  );

  videosToPreload.forEach((video) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'video';
    link.href = video.video_url;
    document.head.appendChild(link);
  });
};

/**
 * Debounce function for performance
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function for scroll events
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in ms
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Check if video should be loaded based on viewport
 * @param {HTMLElement} element - Video element
 * @param {number} threshold - Distance threshold in pixels
 */
export const isInViewport = (element, threshold = 100) => {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= -threshold &&
    rect.left >= -threshold &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + threshold &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth) + threshold
  );
};

/**
 * Format view count for display
 * @param {number} count - View count
 */
export const formatViewCount = (count) => {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
};

/**
 * Format duration for video timestamp
 * @param {number} seconds - Duration in seconds
 */
export const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};
