#!/usr/bin/env python3
"""
Cross-platform build script for DeSciOS Launcher
Builds macOS DMG and Windows EXE from Linux using Docker
"""

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

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def check_linux():
    """Check if we're running on Linux"""
    if platform.system() != "Linux":
        print("Error: This script is designed to run on Linux")
        sys.exit(1)

def check_docker():
    """Check if Docker is available"""
    if shutil.which('docker') is None:
        print("Error: Docker is required for cross-platform builds")
        print("Please install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    # Test Docker
    try:
        subprocess.run(['docker', 'version'], check=True, capture_output=True)
        print("✓ Docker is available")
    except subprocess.CalledProcessError:
        print("Error: Docker is not running or not accessible")
        print("Please start Docker and try again")
        sys.exit(1)

def create_macos_dockerfile():
    """Create Dockerfile for macOS build environment"""
    dockerfile_content = '''FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install pyinstaller pyyaml

# Install create-dmg (macOS package creation tool)
RUN curl -L https://github.com/create-dmg/create-dmg/releases/download/v1.1.0/create-dmg-1.1.0.tar.gz | tar -xz -C /tmp && \\
    mv /tmp/create-dmg-1.1.0/create-dmg /usr/local/bin/ && \\
    chmod +x /usr/local/bin/create-dmg

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build command
CMD ["python3", "build/build_macos.py"]
'''
    
    with open("build/Dockerfile.macos", "w") as f:
        f.write(dockerfile_content)

def create_windows_dockerfile():
    """Create Dockerfile for Windows build environment"""
    dockerfile_content = '''FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    wget \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install pyinstaller pyyaml

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build command
CMD ["python3", "build/build_windows.py"]
'''
    
    with open("build/Dockerfile.windows", "w") as f:
        f.write(dockerfile_content)

def build_macos_dmg():
    """Build macOS DMG using Docker"""
    print("🍎 Building macOS DMG using Docker...")
    
    # Create Dockerfile
    create_macos_dockerfile()
    
    # Build Docker image
    image_name = "descios-macos-builder"
    try:
        subprocess.run([
            'docker', 'build', 
            '-f', 'build/Dockerfile.macos',
            '-t', image_name,
            '.'
        ], check=True)
        print("✓ macOS Docker image built")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build macOS Docker image: {e}")
        return False
    
    # Run build in container
    try:
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}/dist:/app/dist',
            '-v', f'{os.getcwd()}:/app',
            image_name
        ], check=True)
        print("✓ macOS DMG build completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ macOS DMG build failed: {e}")
        return False

def build_windows_exe():
    """Build Windows EXE using Docker"""
    print("🪟 Building Windows EXE using Docker...")
    
    # Create Dockerfile
    create_windows_dockerfile()
    
    # Build Docker image
    image_name = "descios-windows-builder"
    try:
        subprocess.run([
            'docker', 'build', 
            '-f', 'build/Dockerfile.windows',
            '-t', image_name,
            '.'
        ], check=True)
        print("✓ Windows Docker image built")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build Windows Docker image: {e}")
        return False
    
    # Run build in container
    try:
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}/dist:/app/dist',
            '-v', f'{os.getcwd()}:/app',
            image_name
        ], check=True)
        print("✓ Windows EXE build completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Windows EXE build failed: {e}")
        return False

def build_all_platforms():
    """Build packages for all platforms"""
    print("🚀 Building DeSciOS Launcher for all platforms...")
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    # Build Linux package first (native)
    print("\n🐧 Building Linux package (native)...")
    try:
        subprocess.run(['python3', 'build/build_launcher.py'], check=True)
        subprocess.run(['python3', 'build/build_deb.py'], check=True)
        print("✓ Linux package built")
    except subprocess.CalledProcessError as e:
        print(f"✗ Linux build failed: {e}")
        return False
    
    # Build macOS DMG
    print("\n🍎 Building macOS DMG...")
    if not build_macos_dmg():
        print("⚠️  macOS build failed, continuing...")
    
    # Build Windows EXE
    print("\n🪟 Building Windows EXE...")
    if not build_windows_exe():
        print("⚠️  Windows build failed, continuing...")
    
    return True

def cleanup():
    """Clean up Docker images and temporary files"""
    print("\n🧹 Cleaning up...")
    
    # Remove Docker images
    for image in ["descios-macos-builder", "descios-windows-builder"]:
        try:
            subprocess.run(['docker', 'rmi', image], capture_output=True)
        except:
            pass
    
    # Remove Dockerfiles
    for dockerfile in ["build/Dockerfile.macos", "build/Dockerfile.windows"]:
        if os.path.exists(dockerfile):
            os.remove(dockerfile)

def main():
    """Main build function"""
    print("🌍 DeSciOS Launcher Cross-Platform Build System")
    print("=" * 50)
    
    # Check requirements
    check_linux()
    check_docker()
    
    # Check if we're in the right directory
    if not os.path.exists("descios_launcher/main.py"):
        print("✗ Error: descios_launcher/main.py not found")
        print("Please run this script from the DeSciOS root directory")
        sys.exit(1)
    
    # Build all platforms
    success = build_all_platforms()
    
    # Cleanup
    cleanup()
    
    if success:
        print("\n🎉 Cross-platform build completed!")
        print("\nGenerated packages:")
        
        # List generated files
        if os.path.exists("descios-launcher_0.1.0_amd64.deb"):
            print("- descios-launcher_0.1.0_amd64.deb (Linux)")
        
        if os.path.exists("DeSciOS-Launcher-0.1.0-macOS.dmg"):
            print("- DeSciOS-Launcher-0.1.0-macOS.dmg (macOS)")
        
        if os.path.exists("DeSciOS-Launcher-0.1.0-Windows.zip"):
            print("- DeSciOS-Launcher-0.1.0-Windows.zip (Windows)")
        
        print("\nNote: Cross-platform builds may have limitations.")
        print("For best results, build on the target platform.")
    else:
        print("\n❌ Build completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main() 