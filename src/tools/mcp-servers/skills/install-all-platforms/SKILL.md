---
name: mcp-install-all
description: Unified installation guide for all MCP servers across Windows, Linux, macOS, and Termux (Android). Covers setup, registration, and per-server notes.
---

# Install Guide: MCP Server Suite

> Universal installation procedure for all 5 MCP servers.
> OS-specific sections are marked with 🤖 🐧 🍎 🪟 icons.

---

## All Servers

| Server | Dir | Root? | External Deps |
|:-------|:----|:-----:|:--------------|
| swarm-playground-gateway | `mcp-servers/swarm-playground-gateway/` | No | Swarm API on :5000 |
| native-ai-engine-bridge | `mcp-servers/native-ai-engine-bridge/` | Yes | Magisk, WASM bridge |
| device-system-tools | `mcp-servers/device-system-tools/` | Kill only | /proc, /sys access |
| project-manager | `mcp-servers/project-manager/` | No | None |
| sqlite-database-tools | `mcp-servers/sqlite-database-tools/` | No | sqlite3 (stdlib) |

---

## Step 1: Install Python 3.10+

### 🤖 Termux (Android)
```bash
pkg update && pkg upgrade -y
pkg install python -y
```

### 🐧 Linux
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv

# Fedora
sudo dnf install -y python3 python3-pip

# Arch
sudo pacman -Syu --noconfirm python python-pip
```

### 🍎 macOS
```bash
brew install python@3.12
```

### 🪟 Windows
```powershell
winget install Python.Python.3.12
# OR download from python.org — check "Add to PATH"
```

---

## Step 2: Create Virtual Environment (Recommended)

### 🐧 🍎 Linux / macOS
```bash
cd ~/Projects/mcp-servers
python3 -m venv .venv
source .venv/bin/activate
```

### 🪟 Windows
```powershell
cd $HOME\Projects\mcp-servers
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 🤖 Termux
```bash
# Venv optional on Termux — pip installs globally by default
# If you want isolation:
python3 -m venv ~/Projects/mcp-servers/.venv
source ~/Projects/mcp-servers/.venv/bin/activate
```

---

## Step 3: Install MCP SDK

```bash
pip install "mcp[cli]"
```

Verify:
```bash
python3 -c "import mcp; print('MCP SDK:', mcp.__version__)"
```

> **Troubleshooting**: If you get `externally-managed-environment`:
> - Use a venv (Step 2), OR
> - `pip install --break-system-packages "mcp[cli]"`

---

## Step 4: Register Servers with Antigravity

Create/update `mcp_config.json` at:

| OS | Path |
|:---|:-----|
| 🤖 Termux | `~/.gemini/config/mcp_config.json` |
| 🐧 Linux | `~/.gemini/config/mcp_config.json` |
| 🍎 macOS | `~/.gemini/config/mcp_config.json` |
| 🪟 Windows | `%USERPROFILE%\.gemini\config\mcp_config.json` |

### 🤖 Termux Config
```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "python3",
      "args": ["/data/data/com.termux/files/home/Projects/mcp-servers/swarm-playground-gateway/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "native-ai-engine": {
      "command": "python3",
      "args": ["/data/data/com.termux/files/home/Projects/mcp-servers/native-ai-engine-bridge/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "device-tools": {
      "command": "python3",
      "args": ["/data/data/com.termux/files/home/Projects/mcp-servers/device-system-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "project-manager": {
      "command": "python3",
      "args": ["/data/data/com.termux/files/home/Projects/mcp-servers/project-manager/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "sqlite-tools": {
      "command": "python3",
      "args": ["/data/data/com.termux/files/home/Projects/mcp-servers/sqlite-database-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    }
  }
}
```

### 🐧 Linux Config (with venv)
```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "/home/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/home/USER/Projects/mcp-servers/swarm-playground-gateway/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "native-ai-engine": {
      "command": "/home/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/home/USER/Projects/mcp-servers/native-ai-engine-bridge/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "device-tools": {
      "command": "/home/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/home/USER/Projects/mcp-servers/device-system-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "project-manager": {
      "command": "/home/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/home/USER/Projects/mcp-servers/project-manager/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "sqlite-tools": {
      "command": "/home/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/home/USER/Projects/mcp-servers/sqlite-database-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    }
  }
}
```

### 🍎 macOS Config (with venv)
```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "/Users/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/Users/USER/Projects/mcp-servers/swarm-playground-gateway/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "native-ai-engine": {
      "command": "/Users/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/Users/USER/Projects/mcp-servers/native-ai-engine-bridge/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "device-tools": {
      "command": "/Users/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/Users/USER/Projects/mcp-servers/device-system-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "project-manager": {
      "command": "/Users/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/Users/USER/Projects/mcp-servers/project-manager/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    },
    "sqlite-tools": {
      "command": "/Users/USER/Projects/mcp-servers/.venv/bin/python3",
      "args": ["/Users/USER/Projects/mcp-servers/sqlite-database-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1"}
    }
  }
}
```

### 🪟 Windows Config (with venv)
```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "C:/Users/USER/Projects/mcp-servers/.venv/Scripts/python.exe",
      "args": ["C:/Users/USER/Projects/mcp-servers/swarm-playground-gateway/server.py"],
      "env": {"PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"}
    },
    "native-ai-engine": {
      "command": "C:/Users/USER/Projects/mcp-servers/.venv/Scripts/python.exe",
      "args": ["C:/Users/USER/Projects/mcp-servers/native-ai-engine-bridge/server.py"],
      "env": {"PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"}
    },
    "device-tools": {
      "command": "C:/Users/USER/Projects/mcp-servers/.venv/Scripts/python.exe",
      "args": ["C:/Users/USER/Projects/mcp-servers/device-system-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"}
    },
    "project-manager": {
      "command": "C:/Users/USER/Projects/mcp-servers/.venv/Scripts/python.exe",
      "args": ["C:/Users/USER/Projects/mcp-servers/project-manager/server.py"],
      "env": {"PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"}
    },
    "sqlite-tools": {
      "command": "C:/Users/USER/Projects/mcp-servers/.venv/Scripts/python.exe",
      "args": ["C:/Users/USER/Projects/mcp-servers/sqlite-database-tools/server.py"],
      "env": {"PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1"}
    }
  }
}
```

> Replace `USER` with your actual username in all configs.

---

## Step 5: Verify

Restart Antigravity, then in a new session:
```
Use the playground_health tool to check swarm status.
Use the device_summary tool for a system health check.
Use the list_projects tool to see all projects.
Use the list_tables tool to inspect the memory database.
```

---

## Per-Server Notes

### native-ai-engine-bridge (Termux only)
- Requires Magisk root and the engine overlay at `/system/bin/native_ai_engine`
- Model must be at `~/models/phi-3-mini-q4.gguf`
- **Not functional on Linux/macOS/Windows** unless you adapt the engine binary

### device-system-tools
- Full functionality on **Termux** and **Linux** (procfs/sysfs)
- **macOS**: Partial — no /sys/class/power_supply, uses different thermal APIs
- **Windows**: Not supported (no procfs/sysfs)

### project-manager
- **Full cross-platform** — only uses pathlib/os for filesystem ops
- Adjust `PROJECTS_ROOT` in server.py if your projects aren't at `~/Projects/`

### sqlite-database-tools
- **Full cross-platform** — stdlib sqlite3
- Default DB path points to Termux playground; adjust for other OS

### swarm-playground-gateway
- Requires the Swarm Playground Flask API running on port 5000
- **Cross-platform** if you deploy the Playground on any OS
