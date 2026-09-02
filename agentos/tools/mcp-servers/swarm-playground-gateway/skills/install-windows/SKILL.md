---
name: mcp-install-windows
description: Step-by-step installation guide for the Swarm Playground Gateway MCP server on Windows. Covers Python installation, venv setup, MCP SDK, PowerShell config, and Antigravity registration.
---

# Install: Swarm Playground Gateway — Windows

> **Platform**: Windows 10 / 11
> **Shell**: PowerShell / Command Prompt
> **Package Manager**: winget / pip

---

## Prerequisites

- Windows 10 (build 19041+) or Windows 11
- Python 3.10+ installed
- Antigravity CLI installed
- The Swarm Playground project available on the machine

---

## Step 1: Install Python

### Option A: winget (Recommended)
```powershell
winget install Python.Python.3.12
```

### Option B: Microsoft Store
Search "Python 3.12" in Microsoft Store and install.

### Option C: python.org
Download from https://www.python.org/downloads/ — **check "Add to PATH"** during installation.

Verify:
```powershell
python --version    # Should be 3.10+
pip --version
```

> [!WARNING]
> On Windows, use `python` (not `python3`). The `python3` command may not exist unless aliased.

## Step 2: Create a Virtual Environment

```powershell
# Create project directory
New-Item -ItemType Directory -Force -Path "$HOME\Projects\mcp-servers\swarm-playground-gateway"
Set-Location "$HOME\Projects\mcp-servers\swarm-playground-gateway"

# Create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> [!NOTE]
> If you get an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

## Step 3: Install the MCP Python SDK

```powershell
pip install "mcp[cli]"
```

Verify:
```powershell
python -c "import mcp; print('MCP SDK:', mcp.__version__)"
```

## Step 4: Deploy the Server

Ensure `server.py` is placed at:
```
%USERPROFILE%\Projects\mcp-servers\swarm-playground-gateway\server.py
```

## Step 5: Configure the Playground Base URL

Edit `server.py` if the Swarm Playground runs on a different host/port:
```python
PLAYGROUND_BASE = "http://127.0.0.1:5000"
```

## Step 6: Register with Antigravity

Create or update `%USERPROFILE%\.gemini\config\mcp_config.json`:

```json
{
  "mcpServers": {
    "swarm-playground": {
      "command": "C:/Users/<YourUsername>/Projects/mcp-servers/swarm-playground-gateway/.venv/Scripts/python.exe",
      "args": [
        "C:/Users/<YourUsername>/Projects/mcp-servers/swarm-playground-gateway/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

> [!IMPORTANT]
> - Use **forward slashes** (`/`) in JSON paths, not backslashes
> - Point `command` to the **venv's `python.exe`**, not the system Python
> - Replace `<YourUsername>` with your Windows username
> - `PYTHONUTF8` prevents `UnicodeDecodeError` on Windows stdio transport

## Step 7: Start the Playground

```powershell
# In a separate terminal
Set-Location "$HOME\Projects\local\agents-playground"
python src\ui\dashboard.py

# Verify in another terminal
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/actors"
```

## Step 8: Test End-to-End

Open a new Antigravity session and ask:
```
Use the playground_health tool to check the swarm status.
```

---

## Windows Service (Optional — NSSM)

To run the Playground as a Windows background service using [NSSM](https://nssm.cc/):

```powershell
# Install NSSM
winget install NSSM.NSSM

# Register service
nssm install SwarmPlayground "C:\Users\<YourUsername>\Projects\local\agents-playground\.venv\Scripts\python.exe" "src\ui\dashboard.py"
nssm set SwarmPlayground AppDirectory "C:\Users\<YourUsername>\Projects\local\agents-playground"
nssm set SwarmPlayground AppStdout "C:\Users\<YourUsername>\Projects\logs\swarm-stdout.log"
nssm set SwarmPlayground AppStderr "C:\Users\<YourUsername>\Projects\logs\swarm-stderr.log"

# Start
nssm start SwarmPlayground
```

## Task Scheduler Alternative

1. Open Task Scheduler → Create Basic Task
2. Name: "Swarm Playground"
3. Trigger: "When I log on"
4. Action: Start a Program
   - Program: `C:\Users\<YourUsername>\Projects\local\agents-playground\.venv\Scripts\python.exe`
   - Arguments: `src\ui\dashboard.py`
   - Start in: `C:\Users\<YourUsername>\Projects\local\agents-playground`

## Windows-Specific Notes

- **Windows Defender**: May flag the MCP server on first run. Allow through "Windows Security → Virus & threat protection → Allowed threats"
- **Port 5000**: Windows doesn't have the macOS AirPlay conflict, but check if IIS or other services use it: `netstat -ano | findstr :5000`
- **WSL alternative**: If you prefer Linux tooling, install WSL2 and follow the Linux guide instead. Paths would be under `/home/<user>/`
- **Line endings**: Ensure `server.py` uses LF (Unix) line endings, not CRLF. Git config: `git config core.autocrlf input`
- **Long paths**: Enable long path support if your project path exceeds 260 chars:
  ```powershell
  # Run as Administrator
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
  ```

## Troubleshooting

| Issue | Fix |
|:------|:----|
| `python` opens Microsoft Store | Remove the Store alias: Settings → Apps → Advanced app settings → App execution aliases → disable Python |
| `'pip' is not recognized` | Reinstall Python with "Add to PATH" checked, or use `python -m pip` |
| Execution policy blocks `.ps1` scripts | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `ConnectionRefusedError` on port 5000 | Start the Playground first; check Windows Firewall isn't blocking localhost |
| `UnicodeDecodeError` in server output | Set env: `$env:PYTHONUTF8 = "1"` or add `"PYTHONUTF8": "1"` to mcp_config env |
| venv won't activate in CMD | Use `.\. venv\Scripts\activate.bat` instead of `.ps1` |
