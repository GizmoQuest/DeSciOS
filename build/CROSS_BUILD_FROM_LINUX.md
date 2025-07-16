# Building DMG and EXE from Linux

This guide explains how to build macOS DMG and Windows EXE packages directly from Linux using Docker.

## 🎯 Quick Start

```bash
# Build all platforms from Linux
cd build
make cross

# Or run directly
python3 build_simple_cross.py
```

## 📋 Requirements

- **Linux system** (Ubuntu/Debian recommended)
- **Docker** installed and running
- **Python 3.6+** with pip

## 🔧 Setup

### Install Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io
sudo usermod -aG docker $USER

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Log out and back in for group changes
```

### Verify Setup
```bash
# Check Docker
docker --version
docker run hello-world

# Check Python
python3 --version
pip3 --version
```

## 🚀 Build Process

### Option 1: Using Make
```bash
cd build
make cross
```

### Option 2: Direct Script
```bash
cd build
python3 build_simple_cross.py
```

### Option 3: Individual Platforms
```bash
# Build macOS only
python3 build_simple_cross.py macos

# Build Windows only  
python3 build_simple_cross.py windows
```

## 📦 Output Files

After successful build, you'll get:

### macOS Package
- `DeSciOS-Launcher-0.1.0-macOS.zip`
- Contains: `DeSciOS Launcher.app/` + installation instructions

### Windows Package
- `DeSciOS-Launcher-0.1.0-Windows.zip`
- Contains: `DeSciOS Launcher.exe` + installation instructions

## 🔍 How It Works

1. **Docker Containers**: Uses Python Docker images for each platform
2. **PyInstaller**: Cross-compiles the Python application
3. **Volume Mounting**: Shares source code and output directories
4. **Package Creation**: Creates ZIP packages with installation instructions

## ⚠️ Limitations

### Cross-Compilation Limitations
- **macOS**: Cannot create proper DMG files (uses ZIP instead)
- **Windows**: May have compatibility issues with some libraries
- **Performance**: Cross-compiled binaries may be larger
- **Compatibility**: Some platform-specific features may not work

### Recommended Approach
For production releases, build on native platforms:
- **macOS**: Use `make dmg` on a Mac
- **Windows**: Use `make exe` on Windows
- **Linux**: Use `make deb` on Linux

## 🧪 Testing

### Test the Build Process
```bash
# Clean previous builds
make clean

# Build cross-platform
make cross

# Check output files
ls -la *.zip
ls -la dist/
```

### Test Packages (if possible)
```bash
# Extract and test macOS package
unzip DeSciOS-Launcher-0.1.0-macOS.zip
# Test on macOS system

# Extract and test Windows package  
unzip DeSciOS-Launcher-0.1.0-Windows.zip
# Test on Windows system
```

## 🐛 Troubleshooting

### Docker Issues
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check Docker permissions
groups $USER | grep docker
```

### Build Failures
```bash
# Clean Docker images
docker system prune -a

# Check available disk space
df -h

# Check Docker logs
docker logs <container_id>
```

### Memory Issues
```bash
# Increase Docker memory limit
# Edit /etc/docker/daemon.json
{
  "memory": "4g"
}

# Restart Docker
sudo systemctl restart docker
```

## 📋 Build Checklist

Before releasing cross-platform builds:

- [ ] Docker is running and accessible
- [ ] All platforms build successfully
- [ ] Package files are created
- [ ] Installation instructions are included
- [ ] File sizes are reasonable
- [ ] Test on target platforms (if possible)

## 🎉 Success Indicators

### Successful Build Output
```
🌍 DeSciOS Launcher Cross-Platform Build (Linux)
==================================================

Building for macos...
✓ macos build completed
✓ Created DeSciOS-Launcher-0.1.0-macOS.zip

Building for windows...
✓ windows build completed  
✓ Created DeSciOS-Launcher-0.1.0-Windows.zip

==================================================
Build Summary:
  macos: ✓ Success
  windows: ✓ Success

🎉 Cross-platform build completed!
```

### Generated Files
```
DeSciOS-Launcher-0.1.0-macOS.zip     # macOS package
DeSciOS-Launcher-0.1.0-Windows.zip   # Windows package
dist/                                 # Build artifacts
```

---

**Note**: Cross-platform builds are convenient but may have limitations. For best results and full compatibility, build on the target platform when possible. 