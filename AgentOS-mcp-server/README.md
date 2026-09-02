# AgentOS MCP Server: The Ultimate Universal AI OS Bridge

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue.svg)](https://modelcontextprotocol.io/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

**AgentOS MCP Server** is a highly extensible, standardized Model Context Protocol (MCP) server that transforms any operating system into an autonomous playground for AI agents. By dynamically mapping 49 modular OS plugins into standardized MCP tools, it allows agents like Claude, VS Code (Cursor), and Antigravity to seamlessly command, query, and manipulate the underlying system.

## 🚀 Key Features

*   **Universal MCP Compatibility:** Built purely on the official MCP Python SDK (`mcp.server.Server`), ensuring zero-config compatibility with Claude Desktop, Cursor, VS Code, and any other MCP-enabled client.
*   **49 Built-in Capabilities:** Instantly equips your AI with 49 native tools out of the box, including system monitoring (`process_list`, `mem_check`), development utilities (`git_commit_auto`, `build_compiler`), and security features (`firewall_config`).
*   **Safe Execution via Simulation:** The core `DispatchNetwork` routing engine enforces a mandatory simulation mode (`mode: "simulate"` vs `mode: "execute"`) for task validation before real-world execution.
*   **Dynamic Schema Loading:** Add new capabilities instantly by dropping a JSON schema and shell script into the `plugins/` directory.

## 🛠️ Installation & Setup

Connecting your AI agent to AgentOS is incredibly simple. Choose your platform below.

### 1. Claude Desktop App
Add the following configuration to your `claude_desktop_config.json` file (typically located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "AgentOS": {
      "command": "python3",
      "args": [
        "/absolute/path/to/AgentOS-mcp-server/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/absolute/path/to/AgentOS-mcp-server"
      }
    }
  }
}
```

### 2. VS Code / Cursor
Navigate to your MCP Server settings within your editor and register a new standard `stdio` server:
*   **Name:** `AgentOS`
*   **Command:** `python3`
*   **Args:** `["/absolute/path/to/AgentOS-mcp-server/server.py"]`

### 3. Antigravity Agent
AgentOS was designed natively for the Polymath Swarm ecosystem. Simply insert the block above into `~/.gemini/config/mcp_config.json`.

## 🏗️ Architecture Design

AgentOS utilizes a robust internal dispatch architecture to manage OS execution:
1.  **ToolsManager:** Dynamically parses `plugins/*.json` to load schemas.
2.  **MCP Wrapper:** Exposes schemas securely via `mcp.types.Tool`.
3.  **DispatchNetwork:** Routes validated payloads to the underlying Bash implementations, trapping errors and passing outputs securely back to the LLM context.

> **Citation Note**: The Model Context Protocol implementation conforms to the standard specification outlined at [modelcontextprotocol.io](https://modelcontextprotocol.io).

## 🛡️ Security Disclaimer
This server exposes direct OS-level execution to language models. Always ensure you are running trusted plugins and utilizing `mode: "simulate"` for experimental tools.
