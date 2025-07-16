#!/usr/bin/env python3
"""
Build script for creating DeSciOS Launcher EXE installer for Windows
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def check_windows():
    """Check if we're running on Windows"""
    if platform.system() != "Windows":
        print("Error: This script must be run on Windows")
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
    
    try:
        import pyyaml
        print("✓ PyYAML already installed")
    except ImportError:
        print("Installing PyYAML...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        print("✓ PyYAML installed")

def build_windows_exe():
    """Build the Windows EXE"""
    print("Building Windows EXE...")
    
    # Create spec file for Windows
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
    
    with open("descios_launcher.spec", "w") as f:
        f.write(spec_content)
    
    # Build with PyInstaller
    cmd = ["pyinstaller", "--clean", "--noconfirm", "descios_launcher.spec"]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Windows EXE built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False
    finally:
        # Clean up spec file
        if os.path.exists("descios_launcher.spec"):
            os.remove("descios_launcher.spec")

def create_installer():
    """Create Windows installer using NSIS or similar"""
    print("Creating Windows installer...")
    
    exe_path = "dist/DeSciOS Launcher.exe"
    installer_name = "DeSciOS-Launcher-0.1.0-Windows-x86_64.exe"
    
    if not os.path.exists(exe_path):
        print(f"✗ EXE not found at {exe_path}")
        return False
    
    # For now, we'll create a simple zip installer
    # In a full implementation, you'd use NSIS or Inno Setup
    import zipfile
    
    zip_name = "DeSciOS-Launcher-0.1.0-Windows-x86_64.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the EXE
        zipf.write(exe_path, "DeSciOS Launcher.exe")
        
        # Add installation instructions
        instructions = """DeSciOS Launcher - Windows Installation
========================================

1. Extract this ZIP file to a folder of your choice
2. Run "DeSciOS Launcher.exe" to start the application
3. Optionally create a desktop shortcut

Requirements:
- Windows 10 or later
- Python 3.6+ (included)
- Docker Desktop for Windows
- Git (for auto-clone feature)

Installation:
- Extract to C:\\Program Files\\DeSciOS\\ (recommended)
- Or extract to any folder and run from there

Usage:
- Double-click "DeSciOS Launcher.exe"
- Or run from command prompt: "DeSciOS Launcher.exe"

Troubleshooting:
- If you get a security warning, click "More info" then "Run anyway"
- Make sure Docker Desktop is running
- Ensure Git is installed and accessible from PATH
"""
        
        zipf.writestr("INSTALL.txt", instructions)
    
    print(f"✓ Windows package created: {zip_name}")
    return True

def create_install_instructions():
    """Create installation instructions for Windows"""
    instructions = """DeSciOS Launcher - Windows Installation
========================================

Quick Install:
1. Download the ZIP file
2. Extract to a folder (e.g., C:\\Program Files\\DeSciOS\\)
3. Run "DeSciOS Launcher.exe"

Requirements:
- Windows 10 or later
- Python 3.6+ (included in the package)
- Docker Desktop for Windows
- Git (for auto-clone feature)

Installation Steps:
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install Docker Desktop and restart your computer
3. Download Git from https://git-scm.com/download/win
4. Install Git with default settings
5. Extract this package and run "DeSciOS Launcher.exe"

Usage:
- Double-click the EXE file to launch
- The launcher will automatically find or clone DeSciOS
- Configure your scientific applications and deploy

Troubleshooting:
- If Windows Defender blocks the EXE, click "More info" then "Run anyway"
- Ensure Docker Desktop is running before using the launcher
- Check that Git is in your PATH: git --version
"""
    
    with open("dist/WINDOWS_INSTALL.txt", "w") as f:
        f.write(instructions)

def main():
    """Main build function"""
    print("🪟 DeSciOS Launcher Windows Build System")
    print("=" * 40)
    
    # Check if we're on Windows
    check_windows()
    
    # Check if we're in the right directory
    if not os.path.exists("descios_launcher/main.py"):
        print("✗ Error: descios_launcher/main.py not found")
        print("Please run this script from the DeSciOS root directory")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Build the EXE
    if not build_windows_exe():
        sys.exit(1)
    
    # Create installer
    if not create_installer():
        sys.exit(1)
    
    # Create installation instructions
    create_install_instructions()
    
    print("\n🎉 Windows build completed successfully!")
    print("Files created:")
    print("- dist/DeSciOS Launcher.exe (Executable)")
    print("- DeSciOS-Launcher-0.1.0-Windows.zip (Package)")
    print("- dist/WINDOWS_INSTALL.txt (Installation instructions)")

if __name__ == "__main__":
    main() 