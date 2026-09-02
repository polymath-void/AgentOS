# Project Manager — MCP Server

Automates project directory indexing, chat session tracking, and workspace
scaffolding. Manages project-dir.md, sub-dir.md, and active_chats.md.

## Quick Start

```bash
pip install "mcp[cli]"
python3 server.py
```

## Tools

| Tool | Description |
|:-----|:------------|
| `list_projects` | Parse projects from project-dir.md |
| `get_project_tree` | Filtered directory tree (excludes build artifacts) |
| `update_project_index` | Rescan ~/Projects/ and regenerate index |
| `update_subtree` | Regenerate sub-dir.md for a project |
| `log_chat` | Record conversation ID + project tag |
| `get_active_chats` | List tracked chat sessions |
| `create_project` | Scaffold with templates (python/rust/node/web/native-ai) |

## Scaffold Templates

- **python** — src/, tests/, docs/, requirements.txt, .gitignore
- **rust** — src/main.rs, Cargo.toml, .gitignore
- **node** — src/index.js, package.json, .gitignore
- **web** — index.html, css/, js/, assets/
- **native-ai** — src/, wasm/, models/, bridge.py

## Security

- Path traversal protection (stays within ~/Projects/)
- Atomic writes with backup (.bak) to prevent corruption
- No code execution — only reads/writes markdown and creates dirs

## Architecture

```
AI Agent ↔ stdio ↔ MCP Server ↔ ~/Projects/*.md (read/write)
                                    ↕
                              os.walk (filtered)
```

## Requirements

- Python 3.10+, `mcp[cli]`
- No root required
