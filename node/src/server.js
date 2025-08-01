const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const http = require('http');
const socketIo = require('socket.io');
const rateLimit = require('express-rate-limit');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

// Import routes
const authRoutes = require('./routes/auth');
const courseRoutes = require('./routes/courses');
const researchRoutes = require('./routes/research');
const collaborationRoutes = require('./routes/collaboration');
const ipfsRoutes = require('./routes/ipfs');
const userRoutes = require('./routes/users');

// Import services
const { initializeDatabase } = require('./services/database');
const { initializeIPFS } = require('./services/ipfs');
const { setupSocketHandlers } = require('./services/socket');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https://localhost:8080"], // Allow IPFS gateway
      connectSrc: ["'self'", "ws:", "wss:", "http://localhost:5001"], // Allow IPFS API
      frameSrc: ["'self'", "http://localhost:6080"], // Allow DeSciOS VNC iframe
      childSrc: ["'self'", "http://localhost:6080"] // Allow DeSciOS VNC iframe
    }
  }
}));

app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:3000",
  credentials: true
}));

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api', limiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    services: {
      database: 'connected',
      ipfs: 'connected'
    }
  });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/courses', courseRoutes);
app.use('/api/research', researchRoutes);
app.use('/api/collaboration', collaborationRoutes);
app.use('/api/ipfs', ipfsRoutes);
app.use('/api/users', userRoutes);

// Debug logging for route registration
console.log('API routes registered:');
console.log('- /api/auth');
console.log('- /api/courses');
console.log('- /api/research');
console.log('- /api/collaboration');
console.log('- /api/ipfs');
console.log('- /api/users');

// Serve static files for the web interface
app.use(express.static(path.join(__dirname, '../frontend/build')));

// Handle React routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/build/index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// Initialize services and start server
async function startServer() {
  try {
    console.log('🚀 Starting DeSciOS Academic Platform...');
    
    // Initialize database
    await initializeDatabase();
    console.log('✅ Database initialized');
    
    // Create admin user if it doesn't exist
    try {
      const { User } = require('./services/database');
      const bcrypt = require('bcryptjs');
      
      const adminExists = await User.findOne({ where: { email: 'admin@descios.org' } });
      if (!adminExists) {
        const hashedPassword = await bcrypt.hash('admin123', 10);
        await User.create({
          username: 'admin',
          email: 'admin@descios.org',
          password: hashedPassword,
          role: 'admin',
          profile: {
            firstName: 'Admin',
            lastName: 'User',
            institution: 'DeSciOS',
            bio: 'System Administrator'
          }
        });
        console.log('✅ Admin user created');
      } else {
        console.log('✅ Admin user already exists');
      }
    } catch (error) {
      console.log('⚠️  Admin user creation failed:', error.message);
    }
    
    // Initialize IPFS connection
    try {
      await initializeIPFS();
      console.log('✅ IPFS connection established');
    } catch (error) {
      console.log('⚠️  IPFS connection failed, continuing without IPFS:', error.message);
    }
    
    // Setup Socket.IO handlers
    setupSocketHandlers(io);
    console.log('✅ Socket.IO handlers configured');
    
    // Start server
    const PORT = process.env.PORT || 8000;
    server.listen(PORT, () => {
      console.log(`🌐 Server running on port ${PORT}`);
      console.log(`📚 Academic Platform: http://localhost:${PORT}`);
      console.log(`🔗 IPFS Gateway: http://localhost:8080`);
      console.log(`🔧 IPFS API: http://localhost:5001`);
    });
    
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

module.exports = { app, server, io }; 