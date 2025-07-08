#!/bin/bash

echo "🔍 DeSciOS IPFS Status Checker"
echo "================================"

# Check if IPFS is installed
if ! command -v ipfs &> /dev/null; then
    echo "❌ IPFS is not installed"
    exit 1
fi

echo "✅ IPFS is installed"

# Check if IPFS is initialized
if [ ! -d "$HOME/.ipfs" ]; then
    echo "⚠️  IPFS not initialized. Initializing now..."
    ipfs init --profile=server
fi

# Check if IPFS daemon is running
if pgrep -f "ipfs daemon" > /dev/null; then
    echo "✅ IPFS daemon is running"
    
    # Get IPFS node info
    echo ""
    echo "📊 IPFS Node Information:"
    echo "------------------------"
    ipfs id
    
    echo ""
    echo "🌐 IPFS Gateway: http://localhost:8080"
    echo "🔧 IPFS API: http://localhost:5001"
    echo "📁 IPFS Web UI: http://localhost:5001/webui"
    echo "🔗 IPFS Swarm Port: 4001 (TCP/UDP)"
    
else
    echo "❌ IPFS daemon is not running"
    echo "💡 Starting IPFS daemon..."
    ipfs daemon --enable-gc --routing=dht &
    sleep 3
    
    if pgrep -f "ipfs daemon" > /dev/null; then
        echo "✅ IPFS daemon started successfully"
        echo ""
        echo "📊 IPFS Node Information:"
        echo "------------------------"
        ipfs id
    else
        echo "❌ Failed to start IPFS daemon"
        exit 1
    fi
fi

echo ""
echo "🎉 IPFS is ready to use!"
echo "💡 You can now use IPFS Desktop or command line tools" 