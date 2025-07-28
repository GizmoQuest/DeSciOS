# DeSciOS Academic Platform - Permanent Fixes

## Overview
This document describes the permanent fixes implemented to ensure the DeSciOS Academic Platform works correctly every time the Docker container starts, without requiring manual intervention.

## Issues Fixed

### 1. Database Initialization Issues
**Problem**: The database initialization script had schema mismatches and wasn't reliably creating users on container startup.

**Solution**: 
- Created a simplified `ensure-admin.js` script that reliably creates the admin user
- Updated the startup process to use this script instead of the complex initialization
- Fixed schema mismatches between init-db.js and the main database service

### 2. Startup Process Reliability
**Problem**: The academic platform wasn't reliably starting with proper database initialization.

**Solution**:
- Created a dedicated `start-academic.sh` startup script
- Updated supervisord configuration to use the new startup script
- Added proper error handling and logging

### 3. Authentication Issues
**Problem**: Login was failing due to database schema mismatches and missing users.

**Solution**:
- Fixed the User model schema to use `username` instead of `name`
- Ensured consistent database schema between initialization and main application
- Created reliable admin user creation process

## Files Modified

### 1. `Dockerfile`
- Added database initialization during build process
- Made startup scripts executable
- Ensured proper file permissions

### 2. `supervisord.conf`
- Updated academic platform startup command to use the new startup script
- Added proper environment variables and user context

### 3. `node/src/scripts/init-db.js`
- Fixed User model schema to match main application
- Added intelligent database initialization (only reinitialize if needed)
- Fixed field names (`username` instead of `name`)

### 4. `node/start-academic.sh` (NEW)
- Dedicated startup script for the academic platform
- Ensures database is ready before starting server
- Proper environment variable setup
- Error handling and logging

### 5. `node/ensure-admin.js` (NEW)
- Simple, reliable script to ensure admin user exists
- Uses the same database service as the main application
- Idempotent - safe to run multiple times

## How It Works

### Container Startup Process
1. **Docker Build**: Database initialization happens during build
2. **Container Start**: Supervisord starts the academic platform
3. **Startup Script**: `start-academic.sh` ensures database is ready
4. **Admin Check**: `ensure-admin.js` creates admin user if needed
5. **Server Start**: Academic platform server starts on port 8000

### Database Initialization
- The `ensure-admin.js` script checks if admin user exists
- If not found, creates the admin user with correct schema
- Uses the same database service as the main application
- Safe to run multiple times (idempotent)

### Authentication
- Admin user: `admin@descios.org` / `admin123`
- Schema uses `username` field for login
- Password properly hashed with bcrypt
- Role-based access control implemented

## Testing the Fixes

### 1. Build New Container
```bash
docker build -t descios .
```

### 2. Run Container
```bash
docker run -d --name descios-test -p 6080:6080 -p 8000:8000 descios
```

### 3. Verify Startup
```bash
# Check if academic platform is running
docker exec descios-test netstat -tuln | grep 8000

# Check logs
docker exec descios-test tail -f /home/deScier/.academic/logs/backend.log

# Verify admin user exists
docker exec descios-test bash -c "cd /home/deScier/DeSciOS/node && node ensure-admin.js"
```

### 4. Test Login
- Open browser to `http://localhost:6080`
- Navigate to Academic Platform
- Login with: `admin@descios.org` / `admin123`

## Default Users Created

| Email | Password | Role | Username |
|-------|----------|------|----------|
| admin@descios.org | admin123 | admin | admin |
| instructor@descios.org | instructor123 | instructor | janesmith |
| researcher@descios.org | researcher123 | researcher | johndoe |
| student@descios.org | student123 | student | alicejohnson |

## Troubleshooting

### If Login Still Fails
1. Check if server is running: `docker exec descios netstat -tuln | grep 8000`
2. Check server logs: `docker exec descios tail -f /home/deScier/.academic/logs/backend.log`
3. Manually create admin user: `docker exec descios bash -c "cd /home/deScier/DeSciOS/node && node ensure-admin.js"`

### If Database Issues Occur
1. Check database file: `docker exec descios ls -la /home/deScier/.academic/`
2. Verify database schema: `docker exec descios bash -c "cd /home/deScier/DeSciOS/node && node -e \"const { User } = require('./src/services/database'); User.count().then(c => console.log('Users:', c));\""`

### If Server Won't Start
1. Check port conflicts: `docker exec descios netstat -tuln | grep 8000`
2. Check supervisord status: `docker exec descios supervisorctl status`
3. Restart academic platform: `docker exec descios supervisorctl restart academic-platform`

## Benefits of These Fixes

1. **Reliability**: Academic platform starts correctly every time
2. **Consistency**: Database schema is consistent across all components
3. **Simplicity**: Simple, focused scripts instead of complex initialization
4. **Maintainability**: Clear separation of concerns and proper error handling
5. **User Experience**: Login works immediately without manual intervention

## Future Improvements

1. **Additional Users**: Add more sample users during initialization
2. **Sample Data**: Create sample courses, research projects, and collaborations
3. **Configuration**: Make database path and credentials configurable
4. **Backup**: Add database backup and restore functionality
5. **Monitoring**: Add health checks and monitoring endpoints 