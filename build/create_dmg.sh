#!/bin/bash
# Create DMG for macOS
# This script should be run on macOS

APP_NAME="DeSciOS Launcher"
DMG_NAME="descios-launcher-0.1.0-macos.dmg"
APP_PATH="dist/descios.app"
DMG_PATH="dist/$DMG_NAME"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check if app exists
if [[ ! -d "$APP_PATH" ]]; then
    echo "Error: $APP_PATH not found. Build the app first."
    exit 1
fi

echo "Creating DMG for $APP_NAME..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/$APP_NAME"

# Copy app to temp directory
cp -R "$APP_PATH" "$TEMP_DIR/$APP_NAME/"

# Create DMG
hdiutil create -volname "$APP_NAME" -srcfolder "$TEMP_DIR" -ov -format UDZO "$DMG_PATH"

# Clean up
rm -rf "$TEMP_DIR"

echo "✓ DMG created: $DMG_PATH"
