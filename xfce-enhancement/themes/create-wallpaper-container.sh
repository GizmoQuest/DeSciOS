#!/bin/bash

# Create a beautiful modern wallpaper using ImageMagick
# This creates a stunning gradient background with subtle patterns
# Container version - uses /root paths

WALLPAPER_DIR="/root/.local/share/backgrounds/descios"
mkdir -p "$WALLPAPER_DIR"

# Create main wallpaper with modern gradient
convert -size 1920x1080 \
  -define gradient:vector=0,0,1,1 \
  gradient:'#667eea-#764ba2' \
  -blur 0x2 \
  -modulate 110,90,100 \
  "$WALLPAPER_DIR/descios-modern.jpg"

# Create alternative dark theme wallpaper
convert -size 1920x1080 \
  -define gradient:vector=0,0,1,1 \
  gradient:'#2C3E50-#34495E' \
  -blur 0x3 \
  -modulate 95,85,110 \
  "$WALLPAPER_DIR/descios-dark.jpg"

# Create light theme wallpaper
convert -size 1920x1080 \
  -define gradient:vector=0,0,1,1 \
  gradient:'#E3F2FD-#BBDEFB' \
  -blur 0x2 \
  -modulate 105,95,100 \
  "$WALLPAPER_DIR/descios-light.jpg"

# Create a more dramatic sci-fi style wallpaper
convert -size 1920x1080 \
  -define gradient:vector=0,0,1,1 \
  gradient:'#0F2027-#203A43-#2C5364' \
  -blur 0x1 \
  -modulate 100,80,120 \
  "$WALLPAPER_DIR/descios-scifi.jpg"

echo "Beautiful wallpapers created in $WALLPAPER_DIR"
echo "Available wallpapers:"
ls -la "$WALLPAPER_DIR" 