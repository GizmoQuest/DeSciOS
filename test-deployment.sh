#!/bin/bash

# Test script to verify DeSciOS deployment status
echo "🧪 Testing DeSciOS deployment status..."

# Check if container is running
echo "📊 Checking container status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Container is running"
else
    echo "❌ Container is not running"
    echo "Starting container..."
    docker-compose up -d
    sleep 30
fi

# Check container logs
echo "📋 Checking container logs..."
docker-compose logs --tail=20

# Test service endpoints
echo "🔍 Testing service endpoints..."
echo "Testing noVNC (should return HTML):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:6080/vnc.html || echo "Failed"

echo "Testing Academic Platform (should return HTML or redirect):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 || echo "Failed"

echo "Testing IPFS API (should return JSON):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/v0/version || echo "Failed"

# Check volume permissions
echo "📁 Checking volume permissions..."
if [ -d "./data" ]; then
    echo "Data directory exists:"
    ls -la ./data/
else
    echo "No data directory found"
fi

echo "✅ Deployment test completed!"
echo "Access DeSciOS at: http://localhost:6080/vnc.html" 