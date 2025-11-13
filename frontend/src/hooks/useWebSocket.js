/**
 * Simple WebSocket Hook - Fresh Implementation
 * No complex reconnection logic, just clean connection management
 */

import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (url, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const onMessageRef = useRef(onMessage);
  const connectionAttemptedRef = useRef(false);

  // Keep callback ref updated without triggering reconnects
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    if (!url) {
      console.log('⚠️ No URL provided to WebSocket');
      return;
    }

    // Prevent duplicate connections
    if (connectionAttemptedRef.current && wsRef.current) {
      console.log('⚠️ Connection already exists, skipping');
      return;
    }

    connectionAttemptedRef.current = true;
    console.log('🔌 Attempting WebSocket connection to:', url.replace(/token=[^&]+/, 'token=***'));

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket CONNECTED!');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type !== 'pong' && onMessageRef.current) {
            onMessageRef.current(data);
          }
        } catch (error) {
          console.error('Parse error:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket ERROR:', error);
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket CLOSED - Code:', event.code, 'Reason:', event.reason || 'No reason provided');
        setIsConnected(false);
        wsRef.current = null;
        connectionAttemptedRef.current = false;
      };
    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
      connectionAttemptedRef.current = false;
    }

    // Cleanup on unmount
    return () => {
      console.log('🧹 Cleaning up WebSocket...');
      connectionAttemptedRef.current = false;
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [url]); // ONLY url as dependency!

  const send = (data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
      return true;
    }
    console.warn('⚠️ WebSocket not connected');
    return false;
  };

  return { isConnected, send };
};

export default useWebSocket;
