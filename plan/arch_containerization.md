# ComputeRes Containerization and Packaging Blueprint

## 1. Executive Summary

This document outlines the architectural blueprint for the containerization (Docker) and portable Python packaging (PyPI/Pipx) of the ComputeRes ecosystem. The primary objective is to maintain strict platform independence and kernel agnosticism while seamlessly orchestrating complex dependencies, including ZeroMQ bindings, async WebRTC libraries, and WebAssembly (WASM) runtime engines.

## 2. Core Packaging Philosophy

- **Kernel Agnosticism**: No reliance on specific kernel features (e.g., io_uring, specific eBPF capabilities) without graceful fallbacks.
- **Isolated Environments**: Usage of `pipx` for CLI deployments to avoid system Python pollution.
- **Multi-Architecture**: First-class support for `linux/amd64`, `linux/arm64`, and macOS (`darwin/arm64`).
- **Binary Wheels**: Leverage `cibuildwheel` to distribute pre-compiled native extensions, reducing the burden on the end-user.

## 3. Containerization Strategy (Docker)

To support complex native dependencies (ZeroMQ, WebRTC, WASM), we employ a multi-stage Docker build strategy using Debian Slim as the base image to ensure `glibc` compatibility (Alpine/musl often struggles with pre-compiled Python wheels for WebRTC and WASM).

### 3.1. Base Image Selection
- **Build Stage**: `python:3.11-slim-bookworm` (Includes build toolchains: `build-essential`, `cmake`, `pkg-config`).
- **Runtime Stage**: `python:3.11-slim-bookworm` (Minimal runtime dependencies).

### 3.2. Handling Complex Dependencies
1. **ZeroMQ (`pyzmq`)**:
   - Install `libzmq3-dev` in the build stage.
   - Use pre-compiled wheels in the runtime stage to avoid compiling C++ extensions on deployment.
   - **Networking**: Default to TCP (`tcp://`) instead of IPC (`ipc://`) to ensure seamless inter-container and cross-host communication, bypassing UNIX domain socket volume sharing complexities.
2. **Async WebRTC (`aiortc` / `webrtc`)**:
   - Requires system-level media libraries: `libavcodec-dev`, `libavdevice-dev`, `libavfilter-dev`, `libavformat-dev`, `libavutil-dev`, `libsrtp2-dev`, `libopus-dev`, `libvpx-dev`.
   - Install these in the runtime image to support the Python bindings.
3. **WASM Runtime (`wasmtime-py` / `wasmer`)**:
   - Rely on pre-compiled wheels provided by the runtime maintainers.
   - For custom WASM host functions, ensure Rust (`cargo`) is available in the build stage, compiling down to a shared object (`.so`) that is copied to the runtime stage.

### 3.3. Multi-Stage Dockerfile Example (Abridged)
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake pkg-config git \
    libzmq3-dev libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
    libsrtp2-dev libopus-dev libvpx-dev python3-dev
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzmq5 libavformat59 libavcodec59 libavdevice59 libavutil57 \
    libswscale6 libswresample4 libavfilter8 libsrtp2-1 libopus0 libvpx7 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . /app
CMD ["python", "-m", "compute_res.core"]
```

## 4. Portable Python Packaging (PyPI & Pipx)

The ComputeRes CLI and core libraries must be installable via standard Python tools without requiring the user to install complex C-toolchains.

### 4.1. Dependency Segregation (`pyproject.toml`)
Define optional dependency groups to allow users to install only what they need, keeping the core lightweight.

```toml
[project]
name = "compute_res"
version = "1.0.0"
dependencies = [
    "pyzmq>=25.0.0",
    "pydantic>=2.0.0",
    "asyncio"
]

[project.optional-dependencies]
webrtc = ["aiortc>=1.5.0", "av>=10.0.0"]
wasm = ["wasmtime>=12.0.0"]
all = ["compute_res[webrtc,wasm]"]

[project.scripts]
compute_res = "compute_res.cli:main"
```

### 4.2. Distribution via `cibuildwheel`
To ensure platform independence (macOS, Windows, Linux) without requiring local compilation of ZeroMQ, WebRTC, or WASM bindings:
- Utilize GitHub Actions running `cibuildwheel`.
- Build `manylinux` wheels for Linux (`x86_64` and `aarch64`).
- Build macOS wheels (`universal2` or `arm64` + `x86_64`).
- Build Windows wheels (`AMD64`).

### 4.3. Execution via `pipx`
For standalone CLI usage, `pipx` is the recommended installation method. It creates an isolated virtual environment, preventing dependency conflicts with system packages.
```bash
# Install core
pipx install compute_res

# Install with WebRTC and WASM capabilities injected
pipx install "compute_res[all]"
```

## 5. Security & Privilege Boundaries
- **Rootless Execution**: The Docker container should define a `USER compute_res` and drop root privileges immediately.
- **WASM Sandboxing**: The WASM runtime (e.g., Wasmtime) inherently provides strict memory sandboxing and capability-based security (WASI). ComputeRes must not expose the host filesystem or network to WASM modules by default.

## 6. Conclusion
By leveraging Debian-slim for glibc compatibility, multi-stage Docker builds for lean images, `cibuildwheel` for native extension pre-compilation, and `pipx` for isolated execution, ComputeRes achieves true platform independence. It can run on macOS laptops for local development, Linux servers for production, and ARM-based edge devices, all while securely orchestrating WebRTC and WASM workloads over a ZeroMQ backbone.
