import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiX, FiUsers, FiMic, FiMicOff, FiVideo, FiVideoOff } from 'react-icons/fi';
import { getActiveSessions, joinLive, endLive } from '../api/liveApi';
import GiftButton from './GiftButton';
import toast from 'react-hot-toast';

const LiveRoom = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [isHost, setIsHost] = useState(false);
  const [viewerCount, setViewerCount] = useState(0);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [stream, setStream] = useState(null);
  const [isLoadingMedia, setIsLoadingMedia] = useState(false);
  
  const videoRef = useRef(null);

  useEffect(() => {
    fetchSessionDetails();
    joinSession();

    // Simulate viewer count updates
    const interval = setInterval(() => {
      setViewerCount(prev => Math.max(0, prev + Math.floor(Math.random() * 3) - 1));
    }, 5000);

    return () => {
      clearInterval(interval);
      stopMediaStream();
    };
  }, [sessionId]);

  const fetchSessionDetails = async () => {
    try {
      const sessions = await getActiveSessions();
      const currentSession = sessions.find(s => s.id === sessionId);
      if (currentSession) {
        setSession(currentSession);
        setViewerCount(currentSession.viewer_count);
        
        // Check if current user is host
        const currentUserId = localStorage.getItem('user_id');
        const userIsHost = currentSession.user_id === currentUserId;
        setIsHost(userIsHost);
        
        // Start media stream if host or camera/studio session
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
      
      // Attach stream to video element
      if (videoRef.current && sessionType !== 'voice') {
        videoRef.current.srcObject = mediaStream;
      }
      
      toast.success(sessionType === 'voice' ? 'Microphone ready' : 'Camera and microphone ready');
    } catch (error) {
      console.error('Failed to access media devices:', error);
      if (error.name === 'NotAllowedError') {
        toast.error('Camera/microphone access denied. Please allow access in your browser settings.');
      } else if (error.name === 'NotFoundError') {
        toast.error('No camera or microphone found.');
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
  };

  const toggleAudio = () => {
    if (stream) {
      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setAudioEnabled(audioTrack.enabled);
      }
    }
  };

  const toggleVideo = () => {
    if (stream) {
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setVideoEnabled(videoTrack.enabled);
      }
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

  return (
    <div className="h-screen bg-black relative">
      {/* Video Stream Area */}
      <div className="h-full w-full flex items-center justify-center">
        {session?.session_type === 'voice' ? (
          // Voice-only session - show avatar
          <div className="text-center">
            <div className="w-32 h-32 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4 relative">
              <span className="text-white text-4xl font-bold">
                {session.username?.charAt(0).toUpperCase()}
              </span>
              {stream && (
                <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <FiMic className="text-white" size={16} />
                </div>
              )}
            </div>
            <h2 className="text-white text-2xl font-bold mb-2">{session.title}</h2>
            <p className="text-gray-300">@{session.username}</p>
            <p className="text-gray-400 text-sm mt-4">🎙️ Audio Only Session</p>
          </div>
        ) : (
          // Camera/Studio session - show video
          <>
            {stream ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="text-center">
                {isLoadingMedia ? (
                  <>
                    <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-pink-500 mx-auto mb-4"></div>
                    <p className="text-white text-lg">Starting camera...</p>
                  </>
                ) : (
                  <>
                    <div className="w-32 h-32 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-white text-4xl font-bold">
                        {session.username?.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <h2 className="text-white text-2xl font-bold mb-2">{session.title}</h2>
                    <p className="text-gray-300">@{session.username}</p>
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Top Bar */}
      <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/80 to-transparent">
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
          </div>

          <button
            onClick={isHost ? handleEndLive : handleLeave}
            className="p-2 bg-black/50 rounded-full hover:bg-black/70 transition"
          >
            <FiX className="text-white" size={24} />
          </button>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            {/* Host Controls */}
            {isHost && (
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

                {session?.session_type !== 'voice' && (
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
                )}
              </div>
            )}

            {/* Viewer Actions */}
            {!isHost && (
              <div className="flex items-center space-x-4">
                <GiftButton receiverId={session.user_id} />
              </div>
            )}

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
  );
};

export default LiveRoom;
