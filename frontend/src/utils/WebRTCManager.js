/**
 * WebRTC Manager for Multi-User Video/Audio Streaming
 * Handles peer connections with mesh topology (all-to-all)
 * 
 * Features:
 * - Mesh topology (up to 20 participants)
 * - Audio/Video track management
 * - Automatic renegotiation
 * - Connection quality monitoring
 * - Screen sharing support
 */

class WebRTCManager {
  constructor(localStream, onRemoteStream, onRemoteStreamRemoved) {
    this.localStream = localStream;
    this.onRemoteStream = onRemoteStream; // Callback: (userId, stream) => void
    this.onRemoteStreamRemoved = onRemoteStreamRemoved; // Callback: (userId) => void
    
    // Peer connections: userId -> RTCPeerConnection
    this.peerConnections = new Map();
    
    // Remote streams: userId -> MediaStream
    this.remoteStreams = new Map();
    
    // ICE candidates queue (for candidates received before connection created)
    this.iceCandidatesQueue = new Map();
    
    // WebSocket send function (set externally)
    this.sendSignal = null;
    
    // STUN/TURN servers
    this.iceServers = [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' },
      { urls: 'stun:stun2.l.google.com:19302' },
      // Add TURN servers for production
      // {
      //   urls: 'turn:your-turn-server.com:3478',
      //   username: 'username',
      //   credential: 'password'
      // }
    ];
  }

  /**
   * Create peer connection for a remote user
   */
  createPeerConnection(userId) {
    if (this.peerConnections.has(userId)) {
      console.log(`Peer connection already exists for ${userId}`);
      return this.peerConnections.get(userId);
    }

    console.log(`📞 Creating peer connection for user ${userId}`);

    const pc = new RTCPeerConnection({
      iceServers: this.iceServers
    });

    // Add local tracks
    if (this.localStream) {
      this.localStream.getTracks().forEach(track => {
        pc.addTrack(track, this.localStream);
        console.log(`➕ Added local ${track.kind} track for ${userId}`);
      });
    }

    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        console.log(`🧊 ICE candidate for ${userId}`);
        this.sendSignal({
          action: 'webrtc_signal',
          to_user_id: userId,
          signal_type: 'ice_candidate',
          signal_data: {
            candidate: event.candidate.candidate,
            sdpMLineIndex: event.candidate.sdpMLineIndex,
            sdpMid: event.candidate.sdpMid
          }
        });
      }
    };

    // Handle connection state changes
    pc.onconnectionstatechange = () => {
      console.log(`🔗 Connection state for ${userId}:`, pc.connectionState);
      
      if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
        console.warn(`⚠️ Connection ${pc.connectionState} for ${userId}`);
        // Try to reconnect
        setTimeout(() => {
          if (pc.connectionState === 'failed') {
            this.removePeerConnection(userId);
          }
        }, 3000);
      }
    };

    // Handle ICE connection state
    pc.oniceconnectionstatechange = () => {
      console.log(`🧊 ICE state for ${userId}:`, pc.iceConnectionState);
    };

    // Handle remote tracks
    pc.ontrack = (event) => {
      console.log(`📺 Received ${event.track.kind} track from ${userId}`);
      
      const [stream] = event.streams;
      this.remoteStreams.set(userId, stream);
      
      if (this.onRemoteStream) {
        this.onRemoteStream(userId, stream);
      }
    };

    this.peerConnections.set(userId, pc);

    // Process queued ICE candidates
    if (this.iceCandidatesQueue.has(userId)) {
      const candidates = this.iceCandidatesQueue.get(userId);
      console.log(`Processing ${candidates.length} queued ICE candidates for ${userId}`);
      
      candidates.forEach(candidate => {
        pc.addIceCandidate(new RTCIceCandidate(candidate))
          .catch(err => console.error('Error adding ICE candidate:', err));
      });
      
      this.iceCandidatesQueue.delete(userId);
    }

    return pc;
  }

  /**
   * Create and send offer to remote user
   */
  async createOffer(userId) {
    try {
      const pc = this.createPeerConnection(userId);

      const offer = await pc.createOffer({
        offerToReceiveAudio: true,
        offerToReceiveVideo: true
      });

      await pc.setLocalDescription(offer);

      console.log(`📤 Sending offer to ${userId}`);
      
      this.sendSignal({
        action: 'webrtc_signal',
        to_user_id: userId,
        signal_type: 'offer',
        signal_data: {
          sdp: offer.sdp,
          type: offer.type
        }
      });

      return true;
    } catch (error) {
      console.error(`Failed to create offer for ${userId}:`, error);
      return false;
    }
  }

  /**
   * Handle incoming offer from remote user
   */
  async handleOffer(userId, offerData) {
    try {
      console.log(`📥 Received offer from ${userId}`);
      
      const pc = this.createPeerConnection(userId);

      await pc.setRemoteDescription(new RTCSessionDescription(offerData));

      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);

      console.log(`📤 Sending answer to ${userId}`);
      
      this.sendSignal({
        action: 'webrtc_signal',
        to_user_id: userId,
        signal_type: 'answer',
        signal_data: {
          sdp: answer.sdp,
          type: answer.type
        }
      });

      return true;
    } catch (error) {
      console.error(`Failed to handle offer from ${userId}:`, error);
      return false;
    }
  }

  /**
   * Handle incoming answer from remote user
   */
  async handleAnswer(userId, answerData) {
    try {
      console.log(`📥 Received answer from ${userId}`);
      
      const pc = this.peerConnections.get(userId);
      if (!pc) {
        console.error(`No peer connection found for ${userId}`);
        return false;
      }

      await pc.setRemoteDescription(new RTCSessionDescription(answerData));
      return true;
    } catch (error) {
      console.error(`Failed to handle answer from ${userId}:`, error);
      return false;
    }
  }

  /**
   * Handle incoming ICE candidate from remote user
   */
  async handleIceCandidate(userId, candidateData) {
    try {
      const pc = this.peerConnections.get(userId);
      
      if (!pc) {
        // Queue candidate for later
        if (!this.iceCandidatesQueue.has(userId)) {
          this.iceCandidatesQueue.set(userId, []);
        }
        this.iceCandidatesQueue.get(userId).push(candidateData);
        console.log(`🧊 Queued ICE candidate for ${userId} (no connection yet)`);
        return true;
      }

      await pc.addIceCandidate(new RTCIceCandidate(candidateData));
      console.log(`🧊 Added ICE candidate for ${userId}`);
      return true;
    } catch (error) {
      console.error(`Failed to handle ICE candidate from ${userId}:`, error);
      return false;
    }
  }

  /**
   * Remove peer connection for user who left
   */
  removePeerConnection(userId) {
    console.log(`🔌 Removing peer connection for ${userId}`);

    const pc = this.peerConnections.get(userId);
    if (pc) {
      pc.close();
      this.peerConnections.delete(userId);
    }

    const stream = this.remoteStreams.get(userId);
    if (stream) {
      // Stop all tracks
      stream.getTracks().forEach(track => track.stop());
      this.remoteStreams.delete(userId);
      
      if (this.onRemoteStreamRemoved) {
        this.onRemoteStreamRemoved(userId);
      }
    }

    // Clear queued candidates
    this.iceCandidatesQueue.delete(userId);
  }

  /**
   * Update local stream (when user changes audio/video)
   */
  updateLocalStream(newStream) {
    this.localStream = newStream;

    // Update all peer connections with new tracks
    this.peerConnections.forEach((pc, userId) => {
      // Remove old senders
      const senders = pc.getSenders();
      senders.forEach(sender => pc.removeTrack(sender));

      // Add new tracks
      if (newStream) {
        newStream.getTracks().forEach(track => {
          pc.addTrack(track, newStream);
        });
      }

      console.log(`🔄 Updated tracks for ${userId}`);
    });
  }

  /**
   * Toggle local audio
   */
  toggleAudio(enabled) {
    if (this.localStream) {
      this.localStream.getAudioTracks().forEach(track => {
        track.enabled = enabled;
      });
      console.log(`🎤 Audio ${enabled ? 'enabled' : 'disabled'}`);
    }
  }

  /**
   * Toggle local video
   */
  toggleVideo(enabled) {
    if (this.localStream) {
      this.localStream.getVideoTracks().forEach(track => {
        track.enabled = enabled;
      });
      console.log(`📹 Video ${enabled ? 'enabled' : 'disabled'}`);
    }
  }

  /**
   * Replace video track with screen share
   */
  async startScreenShare() {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          cursor: 'always'
        },
        audio: false
      });

      const screenTrack = screenStream.getVideoTracks()[0];

      // Replace video track in all peer connections
      this.peerConnections.forEach((pc, userId) => {
        const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
        if (sender) {
          sender.replaceTrack(screenTrack);
          console.log(`🖥️ Replaced video with screen share for ${userId}`);
        }
      });

      // Stop screen share when user clicks "stop sharing"
      screenTrack.onended = () => {
        this.stopScreenShare();
      };

      return screenStream;
    } catch (error) {
      console.error('Failed to start screen share:', error);
      return null;
    }
  }

  /**
   * Stop screen share and restore camera
   */
  async stopScreenShare() {
    if (this.localStream) {
      const videoTrack = this.localStream.getVideoTracks()[0];

      if (videoTrack) {
        // Replace screen share with camera in all peer connections
        this.peerConnections.forEach((pc, userId) => {
          const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
          if (sender) {
            sender.replaceTrack(videoTrack);
            console.log(`📹 Restored camera for ${userId}`);
          }
        });
      }
    }
  }

  /**
   * Get connection stats for monitoring
   */
  async getConnectionStats(userId) {
    const pc = this.peerConnections.get(userId);
    if (!pc) return null;

    const stats = await pc.getStats();
    const statsObj = {};

    stats.forEach(report => {
      if (report.type === 'inbound-rtp' && report.kind === 'video') {
        statsObj.bytesReceived = report.bytesReceived;
        statsObj.packetsLost = report.packetsLost;
        statsObj.jitter = report.jitter;
      }
    });

    return statsObj;
  }

  /**
   * Clean up all connections
   */
  cleanup() {
    console.log('🧹 Cleaning up WebRTC manager');

    this.peerConnections.forEach((pc, userId) => {
      pc.close();
    });

    this.remoteStreams.forEach((stream, userId) => {
      stream.getTracks().forEach(track => track.stop());
    });

    this.peerConnections.clear();
    this.remoteStreams.clear();
    this.iceCandidatesQueue.clear();
  }
}

export default WebRTCManager;
