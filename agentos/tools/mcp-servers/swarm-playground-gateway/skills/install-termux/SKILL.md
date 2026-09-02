---
name: mcp-install-termux
description: Step-by-step installation guide for the Swarm Playground Gateway MCP server on Android Termux. Covers pkg dependencies, Python setup, MCP SDK, and Antigravity registration.
---

# Install: Swarm Playground Gateway — Termux (Android)

> **Platform**: Android (Termux)
> **Shell**: bash (Termux)
> **Package Manager**: `pkg` / `pip`

---

## Prerequisites

- Termux installed from F-Droid (not Play Store)
- Python 3.10+ available in Termux
- Antigravity CLI installed and configured
- The Swarm Playground project cloned at `~/Projects/local/agents-playground/`

---

## Step 1: Update Termux Packages

```bash
pkg update && pkg upgrade -y
```

## Step 2: Install Python & Dependencies

```bash
# Install Python if not already present
pkg install python -y

# Verify version (must be 3.10+)
python3 --version
```

## Step 3: Install the MCP Python SDK

```bash
pip install "mcp[cli]"
```

> [!NOTE]
> If you encounter build errors for native extensions, install the build toolchain first:
> ```bash
> pkg install build-essential libffi openssl -y
> pip install --upgrade pip setuptools wheel
> pip install "mcp[cli]"
> ```

## Step 4: Clone / Verify the MCP Server

The server should already exist at:
```
~/Projects/mcp-servers/swarm-playground-gateway/server.py
```

If not, create the directory and copy the server file:
```bash
mkdir -p ~/Projects/mcp-servers/swarm-playground-gateway
# Copy server.py into this directory
```

## Step 5: Verify the Server Runs

```bash
# Quick syntax check
python3 -c "import mcp; print('MCP SDK:', mcp.__version__)"

# Test the server starts without errors (Ctrl+C to exit)
python3 ~/Projects/mcp-servers/swarm-playground-gateway/server.py &
sleep 2 && kill %1 2>/dev/null
echo "Server starts OK"
```

## Step 6: Register with Antigravity

Create or update `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "python3",
      "args": [
        "/data/data/com.termux/files/home/Projects/mcp-servers/swarm-playground-gateway/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Step 7: Verify the Playground is Running

The MCP server proxies to the Swarm Playground on port 5000:
```bash
# Start the playground if not running
python3 ~/Projects/local/agents-playground/src/ui/dashboard.py &

# Verify it responds
curl -s http://127.0.0.1:5000/api/actors | python3 -m json.tool
```

## Step 8: Test End-to-End

In a new Antigravity session, the `swarm-playground` MCP tools should appear automatically. Test with:
```
Use the playground_health tool to check the swarm status.
```

---

## Termux-Specific Notes

- **Path prefix**: All Termux paths use `/data/data/com.termux/files/home/` as `$HOME`
- **Background processes**: Use `termux-wake-lock` to prevent Android from killing background services
- **Storage**: Ensure sufficient space (~50MB for MCP SDK + dependencies)
- **Permissions**: No root required for the MCP server itself; root only needed for Native AI Engine tools

## Troubleshooting

| Issue | Fix |
|:------|:----|
| `pip install` fails with `error: externally-managed-environment` | Use `pip install --break-system-packages "mcp[cli]"` or create a venv |
| `ModuleNotFoundError: mcp` | Verify pip installed to the same Python: `python3 -m pip install "mcp[cli]"` |
| Connection refused to port 5000 | Start the Playground: `python3 ~/Projects/local/agents-playground/src/ui/dashboard.py` |
| Server hangs on startup | Ensure nothing else is reading stdin; the server uses stdio transport |
| `libc.so` errors in Termux | Run `pkg install ndk-sysroot` or restart Termux app |
