#!/usr/bin/env python3
"""
Build script for creating DeSciOS Launcher DMG package for macOS
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def check_macos():
    """Check if we're running on macOS"""
    if platform.system() != "Darwin":
        print("Error: This script must be run on macOS")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    # Check for create-dmg
    if shutil.which('create-dmg') is None:
        print("Installing create-dmg...")
        subprocess.check_call(['brew', 'install', 'create-dmg'])
        print("✓ create-dmg installed")

def build_macos_app():
    """Build the macOS .app bundle"""
    print("Building macOS app bundle...")
    
    # Create spec file for macOS
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
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'DeSciOS Configuration',
                'CFBundleTypeIconFile': 'MyDocument.icns',
                'LSItemContentTypes': ['org.descios.config'],
                'LSHandlerRank': 'Owner'
            }
        ]
    },
)'''
    
    with open("descios_launcher.spec", "w") as f:
        f.write(spec_content)
    
    # Build with PyInstaller
    cmd = ["pyinstaller", "--clean", "--noconfirm", "descios_launcher.spec"]
    
    try:
        subprocess.check_call(cmd)
        print("✓ macOS app bundle built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False
    finally:
        # Clean up spec file
        if os.path.exists("descios_launcher.spec"):
            os.remove("descios_launcher.spec")

def create_dmg():
    """Create DMG package"""
    print("Creating DMG package...")
    
    app_path = "dist/DeSciOS Launcher.app"
    dmg_name = "DeSciOS-Launcher-0.1.0-macOS-x86_64.dmg"
    
    if not os.path.exists(app_path):
        print(f"✗ App bundle not found at {app_path}")
        return False
    
    # Create DMG using create-dmg
    cmd = [
        'create-dmg',
        '--volname', 'DeSciOS Launcher',
        '--window-pos', '200', '120',
        '--window-size', '600', '400',
        '--icon-size', '100',
        '--icon', 'DeSciOS Launcher.app', '175', '120',
        '--hide-extension', 'DeSciOS Launcher.app',
        '--app-drop-link', '425', '120',
        dmg_name,
        app_path
    ]
    
    try:
        subprocess.check_call(cmd)
        print(f"✓ DMG package created: {dmg_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ DMG creation failed: {e}")
        return False

def create_install_instructions():
    """Create installation instructions for macOS"""
    instructions = """DeSciOS Launcher - macOS Installation
=====================================

1. Download the DMG file
2. Double-click to mount the DMG
3. Drag "DeSciOS Launcher.app" to your Applications folder
4. Launch from Applications or Spotlight

Alternative installation:
- Right-click the app and select "Open" to bypass Gatekeeper
- Or run: sudo spctl --master-disable (not recommended)

Requirements:
- macOS 10.14 or later
- Python 3.6+ (included)
- Docker Desktop for Mac
- Git (for auto-clone feature)

Usage:
- Launch from Applications folder
- Or run from terminal: /Applications/DeSciOS\\ Launcher.app/Contents/MacOS/descios
"""
    
    with open("dist/MACOS_INSTALL.txt", "w") as f:
        f.write(instructions)

def main():
    """Main build function"""
    print("🍎 DeSciOS Launcher macOS Build System")
    print("=" * 40)
    
    # Check if we're on macOS
    check_macos()
    
    # Check if we're in the right directory
    if not os.path.exists("descios_launcher/main.py"):
        print("✗ Error: descios_launcher/main.py not found")
        print("Please run this script from the DeSciOS root directory")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Build the app
    if not build_macos_app():
        sys.exit(1)
    
    # Create DMG
    if not create_dmg():
        sys.exit(1)
    
    # Create installation instructions
    create_install_instructions()
    
    print("\n🎉 macOS build completed successfully!")
    print("Files created:")
    print("- dist/DeSciOS Launcher.app (App bundle)")
    print("- DeSciOS-Launcher-0.1.0-macOS.dmg (DMG package)")
    print("- dist/MACOS_INSTALL.txt (Installation instructions)")

if __name__ == "__main__":
    main() 