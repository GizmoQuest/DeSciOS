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

## 🧪 Quick Start (Local Docker)

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

Access via:

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
