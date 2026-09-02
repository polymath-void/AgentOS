#!/usr/bin/env bash
# install.sh — SaaS-Agent installer for Termux

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

#
# Detect Termux
#
if [[ -n "${TERMUX_VERSION:-}" ]] || [[ -d "/data/data/com.termux" ]]; then
    TERMUX=1
else
    TERMUX=0
fi

#
# Install Termux packages
#
if [[ "$TERMUX" == "1" ]]; then

    info "Updating repositories..."
    pkg update -y

    info "Installing Termux dependencies..."

    pkg install -y \
        python \
        python-pip \
        python-grpcio \
        clang \
        libffi \
        openssl \
        libjpeg-turbo \
        zlib

    success "Termux packages installed."
fi

#
# Create virtual environment
#
if [[ ! -d "venv" ]]; then

    info "Creating virtual environment..."

    python -m venv venv

    success "Virtual environment created."
fi

#
# Activate venv
#
# shellcheck disable=SC1091
source venv/bin/activate

success "Virtual environment activated."

#
# Upgrade pip INSIDE venv only
#
info "Upgrading pip inside virtual environment..."

python -m pip install --upgrade pip

#
# Install project dependencies
#
info "Installing Python dependencies..."

python -m pip install \
    "fastapi>=0.111.0" \
    "uvicorn[standard]>=0.29.0" \
    "pydantic>=2.7.0" \
    "google-genai>=1.0.0" \
    "httpx>=0.27.0"

success "Python dependencies installed."

#
# Verify imports
#
info "Verifying installation..."

python - <<'PYCHECK'
import sys

checks = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("pydantic", "Pydantic"),
    ("httpx", "httpx"),
    ("google.genai", "google-genai"),
    ("grpc", "grpcio"),
]

failed = []

for module, name in checks:
    try:
        __import__(module)
        print(f"  OK  {name}")
    except Exception as e:
        print(f"  ERR {name}: {e}")
        failed.append(name)

if failed:
    print("\nFailed modules:")
    for item in failed:
        print(f" - {item}")
    sys.exit(1)

print("\nAll dependencies verified.")
PYCHECK

success "Installation complete."

echo
echo "Activate environment:"
echo "    source venv/bin/activate"
echo
echo "Start server:"
echo "    python main.py"
