const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');
const IPFSMessenger = require('../services/messenger');
const { ipfsService } = require('../services/ipfs');

// Initialize messenger service
console.log('🔧 Creating IPFS Messenger instance...');
const messenger = new IPFSMessenger(ipfsService);
console.log('🔧 IPFS Messenger instance created');

// Initialize messenger when IPFS is ready
let messengerInitialized = false;
const initializeMessenger = async () => {
  console.log('🔧 Attempting to initialize messenger...');
  console.log('🔧 Messenger initialized:', messengerInitialized);
  console.log('🔧 IPFS connected:', ipfsService.isConnectedToIPFS());
  
  if (!messengerInitialized && ipfsService.isConnectedToIPFS()) {
    try {
      await messenger.initialize();
      messengerInitialized = true;
      console.log('✅ IPFS Messenger initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize IPFS Messenger:', error);
    }
  } else {
    console.log('🔧 Messenger initialization skipped - already initialized or IPFS not ready');
  }
};

// Don't initialize immediately - wait for first request
console.log('🔧 Messenger routes loaded, waiting for IPFS to be ready...');

// Get messenger status
router.get('/status', authenticateToken, async (req, res) => {
  console.log('🔧 Messenger status endpoint called');
  try {
    // Try to initialize messenger if not already initialized
    if (!messengerInitialized && ipfsService.isConnectedToIPFS()) {
      console.log('🔧 Initializing messenger from status endpoint...');
      await initializeMessenger();
    }
    
    console.log('🔧 Returning messenger status:', {
      connected: messenger.isConnected,
      peerId: messenger.peerId,
      subscriptions: Array.from(messenger.subscriptions.keys())
    });
    
    res.json({
      connected: messenger.isConnected,
      peerId: messenger.peerId,
      subscriptions: Array.from(messenger.subscriptions.keys())
    });
  } catch (error) {
    console.error('Error getting messenger status:', error);
    res.status(500).json({ error: 'Failed to get messenger status' });
  }
});

// Subscribe to a chat room
router.post('/subscribe', authenticateToken, async (req, res) => {
  try {
    const { roomId } = req.body;
    const userId = req.user.userId;

    if (!roomId) {
      return res.status(400).json({ error: 'Room ID is required' });
    }

    const success = await messenger.subscribeToRoom(roomId, userId);
    
    if (success) {
      res.json({ 
        message: 'Subscribed to chat room',
        roomId,
        peerId: messenger.peerId
      });
    } else {
      res.status(500).json({ error: 'Failed to subscribe to chat room' });
    }
  } catch (error) {
    console.error('Error subscribing to chat room:', error);
    res.status(500).json({ error: 'Failed to subscribe to chat room' });
  }
});

// Send a message
router.post('/send', authenticateToken, async (req, res) => {
  try {
    const { roomId, content } = req.body;
    const userId = req.user.userId;
    const senderName = req.user.username || req.user.email;

    if (!roomId || !content) {
      return res.status(400).json({ error: 'Room ID and content are required' });
    }

    const message = await messenger.sendMessage(roomId, userId, senderName, content);
    
    res.json({
      message: 'Message sent successfully',
      data: message
    });
  } catch (error) {
    console.error('Error sending message:', error);
    res.status(500).json({ error: 'Failed to send message' });
  }
});

// Unsubscribe from a chat room
router.post('/unsubscribe', authenticateToken, async (req, res) => {
  try {
    const { roomId } = req.body;
    const userId = req.user.userId;

    if (!roomId) {
      return res.status(400).json({ error: 'Room ID is required' });
    }

    const success = await messenger.unsubscribeFromRoom(roomId);
    
    if (success) {
      res.json({ message: 'Unsubscribed from chat room', roomId });
    } else {
      res.status(500).json({ error: 'Failed to unsubscribe from chat room' });
    }
  } catch (error) {
    console.error('Error unsubscribing from chat room:', error);
    res.status(500).json({ error: 'Failed to unsubscribe from chat room' });
  }
});

// Get peers in a room
router.get('/peers/:roomId', authenticateToken, async (req, res) => {
  try {
    const { roomId } = req.params;
    const peers = await messenger.getRoomPeers(roomId);
    
    res.json({ peers });
  } catch (error) {
    console.error('Error getting room peers:', error);
    res.status(500).json({ error: 'Failed to get room peers' });
  }
});

// Create course chat room
router.post('/course-chat', authenticateToken, async (req, res) => {
  try {
    const { courseId } = req.body;
    const instructorId = req.user.userId;

    if (!courseId) {
      return res.status(400).json({ error: 'Course ID is required' });
    }

    const roomId = await messenger.createCourseChat(courseId, instructorId);
    
    res.json({
      message: 'Course chat room created',
      roomId,
      courseId
    });
  } catch (error) {
    console.error('Error creating course chat room:', error);
    res.status(500).json({ error: 'Failed to create course chat room' });
  }
});

// Create direct message room
router.post('/direct-chat', authenticateToken, async (req, res) => {
  try {
    const { otherUserId } = req.body;
    const currentUserId = req.user.userId;

    if (!otherUserId) {
      return res.status(400).json({ error: 'Other user ID is required' });
    }

    const roomId = await messenger.createDirectChat(currentUserId, otherUserId);
    
    res.json({
      message: 'Direct chat room created',
      roomId,
      participants: [currentUserId, otherUserId]
    });
  } catch (error) {
    console.error('Error creating direct chat room:', error);
    res.status(500).json({ error: 'Failed to create direct chat room' });
  }
});

// Get chat history (placeholder for future implementation)
router.get('/history/:roomId', authenticateToken, async (req, res) => {
  try {
    const { roomId } = req.params;
    const { limit = 50 } = req.query;
    
    const history = await messenger.getChatHistory(roomId, parseInt(limit));
    
    res.json({ history });
  } catch (error) {
    console.error('Error getting chat history:', error);
    res.status(500).json({ error: 'Failed to get chat history' });
  }
});

// WebSocket endpoint for real-time messaging
// Note: This requires additional WebSocket setup in the main server
// For now, we'll use HTTP polling for real-time updates
// TODO: Implement proper WebSocket support

module.exports = router; 