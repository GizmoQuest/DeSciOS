# DeSciOS Academic Platform - Deployment Guide

## Overview
This guide documents all the fixes and updates made to the DeSciOS Academic Platform to ensure they persist when deploying via Docker containers.

## 🎯 Key Fixes Implemented

### 1. **Database Initialization & Authentication**
- **Issue**: Database schema mismatches and missing admin user
- **Fix**: 
  - Fixed User model schema (`username` vs `name` field)
  - Created `ensure-admin.js` for reliable admin user creation
  - Updated `init-db.js` with intelligent database initialization
  - Fixed authentication to use email-based login

### 2. **Dashboard API Integration**
- **Issue**: "Failed to load dashboard data" error
- **Fix**:
  - Updated API endpoints to use correct user ID paths
  - Fixed frontend authentication using `api` instance from AuthContext
  - Simplified backend API endpoints to avoid complex database joins
  - Added proper error handling and data extraction

### 3. **Notification System**
- **Issue**: Static notification bell with no functionality
- **Fix**:
  - Implemented dynamic notification state management
  - Added clickable notification dropdown with read/unread tracking
  - Implemented localStorage persistence for notification state
  - Added visual feedback for read vs unread notifications

## 📁 Critical Files Updated

### Backend Files
```
node/src/routes/users.js          # Fixed API endpoints for dashboard
node/src/scripts/init-db.js       # Fixed database schema and initialization
node/src/services/ipfs.js         # Replaced ipfs-http-client with axios
node/src/server.js                # Added graceful IPFS error handling
```

### Frontend Files
```
node/frontend/src/pages/Dashboard.js      # Fixed API calls and authentication
node/frontend/src/components/Layout.js    # Added notification system
node/frontend/src/context/AuthContext.js  # API interceptors for authentication
```

### Infrastructure Files
```
node/start-academic.sh            # Startup script with database initialization
node/ensure-admin.js              # Admin user creation script
Dockerfile                        # Build process and permissions
supervisord.conf                  # Service management
```

## 🐳 Docker Deployment Process

### Build Process
The Dockerfile automatically:
1. **Copies** the entire `node` directory to `/home/deScier/DeSciOS/node`
2. **Installs** Node.js dependencies for both backend and frontend
3. **Builds** the React frontend with all our fixes
4. **Sets up** startup scripts and permissions
5. **Creates** necessary directories and desktop shortcuts

### Startup Process
1. **Container starts** → `startup.sh` runs
2. **Supervisord starts** → manages all services
3. **Academic platform starts** → `start-academic.sh` runs
4. **Database check** → `ensure-admin.js` creates admin user if needed
5. **Server starts** → on port 8000 with all fixes

## 🔧 Configuration Details

### Environment Variables
```bash
NODE_ENV=production
PORT=8000
IPFS_API_URL=http://localhost:5001
DATABASE_PATH=/home/deScier/.academic/database.sqlite
UPLOADS_PATH=/home/deScier/.academic/uploads
JWT_SECRET=descios-academic-platform-secret
```

### Default Users
| Email | Password | Role | Username |
|-------|----------|------|----------|
| admin@descios.org | admin123 | admin | admin |
| instructor@descios.org | instructor123 | instructor | janesmith |
| researcher@descios.org | researcher123 | researcher | johndoe |
| student@descios.org | student123 | student | alicejohnson |

### Ports Exposed
- **6080**: noVNC (web interface)
- **8000**: Academic Platform
- **5001**: IPFS API
- **8080**: IPFS Gateway
- **4001**: IPFS Swarm (TCP/UDP)

## 🚀 Deployment Commands

### Build New Container
```bash
docker build -t descios .
```

### Run Container
```bash
docker run -d \
  --name descios \
  -p 6080:6080 \
  -p 8000:8000 \
  -p 5001:5001 \
  -p 8080:8080 \
  descios
```

### Verify Deployment
```bash
# Wait for container to fully start (about 30 seconds)
sleep 30

# Copy and run verification script
docker cp verify-container.sh descios:/home/deScier/verify-container.sh
docker exec descios bash -c "chmod +x /home/deScier/verify-container.sh && /home/deScier/verify-container.sh"
```

### Access Platform
1. **Web Interface**: `http://localhost:6080`
2. **Academic Platform**: Navigate to Academic Platform in Firefox
3. **Login**: Use admin@descios.org / admin123

## ✅ Verification Checklist

After deployment, verify:

### Database & Authentication
- [ ] Admin user exists and can login
- [ ] Dashboard loads without "Failed to load dashboard data" error
- [ ] All overview cards show correct counts (initially 0)

### Notification System
- [ ] Notification bell shows "4" initially
- [ ] Clicking bell shows dropdown with 4 notifications
- [ ] Clicking notifications marks them as read
- [ ] Badge count decreases as notifications are read
- [ ] "Mark all as read" works
- [ ] State persists after page refresh

### API Endpoints
- [ ] `/api/users/:id/stats` returns user statistics
- [ ] `/api/users/:id/activity` returns user activity
- [ ] Authentication works with JWT tokens
- [ ] IPFS connection established (with graceful fallback)

## 🔄 Update Process

To update the platform:

1. **Update files** in the `node/` directory
2. **Rebuild container**: `docker build -t descios .`
3. **Stop old container**: `docker stop descios && docker rm descios`
4. **Start new container**: `docker run -d --name descios -p 6080:6080 -p 8000:8000 descios`

## 🐛 Troubleshooting

### Verification Script
Run the comprehensive verification script inside the container:
```bash
# Copy verification script to container
docker cp verify-container.sh descios:/home/deScier/verify-container.sh

# Run verification inside container
docker exec descios bash -c "chmod +x /home/deScier/verify-container.sh && /home/deScier/verify-container.sh"
```

### Common Issues

**Login fails**
```bash
# Check if admin user exists
docker exec descios bash -c "cd /home/deScier/DeSciOS/node && node ensure-admin.js"
```

**Dashboard shows error**
```bash
# Check server logs
docker exec descios tail -f /home/deScier/.academic/logs/backend.log
```

**Notification system not working**
```bash
# Check if frontend was built correctly
docker exec descios ls -la /home/deScier/DeSciOS/node/frontend/build/
```

**Port conflicts**
```bash
# Check what's using port 8000
docker exec descios netstat -tuln | grep 8000
```

**Academic platform not starting**
```bash
# Check supervisord status
docker exec descios supervisorctl status academic-platform

# Check supervisord logs
docker exec descios tail -f /var/log/supervisor/supervisord.log
```

## 📝 Notes

- **Database**: SQLite file stored in `/home/deScier/.academic/database.sqlite`
- **Logs**: Backend logs in `/home/deScier/.academic/logs/backend.log`
- **Uploads**: Files stored in `/home/deScier/.academic/uploads/`
- **Notifications**: State persisted in browser localStorage
- **IPFS**: Graceful fallback if IPFS connection fails

## 🎉 Success Indicators

When everything is working correctly:
- ✅ Login works with admin credentials
- ✅ Dashboard loads without errors
- ✅ Notification system is fully functional
- ✅ All API endpoints respond correctly
- ✅ Database persists across container restarts
- ✅ Frontend builds successfully with all fixes

All fixes are now permanently integrated into the Docker build process and will persist in any new container deployments! 🚀 