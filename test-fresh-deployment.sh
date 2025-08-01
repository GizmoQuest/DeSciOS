#!/bin/bash

# Test script to verify DeSciOS can start with fresh volumes
echo "🧪 Testing DeSciOS deployment with fresh volumes..."

# Stop and remove existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Remove existing volume directories (try without sudo first)
echo "🗑️  Removing existing volume directories..."
if [ -d "./data" ]; then
    if rm -rf ./data/academic ./data/ipfs ./data/user 2>/dev/null; then
        echo "✅ Volume directories removed successfully"
    else
        echo "⚠️  Could not remove volume directories without sudo"
        echo "   You may need to manually remove ./data/ directory"
        echo "   or run: sudo rm -rf ./data/"
    fi
else
    echo "✅ No existing data directory found"
fi

# Rebuild the container
echo "🔨 Rebuilding container..."
docker-compose build --no-cache

# Start the container
echo "🚀 Starting container with fresh volumes..."
docker-compose up -d

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 30

# Check container status
echo "📊 Checking container status..."
docker-compose ps

# Check logs for any errors
echo "📋 Checking container logs..."
docker-compose logs --tail=50

# Test if services are responding
echo "🔍 Testing service endpoints..."
echo "Testing noVNC (should return HTML):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:6080/vnc.html || echo "Failed"

echo "Testing Academic Platform (should return HTML or redirect):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 || echo "Failed"

echo "Testing IPFS API (should return JSON):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/v0/version || echo "Failed"

echo "✅ Fresh deployment test completed!"
echo "Access DeSciOS at: http://localhost:6080/vnc.html" 