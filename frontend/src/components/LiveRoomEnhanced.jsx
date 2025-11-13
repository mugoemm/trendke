import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  FiX, FiUsers, FiMic, FiMicOff, FiVideo, FiVideoOff, 
  FiMaximize2, FiMinimize2, FiUserPlus, FiUserMinus,
  FiMessageSquare, FiHeart, FiMoreVertical, FiImage, FiMonitor
} from 'react-icons/fi';
import { getActiveSessions, joinLive, endLive } from '../api/liveApi';
import api from '../api/videoApi';
import GiftButton from './GiftButton';
import toast from 'react-hot-toast';
import useWebSocket from '../hooks/useWebSocket';
import WebRTCManager from '../utils/WebRTCManager';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const WS_BASE = API_BASE.replace('http', 'ws');

const LiveRoomEnhanced = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [isHost, setIsHost] = useState(false);
  const [viewerCount, setViewerCount] = useState(0);
  
  // Media states
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [stream, setStream] = useState(null);
  const [isLoadingMedia, setIsLoadingMedia] = useState(false);
  const [hideCamera, setHideCamera] = useState(false);
  const [backgroundImage, setBackgroundImage] = useState(null);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  
  // Multi-guest states
  const [guests, setGuests] = useState([]);
  const [remoteStreams, setRemoteStreams] = useState({}); // userId -> MediaStream
  const [pendingRequests, setPendingRequests] = useState([]);
  const [focusedGuestId, setFocusedGuestId] = useState(null);
  const [showGuestRequests, setShowGuestRequests] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  
  const videoRef = useRef(null);
  const guestVideoRefs = useRef({});
  const fileInputRef = useRef(null);
  const webrtcManagerRef = useRef(null);
  const currentUserRef = useRef({ id: null, username: null });

  // Get token from localStorage
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  currentUserRef.current = { id: user.id, username: user.username };

  // Only create WebSocket URL when we have session data
  const [wsUrl, setWsUrl] = useState(null);

  // Update WebSocket URL when session loads
  useEffect(() => {
    if (sessionId && token && (user.username || session?.host_username)) {
      const username = user.username || session?.host_username || 'Guest';
      const url = `${WS_BASE}/ws/live/${sessionId}?token=${token}&username=${encodeURIComponent(username)}`;
      console.log('🔍 WebSocket URL ready:', url.replace(token, '***'));
      setWsUrl(url);
    } else {
      console.warn('⚠️ Missing data for WebSocket - sessionId:', sessionId, 'token:', !!token, 'username:', user.username);
    }
  }, [sessionId, token, session, user.username]);

  const { isConnected, send: sendWS } = useWebSocket(wsUrl, handleWebSocketMessage);

  useEffect(() => {
    fetchSessionDetails();
    joinSession();

    return () => {
      stopMediaStream();
      if (webrtcManagerRef.current) {
        webrtcManagerRef.current.cleanup();
      }
    };
  }, [sessionId]);

  // Handle incoming WebSocket messages
  function handleWebSocketMessage(data) {
    console.log('📨 WebSocket message:', data.type);

    switch (data.type) {
      case 'current_participants':
        // Initial participant list
        handleCurrentParticipants(data.participants);
        setViewerCount(data.viewer_count);
        break;

      case 'user_joined':
        handleUserJoined(data);
        setViewerCount(data.viewer_count);
        break;

      case 'user_left':
        handleUserLeft(data);
        setViewerCount(data.viewer_count);
        break;

      case 'chat_message':
        handleChatMessage(data);
        break;

      case 'reaction':
        handleReaction(data);
        break;

      case 'guest_request':
        handleGuestRequest(data);
        break;

      case 'guest_approved':
        handleGuestApproved(data);
        break;

      case 'guest_rejected':
        toast.error(`Your guest request was declined by ${data.rejected_by}`);
        break;

      case 'guest_joined':
        handleGuestJoined(data);
        break;

      case 'force_mute_audio':
        setAudioEnabled(false);
        if (webrtcManagerRef.current) {
          webrtcManagerRef.current.toggleAudio(false);
        }
        toast.warning(`You were muted by ${data.by}`);
        break;

      case 'force_mute_video':
        setVideoEnabled(false);
        if (webrtcManagerRef.current) {
          webrtcManagerRef.current.toggleVideo(false);
        }
        toast.warning(`Your video was disabled by ${data.by}`);
        break;

      case 'kicked':
        toast.error(`You were removed from the session by ${data.by}`);
        navigate('/');
        break;

      case 'promoted':
        toast.success(`You've been promoted to ${data.new_role}!`);
        if (session) {
          setSession({ ...session, role: data.new_role });
        }
        break;

      case 'participant_media_changed':
        // Update guest media status in UI
        setGuests(prevGuests =>
          prevGuests.map(g =>
            g.user_id === data.user_id
              ? {
                  ...g,
                  audio_enabled: data.audio_enabled ?? g.audio_enabled,
                  video_enabled: data.video_enabled ?? g.video_enabled
                }
              : g
          )
        );
        break;

      case 'webrtc_signal':
        handleWebRTCSignal(data);
        break;

      case 'session_ended':
        toast.info('Live session has ended');
        navigate('/');
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  }

  function handleCurrentParticipants(participants) {
    console.log('👥 Current participants:', participants);
    
    const guestList = participants.filter(p => p.role !== 'viewer');
    setGuests(guestList);

    // Initialize WebRTC connections for existing guests
    if (webrtcManagerRef.current) {
      participants.forEach(p => {
        if (p.user_id !== currentUserRef.current.id && p.role !== 'viewer') {
          // Create offer for existing participants
          setTimeout(() => {
            webrtcManagerRef.current.createOffer(p.user_id);
          }, 1000);
        }
      });
    }
  }

  function handleUserJoined(data) {
    console.log('👤 User joined:', data.username);
    toast.info(`${data.username} joined`);
    
    if (data.role !== 'viewer') {
      setGuests(prev => {
        if (prev.some(g => g.user_id === data.user_id)) {
          return prev;
        }
        return [...prev, {
          user_id: data.user_id,
          username: data.username,
          role: data.role,
          audio_enabled: true,
          video_enabled: true
        }];
      });

      // If I'm already streaming, create offer for new user
      if (webrtcManagerRef.current && data.user_id !== currentUserRef.current.id) {
        setTimeout(() => {
          webrtcManagerRef.current.createOffer(data.user_id);
        }, 500);
      }
    }
  }

  function handleUserLeft(data) {
    console.log('👋 User left:', data.username);
    toast.info(`${data.username} left`);
    
    setGuests(prev => prev.filter(g => g.user_id !== data.user_id));
    
    // Remove WebRTC connection
    if (webrtcManagerRef.current) {
      webrtcManagerRef.current.removePeerConnection(data.user_id);
    }
    
    // Remove remote stream
    setRemoteStreams(prev => {
      const updated = { ...prev };
      delete updated[data.user_id];
      return updated;
    });
  }

  function handleChatMessage(data) {
    setChatMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      user_id: data.user_id,
      username: data.username,
      message: data.message,
      timestamp: data.timestamp
    }]);

    // Auto-scroll chat
    setTimeout(() => {
      const chatContainer = document.querySelector('.chat-messages');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 100);
  }

  function handleReaction(data) {
    console.log('💖 Reaction:', data.reaction, 'from', data.username);
    
    // Show floating reaction animation
    const reactionEl = document.createElement('div');
    reactionEl.className = 'reaction-float';
    reactionEl.textContent = data.reaction;
    reactionEl.style.cssText = `
      position: fixed;
      left: ${Math.random() * 80 + 10}%;
      bottom: 10%;
      font-size: 3rem;
      animation: float-up 3s ease-out forwards;
      pointer-events: none;
      z-index: 9999;
    `;
    
    document.body.appendChild(reactionEl);
    
    setTimeout(() => {
      reactionEl.remove();
    }, 3000);
  }

  function handleGuestRequest(data) {
    console.log('🙋 Guest request from:', data.username);
    
    setPendingRequests(prev => {
      if (prev.some(r => r.user_id === data.user_id)) {
        return prev;
      }
      return [...prev, {
        user_id: data.user_id,
        username: data.username,
        timestamp: data.timestamp
      }];
    });
    
    toast.info(`${data.username} wants to join as guest`, {
      duration: 5000
    });
  }

  function handleGuestApproved(data) {
    toast.success(`You've been approved as a guest by ${data.approved_by}!`);
    
    // Start sending WebRTC stream
    if (webrtcManagerRef.current && stream) {
      guests.forEach(guest => {
        if (guest.user_id !== currentUserRef.current.id) {
          webrtcManagerRef.current.createOffer(guest.user_id);
        }
      });
    }
  }

  function handleGuestJoined(data) {
    console.log('✅ Guest joined:', data.username);
    toast.success(`${data.username} joined as guest`);
  }

  function handleWebRTCSignal(data) {
    if (!webrtcManagerRef.current) return;

    const { signal_type, from_user_id, signal_data } = data;

    switch (signal_type) {
      case 'offer':
        webrtcManagerRef.current.handleOffer(from_user_id, signal_data);
        break;
      
      case 'answer':
        webrtcManagerRef.current.handleAnswer(from_user_id, signal_data);
        break;
      
      case 'ice_candidate':
        webrtcManagerRef.current.handleIceCandidate(from_user_id, signal_data);
        break;
    }
  }

  const fetchSessionDetails = async () => {
    try {
      const sessions = await getActiveSessions();
      const currentSession = sessions.find(s => s.id === sessionId);
      
      if (currentSession) {
        setSession(currentSession);
        setViewerCount(currentSession.viewer_count);
        
        const currentUserId = localStorage.getItem('user_id');
        const userIsHost = currentSession.host_id === currentUserId;
        setIsHost(userIsHost);
        
        // Start media for host OR if it's camera/studio mode (everyone can see video)
        if (userIsHost || currentSession.session_type === 'camera' || currentSession.session_type === 'studio') {
          startMediaStream(currentSession.session_type);
        }
      } else {
        toast.error('Live session not found or has ended');
        navigate('/');
      }
    } catch (error) {
      console.error('Failed to fetch session:', error);
      toast.error('Failed to load live session');
    }
  };

  const joinSession = async () => {
    try {
      await joinLive(sessionId);
    } catch (error) {
      console.error('Failed to join session:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to join session';
      toast.error(errorMsg);
    }
  };

  const updateGuestsAndRequests = async () => {
    try {
      // Get participants (enhanced endpoint - may not exist yet)
      try {
        const response = await api.get(`/live/participants/${sessionId}`);
        const participants = response.data || [];
        setGuests(participants.filter(p => p.role !== 'viewer'));
      } catch (err) {
        // Enhanced endpoint not available, use mock data for now
        console.log('Enhanced participants endpoint not available yet');
      }
      
      // Get pending requests (host only)
      if (isHost) {
        try {
          const requestsResponse = await api.get(`/live/guest-requests/${sessionId}?status=pending`);
          setPendingRequests(requestsResponse.data || []);
        } catch (err) {
          // Enhanced endpoint not available
          console.log('Enhanced guest requests endpoint not available yet');
        }
      }
    } catch (error) {
      console.error('Failed to update guests:', error);
    }
  };

  const startMediaStream = async (sessionType) => {
    setIsLoadingMedia(true);
    try {
      const constraints = {
        audio: true,
        video: sessionType !== 'voice' ? {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        } : false
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      setStream(mediaStream);
      
      if (videoRef.current && sessionType !== 'voice') {
        videoRef.current.srcObject = mediaStream;
      }

      // Initialize WebRTC manager
      webrtcManagerRef.current = new WebRTCManager(
        mediaStream,
        (userId, remoteStream) => {
          console.log(`📹 Received remote stream from ${userId}`);
          setRemoteStreams(prev => ({
            ...prev,
            [userId]: remoteStream
          }));
          
          // Attach to video element
          setTimeout(() => {
            const videoEl = guestVideoRefs.current[userId];
            if (videoEl) {
              videoEl.srcObject = remoteStream;
            }
          }, 100);
        },
        (userId) => {
          console.log(`🔌 Remote stream removed from ${userId}`);
          setRemoteStreams(prev => {
            const updated = { ...prev };
            delete updated[userId];
            return updated;
          });
        }
      );

      // Set WebSocket send function for signaling
      webrtcManagerRef.current.sendSignal = sendWS;
      
      toast.success(sessionType === 'voice' ? 'Microphone ready' : 'Camera and microphone ready');
    } catch (error) {
      console.error('Failed to access media devices:', error);
      if (error.name === 'NotAllowedError') {
        toast.error('Camera/microphone access denied');
      } else if (error.name === 'NotFoundError') {
        toast.error('No camera or microphone found');
      } else {
        toast.error('Failed to access camera/microphone');
      }
    } finally {
      setIsLoadingMedia(false);
    }
  };

  const stopMediaStream = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    
    if (webrtcManagerRef.current) {
      webrtcManagerRef.current.cleanup();
      webrtcManagerRef.current = null;
    }
  };

  const toggleAudio = () => {
    const newState = !audioEnabled;
    setAudioEnabled(newState);
    
    if (webrtcManagerRef.current) {
      webrtcManagerRef.current.toggleAudio(newState);
    }
    
    // Notify others via WebSocket
    sendWS({
      action: 'update_media_status',
      audio_enabled: newState
    });
  };

  const toggleVideo = () => {
    const newState = !videoEnabled;
    setVideoEnabled(newState);
    
    if (webrtcManagerRef.current) {
      webrtcManagerRef.current.toggleVideo(newState);
    }
    
    // Notify others via WebSocket
    sendWS({
      action: 'update_media_status',
      video_enabled: newState
    });
  };

  const handleScreenShare = async () => {
    if (isScreenSharing) {
      // Stop screen sharing
      if (webrtcManagerRef.current) {
        await webrtcManagerRef.current.stopScreenShare();
      }
      setIsScreenSharing(false);
      toast.info('Screen sharing stopped');
    } else {
      // Start screen sharing
      if (webrtcManagerRef.current) {
        const screenStream = await webrtcManagerRef.current.startScreenShare();
        if (screenStream) {
          setIsScreenSharing(true);
          toast.success('Screen sharing started');
        } else {
          toast.error('Failed to start screen sharing');
        }
      }
    }
  };

  const handleRequestGuest = async () => {
    sendWS({
      action: 'request_guest'
    });
    toast.info('Guest request sent to host');
  };

  const handleApproveGuest = async (userId) => {
    sendWS({
      action: 'respond_guest',
      target_user_id: userId,
      approved: true
    });
    
    setPendingRequests(prev => prev.filter(r => r.user_id !== userId));
    toast.success('Guest approved');
  };

  const handleRejectGuest = async (userId) => {
    sendWS({
      action: 'respond_guest',
      target_user_id: userId,
      approved: false
    });
    
    setPendingRequests(prev => prev.filter(r => r.user_id !== userId));
    toast.info('Guest rejected');
  };

  const handleMuteGuest = async (userId, type) => {
    sendWS({
      action: 'participant_action',
      target_user_id: userId,
      action_type: type === 'audio' ? 'mute_audio' : 'mute_video'
    });
    
    toast.info(`Guest ${type} muted`);
  };

  const handleKickGuest = async (userId) => {
    sendWS({
      action: 'participant_action',
      target_user_id: userId,
      action_type: 'kick',
      reason: 'Removed by host'
    });
    
    toast.info('Guest removed');
  };

  const handlePromoteGuest = async (userId, newRole = 'cohost') => {
    sendWS({
      action: 'participant_action',
      target_user_id: userId,
      action_type: 'promote',
      new_role: newRole
    });
    
    toast.info(`Guest promoted to ${newRole}`);
  };

  const sendChatMessage = () => {
    if (!newMessage.trim()) return;
    
    const sent = sendWS({
      action: 'chat',
      message: newMessage.trim()
    });
    
    if (sent) {
      setNewMessage('');
    } else {
      toast.error('Not connected. Please wait...', { id: 'ws-not-connected' });
    }
  };

  const sendReaction = (reaction) => {
    sendWS({
      action: 'reaction',
      reaction
    });
  };

  const handleRequestGuest_OLD = async () => {
    try {
      await api.post('/live/request-guest', {
        session_id: sessionId,
        request_type: 'guest',
        message: 'Can I join the conversation?'
      });
      toast.success('Guest request sent! Waiting for host approval...');
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
      toast.info('Guest request feature coming soon!');
    }
  };

  // OLD FUNCTIONS - REMOVE THESE (now using WebSocket)
  /*
  const handleApproveGuest_OLD = async (requestId) => {
    try {
      await api.post('/live/respond-guest-request', {
        request_id: requestId,
        action: 'approved'
      });
      toast.success('Guest approved!');
      updateGuestsAndRequests();
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
      toast.info('Guest approval feature coming soon!');
    }
  };

  const handleRejectGuest = async (requestId) => {
    try {
      await api.post('/live/respond-guest-request', {
        request_id: requestId,
        action: 'rejected'
      });
      updateGuestsAndRequests();
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
    }
  };

  const handleMuteGuest = async (userId) => {
    try {
      await api.post('/live/manage-participant', {
        session_id: sessionId,
        user_id: userId,
        action: 'mute_audio'
      });
      toast.success('Guest muted');
      updateGuestsAndRequests();
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
      toast.info('Guest controls coming soon!');
    }
  };

  const handleKickGuest = async (userId) => {
    try {
      await api.post('/live/manage-participant', {
        session_id: sessionId,
        user_id: userId,
        action: 'kick'
      });
      toast.success('Guest removed');
      updateGuestsAndRequests();
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
      toast.info('Guest controls coming soon!');
    }
  };

  const handlePromoteToCohost_OLD = async (userId) => {
    try:
      await api.post('/live/manage-participant', {
        session_id: sessionId,
        user_id: userId,
        action: 'promote_cohost'
      });
      toast.success('Guest promoted to co-host!');
      updateGuestsAndRequests();
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
      toast.info('Promotion feature coming soon!');
    }
  };
  */
  // END OLD FUNCTIONS

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    // Use WebSocket for real-time chat
    sendChatMessage();
    
    /* OLD HTTP-based chat
    try {
      await api.post('/live/send-message', {
        session_id: sessionId,
        message: newMessage,
        message_type: 'text'
      });
      setNewMessage('');
      
      // Update chat
      const response = await api.get(`/live/messages/${sessionId}?limit=50`);
      setChatMessages(response.data || []);
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
      toast.info('Chat feature coming soon!');
    }
    */
  };

  const handleReaction_OLD = async (type) => {
    /* OLD HTTP-based reactions
    try {
      await api.post('/live/react', {
        session_id: sessionId,
        reaction_type: type
      });
      
      // Show floating animation
      showFloatingReaction(type);
    } catch (error) {
      console.error('Enhanced endpoint not available:', error);
      // Still show the animation even if backend fails
      showFloatingReaction(type);
    }
    */
  };

  const showFloatingReaction = (type) => {
    const emoji = {
      heart: '❤️',
      fire: '🔥',
      clap: '👏',
      wow: '😮',
      sad: '😢'
    }[type];
    
    // Create floating emoji element (you can enhance this with CSS animations)
    const element = document.createElement('div');
    element.textContent = emoji;
    element.className = 'floating-reaction';
    element.style.cssText = `
      position: fixed;
      bottom: 100px;
      right: ${Math.random() * 100}px;
      font-size: 48px;
      animation: float-up 3s ease-out forwards;
      pointer-events: none;
      z-index: 9999;
    `;
    document.body.appendChild(element);
    setTimeout(() => element.remove(), 3000);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setBackgroundImage(event.target.result);
        setHideCamera(true);
        toast.success('Background image set!');
      };
      reader.readAsDataURL(file);
    }
  };

  const handleEndLive = async () => {
    if (!isHost) return;

    try {
      stopMediaStream();
      await endLive(sessionId);
      toast.success('Live session ended');
      navigate('/');
    } catch (error) {
      toast.error('Failed to end session');
    }
  };

  const handleLeave = () => {
    stopMediaStream();
    navigate('/');
  };

  if (!session) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-pink-500"></div>
      </div>
    );
  }

  const sessionType = session.session_type;
  const maxGuests = sessionType === 'voice' ? 8 : sessionType === 'camera' ? 10 : 20;

  return (
    <div className="h-screen bg-black relative overflow-hidden">
      {/* Connection Status Indicator */}
      <div className="absolute top-4 left-4 z-50 flex items-center gap-2 bg-gray-900/90 px-3 py-2 rounded-lg">
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
        <span className="text-white text-sm font-medium">
          {isConnected ? 'Live' : 'Connecting...'}
        </span>
      </div>

      {/* Main Content Area */}
      <div className="h-full w-full relative">
        {sessionType === 'voice' ? (
          /* =============== VOICE ONLY MODE =============== */
          <div className="h-full flex flex-col items-center justify-center p-4">
            {/* Host Avatar */}
            <div className="mb-8">
              <div className="w-32 h-32 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full flex items-center justify-center relative">
                <span className="text-white text-4xl font-bold">
                  {session.username?.charAt(0).toUpperCase()}
                </span>
                {stream && audioEnabled && (
                  <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                    <FiMic className="text-white" size={20} />
                  </div>
                )}
              </div>
              <h2 className="text-white text-2xl font-bold mt-4 text-center">{session.title}</h2>
              <p className="text-gray-400 text-center">@{session.username}</p>
            </div>

            {/* Guests Grid (Voice Mode) */}
            <div className="grid grid-cols-4 gap-4 max-w-4xl">
              {guests.slice(0, maxGuests).map((guest) => (
                <div key={guest.user_id} className="text-center">
                  <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center relative mx-auto overflow-hidden">
                    {remoteStreams[guest.user_id] ? (
                      <video
                        ref={el => guestVideoRefs.current[guest.user_id] = el}
                        autoPlay
                        playsInline
                        muted
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-white text-xl font-bold">
                        {guest.username?.charAt(0).toUpperCase()}
                      </span>
                    )}
                    <div className={`absolute -bottom-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center ${
                      guest.audio_enabled ? 'bg-green-500' : 'bg-red-500'
                    }`}>
                      {guest.audio_enabled ? <FiMic size={12} /> : <FiMicOff size={12} />}
                    </div>
                    <div className="absolute -top-1 -right-1 px-2 py-0.5 bg-yellow-500 rounded-full text-xs text-black font-bold">
                      {guest.role}
                    </div>
                  </div>
                  <p className="text-white text-sm mt-2">{guest.username}</p>
                  
                  {isHost && (
                    <div className="flex justify-center gap-1 mt-1">
                      <button
                        onClick={() => handleMuteGuest(guest.user_id, 'audio')}
                        className="p-1 bg-gray-700 rounded hover:bg-gray-600"
                        title="Mute audio"
                      >
                        <FiMicOff size={12} />
                      </button>
                      <button
                        onClick={() => handlePromoteGuest(guest.user_id, 'cohost')}
                        className="p-1 bg-blue-700 rounded hover:bg-blue-600"
                        title="Promote"
                      >
                        ⭐
                      </button>
                      <button
                        onClick={() => handleKickGuest(guest.user_id)}
                        className="p-1 bg-red-700 rounded hover:bg-red-600"
                        title="Kick"
                      >
                        <FiUserMinus size={12} />
                      </button>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Empty slots */}
              {guests.length < maxGuests && (
                <div className="w-20 h-20 border-2 border-dashed border-gray-600 rounded-full flex items-center justify-center mx-auto">
                  <FiUserPlus className="text-gray-600" size={24} />
                </div>
              )}
            </div>

            <p className="text-gray-400 text-sm mt-8">
              🎙️ Voice Only Mode • {guests.length}/{maxGuests} Guests
            </p>
          </div>
        ) : sessionType === 'camera' ? (
          /* =============== CAMERA MODE =============== */
          <div className="h-full relative">
            {/* Main Video Display */}
            <div className="h-full w-full">
              {focusedGuestId ? (
                // Focused guest view
                <div className="h-full w-full bg-gray-900">
                  <video
                    ref={(el) => guestVideoRefs.current[focusedGuestId] = el}
                    autoPlay
                    playsInline
                    className="w-full h-full object-contain"
                  />
                  <button
                    onClick={() => setFocusedGuestId(null)}
                    className="absolute top-4 right-4 p-2 bg-black/50 rounded-full"
                  >
                    <FiMinimize2 className="text-white" size={24} />
                  </button>
                </div>
              ) : (
                // Host view
                <div className="h-full w-full">
                  {hideCamera && backgroundImage ? (
                    <div 
                      className="h-full w-full bg-cover bg-center"
                      style={{ backgroundImage: `url(${backgroundImage})` }}
                    >
                      <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                        <div className="text-center">
                          <h2 className="text-white text-3xl font-bold">{session.title}</h2>
                          <p className="text-gray-300 mt-2">@{session.username}</p>
                        </div>
                      </div>
                    </div>
                  ) : stream ? (
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="h-full flex items-center justify-center">
                      {isLoadingMedia ? (
                        <div className="text-center">
                          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-pink-500 mx-auto mb-4"></div>
                          <p className="text-white text-lg">Starting camera...</p>
                        </div>
                      ) : (
                        <div className="text-center">
                          <div className="w-32 h-32 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span className="text-white text-4xl font-bold">
                              {session.username?.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <h2 className="text-white text-2xl font-bold">{session.title}</h2>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Guest Grid Overlay (Bottom) */}
            {guests.length > 0 && !focusedGuestId && (
              <div className="absolute bottom-20 left-0 right-0 p-4">
                <div className="flex overflow-x-auto gap-2 pb-2">
                  {guests.slice(0, maxGuests).map((guest) => (
                    <div
                      key={guest.user_id}
                      className="flex-shrink-0 relative cursor-pointer group"
                      onClick={() => setFocusedGuestId(guest.user_id)}
                    >
                      <div className="w-32 h-32 bg-gray-800 rounded-lg overflow-hidden relative">
                        {/* Guest video placeholder */}
                        <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                          <span className="text-white text-2xl font-bold">
                            {guest.username?.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        
                        {/* Guest info overlay */}
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                          <p className="text-white text-xs font-semibold truncate">{guest.username}</p>
                          <div className="flex gap-1 mt-1">
                            {!guest.audio_enabled && <FiMicOff className="text-red-500" size={12} />}
                            {!guest.video_enabled && <FiVideoOff className="text-red-500" size={12} />}
                          </div>
                        </div>
                        
                        {/* Role badge */}
                        <div className="absolute top-1 right-1 px-1.5 py-0.5 bg-yellow-500 rounded text-xs text-black font-bold">
                          {guest.role}
                        </div>
                        
                        {/* Expand icon on hover */}
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                          <FiMaximize2 className="text-white" size={24} />
                        </div>
                      </div>
                      
                      {/* Host controls */}
                      {isHost && (
                        <div className="absolute -top-2 -right-2 flex gap-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleKickGuest(guest.user_id);
                            }}
                            className="p-1 bg-red-500 rounded-full hover:bg-red-600"
                            title="Kick"
                          >
                            <FiX size={12} />
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          /* =============== STUDIO MODE (TikTok Style) =============== */
          <div className="h-full relative">
            {/* Main stage - Multiple participants in grid */}
            <div className="h-full grid grid-cols-2 gap-1 p-1">
              {/* Host */}
              <div className="relative bg-gray-900 rounded-lg overflow-hidden">
                {hideCamera && backgroundImage ? (
                  <div 
                    className="h-full w-full bg-cover bg-center"
                    style={{ backgroundImage: `url(${backgroundImage})` }}
                  />
                ) : stream ? (
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="h-full flex items-center justify-center bg-gradient-to-br from-pink-900 to-purple-900">
                    <span className="text-white text-6xl font-bold">
                      {session.username?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                )}
                
                {/* Host label */}
                <div className="absolute top-2 left-2 px-3 py-1 bg-red-500 rounded-full">
                  <span className="text-white text-sm font-bold">HOST</span>
                </div>
                
                {/* Username */}
                <div className="absolute bottom-2 left-2 px-3 py-1 bg-black/70 rounded-full">
                  <span className="text-white text-sm font-semibold">@{session.username}</span>
                </div>
              </div>

              {/* Guests (up to 3 visible in main grid) */}
              {guests.slice(0, 3).map((guest, index) => (
                <div key={guest.user_id} className="relative bg-gray-900 rounded-lg overflow-hidden">
                  <div className="h-full flex items-center justify-center bg-gradient-to-br from-blue-900 to-purple-900">
                    <span className="text-white text-6xl font-bold">
                      {guest.username?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  
                  {/* Guest role badge */}
                  <div className="absolute top-2 left-2 px-3 py-1 bg-blue-500 rounded-full">
                    <span className="text-white text-sm font-bold uppercase">{guest.role}</span>
                  </div>
                  
                  {/* Username */}
                  <div className="absolute bottom-2 left-2 px-3 py-1 bg-black/70 rounded-full">
                    <span className="text-white text-sm font-semibold">@{guest.username}</span>
                  </div>
                  
                  {/* Status indicators */}
                  <div className="absolute top-2 right-2 flex gap-2">
                    {!guest.audio_enabled && (
                      <div className="p-1.5 bg-red-500 rounded-full">
                        <FiMicOff className="text-white" size={16} />
                      </div>
                    )}
                    {!guest.video_enabled && (
                      <div className="p-1.5 bg-red-500 rounded-full">
                        <FiVideoOff className="text-white" size={16} />
                      </div>
                    )}
                  </div>
                  
                  {/* Host controls menu */}
                  {isHost && (
                    <div className="absolute bottom-2 right-2">
                      <button className="p-2 bg-black/70 rounded-full hover:bg-black/90">
                        <FiMoreVertical className="text-white" size={16} />
                      </button>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Empty slots */}
              {Array.from({ length: Math.max(0, 4 - guests.length - 1) }).map((_, i) => (
                <div key={`empty-${i}`} className="relative bg-gray-900/50 rounded-lg border-2 border-dashed border-gray-700 flex items-center justify-center">
                  <FiUserPlus className="text-gray-600" size={48} />
                </div>
              ))}
            </div>

            {/* Additional guests carousel (if more than 3) */}
            {guests.length > 3 && (
              <div className="absolute bottom-20 left-0 right-0 p-4">
                <div className="flex overflow-x-auto gap-2">
                  {guests.slice(3).map((guest) => (
                    <div key={guest.user_id} className="flex-shrink-0 w-24 h-24 bg-gray-800 rounded-lg overflow-hidden relative">
                      <div className="h-full flex items-center justify-center bg-gradient-to-br from-blue-600 to-purple-600">
                        <span className="text-white text-xl font-bold">
                          {guest.username?.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="absolute bottom-0 left-0 right-0 bg-black/80 p-1">
                        <p className="text-white text-xs truncate">{guest.username}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Top Bar */}
      <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/80 to-transparent z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="px-4 py-2 bg-red-500 rounded-full flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span className="text-white font-semibold text-sm">LIVE</span>
            </div>
            <div className="px-4 py-2 bg-black/50 rounded-full flex items-center space-x-2">
              <FiUsers className="text-white" />
              <span className="text-white font-semibold">{viewerCount}</span>
            </div>
            {guests.length > 0 && (
              <div className="px-4 py-2 bg-purple-500/80 rounded-full flex items-center space-x-2">
                <FiUserPlus className="text-white" />
                <span className="text-white font-semibold">{guests.length}/{maxGuests}</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {isHost && pendingRequests.length > 0 && (
              <button
                onClick={() => setShowGuestRequests(!showGuestRequests)}
                className="relative px-4 py-2 bg-yellow-500 rounded-full hover:bg-yellow-600"
              >
                <span className="text-black font-bold">{pendingRequests.length} Requests</span>
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-bold">{pendingRequests.length}</span>
                </div>
              </button>
            )}
            
            <button
              onClick={isHost ? handleEndLive : handleLeave}
              className="p-2 bg-black/50 rounded-full hover:bg-black/70 transition"
            >
              <FiX className="text-white" size={24} />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            {/* Host/Guest Controls */}
            {(isHost || guests.some(g => g.user_id === localStorage.getItem('user_id'))) && (
              <div className="flex items-center space-x-4">
                <button
                  onClick={toggleAudio}
                  className={`p-4 rounded-full transition ${
                    audioEnabled ? 'bg-gray-800 hover:bg-gray-700' : 'bg-red-500 hover:bg-red-600'
                  }`}
                  disabled={!stream}
                >
                  {audioEnabled ? (
                    <FiMic className="text-white" size={24} />
                  ) : (
                    <FiMicOff className="text-white" size={24} />
                  )}
                </button>

                {sessionType !== 'voice' && (
                  <>
                    <button
                      onClick={toggleVideo}
                      className={`p-4 rounded-full transition ${
                        videoEnabled ? 'bg-gray-800 hover:bg-gray-700' : 'bg-red-500 hover:bg-red-600'
                      }`}
                      disabled={!stream}
                    >
                      {videoEnabled ? (
                        <FiVideo className="text-white" size={24} />
                      ) : (
                        <FiVideoOff className="text-white" size={24} />
                      )}
                    </button>

                    <button
                      onClick={handleScreenShare}
                      className={`p-4 rounded-full transition ${
                        isScreenSharing ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
                      }`}
                      disabled={!stream}
                      title={isScreenSharing ? 'Stop screen share' : 'Share screen'}
                    >
                      <FiMonitor className="text-white" size={24} />
                    </button>

                    {isHost && (
                      <>
                        <button
                          onClick={() => setHideCamera(!hideCamera)}
                          className={`p-4 rounded-full transition ${
                            hideCamera ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
                          }`}
                        >
                          <FiImage className="text-white" size={24} />
                        </button>

                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={handleImageUpload}
                        />
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          className="px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-full text-white font-semibold"
                        >
                          Upload BG
                        </button>
                      </>
                    )}
                  </>
                )}
              </div>
            )}

            {/* Viewer Actions */}
            {!isHost && !guests.some(g => g.user_id === localStorage.getItem('user_id')) && (
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleRequestGuest}
                  className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 rounded-full font-semibold text-white flex items-center gap-2"
                >
                  <FiUserPlus size={20} />
                  Request to Join
                </button>
                <GiftButton receiverId={session.host_id} />
              </div>
            )}

            {/* Chat & Reactions */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowChat(!showChat)}
                className="p-4 bg-gray-800 hover:bg-gray-700 rounded-full"
              >
                <FiMessageSquare className="text-white" size={24} />
              </button>

              {/* Quick Reactions */}
              <div className="flex gap-2">
                {[
                  { type: 'heart', emoji: '❤️' },
                  { type: 'fire', emoji: '🔥' },
                  { type: 'clap', emoji: '👏' },
                  { type: 'wow', emoji: '😮' }
                ].map(({ type, emoji }) => (
                  <button
                    key={type}
                    onClick={() => sendReaction(emoji)}
                    className="p-3 bg-gray-800 hover:bg-gray-700 rounded-full text-2xl transition transform hover:scale-110"
                    title={`Send ${type} reaction`}
                  >
                    {emoji}
                  </button>
                ))}
              </div>

              {/* End/Leave Button */}
              <button
                onClick={isHost ? handleEndLive : handleLeave}
                className={`px-6 py-3 rounded-full font-semibold transition ${
                  isHost
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-gray-800 hover:bg-gray-700 text-white'
                }`}
              >
                {isHost ? 'End Live' : 'Leave'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Guest Requests Panel */}
      {showGuestRequests && isHost && (
        <div className="absolute top-20 right-4 w-80 bg-gray-900 rounded-lg shadow-2xl p-4 z-20 max-h-96 overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-white font-bold text-lg">Guest Requests ({pendingRequests.length})</h3>
            <button onClick={() => setShowGuestRequests(false)}>
              <FiX className="text-white" size={20} />
            </button>
          </div>
          
          <div className="space-y-3">
            {pendingRequests.map((request) => (
              <div key={request.id} className="bg-gray-800 p-3 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="text-white font-semibold">{request.username}</p>
                    {request.message && (
                      <p className="text-gray-400 text-sm">{request.message}</p>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApproveGuest(request.id)}
                    className="flex-1 py-2 bg-green-500 hover:bg-green-600 rounded text-white font-semibold"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleRejectGuest(request.id)}
                    className="flex-1 py-2 bg-red-500 hover:bg-red-600 rounded text-white font-semibold"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chat Panel */}
      {showChat && (
        <div className="absolute bottom-20 right-4 w-80 h-96 bg-gray-900/95 rounded-lg shadow-2xl flex flex-col z-20">
          <div className="flex justify-between items-center p-4 border-b border-gray-700">
            <h3 className="text-white font-bold">Live Chat</h3>
            <button onClick={() => setShowChat(false)}>
              <FiX className="text-white" size={20} />
            </button>
          </div>
          
          <div className="chat-messages flex-1 overflow-y-auto p-4 space-y-2">
            {chatMessages.length === 0 ? (
              <p className="text-gray-500 text-center text-sm">No messages yet...</p>
            ) : (
              chatMessages.map((msg) => (
                <div key={msg.id} className="bg-gray-800 p-2 rounded animate-slide-in">
                  <p className="text-pink-400 font-semibold text-sm">{msg.username}</p>
                  <p className="text-gray-300 text-sm">{msg.message}</p>
                  <p className="text-gray-600 text-xs mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              ))
            )}
          </div>
          
          <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-700">
            <div className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 px-3 py-2 bg-gray-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-pink-500 hover:bg-pink-600 rounded-lg text-white font-semibold"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Floating Reactions Animation Styles */}
      <style jsx>{`
        @keyframes float-up {
          0% {
            transform: translateY(0) scale(1);
            opacity: 1;
          }
          100% {
            transform: translateY(-300px) scale(1.5);
            opacity: 0;
          }
        }
        .floating-reaction {
          animation: float-up 3s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default LiveRoomEnhanced;
