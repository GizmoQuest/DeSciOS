#!/bin/bash

# MIT License
#
# Copyright (c) 2025 Avimanyu Bandyopadhyay
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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