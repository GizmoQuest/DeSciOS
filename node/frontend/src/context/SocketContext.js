import React, { createContext, useContext, useEffect, useState } from 'react';
import io from 'socket.io-client';
import { useAuth } from './AuthContext';
import toast from 'react-hot-toast';

const SocketContext = createContext();

export function SocketProvider({ children }) {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const { user, token } = useAuth();

  useEffect(() => {
    if (user && token) {
      // Initialize socket connection
      const newSocket = io('http://localhost:8000', {
        auth: {
          token: token
        },
        transports: ['websocket']
      });

      // Connection event handlers
      newSocket.on('connect', () => {
        console.log('Connected to server');
        setConnected(true);
        setSocket(newSocket);
      });

      newSocket.on('disconnect', () => {
        console.log('Disconnected from server');
        setConnected(false);
      });

      newSocket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        setConnected(false);
      });

      // Authentication events
      newSocket.on('authenticated', (data) => {
        console.log('Socket authenticated:', data);
        toast.success('Connected to real-time services');
      });

      newSocket.on('authentication_error', (error) => {
        console.error('Authentication error:', error);
        toast.error('Real-time connection failed');
      });

      // User presence events
      newSocket.on('user_online', (userData) => {
        setOnlineUsers(prev => {
          const filtered = prev.filter(u => u.id !== userData.id);
          return [...filtered, userData];
        });
      });

      newSocket.on('user_offline', (userId) => {
        setOnlineUsers(prev => prev.filter(u => u.id !== userId));
      });

      newSocket.on('online_users', (users) => {
        setOnlineUsers(users);
      });

      // Notification events
      newSocket.on('notification', (notification) => {
        toast.success(notification.message);
      });

      // Collaboration events
      newSocket.on('collaboration_invite', (data) => {
        toast.success(`Invited to collaboration: ${data.collaboration.name}`);
      });

      newSocket.on('collaboration_update', (data) => {
        // Handle collaboration updates
        console.log('Collaboration updated:', data);
      });

      // Course events
      newSocket.on('course_enrollment', (data) => {
        toast.success(`Enrolled in course: ${data.course.title}`);
      });

      newSocket.on('course_update', (data) => {
        console.log('Course updated:', data);
      });

      // Research events
      newSocket.on('research_invite', (data) => {
        toast.success(`Invited to research project: ${data.project.title}`);
      });

      newSocket.on('research_update', (data) => {
        console.log('Research project updated:', data);
      });

      // Message events
      newSocket.on('new_message', (message) => {
        // Handle new messages in real-time
        console.log('New message:', message);
      });

      // Typing events
      newSocket.on('user_typing', (data) => {
        console.log('User typing:', data);
      });

      newSocket.on('user_stopped_typing', (data) => {
        console.log('User stopped typing:', data);
      });

      // Error handling
      newSocket.on('error', (error) => {
        console.error('Socket error:', error);
        toast.error('Connection error occurred');
      });

      return () => {
        newSocket.close();
      };
    } else {
      // Clean up socket when user logs out
      if (socket) {
        socket.close();
        setSocket(null);
        setConnected(false);
        setOnlineUsers([]);
      }
    }
  }, [user, token]);

  // Socket helper functions
  const joinRoom = (roomId) => {
    if (socket) {
      socket.emit('join_room', roomId);
    }
  };

  const leaveRoom = (roomId) => {
    if (socket) {
      socket.emit('leave_room', roomId);
    }
  };

  const sendMessage = (data) => {
    if (socket) {
      socket.emit('send_message', data);
    }
  };

  const startTyping = (roomId) => {
    if (socket) {
      socket.emit('start_typing', { roomId });
    }
  };

  const stopTyping = (roomId) => {
    if (socket) {
      socket.emit('stop_typing', { roomId });
    }
  };

  const updateUserPresence = (status) => {
    if (socket) {
      socket.emit('update_presence', { status });
    }
  };

  const subscribeToCollaboration = (collaborationId) => {
    if (socket) {
      socket.emit('subscribe_collaboration', { collaborationId });
    }
  };

  const unsubscribeFromCollaboration = (collaborationId) => {
    if (socket) {
      socket.emit('unsubscribe_collaboration', { collaborationId });
    }
  };

  const subscribeToResearch = (researchId) => {
    if (socket) {
      socket.emit('subscribe_research', { researchId });
    }
  };

  const unsubscribeFromResearch = (researchId) => {
    if (socket) {
      socket.emit('unsubscribe_research', { researchId });
    }
  };

  const subscribeToDocument = (documentId) => {
    if (socket) {
      socket.emit('subscribe_document', { documentId });
    }
  };

  const unsubscribeFromDocument = (documentId) => {
    if (socket) {
      socket.emit('unsubscribe_document', { documentId });
    }
  };

  const value = {
    socket,
    connected,
    onlineUsers,
    joinRoom,
    leaveRoom,
    sendMessage,
    startTyping,
    stopTyping,
    updateUserPresence,
    subscribeToCollaboration,
    unsubscribeFromCollaboration,
    subscribeToResearch,
    unsubscribeFromResearch,
    subscribeToDocument,
    unsubscribeFromDocument
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
}

export default SocketContext; 