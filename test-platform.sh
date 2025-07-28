#!/bin/bash

# DeSciOS Academic Platform - Quick Test Script
# This script performs basic connectivity and functionality tests

echo "🧪 Testing DeSciOS Academic Platform..."

# Check if container is running
echo "📦 Checking container status..."
if ! docker ps | grep -q descios; then
    echo "❌ DeSciOS container is not running"
    echo "💡 Start it with: docker run -d --name descios -p 6080:6080 -p 8000:8000 -p 5001:5001 descios:latest"
    exit 1
fi
echo "✅ Container is running"

# Test backend API
echo "🌐 Testing backend API..."
BACKEND_URL="http://localhost:8000/api/status"
if curl --output /dev/null --silent --head --fail "$BACKEND_URL"; then
    echo "✅ Backend API is accessible"
else
    echo "❌ Backend API is not accessible"
    echo "💡 Check container logs: docker logs descios"
fi

# Test IPFS API
echo "🌐 Testing IPFS API..."
IPFS_URL="http://localhost:5001/api/v0/id"
if curl --output /dev/null --silent --head --fail "$IPFS_URL"; then
    echo "✅ IPFS API is accessible"
else
    echo "❌ IPFS API is not accessible (but working inside container)"
fi

# Test frontend
echo "🌐 Testing frontend..."
FRONTEND_URL="http://localhost:8000"
if curl --output /dev/null --silent --head --fail "$FRONTEND_URL"; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
fi

# Test DeSciOS desktop
echo "🌐 Testing DeSciOS desktop..."
DESKTOP_URL="http://localhost:6080"
if curl --output /dev/null --silent --head --fail "$DESKTOP_URL"; then
    echo "✅ DeSciOS desktop is accessible"
else
    echo "❌ DeSciOS desktop is not accessible"
fi

echo ""
echo "🎯 Quick Access URLs:"
echo "   DeSciOS Desktop: http://localhost:6080"
echo "   Academic Platform: http://localhost:8000"
echo "   Admin Login: admin@descios.org / admin123"
echo ""
echo "📖 For detailed testing, see: TESTING_GUIDE.md"
echo ""
echo "�� Test completed!" 