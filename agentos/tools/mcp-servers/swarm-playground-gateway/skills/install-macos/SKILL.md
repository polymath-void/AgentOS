---
name: mcp-install-macos
description: Step-by-step installation guide for the Swarm Playground Gateway MCP server on macOS. Covers Homebrew, Python venv, MCP SDK, and Antigravity registration.
---

# Install: Swarm Playground Gateway — macOS

> **Platform**: macOS (Ventura / Sonoma / Sequoia)
> **Shell**: zsh (default)
> **Package Manager**: Homebrew + pip

---

## Prerequisites

- macOS 13+ (Ventura or later recommended)
- Homebrew installed (`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- Antigravity CLI installed
- The Swarm Playground project available on the machine

---

## Step 1: Install Python via Homebrew

macOS ships with Python 3, but Homebrew's version is easier to manage:

```bash
brew install python@3.12
```

Verify:
```bash
python3 --version   # Should be 3.10+
```

## Step 2: Create a Virtual Environment

```bash
mkdir -p ~/Projects/mcp-servers/swarm-playground-gateway
cd ~/Projects/mcp-servers/swarm-playground-gateway

python3 -m venv .venv
source .venv/bin/activate
```

## Step 3: Install the MCP Python SDK

```bash
pip install "mcp[cli]"
```

Verify:
```bash
python3 -c "import mcp; print('MCP SDK:', mcp.__version__)"
```

## Step 4: Deploy the Server

```bash
# Ensure server.py is in place
ls -la ~/Projects/mcp-servers/swarm-playground-gateway/server.py
```

## Step 5: Configure the Playground Base URL

Edit `server.py` if needed:
```python
PLAYGROUND_BASE = "http://127.0.0.1:5000"
```

## Step 6: Register with Antigravity

Create or update `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "/Users/<your-user>/Projects/mcp-servers/swarm-playground-gateway/.venv/bin/python3",
      "args": [
        "/Users/<your-user>/Projects/mcp-servers/swarm-playground-gateway/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

> [!IMPORTANT]
> Use absolute paths. `~` is not expanded in JSON configs. Replace `<your-user>` with your macOS username.

## Step 7: Start the Playground

```bash
cd ~/Projects/local/agents-playground
python3 src/ui/dashboard.py &

# Verify
curl -s http://127.0.0.1:5000/api/actors | python3 -m json.tool
```

## Step 8: Test End-to-End

Open a new Antigravity session and ask:
```
Use the playground_health tool to check the swarm status.
```

---

## LaunchAgent (Optional — Auto-Start)

To auto-start the Playground on login:

```xml
<!-- ~/Library/LaunchAgents/com.swarm.playground.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.swarm.playground</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USER/Projects/local/agents-playground/.venv/bin/python3</string>
        <string>src/ui/dashboard.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USER/Projects/local/agents-playground</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/swarm-playground.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/swarm-playground.err</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.swarm.playground.plist
```

## macOS-Specific Notes

- **Gatekeeper**: If Python scripts are blocked, run `xattr -cr ~/Projects/mcp-servers/` to remove quarantine flags
- **Firewall**: macOS may prompt to allow incoming connections for the Playground. Allow for `python3` on port 5000 (localhost only)
- **Apple Silicon (M1/M2/M3)**: The MCP SDK and all dependencies are ARM-native via Homebrew. No Rosetta needed
- **Keychain prompts**: If `pip install` triggers keychain access prompts, run `security unlock-keychain` first

## Troubleshooting

| Issue | Fix |
|:------|:----|
| `python3: command not found` | Run `brew install python@3.12` and restart terminal |
| `pip install` permission denied | Use a venv (Step 2), never `sudo pip` |
| Port 5000 conflict (AirPlay Receiver) | Disable in System Settings → General → AirDrop & Handoff → AirPlay Receiver, or change `PLAYGROUND_BASE` port |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Run `/Applications/Python\ 3.x/Install\ Certificates.command` |
| MCP tools not appearing | Restart Antigravity after updating `mcp_config.json` |
