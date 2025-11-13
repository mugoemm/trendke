import React from 'react';

/**
 * Skeleton loader for video cards
 */
export const VideoSkeleton = () => (
  <div className="h-screen bg-gray-950 flex items-center justify-center">
    <div className="w-full max-w-md">
      <div className="animate-pulse">
        <div className="bg-gray-800 h-96 rounded-lg mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-800 rounded w-3/4"></div>
          <div className="h-4 bg-gray-800 rounded w-1/2"></div>
        </div>
      </div>
    </div>
  </div>
);

/**
 * Spinner component
 */
export const Spinner = ({ size = 'md', color = 'pink' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const colors = {
    pink: 'border-pink-500',
    purple: 'border-purple-500',
    white: 'border-white',
    gray: 'border-gray-500'
  };

  return (
    <div className={`${sizes[size]} border-4 ${colors[color]} border-t-transparent rounded-full animate-spin`}></div>
  );
};

/**
 * Full page loader
 */
export const PageLoader = ({ message = 'Loading...' }) => (
  <div className="fixed inset-0 bg-gray-950 flex flex-col items-center justify-center z-50">
    <div className="relative">
      <div className="absolute inset-0 rounded-full border-4 border-pink-500/30"></div>
      <div className="absolute inset-0 rounded-full border-4 border-t-pink-500 border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
      <div className="w-16 h-16"></div>
    </div>
    {message && (
      <p className="mt-6 text-gray-400 text-sm font-medium">{message}</p>
    )}
  </div>
);

/**
 * Button with loading state
 */
export const LoadingButton = ({ 
  children, 
  loading, 
  disabled, 
  className = '',
  ...props 
}) => (
  <button
    disabled={loading || disabled}
    className={`relative ${className} ${loading || disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
    {...props}
  >
    {loading && (
      <span className="absolute inset-0 flex items-center justify-center">
        <Spinner size="sm" color="white" />
      </span>
    )}
    <span className={loading ? 'invisible' : ''}>{children}</span>
  </button>
);

/**
 * Card skeleton for profiles/lists
 */
export const CardSkeleton = () => (
  <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 animate-pulse">
    <div className="flex items-center space-x-4 mb-4">
      <div className="w-12 h-12 bg-gray-300 dark:bg-gray-700 rounded-full"></div>
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4"></div>
        <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded w-1/2"></div>
      </div>
    </div>
    <div className="space-y-2">
      <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded"></div>
      <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded w-5/6"></div>
    </div>
  </div>
);

/**
 * Error state component
 */
export const ErrorState = ({ 
  title = 'Something went wrong',
  message = 'Please try again later',
  onRetry 
}) => (
  <div className="flex flex-col items-center justify-center min-h-[400px] text-center px-4">
    <div className="text-6xl mb-4">😕</div>
    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{title}</h3>
    <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all"
      >
        Try Again
      </button>
    )}
  </div>
);

export default {
  VideoSkeleton,
  Spinner,
  PageLoader,
  LoadingButton,
  CardSkeleton,
  ErrorState
};
