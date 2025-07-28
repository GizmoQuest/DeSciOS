#!/bin/bash

# Academic Platform Startup Script
# This script ensures the database is properly initialized before starting the server

set -e

echo "🚀 Starting DeSciOS Academic Platform..."

# Set environment variables
export NODE_ENV=production
export PORT=8000
export IPFS_API_URL=http://localhost:5001
export DATABASE_PATH=/home/deScier/.academic/database.sqlite
export UPLOADS_PATH=/home/deScier/.academic/uploads
export JWT_SECRET=descios-academic-platform-secret

# Change to the academic platform directory
cd /home/deScier/DeSciOS/node

# Create necessary directories if they don't exist
mkdir -p /home/deScier/.academic/uploads
mkdir -p /home/deScier/.academic/logs

# Ensure database is initialized and admin user exists
echo "📊 Ensuring database is ready..."
node ensure-admin.js

# Start the academic platform server
echo "🌐 Starting academic platform server on port $PORT..."
npm start 