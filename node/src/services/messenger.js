const { EventEmitter } = require('events');

class IPFSMessenger extends EventEmitter {
  constructor(ipfsService) {
    super();
    this.ipfs = ipfsService;
    this.subscriptions = new Map();
    this.peerId = null;
    this.isConnected = false;
  }

  async initialize() {
    try {
      console.log('🔧 Initializing IPFS Messenger...');
      console.log('🔧 IPFS service connected:', this.ipfs.isConnectedToIPFS());
      
      // Get the IPFS node instance
      const ipfsNode = await this.ipfs.getNode();
      console.log('🔧 IPFS node data:', JSON.stringify(ipfsNode, null, 2));
      
      this.peerId = ipfsNode.ID;
      this.isConnected = true;
      
      console.log('✅ IPFS Messenger initialized with peer ID:', this.peerId);
      return true;
    } catch (error) {
      console.error('❌ Failed to initialize IPFS Messenger:', error);
      return false;
    }
  }

  // Subscribe to a chat room
  async subscribeToRoom(roomId, userId) {
    try {
      console.log(`🔧 Attempting to subscribe to room: ${roomId} for user: ${userId}`);
      const topic = `academic-chat-${roomId}`;
      console.log(`🔧 Topic: ${topic}`);
      
      // Subscribe to the topic
      const result = await this.ipfs.subscribe(topic, (message) => {
        try {
          const data = JSON.parse(message.data.toString());
          
          // Only emit messages from other users
          if (data.senderId !== userId) {
            this.emit('message', {
              roomId,
              senderId: data.senderId,
              senderName: data.senderName,
              content: data.content,
              timestamp: data.timestamp,
              messageId: data.messageId
            });
          }
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      });

      console.log(`🔧 Subscribe result:`, result);
      this.subscriptions.set(roomId, topic);
      console.log(`✅ Subscribed to chat room: ${roomId}`);
      console.log(`🔧 Current subscriptions:`, Array.from(this.subscriptions.keys()));
      return true;
    } catch (error) {
      console.error(`❌ Failed to subscribe to room ${roomId}:`, error);
      return false;
    }
  }

  // Send a message to a chat room
  async sendMessage(roomId, userId, senderName, content) {
    try {
      const topic = `academic-chat-${roomId}`;
      const message = {
        senderId: userId,
        senderName: senderName,
        content: content,
        timestamp: new Date().toISOString(),
        messageId: `${userId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };

      await this.ipfs.publish(topic, JSON.stringify(message));
      
      // Emit the message locally as well
      this.emit('message', {
        roomId,
        ...message
      });

      console.log(`✅ Message sent to room ${roomId}`);
      return message;
    } catch (error) {
      console.error(`❌ Failed to send message to room ${roomId}:`, error);
      throw error;
    }
  }

  // Unsubscribe from a chat room
  async unsubscribeFromRoom(roomId) {
    try {
      const topic = this.subscriptions.get(roomId);
      if (topic) {
        await this.ipfs.unsubscribe(topic);
        this.subscriptions.delete(roomId);
        console.log(`✅ Unsubscribed from chat room: ${roomId}`);
      }
      return true;
    } catch (error) {
      console.error(`❌ Failed to unsubscribe from room ${roomId}:`, error);
      return false;
    }
  }

  // Get list of peers in a room
  async getRoomPeers(roomId) {
    try {
      const topic = `academic-chat-${roomId}`;
      const peers = await this.ipfs.getPeers(topic);
      return peers;
    } catch (error) {
      console.error(`❌ Failed to get peers for room ${roomId}:`, error);
      return [];
    }
  }

  // Create a course-specific chat room
  async createCourseChat(courseId, instructorId) {
    const roomId = `course-${courseId}`;
    await this.subscribeToRoom(roomId, instructorId);
    return roomId;
  }

  // Create a direct message room
  async createDirectChat(user1Id, user2Id) {
    const roomId = `dm-${[user1Id, user2Id].sort().join('-')}`;
    await this.subscribeToRoom(roomId, user1Id);
    return roomId;
  }

  // Get chat history (if using OrbitDB or similar)
  async getChatHistory(roomId, limit = 50) {
    // This would integrate with OrbitDB or IPFS storage
    // For now, return empty array
    return [];
  }

  // Disconnect from all rooms
  async disconnect() {
    try {
      for (const [roomId] of this.subscriptions) {
        await this.unsubscribeFromRoom(roomId);
      }
      this.isConnected = false;
      console.log('✅ Disconnected from all chat rooms');
    } catch (error) {
      console.error('❌ Error disconnecting from chat rooms:', error);
    }
  }
}

module.exports = IPFSMessenger; 