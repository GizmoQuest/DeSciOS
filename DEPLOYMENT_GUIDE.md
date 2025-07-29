# DeSciOS Academic Platform - Deployment Guide

## 🎯 Overview

This guide documents the complete integration of the DeSciOS Academic Platform into the DeSciOS container environment. All fixes have been made permanent and will work correctly for fresh deployments.

## ✅ Verified Fixes Included

### 1. **IPFS Service Fix**
- **Issue**: IPFS service was using `GET` request for `/id` endpoint, causing 405 errors
- **Fix**: Changed to `POST` request in `node/src/services/ipfs.js`
- **Status**: ✅ Permanent in Dockerfile

### 2. **Authentication Fix**
- **Issue**: Frontend sent `email` but backend expected `username` for login
- **Fix**: Updated `node/src/routes/auth.js` to accept `email` for authentication
- **Status**: ✅ Permanent in Dockerfile

### 3. **Database Path Fix**
- **Issue**: Database service used hardcoded path instead of environment variable
- **Fix**: Updated `node/src/services/database.js` to use `process.env.DATABASE_PATH`
- **Status**: ✅ Permanent in Dockerfile

### 4. **Frontend Build Fix**
- **Issue**: Missing essential React files causing build failures
- **Fix**: Created missing `index.html`, `index.js`, and other frontend files
- **Status**: ✅ Permanent in Dockerfile

### 5. **IPFS HTTP Client Fix**
- **Issue**: `ipfs-http-client` library had module resolution conflicts
- **Fix**: Replaced with direct `axios` HTTP requests in `node/src/services/ipfs.js`
- **Status**: ✅ Permanent in Dockerfile

### 6. **Database Initialization Fix**
- **Issue**: Database and admin user not created reliably
- **Fix**: Created `ensure-admin.js` and `start-academic.sh` for robust startup
- **Status**: ✅ Permanent in Dockerfile

### 7. **API Response Fix**
- **Issue**: Frontend expected `response.data` but backend returned nested objects
- **Fix**: Updated all frontend components to correctly access `response.data.projects`, etc.
- **Status**: ✅ Permanent in Dockerfile

### 8. **Notification System Fix**
- **Issue**: Notification bell was static and didn't persist state
- **Fix**: Implemented dynamic state with `localStorage` persistence in `Layout.js`
- **Status**: ✅ Permanent in Dockerfile

### 9. **Feature Completeness Fix**
- **Issue**: All pages showed "Coming soon..." placeholders
- **Fix**: Fully implemented all pages with forms, API integration, and UI logic
- **Status**: ✅ Permanent in Dockerfile

## 🐳 Dockerfile Integration

The Dockerfile now includes:

```dockerfile
# Install DeSciOS Academic Platform
COPY node /home/$USER/DeSciOS/node
RUN chown -R $USER:$USER /home/$USER/DeSciOS && \
    mkdir -p /home/$USER/.academic/uploads /home/$USER/.academic/logs && \
    chown -R $USER:$USER /home/$USER/.academic && \
    cd /home/$USER/DeSciOS/node && \
    npm install && \
    cd frontend && \
    npm install && \
    npm run build && \
    chown -R $USER:$USER /home/$USER/DeSciOS && \
    chmod +x start-academic.sh && \
    chmod +x ensure-admin.js && \
    echo '[Desktop Entry]\nName=Academic Platform\nExec=firefox http://localhost:8000\nIcon=applications-science\nType=Application\nCategories=Education;' \
    > /usr/share/applications/academic-platform.desktop
```

## 🔧 Supervisord Configuration

The academic platform is automatically started via supervisord:

```ini
[program:academic-platform]
command=/bin/bash -c "sleep 10 && su - deScier -c '/home/deScier/DeSciOS/node/start-academic.sh'"
user=deScier
environment=HOME="/home/deScier",USER="deScier"
directory=/home/deScier/DeSciOS/node
autorestart=true
autostart=true
```

## 🚀 Deployment Steps

### 1. **Pre-deployment Verification**
```bash
./verify-dockerfile.sh
```

### 2. **Build Docker Image**
```bash
docker build -t descios .
```

### 3. **Run Container**
```bash
docker run -d --name descios-new \
  -p 6080:6080 \
  -p 8000:8000 \
  -p 5001:5001 \
  -p 8080:8080 \
  descios
```

### 4. **Access the Platform**
- **DeSciOS Desktop**: http://localhost:6080
- **Academic Platform**: http://localhost:8000
- **Admin Login**: `admin@descios.org` / `admin123`

## 📋 Default Users

| Email | Password | Role | Description |
|-------|----------|------|-------------|
| `admin@descios.org` | `admin123` | Admin | System Administrator |
| `professor@university.edu` | `professor123` | Professor | Sample Professor |
| `student@university.edu` | `student123` | Student | Sample Student |

## 🔍 Testing Checklist

### ✅ Login & Authentication
- [ ] Admin can log in with `admin@descios.org` / `admin123`
- [ ] Dashboard loads with statistics
- [ ] Logout works correctly

### ✅ Core Features
- [ ] **Dashboard**: Shows user statistics and activity
- [ ] **Courses**: Create, view, and manage courses
- [ ] **Research**: Create, view, and manage research projects
- [ ] **Collaboration**: Create and manage collaboration workspaces
- [ ] **Users**: User management (admin only)
- [ ] **IPFS Manager**: File upload and management
- [ ] **Profile**: User profile management
- [ ] **Settings**: Application settings

### ✅ IPFS Integration
- [ ] IPFS status shows connected
- [ ] File uploads work correctly
- [ ] Files are pinned and retrievable
- [ ] Gateway URLs work

### ✅ UI/UX Features
- [ ] Notification bell shows dynamic count
- [ ] Notifications persist across page refreshes
- [ ] All forms work correctly
- [ ] Error handling shows proper messages
- [ ] Loading states work correctly

## 🛠️ Troubleshooting

### Common Issues

1. **IPFS Connection Failed**
   - Check if IPFS daemon is running: `docker exec descios-new ipfs id`
   - Restart IPFS: `docker exec descios-new ipfs daemon`

2. **Database Issues**
   - Check database file: `docker exec descios-new ls -la /home/deScier/.academic/`
   - Reinitialize: `docker exec descios-new bash -c "cd /home/deScier/DeSciOS/node && node ensure-admin.js"`

3. **Frontend Not Loading**
   - Check if frontend was built: `docker exec descios-new ls -la /home/deScier/DeSciOS/node/frontend/build/`
   - Rebuild: `docker exec descios-new bash -c "cd /home/deScier/DeSciOS/node/frontend && npm run build"`

4. **API Endpoints Not Working**
   - Check server logs: `docker exec descios-new ps aux | grep "npm start"`
   - Restart server: `docker exec descios-new pkill -f "npm start" && docker exec descios-new bash -c "cd /home/deScier/DeSciOS/node && npm start"`

## 📁 File Structure

```
DeSciOS/
├── node/                          # Academic Platform
│   ├── start-academic.sh         # Startup script
│   ├── ensure-admin.js           # Admin user creation
│   ├── package.json              # Backend dependencies
│   ├── src/
│   │   ├── server.js             # Main server
│   │   ├── services/
│   │   │   ├── database.js       # Database models
│   │   │   ├── ipfs.js           # IPFS service (FIXED)
│   │   │   └── socket.js         # WebSocket service
│   │   ├── routes/
│   │   │   ├── auth.js           # Authentication (FIXED)
│   │   │   ├── users.js          # User management
│   │   │   └── ipfs.js           # IPFS routes
│   │   └── scripts/
│   │       └── init-db.js        # Database initialization
│   └── frontend/                 # React frontend
│       ├── src/
│       │   ├── pages/            # All pages (FULLY IMPLEMENTED)
│       │   ├── components/       # UI components
│       │   └── context/          # React contexts
│       └── public/               # Static assets
├── Dockerfile                    # Container definition (UPDATED)
├── supervisord.conf              # Process management (UPDATED)
└── verify-dockerfile.sh          # Pre-build verification
```

## 🎉 Success Indicators

When deployment is successful, you should see:

1. **Container startup logs**:
   ```
   ✅ Database connection established successfully
   ✅ IPFS connection established: [NODE_ID]
   ✅ Socket.IO service initialized
   🌐 Server running on port 8000
   ```

2. **Academic Platform accessible** at http://localhost:8000

3. **All features working** without "Coming soon..." messages

4. **IPFS file uploads working** without "Failed to upload files" errors

## 🔄 Updates and Maintenance

To update the platform:

1. Make changes to the `node/` directory
2. Run `./verify-dockerfile.sh` to ensure all files are present
3. Rebuild the Docker image: `docker build -t descios .`
4. Stop and remove the old container
5. Run the new container

All fixes are now **permanent** and will work correctly for fresh deployments! 🚀 