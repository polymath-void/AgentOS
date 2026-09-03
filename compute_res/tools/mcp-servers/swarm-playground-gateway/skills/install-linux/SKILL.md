---
name: mcp-install-linux
description: Step-by-step installation guide for the Swarm Playground Gateway MCP server on Linux (Ubuntu/Debian, Fedora, Arch). Covers system deps, Python venv, MCP SDK, and Antigravity registration.
---

# Install: Swarm Playground Gateway — Linux

> **Platform**: Linux (Ubuntu/Debian, Fedora/RHEL, Arch)
> **Shell**: bash / zsh
> **Package Manager**: apt / dnf / pacman + pip

---

## Prerequisites

- Linux distribution with Python 3.10+
- Antigravity CLI installed
- Network access for pip packages
- The Swarm Playground project available on the machine

---

## Step 1: Install System Dependencies

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

### Fedora / RHEL
```bash
sudo dnf install -y python3 python3-pip git curl
```

### Arch Linux
```bash
sudo pacman -Syu --noconfirm python python-pip git curl
```

## Step 2: Create a Virtual Environment (Recommended)

```bash
mkdir -p ~/Projects/mcp-servers/swarm-playground-gateway
cd ~/Projects/mcp-servers/swarm-playground-gateway

python3 -m venv .venv
source .venv/bin/activate
```

> [!TIP]
> Using a venv avoids conflicts with system Python packages and the `externally-managed-environment` error on modern distros.

## Step 3: Install the MCP Python SDK

```bash
pip install "mcp[cli]"
```

Verify:
```bash
python3 -c "import mcp; print('MCP SDK:', mcp.__version__)"
```

## Step 4: Deploy the Server

Copy `server.py` into the project directory:
```bash
# If cloning from a repo:
# git clone <repo-url> ~/Projects/mcp-servers/swarm-playground-gateway

# Verify the file exists
ls -la ~/Projects/mcp-servers/swarm-playground-gateway/server.py
```

## Step 5: Configure the Playground Base URL

Edit `server.py` if the Swarm Playground runs on a different host/port:
```python
# Default — change if needed
PLAYGROUND_BASE = "http://127.0.0.1:5000"
```

## Step 6: Register with Antigravity

Create or update `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "/home/<your-user>/Projects/mcp-servers/swarm-playground-gateway/.venv/bin/python3",
      "args": [
        "/home/<your-user>/Projects/mcp-servers/swarm-playground-gateway/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

> [!IMPORTANT]
> When using a venv, the `command` must point to the **venv's Python binary**, not the system `python3`. This ensures the MCP SDK is found.

## Step 7: Start the Playground

```bash
# Start the Swarm Playground API
cd ~/Projects/local/agents-playground
python3 src/ui/dashboard.py &

# Verify
curl -s http://127.0.0.1:5000/api/actors | python3 -m json.tool
```

## Step 8: Test End-to-End

```bash
# Quick smoke test — run server directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  ~/Projects/mcp-servers/swarm-playground-gateway/.venv/bin/python3 \
  ~/Projects/mcp-servers/swarm-playground-gateway/server.py
```

Or open a new Antigravity session and ask:
```
Use the playground_health tool to check the swarm status.
```

---

## Systemd Service (Optional)

To run the Playground as a background service:

```ini
# ~/.config/systemd/user/swarm-playground.service
[Unit]
Description=Neural Agent Swarm Playground
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/Projects/local/agents-playground
ExecStart=%h/Projects/local/agents-playground/.venv/bin/python3 src/ui/dashboard.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now swarm-playground
```

## Troubleshooting

| Issue | Fix |
|:------|:----|
| `externally-managed-environment` error | Use a venv (Step 2) or `pip install --break-system-packages` |
| `command not found: python3` | Install Python: `sudo apt install python3` |
| MCP tools don't appear in Antigravity | Verify `mcp_config.json` path and restart Antigravity |
| Port 5000 already in use | Check with `lsof -i :5000` and kill the conflicting process |
| Firewall blocking localhost | Shouldn't happen, but check `iptables -L` or `ufw status` |
