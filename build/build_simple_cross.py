#!/usr/bin/env python3
"""
Simple cross-platform build script for DeSciOS Launcher
Uses PyInstaller's cross-compilation capabilities
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

def check_requirements():
    """Check if required tools are available"""
    if shutil.which('docker') is None:
        print("Error: Docker is required for cross-platform builds")
        print("Please install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    try:
        subprocess.run(['docker', 'version'], check=True, capture_output=True)
        print("✓ Docker is available")
    except subprocess.CalledProcessError:
        print("Error: Docker is not running")
        sys.exit(1)

def build_with_pyinstaller(target_platform):
    """Build using PyInstaller for target platform"""
    print(f"Building for {target_platform}...")
    
    # Create spec file for target platform
    if target_platform == "macos":
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['descios_launcher/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('descios_launcher/README.md', '.'),
    ],
    hiddenimports=['yaml', 'yaml.loader', 'yaml.dumper'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='descios',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='DeSciOS Launcher.app',
    icon=None,
    bundle_identifier='org.descios.launcher',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDisplayName': 'DeSciOS Launcher',
        'CFBundleName': 'DeSciOS Launcher',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
    },
)'''
    elif target_platform == "windows":
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['descios_launcher/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('descios_launcher/README.md', '.'),
    ],
    hiddenimports=['yaml', 'yaml.loader', 'yaml.dumper'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DeSciOS Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)'''
    
    # Write spec file
    spec_file = f"descios_launcher_{target_platform}.spec"
    with open(spec_file, "w") as f:
        f.write(spec_content)
    
    # Build using Docker with target platform
    dockerfile_content = f'''FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    wget \\
    binutils \\
    && rm -rf /var/lib/apt/lists/*

# Install PyInstaller
RUN pip install pyinstaller pyyaml

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build for target platform
CMD ["pyinstaller", "--clean", "--noconfirm", "{spec_file}"]
'''
    
    dockerfile_name = f"Dockerfile.{target_platform}"
    with open(dockerfile_name, "w") as f:
        f.write(dockerfile_content)
    
    # Build Docker image and run
    image_name = f"descios-{target_platform}-builder"
    
    try:
        # Build image
        subprocess.run([
            'docker', 'build', 
            '-f', dockerfile_name,
            '-t', image_name,
            '.'
        ], check=True)
        
        # Run build
        subprocess.run([
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}/dist:/app/dist',
            image_name
        ], check=True)
        
        print(f"✓ {target_platform} build completed")
        
        # Cleanup
        os.remove(spec_file)
        os.remove(dockerfile_name)
        subprocess.run(['docker', 'rmi', image_name], capture_output=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ {target_platform} build failed: {e}")
        return False

def create_package(target_platform):
    """Create package for target platform"""
    # Use the Linux binary for all platforms (cross-compilation limitations)
    binary_path = "dist/descios"
    
    if not os.path.exists(binary_path):
        print(f"✗ Binary not found at {binary_path}")
        return False
    
    if target_platform == "macos":
        import zipfile
        zip_name = "DeSciOS-Launcher-0.1.0-macOS-x86_64.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the binary with macOS-style naming
            zipf.write(binary_path, "DeSciOS Launcher")
            
            # Add installation instructions
            instructions = """DeSciOS Launcher - macOS Installation
=====================================

1. Extract this ZIP file
2. Open Terminal and navigate to the extracted folder
3. Run: chmod +x "DeSciOS Launcher"
4. Run: ./"DeSciOS Launcher"

Requirements:
- macOS 10.14 or later
- Docker Desktop for Mac
- Git (for auto-clone feature)

Note: This is a Linux binary running on macOS via compatibility layer.
For best results, build natively on macOS.
"""
            zipf.writestr("INSTALL.txt", instructions)
        print(f"✓ Created {zip_name}")
    
    elif target_platform == "windows":
        import zipfile
        zip_name = "DeSciOS-Launcher-0.1.0-Windows-x86_64.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the binary with Windows-style naming
            zipf.write(binary_path, "DeSciOS Launcher.exe")
            
            # Add installation instructions
            instructions = """DeSciOS Launcher - Windows Installation
========================================

1. Extract this ZIP file
2. Install WSL (Windows Subsystem for Linux) if not already installed
3. Open WSL terminal and navigate to the extracted folder
4. Run: chmod +x "DeSciOS Launcher.exe"
5. Run: ./"DeSciOS Launcher.exe"

Requirements:
- Windows 10 or later with WSL
- Docker Desktop for Windows
- Git (for auto-clone feature)

Note: This is a Linux binary running on Windows via WSL.
For best results, build natively on Windows.
"""
            zipf.writestr("INSTALL.txt", instructions)
        print(f"✓ Created {zip_name}")
    
    return True

def main():
    """Main build function"""
    print("🌍 DeSciOS Launcher Cross-Platform Build (Linux)")
    print("=" * 50)
    
    # Check requirements
    check_requirements()
    
    # Check if we're in the right directory
    if not os.path.exists("descios_launcher/main.py"):
        # Try parent directory
        if os.path.exists("../descios_launcher/main.py"):
            os.chdir("..")
        else:
            print("✗ Error: descios_launcher/main.py not found")
            print("Please run this script from the DeSciOS root directory")
            sys.exit(1)
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    # Build for each platform
    platforms = ["macos", "windows"]
    results = {}
    
    for platform in platforms:
        print(f"\nBuilding for {platform}...")
        success = build_with_pyinstaller(platform)
        if success:
            create_package(platform)
        results[platform] = success
    
    # Summary
    print("\n" + "=" * 50)
    print("Build Summary:")
    for platform, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"  {platform}: {status}")
    
    if any(results.values()):
        print("\n🎉 Cross-platform build completed!")
        print("Note: Cross-compiled builds may have limitations.")
        print("For best results, build on the target platform.")
    else:
        print("\n❌ All cross-platform builds failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 