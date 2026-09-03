# ComputeRes Docker Deployment Architecture: High-Performance Blueprint

This is the absolute, definitive integration guide for deploying the ComputeRes ecosystem. The architecture utilizes `python:3.10-slim-bullseye` as the deployment target to guarantee rapid, zero-compilation builds using pre-compiled `manylinux` wheels. This approach avoids C-compilation failures on edge devices while maintaining a minimal footprint.

## 1. ComputeRes Ecosystem Components

The ComputeRes swarm architecture consists of the following interconnected modules running within the deployment environment:
* **`broker.py`**: Manages the ZeroMQ internal control plane and message routing.
* **`mcp_server.py`**: Handles external connections and Model Context Protocol (MCP) integrations.
* **`mesh.py`**: Establishes WebRTC connections and manages the distributed mesh network.
* **`wasm_engine.py`**: Sandboxed execution environment for WebAssembly workloads powered by Wasmtime.
* **`kernel.py`**: The core execution loop and process manager orchestrating the system.

## 2. Dependency Management (`pyproject.toml`)

To ensure deterministic builds and leverage pre-compiled wheels for heavy native extensions (`aiortc`, `pyzmq`, `wasmtime`), specify the exact dependencies in your `pyproject.toml`.

```toml
[project]
name = "compute_res"
version = "1.0.0"
description = "ComputeRes High-Performance Swarm Ecosystem"
requires-python = ">=3.10"
dependencies = [
    "aiortc>=1.6.0",
    "wasmtime>=16.0.0",
    "websockets",
    "pyzmq"
]
```

## 3. Dockerfile Syntax

The following `Dockerfile` provides the exact syntax required to package the entire ComputeRes ecosystem into a robust, edge-ready container.

```dockerfile
# Base Image: Minimal Debian-based glibc environment for manylinux wheel compatibility
FROM python:3.10-slim-bullseye

# Environment Variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Upgrade pip to ensure proper manylinux wheel resolution
RUN pip install --upgrade pip

# Copy dependency configuration and install
COPY pyproject.toml .
# Note: In a real environment, you might use build tools like `pip install .` 
# For this blueprint, we install dependencies directly from the pyproject configuration
RUN pip install .

# Copy the ComputeRes ecosystem files
COPY broker.py mcp_server.py mesh.py wasm_engine.py kernel.py ./

# Expose ports for WebRTC (UDP) and ZeroMQ (TCP) if not using host networking
EXPOSE 5557/tcp
EXPOSE 20000-20100/udp

# Execution Command
CMD ["python", "kernel.py"]
```

## 4. Network Configuration and Port Mapping

ComputeRes relies on distinct communication vectors that require specific Docker networking strategies.

### ZeroMQ (Internal IPC / Control Plane)
* **Protocol/Port:** `TCP` on port `5557`.
* **Binding:** Ensure `broker.py` binds to `tcp://0.0.0.0:5557` inside the container if external swarm communication is needed.
* **Mapping:** Map the port when running the container: `-p 5557:5557`.
* **Security Note:** If running locally or within a trusted cluster, use Docker bridge networks (`--network compute_res-net`) rather than exposing to the host directly.

### WebRTC (Mesh Network / Media Streaming)
* **Protocol/Port:** `UDP` constrained to a specific port range (e.g., `20000-20100`).
* **Configuration:** `mesh.py` must configure `aiortc`'s ICE agent to utilize this specific UDP port range to avoid ephemeral port chaos.
* **Mapping:** Due to `docker-proxy` overhead when mapping large port ranges (`-p 20000-20100:20000-20100/udp`), it is highly recommended to use **Host Networking**.
  * Use `--network host` to bind the container directly to the host's interfaces, bypassing Docker's NAT and providing bare-metal UDP latency for `mesh.py`.

## 5. Execution Command

To deploy the ComputeRes ecosystem with the recommended network settings, use the following `docker run` execution command:

```bash
# Recommended Execution (Host Networking for Optimal WebRTC Performance)
docker run -d \
  --name compute_res-core \
  --network host \
  --restart unless-stopped \
  compute_res:latest
```

Alternatively, if strict network isolation is required (accepting the `docker-proxy` overhead):

```bash
# Isolated Execution (Explicit Port Mapping)
docker run -d \
  --name compute_res-core \
  -p 5557:5557/tcp \
  -p 20000-20100:20000-20100/udp \
  --restart unless-stopped \
  compute_res:latest
```
