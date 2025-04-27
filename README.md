# 🌐 Xadia

> *A lightweight, browser-accessible desktop streaming environment — the first step toward an open-source alternative to [Google Stadia](https://stadia.google.com/gg/), which was shut down on January 18, 2023.*

![Xadia](./os.svg)



## 🚀 Overview

**Xadia** is a containerized, headless desktop environment designed for remote accessibility via web browsers. Built on XFCE, noVNC, and supervised with `supervisord`, it provides a fully interactive Linux GUI experience accessible anywhere — no physical monitor required.

It’s ideal for:

- Remote access to graphical applications
- Teaching or training environments
- Lightweight game streaming
- Cloud desktop experiments
- The foundations of a decentralized Stadia-like system

---

## ⚠️ Disclaimer

> ⚠️ **Experimental Project — Expect Rough Edges**

Xadia OS is in its earliest phase of development and is currently highly **experimental**. While it lays the groundwork for a future open-source streaming OS, this release should **not** be considered production-ready or feature-complete.

You **might encounter**:
- Unpolished UI experiences
- Missing features (e.g., GPU acceleration, controller support)
- Stability or compatibility issues
- Limited automation or orchestration

We welcome testers, tinkerers, and open-source contributors — but **please temper your expectations** and join with a spirit of exploration, not as end users expecting a plug-and-play cloud gaming platform (yet!).

---

## 📦 What's Inside

| Component        | Description                                                      |
|------------------|------------------------------------------------------------------|
| **XFCE4**         | Lightweight desktop environment with a customized panel layout   |
| **TigerVNC**      | VNC server to expose the XFCE desktop over VNC                  |
| **noVNC + Websockify** | Converts VNC to WebSocket, enabling access via any modern browser |
| **JupyterLab**    | Optional dev interface, can be replaced with any graphical app  |
| **Supervisor**    | Process manager to keep all components running                  |
| **Dockerized**    | Fully containerized for portability and reproducibility         |

---

## 🛠️ Features

- 🌐 **Full desktop streaming from any browser**
- ⚙️ **Supervisor-powered service orchestration**
- 📁 **Persistent user profiles and logs**
- 🧠 **Modular for integration with other backends like Sunshine + Moonlight**
- 🧪 **Easy to extend with custom apps or launchers (e.g., Steam, VSCode, games)**

---

## 📁 File Structure

| File | Description |
|------|-------------|
| `Dockerfile` | Builds the full container with all necessary components |
| `startup.sh` | Entrypoint script to initialize environment and permissions |
| `supervisord.conf` | Launches `vncserver`, `noVNC`, and `jupyterlab` |
| `xfce4-panel.xml` | Custom XFCE panel configuration |
| `os.svg` | Branding/logo for Xadia OS |

---

## 🧪 Quick Start (Local Docker)

```bash
# Clone the repo
git clone https://github.com/avimanyu786/xadia.git
cd xadia

# Build the Docker image
docker build -t xadia .

# Run the container
docker run -d -p 6080:6080 -p 8888:8888 -e JUPYTER_TOKEN=1234 --name xadia-desktop xadia
```


Then visit:

- 🌐 `http://localhost:6080` → for full XFCE desktop in browser (default login password for now  is 1234) 
- 🧪 `http://localhost:8888` → for JupyterLab (optional)

---

## 💡 Inspiration & Vision

While mature platforms like **Sunshine + Moonlight** already provide exceptional low-latency game streaming, **Xadia is not here to replace them — it is here to complement and expand them.**

Think of Xadia as a **unified, containerized platform** capable of hosting:

- A full Linux desktop environment
- A cloud-based development toolkit
- A lightweight virtual desktop infrastructure (VDI) for students or remote teams
- A pre-configured Sunshine game streaming server
- Or all of the above — accessible directly via browser, from anywhere

In the future, Xadia can act as a **host** for Sunshine, enabling seamless switching between a general-purpose GUI (via XFCE + noVNC) and low-latency, GPU-accelerated game streaming.

Rather than reinventing the wheel, Xadia aims to **build the vehicle around it** — one that is modular, portable, and open by design.

> This is not just another streamer.  
> It’s a framework for *experiments, education, gaming, and open source computing.*

---

## ⚖️ License

This project is licensed under the **MIT License**.

> Xadia is free software — built for the community, by the community and therefore of the community.

---