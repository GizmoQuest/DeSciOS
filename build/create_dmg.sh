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
