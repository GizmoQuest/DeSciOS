# 🧬 DeSciOS

> *An open, browser-accessible scientific operating system — the foundation for decentralized, AI-powered research and collaboration.*

![DeSciOS](./os.svg)

---

## 🚀 Overview

**DeSciOS** is a containerized, headless Linux desktop environment purpose-built for decentralized science. Accessible entirely through a browser, it combines lightweight desktop streaming with research productivity tools and AI-readiness.

***Key goal**: Decentralize open source scientific software that remains trapped in centralized silos.*

Originally inspired by the idea of a Stadia-like environment, **DeSciOS** evolves that vision toward enabling:

- Local-first scientific computing
- AI-assisted research writing (LLM support coming soon)
- Peer-to-peer publishing workflows (IPFS support included)
- Modular scientific desktop environments for students, researchers, and citizen scientists

---

## ⚠️ Disclaimer

> ⚠️ **Experimental Project — Expect Rough Edges**

DeSciOS is currently under active development and remains **experimental**. It provides a proof-of-concept platform for future decentralized science infrastructure. While usable today, it is **not yet production-ready**.

You **might encounter**:
- Unpolished workflows
- GPU acceleration limitations (browser-dependent)
- Missing features like built-in LLMs
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
| **JupyterLab**    | Development notebook environment with BeakerX multi-language support |
| **RStudio**       | Full-featured R development environment                          |
| **Spyder**        | Scientific Python IDE                                            |
| **UGENE**         | Bioinformatics suite                                             |
| **ParaView**      | Scientific visualization tool                                    |
| **CellModeller**  | Multicellular modelling framework                                |
| **GNU Octave**    | MATLAB-like numerical computing                                  |
| **Fiji/ImageJ**   | Image processing and analysis                                    |
| **QGIS**          | Geographic Information System                                    |
| **Avogadro**      | Molecular modeling and visualization                             |
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
- 📁 **Persistent scientific workspace (home folder mountable)**
- 🧬 **Comprehensive scientific software suite**
- 📊 **Data analysis tools (R, Python, Octave)**
- 🔬 **Bioinformatics and cellular/molecular modeling**
- 🗺️ **Geospatial analysis with QGIS**
- 🖼️ **Image processing with Fiji/ImageJ**
- 📡 **Decentralized tools (IPFS, Syncthing)**
- 💰 **Cryptocurrency integration (Nano wallet)**
- 🔌 **Modular architecture for additional tools**

---

## 📁 File Structure

| File | Description |
|------|-------------|
| `Dockerfile` | Builds the full container with XFCE, noVNC, scientific tools, etc. |
| `startup.sh` | Entrypoint script for initializing the desktop environment |
| `supervisord.conf` | Orchestrates services like `vncserver`, `noVNC`, and `jupyterlab` |
| `xfce4-panel.xml` | Pre-configured XFCE panel layout |
| `os.svg` | DeSciOS branding/logo image |

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

> **Security Note**: For production use, always set a custom password during build using `--build-arg PASSWORD=your_secure_password`. The default password is for development purposes only.

---

## 💡 Vision: A Decentralized Research Desktop

DeSciOS is designed for:

* Students needing a portable research environment
* Scientists working offline or from remote labs
* Contributors to the DeSci India and global DeSci movement
* Educators seeking open, reproducible science infrastructure

Future integrations will enable:

* ✅ Local LLMs with Ollama and WebLLM
* ✅ Enhanced IPFS-based publishing and archiving
* ✅ Nano-based micropayments and research grant flows

> **Build open science tools. Host your own lab. Publish without gatekeepers.**

---

## ⚖️ License

This project is licensed under the **MIT License**.

> DeSciOS is free and open — built for the community, by the community.
