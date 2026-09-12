#!/usr/bin/env bash
set -e

echo "==================================================="
echo "🌌 ComputeRes AI Operating System Installer"
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
    echo "❌ Error: Python 3.10+ is required to install ComputeRes."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python Version: ${PYTHON_VERSION}"

echo ""
echo "[2/4] Installing ComputeRes Core Packages..."
pip install --upgrade pip
pip install compute-res pyzmq aiortc wasmtime textual rich

echo ""
echo "[3/4] Initializing ComputeRes Environment Specs..."
mkdir -p ~/.compute_res/tools/evolved_skills
mkdir -p ~/.compute_res/memory
mkdir -p ~/.compute_res/manifests

echo ""
echo "[4/4] Verifying Installation..."
python3 -c "import compute_res; print('✅ ComputeRes Core Version:', getattr(compute_res, '__version__', '1.0.0'))"

echo ""
echo "==================================================="
echo "🎉 ComputeRes Installation Complete!"
echo ""
echo "To boot the Kernel:"
echo "  compute_res"
echo ""
echo "To open the Telemetry Dashboard:"
echo "  python3 -m compute_res.telemetry.core.app"
echo "==================================================="
