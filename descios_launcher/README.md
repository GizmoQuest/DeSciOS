# DeSciOS Launcher

A GUI application for customizing DeSciOS Docker builds with an intuitive interface.

## Features

- **Application Selection**: Choose which scientific applications to include in your DeSciOS build
- **Ollama Model Configuration**: Customize which AI models to install
- **User Settings**: Configure username and VNC password
- **GPU Support**: Enable/disable GPU acceleration with automatic Docker command generation
- **Docker Build Integration**: Generate custom Dockerfiles and build images directly
- **One-Click Deployment**: Deploy and automatically launch DeSciOS with the Deploy button
- **Configuration Management**: Save and load your build configurations

## Usage

### Running the Launcher

```bash
python3 descios_launcher/main.py
```

### Tabs Overview

1. **Applications Tab**
   - Select which applications to install
   - Mandatory: DeSciOS Assistant, Font, and Python3-pip (always included)
   - Optional: All other scientific applications (JupyterLab is now truly optional!)
   - Use "Select All", "Select None", or "Reset to Defaults" buttons

2. **Settings Tab**
   - Configure Ollama AI models (one per line)
   - Set username and VNC password
   - Enable/disable GPU support for deployment
   - Default models: deepseek-r1:8b, minicpm-v:8b

3. **Build & Deploy Tab**
   - Set custom Docker image tag
   - Generate customized Dockerfile with essential Qt dependencies
   - Build Docker image with real-time logging
   - **Deploy!** - One-click deployment with automatic web interface launch
   - View GPU-aware deployment commands
   - Save/load configurations
   - Comprehensive build and deployment logs

### Available Applications

- **JupyterLab** - Interactive development environment for notebooks
- **R & RStudio** - Statistical computing language and IDE
- **Spyder** - Scientific Python IDE
- **UGENE** - Bioinformatics suite
- **GNU Octave** - MATLAB-compatible scientific computing
- **Fiji (ImageJ)** - Image processing and analysis
- **Nextflow** - Workflow management system
- **QGIS & GRASS GIS** - Geographic Information Systems
- **IPFS Desktop** - Decentralized file system GUI
- **Syncthing** - Continuous file synchronization
- **EtherCalc** - Collaborative spreadsheet (browser-based)
- **BeakerX** - Multi-language kernel extension for JupyterLab
- **NGL Viewer** - Molecular visualization (browser-based)
- **Remix IDE** - Ethereum development environment (browser-based)
- **Nault** - Nano cryptocurrency wallet (browser-based)
- **CellModeller** - Bacterial cell growth simulation

## Building and Deploying Custom DeSciOS

### Quick Start (Recommended)
1. Open the launcher: `python3 descios_launcher/main.py`
2. Select desired applications in the **Applications** tab
3. Configure settings in the **Settings** tab (enable GPU if available)
4. Go to **Build & Deploy** tab
5. Click **"Generate Dockerfile"** to create `Dockerfile.custom` (skip if using defaults)
6. Click **"Build Docker Image"** to build your custom image
7. Click **"Deploy!"** to automatically launch DeSciOS and open web interface

### Default Configuration Fast Track
If you want all applications with default settings:
1. Open the launcher (all applications are selected by default)
2. Go directly to **Build & Deploy** tab
3. Click **"Build Docker Image"** - it will automatically use the original `Dockerfile` for maximum speed
4. Click **"Deploy!"** when build completes

The launcher automatically detects when you're using the default configuration and builds directly from the original `Dockerfile`, skipping the custom generation step for faster builds.

### Manual Deployment
After building, you can also run manually:
```bash
# With GPU support
docker run -d --gpus all -p 6080:6080 --name descios your-custom-tag

# Without GPU
docker run -d -p 6080:6080 --name descios your-custom-tag
```

## Deploy Button Features

The **Deploy!** button provides one-click deployment with:

- **Smart GPU Detection**: Automatically uses `--gpus all` flag when GPU support is enabled
- **Container Management**: Stops and removes existing containers to prevent conflicts
- **Image Validation**: Checks if the Docker image exists before deployment
- **Automatic Launch**: Opens `http://localhost:6080/vnc.html` in your default browser
- **Status Logging**: Real-time deployment status and container information

## Intelligent Build System

The launcher features smart build detection:

- **Default Configuration**: Automatically uses the original `Dockerfile` for maximum speed when all default settings are detected
- **Custom Configuration**: Generates and uses `Dockerfile.custom` when any settings are modified
- **Real-time Detection**: Shows build status and which Dockerfile will be used
- **No Manual Steps**: Skip Dockerfile generation when using defaults - just click "Build Docker Image"

## GPU Support

DeSciOS supports GPU acceleration for scientific computing workloads:

### Requirements
- NVIDIA GPU with CUDA support
- NVIDIA Docker runtime installed
- Compatible GPU drivers

### Configuration
1. In the Settings tab, check "Enable GPU support"
2. The launcher will automatically generate Docker commands with `--gpus all` flag
3. GPU-enabled applications (like ML frameworks) will have access to GPU acceleration
4. The Deploy button respects GPU settings automatically

## Access DeSciOS

After deployment, access DeSciOS through:
- **Web Interface**: http://localhost:6080/vnc.html (automatically opened by Deploy button)
- **Direct VNC**: localhost:5901 (with configured password)

## Container Management

```bash
# Stop the container
docker stop descios

# Restart the container
docker start descios

# Remove the container
docker rm descios

# View logs
docker logs descios
```

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- Docker (for building images)
- xdg-open (for automatic web interface launch)

## Troubleshooting

### Qt Platform Plugin Issues
The launcher now automatically includes essential Qt dependencies to fix GUI application errors like:
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

### JupyterLab Not Installing
JupyterLab is now truly optional - it will only be included if explicitly selected in the Applications tab.

### GPU Support Not Working
Ensure you have:
- NVIDIA Container Toolkit installed
- Compatible GPU drivers
- GPU support enabled in Settings tab

## Installation in DeSciOS

The launcher will be automatically installed when building DeSciOS and available as "DeSciOS Launcher" in the applications menu. 