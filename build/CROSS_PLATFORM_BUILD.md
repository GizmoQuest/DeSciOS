# Cross-Platform Build Guide

This guide explains how to build DeSciOS Launcher packages for Linux, macOS, and Windows.

## 🎯 Quick Start

### Linux (Debian/Ubuntu)
```bash
# Build .deb package
cd build
make deb
```

### macOS
```bash
# Build DMG package
cd build
make dmg
```

### Windows
```bash
# Build EXE package
cd build
make exe
```

## 📋 Prerequisites

### All Platforms
- Python 3.6 or later
- PyInstaller
- PyYAML

### Linux (Debian/Ubuntu)
- dpkg-dev
- gzip

### macOS
- Homebrew (for create-dmg)
- Xcode Command Line Tools

### Windows
- No additional tools required (uses built-in zip)

## 🔨 Build Process

### 1. Linux (.deb Package)

**Requirements:**
```bash
# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip dpkg-dev gzip

# Install Python packages
pip3 install pyinstaller pyyaml
```

**Build:**
```bash
cd build
make deb
```

**Output:**
- `descios-launcher_0.1.0_amd64.deb` - Debian package
- `dist/descios` - Binary executable

### 2. macOS (.app + DMG)

**Requirements:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install create-dmg
pip3 install pyinstaller pyyaml
```

**Build:**
```bash
cd build
make dmg
```

**Output:**
- `DeSciOS-Launcher-0.1.0-macOS.dmg` - DMG package
- `dist/DeSciOS Launcher.app` - App bundle

### 3. Windows (.exe + ZIP)

**Requirements:**
```bash
# Install Python packages
pip install pyinstaller pyyaml
```

**Build:**
```bash
cd build
make exe
```

**Output:**
- `DeSciOS-Launcher-0.1.0-Windows.zip` - ZIP package
- `dist/DeSciOS Launcher.exe` - Executable

## 📦 Package Contents

### Linux (.deb)
```
/usr/local/bin/descios                    # Main executable
/usr/share/applications/descios-launcher.desktop  # Menu entry
/usr/share/pixmaps/descios.svg            # Application icon
/usr/share/doc/descios-launcher/          # Documentation
```

### macOS (.app)
```
DeSciOS Launcher.app/
├── Contents/
│   ├── MacOS/descios                     # Main executable
│   ├── Info.plist                        # App metadata
│   └── Resources/                        # App resources
```

### Windows (.exe)
```
DeSciOS Launcher.exe                      # Self-contained executable
INSTALL.txt                               # Installation instructions
```

## 🚀 Installation

### Linux
```bash
sudo dpkg -i descios-launcher_0.1.0_amd64.deb
sudo apt-get install -f
descios
```

### macOS
1. Double-click DMG to mount
2. Drag app to Applications folder
3. Launch from Applications or Spotlight

### Windows
1. Extract ZIP file
2. Run `DeSciOS Launcher.exe`
3. Optionally create desktop shortcut

## 🔧 Advanced Build Options

### Custom Icons
Add icons to the build process:
- Linux: `descios.svg` in `build/` directory
- macOS: `descios.icns` in `build/` directory  
- Windows: `descios.ico` in `build/` directory

### Code Signing (macOS)
```bash
# Sign the app bundle
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/DeSciOS Launcher.app"

# Notarize (requires Apple Developer account)
xcrun altool --notarize-app --primary-bundle-id "org.descios.launcher" --username "your-email@example.com" --password "@env:APPLE_ID_PASSWORD" --file "DeSciOS-Launcher-0.1.0-macOS.dmg"
```

### Windows Installer (Advanced)
For a proper Windows installer, use NSIS or Inno Setup:

**NSIS Example:**
```nsi
!include "MUI2.nsh"

Name "DeSciOS Launcher"
OutFile "DeSciOS-Launcher-Setup.exe"
InstallDir "$PROGRAMFILES\DeSciOS"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\DeSciOS Launcher.exe"
    CreateDirectory "$SMPROGRAMS\DeSciOS"
    CreateShortCut "$SMPROGRAMS\DeSciOS\DeSciOS Launcher.lnk" "$INSTDIR\DeSciOS Launcher.exe"
    CreateShortCut "$DESKTOP\DeSciOS Launcher.lnk" "$INSTDIR\DeSciOS Launcher.exe"
SectionEnd
```

## 🧪 Testing

### Test Installation
```bash
# Linux
descios --version

# macOS
/Applications/DeSciOS\ Launcher.app/Contents/MacOS/descios --version

# Windows
"DeSciOS Launcher.exe" --version
```

### Test Auto-clone Feature
```bash
# Move DeSciOS directory temporarily
mv ~/DeSciOS ~/DeSciOS_backup

# Run launcher - should auto-clone
descios

# Restore directory
mv ~/DeSciOS_backup ~/DeSciOS
```

## 🐛 Troubleshooting

### Common Issues

**PyInstaller Build Failures:**
```bash
# Clear PyInstaller cache
rm -rf ~/.cache/pyinstaller/

# Reinstall PyInstaller
pip uninstall pyinstaller
pip install pyinstaller
```

**Missing Dependencies:**
```bash
# Install all dependencies
pip install pyinstaller pyyaml
```

**macOS DMG Creation:**
```bash
# Install create-dmg
brew install create-dmg

# Check if Homebrew is in PATH
echo $PATH | grep -q /opt/homebrew/bin
```

**Windows EXE Issues:**
```bash
# Check Python installation
python --version

# Install Visual C++ Redistributable if needed
# Download from Microsoft website
```

## 📋 Build Checklist

Before releasing:

- [ ] All platforms build successfully
- [ ] Auto-clone feature works on all platforms
- [ ] GUI launches without errors
- [ ] Dependencies are properly bundled
- [ ] Installation instructions are clear
- [ ] Package sizes are reasonable
- [ ] Version numbers are consistent

## 🎉 Release Process

1. **Build all platforms:**
   ```bash
   # Linux
   make deb
   
   # macOS  
   make dmg
   
   # Windows
   make exe
   ```

2. **Test packages:**
   - Install on clean systems
   - Test auto-clone functionality
   - Verify GUI works correctly

3. **Create release:**
   - Upload packages to GitHub Releases
   - Write release notes
   - Tag the release

---

**DeSciOS Launcher** - Cross-platform scientific computing deployment made easy! 