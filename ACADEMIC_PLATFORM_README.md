# DeSciOS Academic Platform Integration

This document explains how to build and run the DeSciOS container with the integrated Academic Platform for learning, teaching, and research collaboration.

## 🏗️ **Architecture Overview**

The Academic Platform is now fully integrated into DeSciOS as a native service that runs alongside other components:

- **Backend**: Node.js/Express server with Socket.io for real-time features
- **Frontend**: React application with Material-UI components  
- **Database**: SQLite for persistent storage
- **IPFS Integration**: Leverages existing DeSciOS IPFS daemon
- **Real-time**: WebSocket connections for live collaboration
- **Authentication**: JWT-based with role-based access control

## 📦 **What's Included**

### **Backend Services**
- REST API for courses, research, collaboration, and user management
- Socket.io for real-time features (messaging, document editing, user presence)
- IPFS integration for decentralized content storage
- JWT authentication with role-based permissions

### **Frontend Application**
- Modern React SPA with Material-UI design
- Dashboard with activity overview and quick actions
- Course management (create, enroll, teach)
- Research project collaboration
- Real-time collaboration workspaces
- IPFS file manager
- User management and profiles

### **Database**
- SQLite database with comprehensive academic models
- Pre-populated with sample data and default users
- Support for courses, research projects, collaborations, documents, and peer reviews

## 🔧 **Integration Details**

### **Services Added to DeSciOS**

1. **Academic Platform Service** (`supervisord.conf`):
   - Starts after IPFS daemon (10-second delay)
   - Runs on port 8000
   - Auto-restarts on failure

2. **Desktop Integration**:
   - Desktop shortcut to access platform via Firefox
   - Integrated with existing DeSciOS applications

3. **Network Ports**:
   - `8000`: Academic Platform web interface
   - `5001`: IPFS API (shared with existing IPFS)
   - `8080`: IPFS Gateway (shared with existing IPFS)

## 🚀 **Building and Running**

### **1. Build the Container**

```bash
# Clone the repository (if not already done)
git clone https://github.com/your-org/DeSciOS.git
cd DeSciOS

# Build the container with academic platform
docker build -t descios:academic .
```

### **2. Run the Container**

```bash
# Run with port mapping
docker run -d \
  --name descios \
  -p 6080:6080 \
  -p 8000:8000 \
  -p 5001:5001 \
  -p 8080:8080 \
  -p 4001:4001 \
  descios:academic
```

### **3. Access the Platform**

- **VNC Desktop**: http://localhost:6080
- **Academic Platform**: http://localhost:8000
- **IPFS Gateway**: http://localhost:8080
- **IPFS API**: http://localhost:5001

## 👥 **Default Users**

The platform comes with pre-configured users for testing:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Admin | admin@descios.org | admin123 | System administrator |
| Instructor | instructor@descios.org | instructor123 | Course instructor |
| Researcher | researcher@descios.org | researcher123 | Research project leader |
| Student | student@descios.org | student123 | Student user |

## 🎯 **Features**

### **For Students**
- Browse and enroll in courses
- Access course materials and assignments
- Participate in research projects
- Join collaboration workspaces
- Real-time messaging and document editing

### **For Instructors**
- Create and manage courses
- Upload course materials to IPFS
- Track student progress
- Facilitate online discussions
- Peer review management

### **For Researchers**
- Create research projects
- Collaborate with team members
- Share research data via IPFS
- Document research findings
- Peer review system

### **For Admins**
- User management and roles
- System monitoring
- Platform configuration
- Usage analytics

## 🗂️ **File Structure**

```
DeSciOS/
├── node/                          # Academic Platform
│   ├── src/
│   │   ├── routes/               # API routes
│   │   ├── services/             # Core services
│   │   ├── middleware/           # Express middleware
│   │   └── scripts/              # Utility scripts
│   ├── frontend/                 # React frontend
│   │   ├── src/
│   │   │   ├── components/       # UI components
│   │   │   ├── pages/           # Page components
│   │   │   ├── context/         # React contexts
│   │   │   └── hooks/           # Custom hooks
│   │   └── build/               # Built frontend files
│   └── package.json
├── Dockerfile                    # Updated with Node.js
├── supervisord.conf             # Updated with academic service
└── ACADEMIC_PLATFORM_README.md  # This file
```

## 🔧 **Configuration**

### **Environment Variables**

The platform uses these environment variables (set in `supervisord.conf`):

```bash
NODE_ENV=production
PORT=8000
IPFS_API_URL=http://localhost:5001
DATABASE_PATH=/home/deScier/.academic/database.sqlite
UPLOADS_PATH=/home/deScier/.academic/uploads
JWT_SECRET=descios-academic-platform-secret
```

### **Storage Locations**

- **Database**: `/home/deScier/.academic/database.sqlite`
- **Uploads**: `/home/deScier/.academic/uploads/`
- **Logs**: `/home/deScier/.academic/logs/`

## 🛠️ **Development**

### **Running in Development Mode**

To develop or test the platform:

```bash
# Enter the container
docker exec -it descios bash

# Navigate to the platform directory
cd /home/deScier/DeSciOS/node

# Install dependencies (if needed)
npm install

# Run in development mode
npm run dev
```

### **Frontend Development**

```bash
# Enter the container
docker exec -it descios bash

# Navigate to frontend directory
cd /home/deScier/DeSciOS/node/frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📊 **Database Management**

### **Reinitialize Database**

```bash
# Enter container
docker exec -it descios bash

# Navigate to platform directory
cd /home/deScier/DeSciOS/node

# Reinitialize database (WARNING: This will delete all data)
npm run init-db
```

### **Database Backup**

```bash
# Copy database from container
docker cp descios:/home/deScier/.academic/database.sqlite ./backup.sqlite
```

## 🔍 **Troubleshooting**

### **Platform Not Starting**

```bash
# Check service status
docker exec -it descios supervisorctl status

# Check logs
docker exec -it descios tail -f /home/deScier/.academic/logs/backend.log

# Restart the service
docker exec -it descios supervisorctl restart academic-platform
```

### **IPFS Connection Issues**

```bash
# Check IPFS daemon status
docker exec -it descios supervisorctl status ipfs

# Test IPFS API
docker exec -it descios curl http://localhost:5001/api/v0/version
```

### **Database Issues**

```bash
# Check database file
docker exec -it descios ls -la /home/deScier/.academic/

# Reinitialize if corrupted
docker exec -it descios bash -c "cd /home/deScier/DeSciOS/node && npm run init-db"
```

## 🚀 **Next Steps**

1. **Access the Platform**: Open http://localhost:8000 in your browser
2. **Login**: Use any of the default user accounts
3. **Explore**: Try creating courses, research projects, and collaborations
4. **Test IPFS**: Upload files and see them stored in IPFS
5. **Real-time Features**: Test messaging and live collaboration

## 📝 **Support**

For issues or questions:

1. Check the logs: `docker exec -it descios tail -f /home/deScier/.academic/logs/backend.log`
2. Verify services: `docker exec -it descios supervisorctl status`
3. Test IPFS: `docker exec -it descios curl http://localhost:5001/api/v0/version`

## 🎉 **Conclusion**

The Academic Platform is now fully integrated into DeSciOS, providing a complete solution for decentralized academic collaboration. The platform leverages IPFS for content storage, provides real-time collaboration features, and supports the full academic workflow from teaching to research.

Happy collaborating! 🎓🔬🚀 