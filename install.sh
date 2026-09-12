#!/usr/bin/env bash
set -e

echo "==================================================="
echo "🌌 Compute-OS AI Operating System Installer"
echo "==================================================="
echo ""

# Detect OS & Architecture
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "[1/4] Checking System Architecture..."
echo "  OS: ${OS}"
echo "  Arch: ${ARCH}"

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3.10+ is required to install Compute-OS."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python Version: ${PYTHON_VERSION}"

echo ""
echo "[2/4] Installing Compute-OS Core Packages..."
pip install --upgrade pip
pip install compute-os pyzmq aiortc wasmtime textual rich

echo ""
echo "[3/4] Initializing Compute-OS Environment Specs..."
mkdir -p ~/.compute_res/tools/evolved_skills
mkdir -p ~/.compute_res/memory
mkdir -p ~/.compute_res/manifests

echo ""
echo "[4/4] Verifying Installation..."
python3 -c "import compute_res; print('✅ Compute-OS Core Version:', getattr(compute_res, '__version__', '1.0.0'))"

echo ""
echo "==================================================="
echo "🎉 Compute-OS Installation Complete!"
echo ""
echo "To boot the Kernel:"
echo "  compute-os boot"
echo ""
echo "To open the Telemetry Dashboard:"
echo "  python3 -m compute_res.telemetry.core.app"
echo "==================================================="
