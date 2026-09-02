# Swarm Playground Gateway — MCP Server

A Model Context Protocol (MCP) server that bridges the Neural Agent Swarm
Playground into AI agent workflows via stdio transport.

## Quick Start

```bash
# Install dependency
pip install "mcp[cli]"

# Test standalone
python3 server.py
```

## Installation Guides

Detailed, OS-specific setup instructions:

| Platform | Guide |
|:---------|:------|
| 🤖 Android (Termux) | [skills/install-termux/SKILL.md](skills/install-termux/SKILL.md) |
| 🐧 Linux | [skills/install-linux/SKILL.md](skills/install-linux/SKILL.md) |
| 🍎 macOS | [skills/install-macos/SKILL.md](skills/install-macos/SKILL.md) |
| 🪟 Windows | [skills/install-windows/SKILL.md](skills/install-windows/SKILL.md) |

## Registration

Already registered in `~/.gemini/config/mcp_config.json`. Antigravity will
auto-start this server when MCP tools are needed.

## Tools Exposed

| Tool | Description |
|:-----|:------------|
| `execute_code` | Run Python in sandboxed CodeExecutorActor |
| `reason` | Multi-step logic via LogicReasoningActor + PromptMutator |
| `scrape_web` | Delegate web scraping to WebScraperActor |
| `broadcast_mesh` | Send P2P messages across mesh (port 8989) |
| `dispatch_task` | Generic task dispatcher with custom payloads |
| `search_memory` | Query neuro-symbolic episodic memory graph |
| `recent_memories` | Fetch latest N memory events |
| `list_actors` | Get live state of all swarm actors |
| `evolve_skill` | Trigger EvolvOS skill synthesis |
| `playground_health` | Check if swarm API is reachable |

## Resources

| URI | Description |
|:----|:------------|
| `swarm://config` | Current configuration and endpoint map |

## Architecture

```
Antigravity Agent
    ↕ stdio (JSON-RPC)
MCP Server (this)
    ↕ HTTP (urllib)
Swarm Playground Flask API (127.0.0.1:5000)
    ↕ Internal
Actors / Memory / Mesh / EvolvOS
```

## Dependencies

- Python 3.10+
- `mcp` Python SDK (`pip install "mcp[cli]"`)
- Swarm Playground running on port 5000
