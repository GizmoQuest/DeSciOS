#!/usr/bin/env python3
"""
Build script for creating DeSciOS Launcher binaries
Supports Linux, macOS, and Windows platforms
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

def get_platform_info():
    """Get platform-specific information"""
    system = platform.system().lower()
    
    if system == "linux":
        return {
            "name": "linux",
            "binary_name": "descios",
            "extension": "",
            "icon": None  # Could add .png icon later
        }
    elif system == "darwin":
        return {
            "name": "macos", 
            "binary_name": "descios",
            "extension": ".app",
            "icon": None  # Could add .icns icon later
        }
    elif system == "windows":
        return {
            "name": "windows",
            "binary_name": "descios",
            "extension": ".exe", 
            "icon": None  # Could add .ico icon later
        }
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")

def create_spec_file(platform_info):
    """Create PyInstaller spec file for the launcher"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

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
    hooksconfig={{}},
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
    name='{platform_info["binary_name"]}{platform_info["extension"]}',
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
)'''

    if platform_info["name"] == "macos":
        spec_content += f'''

app = BUNDLE(
    exe,
    name='{platform_info["binary_name"]}.app',
    icon=None,
    bundle_identifier='org.descios.launcher',
    info_plist={{
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {{
                'CFBundleTypeName': 'DeSciOS Configuration',
                'CFBundleTypeIconFile': 'MyDocument.icns',
                'LSItemContentTypes': ['org.descios.config'],
                'LSHandlerRank': 'Owner'
            }}
        ]
    }},
)'''

    return spec_content

def build_binary(platform_info):
    """Build the binary using PyInstaller"""
    print(f"Building binary for {platform_info['name']}...")
    
    # Create spec file
    spec_content = create_spec_file(platform_info)
    spec_file = "descios_launcher.spec"
    
    with open(spec_file, "w") as f:
        f.write(spec_content)
    
    # Build with PyInstaller
    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        spec_file
    ]
    
    try:
        subprocess.check_call(cmd)
        print(f"✓ Binary built successfully: dist/{platform_info['binary_name']}{platform_info['extension']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False
    finally:
        # Clean up spec file
        if os.path.exists(spec_file):
            os.remove(spec_file)

def create_build_info():
    """Create build information file"""
    build_info = f"""DeSciOS Launcher Build Information
=====================================

Platform: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Python Version: {sys.version}
Build Date: {subprocess.check_output(['date'], text=True).strip()}

To install:
- Linux: Use the .deb package or copy binary to /usr/local/bin/
- macOS: Copy .app to /Applications/ or run directly
- Windows: Copy .exe to desired location and optionally add to PATH

Usage:
    descios          # Launch the GUI
    descios --help   # Show help information
"""
    
    os.makedirs("dist", exist_ok=True)
    with open("dist/BUILD_INFO.txt", "w") as f:
        f.write(build_info)

def main():
    """Main build function"""
    print("🚀 DeSciOS Launcher Build System")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("descios_launcher/main.py"):
        print("✗ Error: descios_launcher/main.py not found")
        print("Please run this script from the DeSciOS root directory")
        sys.exit(1)
    
    # Get platform info
    try:
        platform_info = get_platform_info()
        print(f"Building for: {platform_info['name']}")
        print(f"Binary name: {platform_info['binary_name']}{platform_info['extension']}")
    except RuntimeError as e:
        print(f"✗ {e}")
        sys.exit(1)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build binary
    success = build_binary(platform_info)
    if not success:
        sys.exit(1)
    
    # Create build info
    create_build_info()
    
    print("\n🎉 Build completed successfully!")
    print(f"Binary location: dist/{platform_info['binary_name']}{platform_info['extension']}")
    print("See dist/BUILD_INFO.txt for installation instructions")

if __name__ == "__main__":
    main() 