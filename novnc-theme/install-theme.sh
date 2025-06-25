#!/bin/bash

# DeSciOS noVNC Theme Installation Script
# This script adds the necessary COPY commands to your Dockerfile

echo "🎨 DeSciOS noVNC Theme Installer"
echo "================================"

# Check if Dockerfile exists
if [ ! -f "../Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found in parent directory"
    echo "   Please run this script from the novnc-theme directory"
    exit 1
fi

# Check if theme files exist
echo "🔍 Checking theme files..."
missing_files=()

if [ ! -f "descios-theme.css" ]; then
    missing_files+=("descios-theme.css")
fi

if [ ! -f "vnc.html" ]; then
    missing_files+=("vnc.html")
fi

if [ ! -d "icons" ]; then
    missing_files+=("icons/")
fi

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Error: Missing theme files:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ All theme files found"

# Check if theme is already installed
if grep -q "DeSciOS noVNC Theme" ../Dockerfile; then
    echo "⚠️  DeSciOS theme appears to already be installed in Dockerfile"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Installation cancelled"
        exit 0
    fi
fi

# Find the line after noVNC installation
novnc_line=$(grep -n "novnc\|websockify" ../Dockerfile | tail -1 | cut -d: -f1)

if [ -z "$novnc_line" ]; then
    echo "❌ Error: Could not find noVNC installation in Dockerfile"
    echo "   Please add the theme installation manually"
    exit 1
fi

echo "📝 Adding DeSciOS theme to Dockerfile..."

# Create backup
cp ../Dockerfile ../Dockerfile.backup
echo "   Created backup: Dockerfile.backup"

# Prepare the installation lines
install_lines="
# Apply DeSciOS noVNC Theme
COPY novnc-theme/descios-theme.css /usr/share/novnc/app/styles/
COPY novnc-theme/vnc.html /usr/share/novnc/
COPY novnc-theme/icons/* /usr/share/novnc/app/images/icons/"

# Insert after noVNC installation
{
    head -n "$novnc_line" ../Dockerfile
    echo "$install_lines"
    tail -n +"$((novnc_line+1))" ../Dockerfile
} > ../Dockerfile.tmp && mv ../Dockerfile.tmp ../Dockerfile

echo "✅ DeSciOS theme successfully added to Dockerfile!"
echo ""
echo "📋 Next steps:"
echo "   1. Rebuild your Docker image: docker build -t descios ."
echo "   2. Run container: docker run -p 6080:6080 descios"
echo "   3. Access via browser: http://localhost:6080"
echo ""
echo "🎨 The DeSciOS theme will be applied automatically!" 