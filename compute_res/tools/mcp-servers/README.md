# MCP Server Suite

A collection of 5 Model Context Protocol (MCP) servers designed for the
Native AI Swarm Architecture on Android Termux. All servers use Python + stdio transport.

## Servers

| # | Server | Tools | Root? | Platform |
|:--|:-------|:-----:|:-----:|:---------|
| 1 | [swarm-playground-gateway](swarm-playground-gateway/) | 10 | No | Cross-platform |
| 2 | [native-ai-engine-bridge](native-ai-engine-bridge/) | 6 | Yes | Termux (Android) |
| 3 | [device-system-tools](device-system-tools/) | 8 | Kill only | Termux / Linux |
| 4 | [project-manager](project-manager/) | 7 | No | Cross-platform |
| 5 | [sqlite-database-tools](sqlite-database-tools/) | 7 | No | Cross-platform |

**Total: 38 tools** available to AI agents.

## Installation

See [skills/install-all-platforms/SKILL.md](skills/install-all-platforms/SKILL.md) for the
unified cross-platform setup guide (Termux, Linux, macOS, Windows).

Quick start:
```bash
pip install "mcp[cli]"
# All servers are registered in ~/.gemini/config/mcp_config.json
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Antigravity Agent                     │
├─────────────────────────────────────────────────────────┤
│  stdio          stdio          stdio        stdio       │
│    ↕               ↕              ↕            ↕        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ │ Swarm    │ │ Engine   │ │ Device   │ │ Project  │   │
│ │ Gateway  │ │ Bridge   │ │ Tools    │ │ Manager  │   │
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│      │             │            │             │         │
│  HTTP:5000    TCP:57160    /proc /sys     ~/Projects/   │
│      ↓             ↓            ↓             ↓         │
│  Flask API    WASM Bridge   Kernel VFS    Filesystem    │
├─────────────────────────────────────────────────────────┤
│                    stdio                                 │
│                      ↕                                   │
│              ┌──────────────┐                            │
│              │ SQLite Tools │                            │
│              └──────┬───────┘                            │
│                     ↓                                    │
│                  *.db files                              │
└─────────────────────────────────────────────────────────┘
```

## Design Docs

Detailed specifications in [../.agents/mcp-designs/](../.agents/mcp-designs/):
- [01-native-ai-engine-bridge.md](../.agents/mcp-designs/01-native-ai-engine-bridge.md)
- [02-swarm-playground-gateway.md](../.agents/mcp-designs/02-swarm-playground-gateway.md)
- [03-device-system-tools.md](../.agents/mcp-designs/03-device-system-tools.md)
- [04-project-manager.md](../.agents/mcp-designs/04-project-manager.md)
- [05-sqlite-database-tools.md](../.agents/mcp-designs/05-sqlite-database-tools.md)

## Dependencies

All servers require only:
- Python 3.10+
- `mcp[cli]` Python SDK
- Standard library (urllib, sqlite3, os, pathlib)

No external packages beyond `mcp` are needed.
