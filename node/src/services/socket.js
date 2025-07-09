const jwt = require('jsonwebtoken');
const { User, Message, Collaboration, CollaborationMember } = require('./database');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

class SocketService {
  constructor(io) {
    this.io = io;
    this.connectedUsers = new Map();
    this.collaborationRooms = new Map();
  }

  // Initialize Socket.IO handlers
  initialize() {
    this.io.use(this.authenticateSocket.bind(this));
    this.io.on('connection', this.handleConnection.bind(this));
    console.log('✅ Socket.IO service initialized');
  }

  // Authenticate socket connection
  async authenticateSocket(socket, next) {
    try {
      const token = socket.handshake.auth.token;
      
      if (!token) {
        return next(new Error('Authentication token required'));
      }

      const decoded = jwt.verify(token, JWT_SECRET);
      const user = await User.findByPk(decoded.userId);
      
      if (!user || !user.isActive) {
        return next(new Error('User not found or inactive'));
      }

      socket.user = {
        id: user.id,
        username: user.username,
        role: user.role,
        profile: user.profile
      };

      next();
    } catch (error) {
      console.error('Socket authentication error:', error);
      next(new Error('Authentication failed'));
    }
  }

  // Handle new socket connection
  handleConnection(socket) {
    console.log(`🔌 User connected: ${socket.user.username} (${socket.id})`);
    
    // Add user to connected users map
    this.connectedUsers.set(socket.user.id, {
      socketId: socket.id,
      user: socket.user,
      connectedAt: new Date()
    });

    // Send welcome message
    socket.emit('connected', {
      message: 'Connected to DeSciOS Academic Platform',
      user: socket.user
    });

    // Set up event handlers
    this.setupEventHandlers(socket);

    // Handle disconnection
    socket.on('disconnect', () => {
      this.handleDisconnection(socket);
    });
  }

  // Set up event handlers for socket
  setupEventHandlers(socket) {
    // Collaboration events
    socket.on('join-collaboration', this.handleJoinCollaboration.bind(this, socket));
    socket.on('leave-collaboration', this.handleLeaveCollaboration.bind(this, socket));
    socket.on('collaboration-message', this.handleCollaborationMessage.bind(this, socket));
    socket.on('collaboration-typing', this.handleCollaborationTyping.bind(this, socket));
    
    // Document editing events
    socket.on('document-edit', this.handleDocumentEdit.bind(this, socket));
    socket.on('document-save', this.handleDocumentSave.bind(this, socket));
    socket.on('document-lock', this.handleDocumentLock.bind(this, socket));
    socket.on('document-unlock', this.handleDocumentUnlock.bind(this, socket));
    
    // Real-time updates
    socket.on('course-update', this.handleCourseUpdate.bind(this, socket));
    socket.on('research-update', this.handleResearchUpdate.bind(this, socket));
    
    // User presence
    socket.on('user-status', this.handleUserStatus.bind(this, socket));
    socket.on('get-online-users', this.handleGetOnlineUsers.bind(this, socket));
  }

  // Handle user joining collaboration
  async handleJoinCollaboration(socket, data) {
    try {
      const { collaborationId } = data;
      
      // Check if user has access to collaboration
      const membership = await CollaborationMember.findOne({
        where: {
          UserId: socket.user.id,
          CollaborationId: collaborationId
        }
      });

      if (!membership) {
        socket.emit('error', { message: 'Access denied to collaboration' });
        return;
      }

      // Join collaboration room
      socket.join(`collaboration-${collaborationId}`);
      
      // Add to collaboration rooms map
      if (!this.collaborationRooms.has(collaborationId)) {
        this.collaborationRooms.set(collaborationId, new Set());
      }
      this.collaborationRooms.get(collaborationId).add(socket.user.id);

      // Notify others in the collaboration
      socket.to(`collaboration-${collaborationId}`).emit('user-joined', {
        user: socket.user,
        timestamp: new Date()
      });

      // Send success confirmation
      socket.emit('collaboration-joined', {
        collaborationId,
        message: 'Joined collaboration successfully'
      });

      console.log(`📚 User ${socket.user.username} joined collaboration ${collaborationId}`);
    } catch (error) {
      console.error('Error joining collaboration:', error);
      socket.emit('error', { message: 'Failed to join collaboration' });
    }
  }

  // Handle user leaving collaboration
  async handleLeaveCollaboration(socket, data) {
    try {
      const { collaborationId } = data;
      
      // Leave collaboration room
      socket.leave(`collaboration-${collaborationId}`);
      
      // Remove from collaboration rooms map
      if (this.collaborationRooms.has(collaborationId)) {
        this.collaborationRooms.get(collaborationId).delete(socket.user.id);
        if (this.collaborationRooms.get(collaborationId).size === 0) {
          this.collaborationRooms.delete(collaborationId);
        }
      }

      // Notify others in the collaboration
      socket.to(`collaboration-${collaborationId}`).emit('user-left', {
        user: socket.user,
        timestamp: new Date()
      });

      console.log(`📚 User ${socket.user.username} left collaboration ${collaborationId}`);
    } catch (error) {
      console.error('Error leaving collaboration:', error);
    }
  }

  // Handle collaboration message
  async handleCollaborationMessage(socket, data) {
    try {
      const { collaborationId, content, type = 'text', parentId } = data;
      
      // Verify user has access to collaboration
      const membership = await CollaborationMember.findOne({
        where: {
          UserId: socket.user.id,
          CollaborationId: collaborationId
        }
      });

      if (!membership) {
        socket.emit('error', { message: 'Access denied to collaboration' });
        return;
      }

      // Create message in database
      const message = await Message.create({
        content,
        type,
        parentId: parentId || null,
        senderId: socket.user.id,
        metadata: {
          collaboration: collaborationId
        }
      });

      // Get message with sender info
      const messageWithSender = await Message.findByPk(message.id, {
        include: [{
          model: User,
          as: 'sender',
          attributes: ['id', 'username', 'profile']
        }]
      });

      // Broadcast to collaboration room
      this.io.to(`collaboration-${collaborationId}`).emit('collaboration-message', {
        message: messageWithSender,
        timestamp: new Date()
      });

      console.log(`💬 Message sent in collaboration ${collaborationId} by ${socket.user.username}`);
    } catch (error) {
      console.error('Error sending collaboration message:', error);
      socket.emit('error', { message: 'Failed to send message' });
    }
  }

  // Handle collaboration typing indicator
  async handleCollaborationTyping(socket, data) {
    try {
      const { collaborationId, isTyping } = data;
      
      // Broadcast typing status to collaboration room (except sender)
      socket.to(`collaboration-${collaborationId}`).emit('collaboration-typing', {
        user: socket.user,
        isTyping,
        timestamp: new Date()
      });
    } catch (error) {
      console.error('Error handling typing indicator:', error);
    }
  }

  // Handle document edit
  async handleDocumentEdit(socket, data) {
    try {
      const { documentId, changes, collaborationId } = data;
      
      // Broadcast document changes to collaboration room
      socket.to(`collaboration-${collaborationId}`).emit('document-edit', {
        documentId,
        changes,
        user: socket.user,
        timestamp: new Date()
      });

      console.log(`📝 Document ${documentId} edited by ${socket.user.username}`);
    } catch (error) {
      console.error('Error handling document edit:', error);
    }
  }

  // Handle document save
  async handleDocumentSave(socket, data) {
    try {
      const { documentId, content, collaborationId } = data;
      
      // Broadcast document save to collaboration room
      socket.to(`collaboration-${collaborationId}`).emit('document-saved', {
        documentId,
        user: socket.user,
        timestamp: new Date()
      });

      console.log(`💾 Document ${documentId} saved by ${socket.user.username}`);
    } catch (error) {
      console.error('Error handling document save:', error);
    }
  }

  // Handle document lock
  async handleDocumentLock(socket, data) {
    try {
      const { documentId, collaborationId } = data;
      
      // Broadcast document lock to collaboration room
      socket.to(`collaboration-${collaborationId}`).emit('document-locked', {
        documentId,
        user: socket.user,
        timestamp: new Date()
      });

      console.log(`🔒 Document ${documentId} locked by ${socket.user.username}`);
    } catch (error) {
      console.error('Error handling document lock:', error);
    }
  }

  // Handle document unlock
  async handleDocumentUnlock(socket, data) {
    try {
      const { documentId, collaborationId } = data;
      
      // Broadcast document unlock to collaboration room
      socket.to(`collaboration-${collaborationId}`).emit('document-unlocked', {
        documentId,
        user: socket.user,
        timestamp: new Date()
      });

      console.log(`🔓 Document ${documentId} unlocked by ${socket.user.username}`);
    } catch (error) {
      console.error('Error handling document unlock:', error);
    }
  }

  // Handle course update
  async handleCourseUpdate(socket, data) {
    try {
      const { courseId, update } = data;
      
      // Broadcast course update to interested users
      socket.broadcast.emit('course-updated', {
        courseId,
        update,
        user: socket.user,
        timestamp: new Date()
      });

      console.log(`📚 Course ${courseId} updated by ${socket.user.username}`);
    } catch (error) {
      console.error('Error handling course update:', error);
    }
  }

  // Handle research update
  async handleResearchUpdate(socket, data) {
    try {
      const { projectId, update } = data;
      
      // Broadcast research update to interested users
      socket.broadcast.emit('research-updated', {
        projectId,
        update,
        user: socket.user,
        timestamp: new Date()
      });

      console.log(`🔬 Research project ${projectId} updated by ${socket.user.username}`);
    } catch (error) {
      console.error('Error handling research update:', error);
    }
  }

  // Handle user status update
  async handleUserStatus(socket, data) {
    try {
      const { status } = data;
      
      // Update user status in connected users map
      if (this.connectedUsers.has(socket.user.id)) {
        this.connectedUsers.get(socket.user.id).status = status;
      }

      // Broadcast status update
      socket.broadcast.emit('user-status-updated', {
        user: socket.user,
        status,
        timestamp: new Date()
      });
    } catch (error) {
      console.error('Error handling user status:', error);
    }
  }

  // Handle get online users
  async handleGetOnlineUsers(socket) {
    try {
      const onlineUsers = Array.from(this.connectedUsers.values()).map(conn => ({
        user: conn.user,
        connectedAt: conn.connectedAt,
        status: conn.status || 'online'
      }));

      socket.emit('online-users', { users: onlineUsers });
    } catch (error) {
      console.error('Error getting online users:', error);
    }
  }

  // Handle user disconnection
  handleDisconnection(socket) {
    console.log(`🔌 User disconnected: ${socket.user.username} (${socket.id})`);
    
    // Remove user from connected users map
    this.connectedUsers.delete(socket.user.id);
    
    // Remove from all collaboration rooms
    this.collaborationRooms.forEach((users, collaborationId) => {
      if (users.has(socket.user.id)) {
        users.delete(socket.user.id);
        
        // Notify others in the collaboration
        socket.to(`collaboration-${collaborationId}`).emit('user-left', {
          user: socket.user,
          timestamp: new Date()
        });
        
        // Clean up empty collaboration rooms
        if (users.size === 0) {
          this.collaborationRooms.delete(collaborationId);
        }
      }
    });

    // Broadcast user offline status
    socket.broadcast.emit('user-offline', {
      user: socket.user,
      timestamp: new Date()
    });
  }

  // Get collaboration room members
  getCollaborationMembers(collaborationId) {
    const members = this.collaborationRooms.get(collaborationId);
    if (!members) return [];
    
    return Array.from(members).map(userId => 
      this.connectedUsers.get(userId)
    ).filter(Boolean);
  }

  // Send notification to user
  sendNotificationToUser(userId, notification) {
    const userConnection = this.connectedUsers.get(userId);
    if (userConnection) {
      this.io.to(userConnection.socketId).emit('notification', notification);
    }
  }

  // Send notification to collaboration
  sendNotificationToCollaboration(collaborationId, notification) {
    this.io.to(`collaboration-${collaborationId}`).emit('notification', notification);
  }
}

// Setup Socket.IO handlers
function setupSocketHandlers(io) {
  const socketService = new SocketService(io);
  socketService.initialize();
  return socketService;
}

module.exports = {
  SocketService,
  setupSocketHandlers
}; 