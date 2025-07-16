#!/usr/bin/env python3
"""
Master build script for DeSciOS Launcher
Builds binaries and packages for different platforms
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are available"""
    print("🔍 Checking prerequisites...")
    
    # Check if we're in the right directory
    if not Path("descios_launcher/main.py").exists():
        print("✗ Error: descios_launcher/main.py not found")
        print("Please run this script from the DeSciOS root directory")
        return False
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("✗ Error: Python 3.6 or later required")
        return False
    
    print("✓ Prerequisites check passed")
    return True

def build_binary():
    """Build the binary using build_launcher.py"""
    if not run_command([sys.executable, "build_launcher.py"], "Building binary"):
        return False
    
    # Verify binary was created
    platform_system = platform.system().lower()
    if platform_system == "linux":
        binary_path = Path("dist/descios")
    elif platform_system == "darwin":
        binary_path = Path("dist/descios.app")
    elif platform_system == "windows":
        binary_path = Path("dist/descios.exe")
    else:
        print(f"✗ Unsupported platform: {platform_system}")
        return False
    
    if not binary_path.exists():
        print(f"✗ Binary not found at {binary_path}")
        return False
    
    print(f"✓ Binary created: {binary_path}")
    return True

def build_deb_package():
    """Build .deb package for Ubuntu/Debian (Linux only)"""
    if platform.system().lower() != "linux":
        print("⚠️  .deb package building only supported on Linux")
        return True  # Not an error, just skip
    
    # Check if dpkg-deb is available
    if not shutil.which("dpkg-deb"):
        print("⚠️  dpkg-deb not found, skipping .deb package creation")
        print("Install with: sudo apt install dpkg-dev")
        return True  # Not an error, just skip
    
    return run_command([sys.executable, "build_deb.py"], "Building .deb package")

def create_release_info():
    """Create release information file"""
    print("\n📋 Creating release information...")
    
    system = platform.system()
    arch = platform.machine()
    
    release_info = f"""DeSciOS Launcher Build Release
===============================

Build Date: {subprocess.check_output(['date'], text=True).strip()}
Platform: {system} {platform.release()}
Architecture: {arch}
Python Version: {sys.version}

Files Created:
"""
    
    # List created files
    dist_dir = Path("dist")
    if dist_dir.exists():
        release_info += "\nBinaries:\n"
        for file in dist_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size
                release_info += f"  - {file.name} ({size:,} bytes)\n"
    
    # List packages
    deb_files = list(Path(".").glob("*.deb"))
    if deb_files:
        release_info += "\nPackages:\n"
        for deb_file in deb_files:
            size = deb_file.stat().st_size
            release_info += f"  - {deb_file.name} ({size:,} bytes)\n"
    
    release_info += f"""
Installation Instructions:
=========================

Linux (Ubuntu/Debian):
  # Using .deb package (recommended)
  sudo dpkg -i descios-launcher_*.deb
  sudo apt-get install -f  # Fix dependencies if needed
  
  # Or manual installation
  sudo cp dist/descios /usr/local/bin/
  sudo chmod +x /usr/local/bin/descios

macOS:
  # Copy to Applications (GUI apps)
  cp -r dist/descios.app /Applications/
  
  # Or copy to PATH for command line
  sudo cp dist/descios.app/Contents/MacOS/descios /usr/local/bin/descios

Windows:
  # Copy to desired location and add to PATH
  copy dist\\descios.exe C:\\Program Files\\DeSciOS\\
  # Add C:\\Program Files\\DeSciOS to your PATH environment variable

Usage:
======
  descios                    # Launch GUI
  descios --help            # Show help (if implemented)

Web Interface after deployment:
  http://localhost:6080/vnc.html

Support:
========
  GitHub: https://github.com/GizmoQuest/DeSciOS
  Issues: https://github.com/GizmoQuest/DeSciOS/issues
"""
    
    with open("RELEASE_INFO.txt", "w") as f:
        f.write(release_info)
    
    print("✓ Release information created: RELEASE_INFO.txt")

def main():
    """Main build orchestration function"""
    print("🚀 DeSciOS Launcher Master Build System")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Build binary
    if not build_binary():
        print("\n❌ Build failed at binary creation stage")
        sys.exit(1)
    
    # Build .deb package (Linux only)  
    if not build_deb_package():
        print("\n❌ Build failed at package creation stage")
        sys.exit(1)
    
    # Create release information
    create_release_info()
    
    print("\n🎉 Build completed successfully!")
    print("=" * 50)
    
    # Show summary
    print("\n📦 Build Summary:")
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    # List created files
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\nBinaries created:")
        for file in dist_dir.iterdir():
            if file.is_file():
                print(f"  - {file}")
    
    deb_files = list(Path(".").glob("*.deb"))
    if deb_files:
        print("\nPackages created:")
        for deb_file in deb_files:
            print(f"  - {deb_file}")
    
    print("\nSee RELEASE_INFO.txt for detailed installation instructions")

if __name__ == "__main__":
    main() 