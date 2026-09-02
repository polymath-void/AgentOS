<div align="center">
  <h1>🌌 AgentOS</h1>
  <p><strong>The Operating System Built Exclusively for Artificial Intelligence.</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker)](https://www.docker.com/)
  [![ZeroMQ IPC](https://img.shields.io/badge/IPC-ZeroMQ-DF0000.svg)](https://zeromq.org/)
  [![WebRTC Mesh](https://img.shields.io/badge/P2P-WebRTC-333333.svg)](https://webrtc.org/)
  [![Wasmtime Sandboxing](https://img.shields.io/badge/Security-WASM-654FF0.svg)](https://wasmtime.dev/)
</div>

---

## 🚀 The Philosophy
**AgentOS does not have a brain.** It does not contain an LLM. It does not think. 

It is the **Environment**. 

It is a mathematically rigorous, mathematically secure, decentralized operating system exposed entirely via the **Model Context Protocol (MCP)**. External AI agents connect to this OS to possess it, execute workloads, compile code, and orchestrate decentralized swarms across the globe.

---

## 🧠 Core Architecture

AgentOS solves the three hardest problems in AI Agent deployment: **Inter-Process Communication (IPC)**, **Security Sandboxing**, and **Decentralized Swarming**.

1. **The Kernel (ZeroMQ):** An ultra-fast, non-blocking asynchronous `ROUTER/DEALER` broker that mathematically queues intents from external LLMs and routes them to internal OS workers instantly.
2. **The Sandbox (Wasmtime):** AI Agents are inherently untrustworthy. Every system operation is executed within a strict WebAssembly (WASM) container enforcing absolute memory capping and CPU instruction metering ("Fuel"). If an agent writes infinite loops, the OS cuts its fuel and kills it gracefully.
3. **The Swarm Mesh (WebRTC):** AgentOS utilizes `aiortc` (SCTP over DTLS over UDP) to punch through NAT firewalls, allowing multiple AgentOS nodes running on laptops, edge devices, and servers to sync decentralized state schemas via CRDTs without a centralized cloud.

*For deep architectural blueprints, see the [Architecture Directory](plan/docker_aiortc_blueprint.md).*

---

## ⚡ Deployment: The Zero-Compilation Matrix

Deploying C-extensions (like WebRTC codecs and ZeroMQ bindings) usually destroys CI/CD pipelines. AgentOS is engineered to deploy in **under 15 seconds**.

By locking the architecture to `python:3.10-slim-bullseye`, we guarantee the resolution of pre-compiled `manylinux2014` wheels. 

```bash
# 1. Clone the Matrix
git clone https://github.com/polymath-void/AgentOS.git
cd AgentOS

# 2. Build the OS (Takes < 15 seconds)
docker build -t agentos-core .

# 3. Boot the Kernel (Host networking for WebRTC UDP performance)
docker run -d --name agentos-kernel --network host agentos-core
```

---

## 📱 Hardware Capabilities: Rooted vs. Non-Rooted Edge Devices

AgentOS is designed to run everywhere—from AWS clusters down to Android smartphones in your pocket. 

### 🟢 Rooted Devices & Standard OS (Linux, macOS, Windows)
If you have root access to `cgroups` and namespaces (e.g., standard servers, laptops, or rooted Android devices), we **strongly recommend** the Docker deployment strategy above. The container isolates the WebRTC C-bindings and prevents capability bleeding from the Wasmtime engine.

### 🟡 Non-Rooted Environments (e.g., Android Termux)
On heavily sandboxed, non-rooted edge devices, the Docker Daemon (`dockerd`) cannot run natively. However, the **AgentOS Kernel is fully OS-agnostic**. 

You can bypass Docker entirely and boot the OS directly into the native Python runtime environment:

```bash
# 1. Install directly from PyPI (Core OS only - bypasses WebRTC C-compilers)
pip install agentos

# (Optional) If you have a rooted GNU environment and want the WebRTC mesh:
# pip install agentos[swarm]

# 2. Boot the native Kernel
agentos
```
*Note: The native python deployment seamlessly maps the `~/.agentos/tools/` filesystem in your home directory to maintain structural consistency without container volumes.*

---

## 🤝 Calling All Engineers (Contribute!)

AgentOS is bleeding-edge. We are actively pushing the boundaries of what autonomous LLM swarms can do on bare-metal systems. 

**We need your help to build the future:**
* **Rust/WASM Engineers:** Help us optimize the Wasmtime memory bounds and build tighter capability sandboxes.
* **Network Architects:** We need stress tests on the WebRTC UDP hole-punching for massive swarm synchronization.
* **Core Python Devs:** Optimize the `asyncio` loop handling the ZeroMQ `ROUTER/DEALER` broker.

**To Contribute:**
1. Fork the repo.
2. Check out the [Architectural Blueprints](plan/).
3. Submit a PR. We review everything. 

Star the repo ⭐ if you believe in the future of Agentic Operating Systems.
