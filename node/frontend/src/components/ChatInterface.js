import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import './ChatInterface.css';

const ChatInterface = ({ roomId, roomType = 'course', participants = [] }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [peers, setPeers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, api } = useAuth();

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat room
  useEffect(() => {
    if (roomId && user) {
      initializeChat();
    }
  }, [roomId, user]);

  const initializeChat = async () => {
    try {
      setIsLoading(true);
      
      // Subscribe to the chat room
      const response = await api.post('/api/messenger/subscribe', {
        roomId: roomId
      });

      if (response.data) {
        setIsConnected(true);
        console.log('✅ Subscribed to chat room:', roomId);
        
        // Get peers in the room
        await getRoomPeers();
      }
    } catch (error) {
      console.error('❌ Failed to initialize chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRoomPeers = async () => {
    try {
      const response = await api.get(`/api/messenger/peers/${roomId}`);
      setPeers(response.data.peers || []);
    } catch (error) {
      console.error('❌ Failed to get room peers:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !isConnected) return;

    try {
      const response = await api.post('/api/messenger/send', {
        roomId: roomId,
        content: newMessage.trim()
      });

      if (response.data) {
        // Add message to local state
        const message = response.data.data;
        setMessages(prev => [...prev, message]);
        setNewMessage('');
      }
    } catch (error) {
      console.error('❌ Failed to send message:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getRoomTitle = () => {
    if (roomType === 'course') {
      return `Course Chat - ${roomId}`;
    } else if (roomType === 'direct') {
      return `Direct Message`;
    }
    return `Chat Room - ${roomId}`;
  };

  return (
    <div className="chat-interface">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-title">
          <h3>{getRoomTitle()}</h3>
          <div className="connection-status">
            <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '●' : '○'}
            </span>
            <span className="status-text">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        <div className="chat-info">
          <span className="peer-count">
            {peers.length} peer{peers.length !== 1 ? 's' : ''} online
          </span>
        </div>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        {isLoading ? (
          <div className="loading-messages">
            <div className="spinner"></div>
            <p>Connecting to chat room...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="empty-messages">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message, index) => (
              <div
                key={message.messageId || index}
                className={`message ${message.senderId === user?.userId ? 'own-message' : 'other-message'}`}
              >
                <div className="message-header">
                  <span className="sender-name">
                    {message.senderId === user?.userId ? 'You' : message.senderName}
                  </span>
                  <span className="message-time">
                    {formatTimestamp(message.timestamp)}
                  </span>
                </div>
                <div className="message-content">
                  {message.content}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Message Input */}
      <form className="message-input-form" onSubmit={sendMessage}>
        <div className="input-container">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={isConnected ? "Type your message..." : "Connecting..."}
            disabled={!isConnected}
            className="message-input"
          />
          <button
            type="submit"
            disabled={!isConnected || !newMessage.trim()}
            className="send-button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22,2 15,22 11,13 2,9"></polygon>
            </svg>
          </button>
        </div>
      </form>

      {/* IPFS Info */}
      <div className="ipfs-info">
        <small>
          Powered by IPFS PubSub • Decentralized messaging
        </small>
      </div>
    </div>
  );
};

export default ChatInterface; 