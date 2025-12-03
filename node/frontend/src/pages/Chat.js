import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import ChatInterface from '../components/ChatInterface';
import './Chat.css';

const Chat = () => {
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [rooms, setRooms] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { user, api } = useAuth();

  useEffect(() => {
    if (user) {
      loadUserRooms();
    }
  }, [user]);

  const loadUserRooms = async () => {
    try {
      setIsLoading(true);
      
      // For demo purposes, create some sample rooms
      // In a real implementation, you'd fetch these from the backend
      const sampleRooms = [
        {
          id: 'course-123',
          name: 'Introduction to Computer Science',
          type: 'course',
          participants: ['instructor', 'student1', 'student2']
        },
        {
          id: 'dm-user-456',
          name: 'Direct Message with John Doe',
          type: 'direct',
          participants: [user.userId, 'user-456']
        },
        {
          id: 'course-789',
          name: 'Advanced Mathematics',
          type: 'course',
          participants: ['instructor', 'student3', 'student4', 'student5']
        }
      ];

      setRooms(sampleRooms);
      
      // Select the first room by default
      if (sampleRooms.length > 0) {
        setSelectedRoom(sampleRooms[0]);
      }
    } catch (error) {
      console.error('Error loading rooms:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewRoom = async (roomType) => {
    try {
      let roomId;
      
      if (roomType === 'course') {
        const courseId = prompt('Enter course ID:');
        if (!courseId) return;
        
        const response = await api.post('/api/messenger/course-chat', {
          courseId: courseId
        });
        
        roomId = response.data.roomId;
      } else if (roomType === 'direct') {
        const otherUserId = prompt('Enter user ID to message:');
        if (!otherUserId) return;
        
        const response = await api.post('/api/messenger/direct-chat', {
          otherUserId: otherUserId
        });
        
        roomId = response.data.roomId;
      }

      if (roomId) {
        const newRoom = {
          id: roomId,
          name: roomType === 'course' ? `Course ${roomId}` : `Direct Message`,
          type: roomType,
          participants: [user.userId]
        };
        
        setRooms(prev => [...prev, newRoom]);
        setSelectedRoom(newRoom);
      }
    } catch (error) {
      console.error('Error creating room:', error);
      alert('Failed to create chat room');
    }
  };

  const getRoomIcon = (type) => {
    if (type === 'course') {
      return '📚';
    } else if (type === 'direct') {
      return '💬';
    }
    return '🏠';
  };

  return (
    <div className="chat-page">
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h2>💬 IPFS Chat</h2>
          <p className="subtitle">Decentralized messaging powered by IPFS</p>
        </div>

        <div className="room-actions">
          <button 
            className="create-room-btn course"
            onClick={() => createNewRoom('course')}
          >
            📚 New Course Chat
          </button>
          <button 
            className="create-room-btn direct"
            onClick={() => createNewRoom('direct')}
          >
            💬 New Direct Message
          </button>
        </div>

        <div className="rooms-list">
          <h3>Chat Rooms</h3>
          {isLoading ? (
            <div className="loading-rooms">
              <div className="spinner"></div>
              <p>Loading rooms...</p>
            </div>
          ) : rooms.length === 0 ? (
            <div className="no-rooms">
              <p>No chat rooms yet</p>
              <p>Create a new room to start chatting!</p>
            </div>
          ) : (
            rooms.map(room => (
              <div
                key={room.id}
                className={`room-item ${selectedRoom?.id === room.id ? 'active' : ''}`}
                onClick={() => setSelectedRoom(room)}
              >
                <span className="room-icon">{getRoomIcon(room.type)}</span>
                <div className="room-info">
                  <span className="room-name">{room.name}</span>
                  <span className="room-type">{room.type}</span>
                </div>
                <span className="participant-count">
                  {room.participants.length}
                </span>
              </div>
            ))
          )}
        </div>

        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-avatar">👤</span>
            <span className="user-name">{user?.username || user?.email}</span>
          </div>
          <div className="connection-status">
            <span className="status-dot connected"></span>
            <span>Connected to IPFS</span>
          </div>
        </div>
      </div>

      <div className="chat-main">
        {selectedRoom ? (
          <ChatInterface
            roomId={selectedRoom.id}
            roomType={selectedRoom.type}
            participants={selectedRoom.participants}
          />
        ) : (
          <div className="no-room-selected">
            <div className="welcome-message">
              <h2>Welcome to IPFS Chat! 🚀</h2>
              <p>Select a chat room from the sidebar to start messaging</p>
              <div className="features">
                <div className="feature">
                  <span className="feature-icon">🔒</span>
                  <div>
                    <h4>Decentralized</h4>
                    <p>No central server, powered by IPFS</p>
                  </div>
                </div>
                <div className="feature">
                  <span className="feature-icon">⚡</span>
                  <div>
                    <h4>Real-time</h4>
                    <p>Instant messaging with PubSub</p>
                  </div>
                </div>
                <div className="feature">
                  <span className="feature-icon">🌐</span>
                  <div>
                    <h4>Peer-to-Peer</h4>
                    <p>Direct communication between users</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat; 