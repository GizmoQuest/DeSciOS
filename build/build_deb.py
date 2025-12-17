#!/usr/bin/env python3
"""
Build .deb package for DeSciOS Launcher on Ubuntu/Debian systems
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
import subprocess
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# Package information
PACKAGE_NAME = "descios-launcher"
PACKAGE_VERSION = "0.1.0"
PACKAGE_ARCH = "amd64"
MAINTAINER = "Avimanyu Bandyopadhyay <avimanyu786@gmail.com>"
DESCRIPTION = "GUI launcher for customizing and deploying DeSciOS scientific computing environments"

def create_package_structure(temp_dir):
    """Create the Debian package directory structure"""
    pkg_dir = Path(temp_dir) / f"{PACKAGE_NAME}_{PACKAGE_VERSION}_{PACKAGE_ARCH}"
    
    # Create directory structure
    dirs = [
        "DEBIAN",
        "usr/local/bin",
        "usr/share/applications",
        "usr/share/pixmaps",
        "usr/share/doc/descios-launcher"
    ]
    
    for dir_path in dirs:
        (pkg_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    return pkg_dir

def create_control_file(pkg_dir):
    """Create the DEBIAN/control file"""
    control_content = f"""Package: {PACKAGE_NAME}
Version: {PACKAGE_VERSION}
Section: science
Priority: optional
Architecture: {PACKAGE_ARCH}
Depends: python3, python3-tk, docker.io | docker-ce
Recommends: firefox | chromium-browser
Suggests: nvidia-container-toolkit
Maintainer: {MAINTAINER}
Description: {DESCRIPTION}
 DeSciOS Launcher provides an intuitive GUI for customizing DeSciOS builds.
 Users can select scientific applications, configure AI models, set user
 preferences, enable GPU support, and deploy customized DeSciOS instances
 with just a few clicks.
 .
 Features:
  - Application selection from comprehensive scientific software suite
  - Smart build system with automatic optimization
  - One-click deployment with automatic browser launch
  - GPU acceleration support for NVIDIA hardware
  - Configuration management and real-time build logging
Homepage: https://github.com/GizmoQuest/DeSciOS
"""
    
    control_file = pkg_dir / "DEBIAN" / "control"
    with open(control_file, "w") as f:
        f.write(control_content)
    
    # Set correct permissions
    control_file.chmod(0o644)

def create_desktop_file(pkg_dir):
    """Create the .desktop file for GUI integration"""
    desktop_content = """[Desktop Entry]
Name=DeSciOS Launcher
Comment=Customize and deploy DeSciOS scientific computing environments
Exec=descios
Icon=descios
Terminal=false
Type=Application
Categories=Science;Education;Development;
Keywords=docker;science;research;ai;launcher;
StartupNotify=true
"""
    
    desktop_file = pkg_dir / "usr/share/applications/descios-launcher.desktop"
    with open(desktop_file, "w") as f:
        f.write(desktop_content)
    
    desktop_file.chmod(0o644)

def create_icon(pkg_dir):
    """Create a simple icon for the application (placeholder)"""
    # For now, we'll create a simple SVG icon
    # In a real deployment, you'd want a proper icon file
    icon_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <rect width="48" height="48" rx="8" fill="#2563eb"/>
  <text x="24" y="30" font-family="monospace" font-size="14" font-weight="bold" 
        text-anchor="middle" fill="white">DS</text>
  <circle cx="12" cy="12" r="3" fill="#10b981"/>
  <circle cx="36" cy="12" r="3" fill="#f59e0b"/>
  <circle cx="36" cy="36" r="3" fill="#ef4444"/>
</svg>"""
    
    icon_file = pkg_dir / "usr/share/pixmaps/descios.svg"
    with open(icon_file, "w") as f:
        f.write(icon_content)
    
    icon_file.chmod(0o644)

def create_postinst_script(pkg_dir):
    """Create post-installation script"""
    postinst_content = """#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi

# Check if Docker is running and accessible
if command -v docker >/dev/null 2>&1; then
    if ! docker info >/dev/null 2>&1; then
        echo "Note: Docker is installed but not accessible. You may need to:"
        echo "  1. Start the Docker service: sudo systemctl start docker"
        echo "  2. Add your user to docker group: sudo usermod -aG docker $USER"
        echo "  3. Log out and back in for group changes to take effect"
    fi
else
    echo "Warning: Docker not found. DeSciOS Launcher requires Docker to function."
    echo "Install Docker using: sudo apt install docker.io"
fi

echo "DeSciOS Launcher installed successfully!"
echo "Run 'descios' to launch the GUI, or find it in your applications menu."

exit 0
"""
    
    postinst_file = pkg_dir / "DEBIAN/postinst"
    with open(postinst_file, "w") as f:
        f.write(postinst_content)
    
    postinst_file.chmod(0o755)

def create_prerm_script(pkg_dir):
    """Create pre-removal script"""
    prerm_content = """#!/bin/bash
set -e

# Nothing special needed for removal
exit 0
"""
    
    prerm_file = pkg_dir / "DEBIAN/prerm"
    with open(prerm_file, "w") as f:
        f.write(prerm_content)
    
    prerm_file.chmod(0o755)

def create_documentation(pkg_dir):
    """Create documentation files"""
    # Copyright file
    copyright_content = f"""Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: DeSciOS Launcher
Upstream-Contact: DeSciOS Team
Source: https://github.com/GizmoQuest/DeSciOS

Files: *
Copyright: {datetime.now().year} DeSciOS Team
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
"""
    
    copyright_file = pkg_dir / "usr/share/doc/descios-launcher/copyright"
    with open(copyright_file, "w") as f:
        f.write(copyright_content)
    
    copyright_file.chmod(0o644)
    
    # Changelog
    changelog_content = f"""descios-launcher ({PACKAGE_VERSION}) stable; urgency=medium

  * Initial release of DeSciOS Launcher
  * GUI application for customizing DeSciOS builds
  * Application selection and configuration management
  * One-click deployment with Docker integration
  * GPU acceleration support

 -- {MAINTAINER}  {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}
"""
    
    changelog_file = pkg_dir / "usr/share/doc/descios-launcher/changelog.Debian"
    with open(changelog_file, "w") as f:
        f.write(changelog_content)
    
    # Compress changelog
    subprocess.run(["gzip", "-9", str(changelog_file)], check=True)
    changelog_file.with_suffix(changelog_file.suffix + ".gz").chmod(0o644)

def copy_binary(pkg_dir):
    """Copy the DeSciOS binary to the package"""
    binary_src = Path("dist/descios")
    binary_dst = pkg_dir / "usr/local/bin/descios"
    
    if not binary_src.exists():
        raise FileNotFoundError(
            "Binary not found at dist/descios. "
            "Please run 'python3 build_launcher.py' first to build the binary."
        )
    
    shutil.copy2(binary_src, binary_dst)
    binary_dst.chmod(0o755)

def build_package(pkg_dir):
    """Build the .deb package"""
    # Use the new naming convention
    pkg_name = f"DeSciOS-Launcher-{PACKAGE_VERSION}-Linux-{PACKAGE_ARCH}.deb"
    
    # Build the package with temporary name
    temp_pkg_name = f"{PACKAGE_NAME}_{PACKAGE_VERSION}_{PACKAGE_ARCH}.deb"
    cmd = ["dpkg-deb", "--build", str(pkg_dir), temp_pkg_name]
    
    try:
        subprocess.run(cmd, check=True, cwd=pkg_dir.parent)
        print(f"✓ Package built successfully")
        
        # Move to current directory and rename
        shutil.move(str(pkg_dir.parent / temp_pkg_name), pkg_name)
        print(f"✓ Package available: {pkg_name}")
        
        return pkg_name
    except subprocess.CalledProcessError as e:
        print(f"✗ Package build failed: {e}")
        return None

def main():
    """Main package build function"""
    print("📦 DeSciOS Launcher .deb Package Builder")
    print("=" * 45)
    
    # Check if we have the binary
    if not Path("dist/descios").exists():
        print("✗ Error: Binary not found at dist/descios")
        print("Please run 'python3 build_launcher.py' first to build the binary.")
        sys.exit(1)
    
    # Check for required tools
    required_tools = ["dpkg-deb", "gzip"]
    for tool in required_tools:
        if shutil.which(tool) is None:
            print(f"✗ Error: Required tool '{tool}' not found")
            print("Please install debian package building tools:")
            print("  sudo apt install dpkg-dev gzip")
            sys.exit(1)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating package structure in {temp_dir}")
        
        # Create package structure
        pkg_dir = create_package_structure(temp_dir)
        print("✓ Package structure created")
        
        # Create package files
        create_control_file(pkg_dir)
        print("✓ Control file created")
        
        create_desktop_file(pkg_dir)
        print("✓ Desktop file created")
        
        create_icon(pkg_dir)
        print("✓ Icon created")
        
        create_postinst_script(pkg_dir)
        create_prerm_script(pkg_dir)
        print("✓ Installation scripts created")
        
        create_documentation(pkg_dir)
        print("✓ Documentation created")
        
        copy_binary(pkg_dir)
        print("✓ Binary copied")
        
        # Build the package
        pkg_name = build_package(pkg_dir)
        if pkg_name:
            print(f"\n🎉 .deb package created successfully!")
            print(f"Package: {pkg_name}")
            print("\nTo install:")
            print(f"  sudo dpkg -i {pkg_name}")
            print("  sudo apt-get install -f  # If there are dependency issues")
            print("\nTo remove:")
            print(f"  sudo apt remove {PACKAGE_NAME}")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main() 