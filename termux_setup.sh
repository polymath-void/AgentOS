#!/data/data/com.termux/files/usr/bin/bash
echo "==================================================="
echo "🚀 ComputeRes: Native Termux Build Optimizer"
echo "==================================================="
echo ""
echo "[1/4] Installing Native C-Compilers and FFmpeg/WebRTC Headers..."
pkg install -y clang ffmpeg libsrtp python curl wget tar || { echo "Failed to install dependencies"; exit 1; }

echo ""
echo "[2/4] Downloading and Patching PyAV Cython Compiler..."
mkdir -p /tmp/compute_res_pyav && cd /tmp/compute_res_pyav
curl -sL https://pypi.org/pypi/av/17.1.0/json | grep -o 'https://[^"]*\.tar\.gz' | head -n 1 | xargs wget -O av.tar.gz
tar -xzf av.tar.gz
cd av-*

# Remove Cython redeclaration of seek_func which crashes Python 3.14 on Termux
sed -i 's/seek_func: seek_func_t = pyio_seek/seek_func = pyio_seek/g' av/container/pyio.py

echo "Building PyAV natively (this will take a few minutes)..."
pip install . || { echo "PyAV compilation failed!"; exit 1; }

echo ""
echo "[3/4] Installing ComputeRes and aiortc..."
cd /data/data/com.termux/files/home/Projects/ComputeRes
pip install .
pip install aiortc

echo ""
echo "[4/4] Patching Bionic libc for WebRTC NAT Hole-punching..."
# Termux uses Bionic libc.so, but aiortc's ifaddr dependency expects GNU libc.so.6
IFADDR_PATH=$(python -c "import ifaddr, os; print(os.path.dirname(ifaddr.__file__))")
sed -i 's/ctypes.util.find_library("socket" if os.uname()\[0\] == "SunOS" else "c")/"libc.so"/g' $IFADDR_PATH/_posix.py

echo ""
echo "==================================================="
echo "✅ ComputeRes WebRTC Swarm is natively compiled for Termux!"
echo "Run 'compute_res' to boot the kernel."
echo "Run 'python3 -m compute_res.telemetry.core.app' in a separate tab for the TUI Dashboard."
echo "==================================================="
