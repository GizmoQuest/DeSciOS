#!/bin/bash

# Set hostname at runtime
hostname DeSciOS
if ! grep -q "DeSciOS" /etc/hosts; then
    echo "127.0.0.1 DeSciOS" >> /etc/hosts
fi

# Initialize IPFS for deScier user
echo "Initializing IPFS..."
su - deScier -c 'ipfs init --profile=server' || echo "IPFS already initialized or failed to initialize"

# Configure IPFS to bind to all interfaces for external access
echo "Configuring IPFS for external access..."
su - deScier -c 'ipfs config Addresses.API "/ip4/0.0.0.0/tcp/5001"'
su - deScier -c 'ipfs config Addresses.Gateway "/ip4/0.0.0.0/tcp/8080"'

# Start IPFS daemon in background
echo "Starting IPFS daemon..."
su - deScier -c 'ipfs daemon --enable-gc --routing=dht' &

# Wait a moment for IPFS to start and check status
sleep 3
echo "Checking IPFS status..."
su - deScier -c 'ipfs id' || echo "IPFS still starting up..."

# Clean up any stale VNC/X server files
echo "Cleaning up stale VNC/X server files..."
rm -f /tmp/.X*-lock /tmp/.X11-unix/X* /tmp/.X*-lock
su - deScier -c 'rm -f ~/.vnc/*.pid ~/.vnc/*.log'

# Initialize VNC environment for deScier user
echo "Initializing VNC environment..."
su - deScier -c 'mkdir -p ~/.vnc'
su - deScier -c 'touch ~/.Xauthority'
su - deScier -c 'xauth generate :1 . trusted'

# Start VNC server manually first to ensure it's working
echo "Starting VNC server..."
su - deScier -c 'vncserver :1 -geometry 1920x1080' &
VNC_PID=$!

# Wait for VNC server to start
sleep 5

# Check if VNC server is running
if ! ps -p $VNC_PID > /dev/null 2>&1; then
    echo "VNC server failed to start, retrying..."
    # Kill any existing VNC processes
    pkill -f vncserver || true
    sleep 2
    # Remove any remaining lock files
    rm -f /tmp/.X*-lock /tmp/.X11-unix/X*
    # Start VNC server again
    su - deScier -c 'vncserver :1 -geometry 1920x1080' &
    VNC_PID=$!
    sleep 5
fi

# Verify VNC server is running
if ps -p $VNC_PID > /dev/null 2>&1; then
    echo "VNC server started successfully (PID: $VNC_PID)"
else
    echo "Warning: VNC server may not be running properly"
fi

# Start websockify for noVNC
echo "Starting noVNC websockify..."
websockify --web=/usr/share/novnc/ 6080 localhost:5901 &
WEBSOCKIFY_PID=$!

# Wait for websockify to start
sleep 3

# Verify websockify is running
if ps -p $WEBSOCKIFY_PID > /dev/null 2>&1; then
    echo "noVNC websockify started successfully (PID: $WEBSOCKIFY_PID)"
else
    echo "Warning: websockify may not be running properly"
fi

# Start supervisord for other services (but not VNC since we started it manually)
echo "Starting supervisord for other services..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &

# Wait for services to stabilize
sleep 10

# Create a script to run as deScier for X server setup
cat > /tmp/setup_x.sh << 'EOF'
#!/bin/bash

# Set DISPLAY variable
export DISPLAY=:1

# Wait for X server to be fully ready
for i in {1..30}; do
    if DISPLAY=:1 xset q &>/dev/null; then
        echo "X server is ready"
        break
    fi
    echo "Waiting for X server... ($i/30)"
    sleep 1
done

# Allow local connections
xhost +local:

# Wait a bit more for XFCE to initialize
sleep 5

# Try to get root window geometry using xwininfo
if DISPLAY=:1 xwininfo -root > ~/.vnc/geometry.log 2>&1; then
    # Extract dimensions from xwininfo output
    WIDTH=$(grep 'Width:' ~/.vnc/geometry.log | awk '{print $2}')
    HEIGHT=$(grep 'Height:' ~/.vnc/geometry.log | awk '{print $2}')
    
    if [ ! -z "$WIDTH" ] && [ ! -z "$HEIGHT" ]; then
        # Calculate cursor position
        X=$((WIDTH * 95 / 100))
        Y=1060
        
        # Try to move cursor using xte
        echo "Attempting to move cursor to $X,$Y" >> ~/.vnc/cursor.log
        for i in {1..5}; do
            if DISPLAY=:1 xte "mousemove $X $Y" 2>/dev/null; then
                echo "Successfully moved cursor using xte (attempt $i)" >> ~/.vnc/cursor.log
                break
            else
                echo "Failed to move cursor using xte (attempt $i)" >> ~/.vnc/cursor.log
                sleep 1
            fi
        done
        
        echo "Screen dimensions from xwininfo: ${WIDTH}x${HEIGHT}" >> ~/.vnc/geometry.log
    else
        echo "Failed to parse dimensions from xwininfo output" >> ~/.vnc/geometry.log
    fi
else
    echo "Failed to get root window info" >> ~/.vnc/geometry.log
fi
EOF

# Make the script executable
chmod +x /tmp/setup_x.sh

# Switch to deScier user and run the script
su - deScier -c '/tmp/setup_x.sh'

# Display final status
echo "=== DeSciOS Startup Complete ==="
echo "VNC Server: $(ps -p $VNC_PID >/dev/null && echo 'Running' || echo 'Not running')"
echo "noVNC: $(ps -p $WEBSOCKIFY_PID >/dev/null && echo 'Running' || echo 'Not running')"
echo "IPFS: $(su - deScier -c 'ipfs id' >/dev/null 2>&1 && echo 'Running' || echo 'Not running')"
echo "Access DeSciOS at: http://localhost:6080/vnc.html"

# Keep the container running
tail -f /dev/null