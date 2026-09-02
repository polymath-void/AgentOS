---
name: install-AgentOS-mcp-server
description: "Guidelines and skills for installing the AgentOS MCP Server across various MCP-enabled platforms (Claude Desktop, Cursor, Antigravity)."
---

# AgentOS MCP Server Installation Skill

This file serves as a comprehensive cheatsheet for AI agents on how to correctly scaffold, install, and configure the **AgentOS-mcp-server** across different environments. 

## 1. Prerequisites Checking
Before modifying configuration files, always verify:
* Python 3.10+ is installed (`python3 --version`).
* The absolute path to the `AgentOS-mcp-server` repository is known.

## 2. Platform-Specific Configuration

### Claude Desktop
**Target File Paths:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Action:** Read the file, inject the JSON blob under the `mcpServers` key, and write back.

### Antigravity (Termux/Android Native)
**Target File Path:** `~/.gemini/config/mcp_config.json`

**Action:** Inject the configuration block to ensure the local agent swarm has OS-level bridging.

### Cursor IDE
**Action:** Instruct the user to open `Cursor Settings > Features > MCP Servers` and click `+ Add New MCP Server`. Provide them with the `command`, `args`, and `env` parameters in a clear, copy-pasteable format.

## 3. The Configuration Payload
Whenever deploying this server, utilize the following precise JSON structure. Replace `/path/to/AgentOS-mcp-server` dynamically based on the user's filesystem.

```json
"AgentOS": {
  "command": "python3",
  "args": [
    "/path/to/AgentOS-mcp-server/server.py"
  ],
  "env": {
    "PYTHONUNBUFFERED": "1",
    "PYTHONPATH": "/path/to/AgentOS-mcp-server"
  }
}
```

## 4. Verification
After configuration, instruct the user to restart their MCP client. The server will dynamically broadcast 49 tools initialized by the `ToolsManager`. If failures occur, check `PYTHONPATH` resolution and ensure all `plugins/*.sh` scripts have `+x` executable bits and correct `#!/usr/bin/env bash` shebangs.
