#!/bin/bash

# Academic Platform Startup Script for DeSciOS
# This script starts both the backend and frontend services

echo "Starting DeSciOS Academic Platform..."

# Set environment variables
export NODE_ENV=production
export PORT=8000
export IPFS_API_URL=http://localhost:5001
export DATABASE_PATH=/home/deScier/.academic/database.sqlite
export UPLOADS_PATH=/home/deScier/.academic/uploads
export JWT_SECRET=descios-academic-platform-secret

# Create necessary directories
mkdir -p /home/deScier/.academic/uploads
mkdir -p /home/deScier/.academic/logs

# Change to the academic platform directory
cd /home/deScier/DeSciOS/node

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing backend dependencies..."
    npm install
fi

# Initialize database if it doesn't exist
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Initializing database..."
    npm run init-db
fi

# Build frontend if build directory doesn't exist
if [ ! -d "frontend/build" ]; then
    echo "Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Start the backend server
echo "Starting backend server on port $PORT..."
npm start >> /home/deScier/.academic/logs/backend.log 2>&1 