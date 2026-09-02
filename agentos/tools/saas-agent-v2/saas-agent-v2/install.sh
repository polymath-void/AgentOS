#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[install]${RESET} $*"; }
success() { echo -e "${GREEN}[ok]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[warn]${RESET} $*"; }
die()     { echo -e "${RED}[error]${RESET} $*" >&2; exit 1; }

# Detect environment
TERMUX=0
if [[ -n "${TERMUX_VERSION:-}" ]] || [[ -d "/data/data/com.termux" ]]; then
    TERMUX=1
fi

# Update and install system deps
if [[ "$TERMUX" == "1" ]]; then
    info "Updating Termux packages…"
    pkg update -y
    pkg install -y python python-pip python-grpcio clang libffi openssl zlib
    success "Termux packages installed"
fi

# Create venv
if [[ ! -d "venv" ]]; then
    info "Creating virtual environment…"
    python -m venv venv
    success "venv created"
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
info "Upgrading pip…"
python -m pip install --upgrade pip

# Install deps
info "Installing Python dependencies…"
python -m pip install -r requirements.txt

# Verify
info "Verifying installation…"
python - << 'VERIFY'
import sys
mods = ['fastapi', 'uvicorn', 'pydantic', 'google', 'httpx']
for m in mods:
    try:
        __import__(m)
        print(f"  ✓ {m}")
    except ImportError:
        print(f"  ✗ {m}")
        sys.exit(1)
VERIFY

success "Installation complete!"
echo
echo "Start server:"
echo "  source venv/bin/activate"
echo "  export GEMINI_API_KEY='your-api-key'"
echo "  python main.py"
echo
echo "Open browser:"
echo "  http://localhost:8000"
