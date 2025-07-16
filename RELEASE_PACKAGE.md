# DeSciOS Launcher - Installation Guide

## 📦 Package Information

**Package Name**: `descios-launcher_0.1.0_amd64.deb`  
**Version**: 0.1.0  
**Architecture**: amd64  
**Size**: ~12.2 MB  
**Build Date**: July 16, 2025

## 🎯 What's Included

This Debian package contains:

- **DeSciOS Launcher Binary**: Self-contained executable (`/usr/local/bin/descios`)
- **Desktop Integration**: Application menu entry and icon
- **Documentation**: Copyright and changelog files
- **Installation Scripts**: Post-installation setup and dependency checks

## 🚀 Quick Install

```bash
# Install the package
sudo dpkg -i descios-launcher_0.1.0_amd64.deb

# Fix any dependency issues (if needed)
sudo apt-get install -f

# Launch DeSciOS
descios
```

### Verify Installation
```bash
# Check if binary is available
which descios

# Check version
descios --version
```

## 📋 System Requirements

### Required Dependencies
- **Python 3**: For runtime support
- **Python3-tk**: GUI toolkit
- **Docker**: Container runtime (docker.io or docker-ce)

### Recommended Dependencies
- **Web Browser**: Firefox or Chromium for accessing DeSciOS web interface
- **NVIDIA Container Toolkit**: For GPU acceleration (optional)

### Installation Commands
```bash
# Install required dependencies
sudo apt update
sudo apt install -y python3 python3-tk docker.io

# For GPU support (optional)
sudo apt install -y nvidia-container-toolkit
```

## 🔧 Usage

### Launching DeSciOS Launcher
```bash
# Command line
descios

# Or find it in your applications menu
# Applications → Science → DeSciOS Launcher
```

### What You Can Do
1. **Select Applications**: Choose which scientific tools to include
2. **Configure AI Models**: Set up Ollama models for AI assistance
3. **Customize Settings**: Set username, password, and GPU options
4. **Build & Deploy**: One-click Docker build and deployment
5. **Access DeSciOS**: Automatic browser launch to the scientific desktop

## 🧹 Uninstallation

```bash
# Remove the package
sudo apt remove descios-launcher

# Or completely purge (removes configuration files)
sudo apt purge descios-launcher
```

## 📁 Package Contents

```
/usr/local/bin/descios                    # Main executable
/usr/share/applications/descios-launcher.desktop  # Menu entry
/usr/share/pixmaps/descios.svg            # Application icon
/usr/share/doc/descios-launcher/          # Documentation
├── copyright                             # License information
└── changelog.Debian.gz                   # Package changelog
```

## 🔍 Troubleshooting

### Common Issues

**1. Docker Permission Issues**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

**2. GUI Not Starting**
```bash
# Check if tkinter is available
python3 -c "import tkinter; print('tkinter available')"

# Install if missing
sudo apt install python3-tk
```

**3. Binary Not Found**
```bash
# Check if binary exists
ls -la /usr/local/bin/descios

# Reinstall if needed
sudo dpkg -i descios-launcher_0.1.0_amd64.deb
```

### Logs and Debugging
```bash
# Run with verbose output
descios --verbose

# Check system logs
journalctl -u docker.service
```

## 🏗️ Building from Source

For developers who want to build their own package:

```bash
# Clone the repository
git clone https://github.com/GizmoQuest/DeSciOS.git
cd DeSciOS

# Set up build environment
python3 -m venv build_env
source build_env/bin/activate
pip install pyinstaller pyyaml

# Install packaging tools
sudo apt install dpkg-dev gzip

# Build everything
cd build
make release
```

## 📞 Support

- **GitHub Issues**: https://github.com/GizmoQuest/DeSciOS/issues
- **Documentation**: https://github.com/GizmoQuest/DeSciOS
- **Community**: DeSci India and global DeSci movement

## 📄 License

This package is licensed under the MIT License. See the copyright file in `/usr/share/doc/descios-launcher/copyright` for details.

---

**DeSciOS Launcher** - Empowering decentralized scientific computing through intuitive GUI deployment. 