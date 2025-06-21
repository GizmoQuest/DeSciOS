#!/bin/bash

# Set hostname at runtime
hostname DeSciOS
if ! grep -q "DeSciOS" /etc/hosts; then
    echo "127.0.0.1 DeSciOS" >> /etc/hosts
fi

# Start supervisord
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &

# Wait for VNC server to start
sleep 5

# Create a script to run as deScier
cat > /tmp/setup_x.sh << 'EOF'
#!/bin/bash

# Set DISPLAY variable
export DISPLAY=:1

# Create .Xauthority if it doesn't exist
touch ~/.Xauthority

# Add local authorization
xauth generate :1 . trusted

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

# Keep the container running
tail -f /dev/null