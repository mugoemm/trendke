/**
 * API Error Handler - Centralized error handling for API calls
 */
import toast from 'react-hot-toast';

export class APIError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.details = details;
  }
}

/**
 * Handle API errors consistently across the app
 * @param {Error} error - The error object
 * @param {string} defaultMessage - Default message if error has no message
 */
export const handleAPIError = (error, defaultMessage = 'An error occurred') => {
  console.error('API Error:', error);

  if (error instanceof APIError) {
    // Handle specific HTTP status codes
    switch (error.status) {
      case 401:
        toast.error('Session expired. Please login again.');
        // Redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        break;
      
      case 403:
        toast.error('You don\'t have permission to perform this action');
        break;
      
      case 404:
        toast.error('Resource not found');
        break;
      
      case 429:
        toast.error('Too many requests. Please slow down.');
        break;
      
      case 500:
      case 502:
      case 503:
        toast.error('Server error. Please try again later.');
        break;
      
      default:
        toast.error(error.message || defaultMessage);
    }
  } else if (error.message === 'Network Error' || error.message.includes('fetch')) {
    toast.error('Network error. Please check your connection.');
  } else {
    toast.error(error.message || defaultMessage);
  }
};

/**
 * Wrap API calls with error handling
 * @param {Function} apiCall - The API function to call
 * @param {string} errorMessage - Custom error message
 */
export const withErrorHandling = async (apiCall, errorMessage) => {
  try {
    return await apiCall();
  } catch (error) {
    handleAPIError(error, errorMessage);
    throw error;
  }
};

/**
 * Retry failed API calls with exponential backoff
 * @param {Function} fn - The function to retry
 * @param {number} maxRetries - Maximum number of retries
 * @param {number} delay - Initial delay in ms
 */
export const retryWithBackoff = async (fn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Don't retry on client errors (4xx)
      if (error instanceof APIError && error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      // Wait with exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};
