# DeSciOS Launcher Build Guide

This guide explains how to build platform-specific binaries and packages for the DeSciOS Launcher.

## 🎯 Quick Start

### Using Make (Recommended)
```bash
# Install dependencies
make deps

# Build everything (binary + package + release info)
make release

# Install system-wide
make install
```

### Manual Process
```bash
# Build binary
python3 build_launcher.py

# Build .deb package (Linux only)
python3 build_deb.py

# Or build everything
python3 build_all.py
```

## 📋 Prerequisites

### All Platforms
- Python 3.6 or later
- tkinter (usually included with Python)
- PyInstaller (installed automatically)

### Linux (Ubuntu/Debian)
```bash
# Essential packages
sudo apt update
sudo apt install -y python3 python3-tk python3-pip

# For .deb package building
sudo apt install -y dpkg-dev gzip

# Install build dependencies
make deps  # or: pip3 install pyinstaller
```

### macOS
```bash
# Python is usually pre-installed
# Install PyInstaller
pip3 install pyinstaller

# Homebrew alternative
brew install python-tk
```

### Windows
```powershell
# Install Python from python.org (includes tkinter)
# Install PyInstaller
pip install pyinstaller
```

## 🔨 Build Process

### 1. Binary Creation (`build_launcher.py`)

Creates platform-specific binaries using PyInstaller:

**Linux**: `dist/descios`  
**macOS**: `dist/descios.app`  
**Windows**: `dist/descios.exe`

Features:
- Single executable with all dependencies
- GUI application (no console window)
- Includes launcher documentation
- UPX compression for smaller size
- Platform-specific optimizations

### 2. Package Creation (`build_deb.py`)

Creates `.deb` package for Ubuntu/Debian systems:

**Output**: `descios-launcher_0.1.0_amd64.deb`

Package includes:
- Binary installation to `/usr/local/bin/descios`
- Desktop entry for applications menu
- Icon and documentation
- Dependency management (python3, python3-tk, docker.io)
- Post-installation scripts for setup
- Proper Debian package structure

### 3. Complete Build (`build_all.py`)

Orchestrates the entire build process:
- Checks prerequisites
- Builds binary
- Creates package (Linux only)
- Generates release information
- Provides installation instructions

## 📦 Package Details

### .deb Package Structure
```
descios-launcher_1.0.0_amd64.deb
├── DEBIAN/
│   ├── control           # Package metadata
│   ├── postinst         # Post-installation script
│   └── prerm            # Pre-removal script
├── usr/local/bin/
│   └── descios          # Main binary
├── usr/share/applications/
│   └── descios-launcher.desktop  # GUI menu entry
├── usr/share/pixmaps/
│   └── descios.svg      # Application icon
└── usr/share/doc/descios-launcher/
    ├── copyright        # License information
    └── changelog.Debian.gz  # Package changelog
```

### Dependencies
- **Required**: python3, python3-tk, docker.io | docker-ce
- **Recommended**: firefox | chromium-browser
- **Suggested**: nvidia-container-toolkit

## 🚀 Installation Methods

### Ubuntu/Debian (.deb package)
```bash
# Install package
sudo dpkg -i descios-launcher_0.1.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

# Verify installation
descios --version
```

### Linux (Manual)
```bash
# Copy binary
sudo cp dist/descios /usr/local/bin/
sudo chmod +x /usr/local/bin/descios

# Verify
descios --version
```

### macOS
```bash
# GUI application
cp -r dist/descios.app /Applications/

# Command line (optional)
sudo cp dist/descios.app/Contents/MacOS/descios /usr/local/bin/descios
```

### Windows
```cmd
# Copy to Program Files
copy dist\descios.exe "C:\Program Files\DeSciOS\"

# Add to PATH (optional)
# Add C:\Program Files\DeSciOS to your PATH environment variable
```

## 🧹 Maintenance

### Clean Build Artifacts
```bash
make clean
# or manually:
rm -rf dist/ build/ *.spec *.deb RELEASE_INFO.txt
```

### Update Version
Update version numbers in:
- `build_deb.py` → `PACKAGE_VERSION`
- `descios_launcher/main.py` → `version=` in argparse

### Rebuild After Changes
```bash
make clean
make release
```

## 🔧 Make Targets

| Target | Description |
|--------|-------------|
| `all` | Build binary and package (default) |
| `binary` | Build binary only |
| `package` | Build binary and package |
| `release` | Complete build with release info |
| `deb` | Build .deb package only |
| `install` | Install launcher system-wide |
| `uninstall` | Remove launcher from system |
| `clean` | Clean build artifacts |
| `deps` | Install build dependencies |
| `run` | Run the launcher (binary or source) |
| `help` | Show available targets |

## 🐛 Troubleshooting

### PyInstaller Issues
```bash
# Clear PyInstaller cache
rm -rf ~/.cache/pyinstaller/

# Reinstall PyInstaller
pip3 uninstall pyinstaller
pip3 install pyinstaller
```

### tkinter Not Found
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS (Homebrew)
brew install python-tk
```

### Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### .deb Build Failures
```bash
# Install packaging tools
sudo apt install dpkg-dev gzip

# Check file permissions
chmod +x build_deb.py
```

## 📋 Build Requirements Summary

| Platform | Binary Size | Build Time | Dependencies |
|----------|-------------|------------|--------------|
| Linux | ~15-20 MB | 30-60s | python3, python3-tk, pyinstaller |
| macOS | ~20-25 MB | 45-75s | python3, pyinstaller |
| Windows | ~20-30 MB | 60-90s | python3, pyinstaller |

## 🎉 Success Indicators

After successful build, you should see:
- ✅ Binary in `dist/` directory
- ✅ `.deb` package in root directory (Linux)
- ✅ `RELEASE_INFO.txt` with instructions
- ✅ No error messages in build output

Test the binary:
```bash
./dist/descios --version
# Should show: DeSciOS Launcher 1.0.0
```

## 📞 Support

If you encounter issues:
1. Check this documentation
2. Clean build artifacts: `make clean`
3. Verify prerequisites are installed
4. Check GitHub issues: https://github.com/GizmoQuest/DeSciOS/issues
5. Create new issue with build logs 