# 🧬 DeSciOS

> *An open, browser-accessible scientific operating system — the foundation for decentralized, AI-powered research and collaboration.*

![DeSciOS](./os.svg)

---

## 🚀 Overview

**DeSciOS** is a containerized, headless Linux desktop environment purpose-built for decentralized science. Accessible entirely through a browser, it combines lightweight desktop streaming with research productivity tools and AI-readiness.

***Key goal**: Decentralize open source scientific software that remains trapped in centralized silos.*

Originally inspired by the idea of a Stadia-like environment, **DeSciOS** evolves that vision toward enabling:

- Local-first scientific computing
- AI-assistance (with Ollama and DeepSeek-R1:8B model)
- Peer-to-peer workflows (IPFS support included)
- Modular scientific desktop environments for students, researchers, and citizen scientists

---

## ⚠️ Disclaimer

> ⚠️ **Experimental Project — Expect Rough Edges**

DeSciOS is currently under active development and remains **experimental**. It provides a proof-of-concept platform for future decentralized science infrastructure. While usable today, it is **not yet production-ready**.

You **might encounter**:
- Unpolished workflows
- GPU acceleration limitations (browser-dependent)
- Manual setup requirements

That said, it's ready for contributors, educators, and DeSci enthusiasts eager to shape open research infrastructure.

---

## 📦 What's Inside

| Component        | Description                                                      |
|------------------|------------------------------------------------------------------|
| **XFCE4**         | Lightweight desktop environment with customized layout           |
| **OpenCL**        | Critical for accelerated computing in diverse scientific tools   |
| **TigerVNC**      | VNC server to expose the XFCE desktop                            |
| **noVNC + Websockify** | Enables browser-based access via WebSocket                     |
| **DeSciOS Assistant** | Native GTK chat interface with Ollama integration for AI assistance |
| **JupyterLab**    | Development notebook environment with BeakerX multi-language support |
| **RStudio**       | Full-featured R development environment                          |
| **Spyder**        | Scientific Python IDE                                            |
| **UGENE**         | Bioinformatics suite                                             |
| **CellModeller**  | Multicellular modelling framework                                |
| **GNU Octave**    | MATLAB-like numerical computing                                  |
| **Fiji/ImageJ**   | Image processing and analysis                                    |
| **QGIS**          | Geographic Information System                                    |
| **GRASS GIS**     | Geographic Information System with full GUI support              |
| **Nextflow**      | Workflow management system for reproducible research             |
| **NGL Viewer**    | Molecular visualization tool (browser-based)                    |
| **IPFS Desktop**  | Decentralized file system interface                              |
| **Syncthing**     | P2P file synchronization                                         |
| **EtherCalc**     | Collaborative spreadsheet                                        |
| **Remix IDE**     | Ethereum development environment                                 |
| **Nault**         | Nano cryptocurrency wallet                                       |
| **Supervisor**    | Process manager for keeping all services alive                  |
| **Dockerized**    | Fully containerized for reproducibility and portability         |

---

## 🛠️ Features

- 🌐 **Full Linux desktop streaming from any modern browser**
- 🤖 **Native AI assistant with dual-model Ollama integration (DeepSeek-R1:8B for text, MiniCPM-V:8B for vision) with automatic screenshot analysis capabilities**
- 📁 **Persistent scientific workspace (home folder mountable)**
- 🧬 **Comprehensive scientific software suite**
- 📊 **Data analysis tools (R, Python, Octave)**
- 🔬 **Bioinformatics and cellular/molecular modeling**
- 🗺️ **Geospatial analysis with QGIS and GRASS GIS**
- 🖼️ **Image processing with Fiji/ImageJ**
- 📡 **Decentralized tools (IPFS, Syncthing)**
- 💰 **Cryptocurrency integration (Nano wallet)**
- 🔍 **Web search and tool discovery capabilities**
- 🔌 **Modular architecture for additional tools**
- 🧪 **Workflow management with Nextflow**
- 🧬 **Molecular visualization with NGL Viewer**

---

## 📁 File Structure

| File | Description |
|------|-------------|
| `Dockerfile` | Builds the full container with XFCE, noVNC, scientific tools, etc. |
| `startup.sh` | Entrypoint script for initializing the desktop environment |
| `supervisord.conf` | Orchestrates services like `vncserver`, `noVNC`, and `jupyterlab` |
| `xfce4-panel.xml` | Pre-configured XFCE panel layout |
| `os.svg` | DeSciOS branding/logo image |
| `descios_assistant/` | DeSciOS Assistant application directory |
| `descios_assistant/main.py` | GTK-based chat interface with Ollama integration |
| `descios_assistant/requirements.txt` | Python dependencies for the assistant |
| `descios_assistant/descios-assistant.desktop` | Desktop entry for the assistant |
| `descios_launcher/` | DeSciOS Launcher application directory |
| `descios_launcher/main.py` | GUI for customizing DeSciOS Docker builds |
| `descios_launcher/README.md` | Detailed launcher documentation |
| `descios_launcher/requirements.txt` | Launcher dependencies (uses Python standard library) |

---

## 🧑‍🔬 DeSciOS Assistant

**DeSciOS Assistant** is a native GTK application that provides AI-powered assistance within the DeSciOS environment. It features:

- **Dual-Model Ollama Integration**: Connects to local Ollama instance with DeepSeek-R1:8B for text responses and MiniCPM-V:8B for vision analysis
- **Vision Capabilities**: Desktop screenshot analysis with intelligent image resizing (1920x1080 → 1344x1344) for visual context understanding
- **Scientific Context**: Aware of DeSciOS environment and available tools
- **Web Search**: Can search and summarize web content for research queries using Brave search
- **Tool Discovery**: Scans and reports installed scientific software from system directories
- **Modern UI**: Clean, responsive interface with Orbitron font and dark theme support
- **Conversation Memory**: Maintains context across multiple interactions
- **Real-time Updates**: Dynamic message updates with WebKit-based rendering

### Assistant Capabilities

- Answer questions about DeSciOS and its components
- Help with scientific computing workflows
- Search the web for research information
- List available tools and software
- Provide guidance on using scientific applications
- Assist with data analysis and visualization tasks
- Analyze desktop screenshots and visual content using computer vision
- Identify and explain scientific visualizations, plots, and interface elements
- Support for markdown rendering in responses

---

## 🚀 DeSciOS Launcher

**DeSciOS Launcher** is a comprehensive GUI application that allows users to customize their DeSciOS builds with an intuitive interface. Instead of manually editing Dockerfiles, users can now select applications, configure settings, and deploy customized DeSciOS instances with just a few clicks.

### Launcher Features

- **Application Selection**: Choose which scientific applications to include in your build from the full suite
- **Smart Build System**: Automatically uses the original Dockerfile for default configurations (faster builds) or generates custom Dockerfiles when needed
- **Ollama Model Configuration**: Customize which AI models to install and configure
- **User Settings**: Set custom username and VNC password for your instance
- **GPU Support**: Enable/disable GPU acceleration with automatic Docker command generation
- **One-Click Deployment**: Build and deploy DeSciOS with automatic web interface launch
- **Configuration Management**: Save and load your build configurations
- **Real-time Build Logging**: Monitor Docker build progress with live output

### Quick Start with Launcher

```bash
# Clone the repo
git clone https://github.com/GizmoQuest/DeSciOS.git
cd DeSciOS

# Install launcher dependencies (for custom app support)
pip install -r descios_launcher/requirements.txt

# Launch the GUI customizer
python3 descios_launcher/main.py
```

1. **Applications Tab**: Select which scientific tools to include (all enabled by default)
2. **Custom Apps Tab**: Create and manage your own custom applications using templates or plugins
3. **Settings Tab**: Configure AI models, username, password, and GPU support  
4. **Build & Deploy Tab**: Generate custom builds and deploy with one click

The launcher automatically detects default configurations and uses the optimized build path for faster deployment.

### Available Applications via Launcher

The launcher allows you to customize which applications are included:

- **Core Components** (always included): DeSciOS Assistant, Python3, system fonts
- **Development**: JupyterLab, Spyder, BeakerX multi-language kernels
- **Data Science**: R & RStudio, GNU Octave
- **Bioinformatics**: UGENE, CellModeller bacterial simulation
- **Image Processing**: Fiji/ImageJ  
- **Geospatial**: QGIS, GRASS GIS
- **Workflows**: Nextflow pipeline manager
- **Decentralized Tools**: IPFS Desktop, Syncthing
- **Web-based Tools**: EtherCalc, NGL Viewer, Remix IDE, Nault wallet

### 🧩 Custom Applications & Extensibility

**For Researchers**: Easily add your own tools and applications!

- **Template-based Builder**: Use pre-built templates for common installation patterns
- **Plugin System**: Load applications from external YAML/JSON files  
- **Community Plugins**: Share and discover applications from other researchers
- **Installation Templates**:
  - Python packages (pip install)
  - System packages (apt install) 
  - GitHub releases and tarballs
  - Web application shortcuts
  - Custom Dockerfile commands

**Example Plugin Structure:**
```
descios_plugins/
├── my_research_tools.yaml
├── bioinformatics_extras.yaml
└── python_data_science.yaml
```

The launcher includes example plugins and comprehensive documentation in the `descios_plugins/` directory.

---

## 📋 System Requirements

### Minimum Requirements

- **Operating System**: Linux, macOS, or Windows with Docker support
- **RAM**: 4GB minimum, 8GB+ recommended for scientific workloads
- **Storage**: 10GB+ free disk space for Docker images and data
- **Network**: Internet connection for initial setup and package downloads

### Required Software

#### For DeSciOS Launcher
- **Python**: 3.6 or later
- **tkinter**: GUI toolkit (usually included with Python)
- **Docker**: 20.10 or later for container management
- **xdg-open** (Linux/macOS): For automatic browser launching

#### For DeSciOS Container
- **Docker**: 20.10 or later with BuildKit support
- **Docker Buildx**: For multi-platform builds (included in recent Docker versions)
- **Modern Web Browser**: Chrome, Firefox, Safari, or Edge for accessing the desktop interface

### Optional Requirements

#### GPU Acceleration (NVIDIA only)
- **NVIDIA GPU**: CUDA-compatible graphics card
- **NVIDIA Container Toolkit**: For Docker GPU access
- **NVIDIA Drivers**: 450.80.02+ or compatible with your GPU
- **CUDA**: 11.0+ (installed automatically in container)

#### Performance Recommendations
- **Multi-core CPU**: 4+ cores recommended for scientific computing
- **SSD Storage**: For faster Docker builds and data processing
- **16GB+ RAM**: For memory-intensive scientific applications

### Installation Prerequisites

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Python and tkinter (if not already installed)
sudo apt install -y python3 python3-tk

# For GPU support (optional)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

#### macOS
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Python 3 is usually pre-installed, tkinter included

# Verify installations
python3 --version
docker --version
```

#### Windows
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Install Python 3 from https://www.python.org/downloads/
# tkinter is included with Python on Windows

# Verify installations in PowerShell or Command Prompt
python --version
docker --version
```

### Browser Requirements

DeSciOS is accessed through a web browser using noVNC. Supported browsers:
- **Chrome/Chromium**: 88+ (recommended for best performance)
- **Firefox**: 85+ 
- **Safari**: 14+
- **Edge**: 88+

### Network Configuration

- **Port 6080**: HTTP access to noVNC interface
- **Port 5901**: Direct VNC access (optional)
- **Firewall**: Ensure ports are accessible if accessing from remote machines

---

## 🧪 Quick Start

### Option 1: GUI Launcher (Recommended)

```bash
# Clone the repo
git clone https://github.com/GizmoQuest/DeSciOS.git
cd DeSciOS

# Launch the GUI customizer
python3 descios_launcher/main.py
```

Use the intuitive GUI to:
- Select which applications to include
- Configure AI models and settings
- Build and deploy with one click
- Automatically launch in your browser

### Option 2: Manual Docker Build

```bash
# Clone the repo
git clone https://github.com/GizmoQuest/DeSciOS.git
cd DeSciOS

# Build the Docker image (with custom password)
docker buildx build --build-arg PASSWORD=your_secure_password -t descios .

# Or build with default password (not recommended for production)
docker build -t descios .

# Run the container
docker run -d -p 6080:6080 --name desci-lab descios

# If you have NVIDIA GPU(s) (Optional)
docker run -d --gpus all -p 6080:6080 --name desci-lab descios
```

### Access DeSciOS

* 🌐 `http://localhost:6080/vnc.html` → Full Linux desktop in browser (use the password you set during build)

> **Security Note**: For production use, always set a custom password during build using `--build-arg PASSWORD=your_secure_password`. The default password `vncpassword` is for development purposes only.

---

## 💡 Vision: A Decentralized Research Desktop

DeSciOS is designed for:

* Students needing a portable research environment
* Scientists working offline or from remote labs
* Contributors to the DeSci India and global DeSci movement
* Educators seeking open, reproducible science infrastructure

> **Build open science tools the decentralized way. Host your own lab. Publish without gatekeepers.**

---

## ⚖️ License

This project is licensed under the **MIT License**.

> DeSciOS is free and open — built for the community, by the community.
