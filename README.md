# 🧬 DeSciOS

> *An open, browser-accessible scientific operating system — the foundation for decentralized, AI-powered research and collaboration.*

![DeSciOS](./os.svg)

---

## 🚀 Overview

**DeSciOS** is a containerized, headless Linux desktop environment purpose-built for decentralized science. Accessible entirely through a browser, it combines lightweight desktop streaming with research productivity tools and AI-readiness.

Originally inspired by the idea of a Stadia-like environment, **DeSciOS** evolves that vision toward enabling:

- Local-first scientific computing
- AI-assisted research writing (LLM support coming soon)
- Peer-to-peer publishing workflows (IPFS support planned)
- Modular scientific desktop environments for students, researchers, and citizen scientists

---

## ⚠️ Disclaimer

> ⚠️ **Experimental Project — Expect Rough Edges**

DeSciOS is currently under active development and remains **experimental**. It provides a proof-of-concept platform for future decentralized science infrastructure. While usable today, it is **not yet production-ready**.

You **might encounter**:
- Unpolished workflows
- GPU acceleration limitations (browser-dependent)
- Missing features like built-in LLMs or decentralized publishing
- Manual setup requirements

That said, it's ready for contributors, educators, and DeSci enthusiasts eager to shape open research infrastructure.

---

## 📦 What's Inside

| Component        | Description                                                      |
|------------------|------------------------------------------------------------------|
| **XFCE4**         | Lightweight desktop environment with customized layout           |
| **TigerVNC**      | VNC server to expose the XFCE desktop                            |
| **noVNC + Websockify** | Enables browser-based access via WebSocket                     |
| **JupyterLab**    | Optional development notebook environment                        |
| **Supervisor**    | Process manager for keeping all services alive                  |
| **Dockerized**    | Fully containerized for reproducibility and portability         |

> ℹ️ **Note**: IPFS and Ollama integrations are planned for future releases.

---

## 🛠️ Features

- 🌐 **Full Linux desktop streaming from any modern browser**
- 📁 **Persistent scientific workspace (home folder mountable)**
- 🧠 **Future-ready for integrating LLMs (e.g., Ollama, WebLLM)**
- 📡 **Designed with decentralized science publishing in mind (e.g., IPFS)**
- 🔌 **Modular architecture to add VS Code, Gradio, or other tools**

---

## 📁 File Structure

| File | Description |
|------|-------------|
| `Dockerfile` | Builds the full container with XFCE, noVNC, JupyterLab, etc. |
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

# Build the Docker image
docker build -t descios .

# Run the container
docker run -d -p 6080:6080 -p 8888:8888 -e JUPYTER_TOKEN=1234 --name desci-lab descios
````

Access via:

* 🌐 `http://localhost:6080` → Full Linux desktop in browser (default password: `1234`)
* 🧪 `http://localhost:8888` → JupyterLab interface (optional)

---

## 💡 Vision: A Decentralized Research Desktop

DeSciOS is designed for:

* Students needing a portable research environment
* Scientists working offline or from remote labs
* Contributors to the DeSci India and global DeSci movement
* Educators seeking open, reproducible science infrastructure

Future integrations will enable:

* ✅ Local LLMs with Ollama and WebLLM
* ✅ IPFS-based publishing and archiving
* ✅ Nano-based micropayments and research grant flows

> **Build open science tools. Host your own lab. Publish without gatekeepers.**

---

## ⚖️ License

This project is licensed under the **MIT License**.

> DeSciOS is free and open — built for the community, by the community.
