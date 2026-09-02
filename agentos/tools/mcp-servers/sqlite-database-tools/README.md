# SQLite Database Tools — MCP Server

Safe, structured access to local SQLite databases. Specialized for the
Swarm Playground's episodic memory but supports any project database.

## Quick Start

```bash
pip install "mcp[cli]"
python3 server.py
```

## Tools

| Tool | Description |
|:-----|:------------|
| `query_db` | Execute SELECT queries with parameterized inputs |
| `list_tables` | List tables with row counts |
| `describe_table` | Column schema, types, constraints, CREATE SQL |
| `search_episodic_memory` | Keyword search across memory.db |
| `insert_memory` | Write State-Action-Observation triplet (only write op) |
| `db_stats` | File size, table count, WAL status, page info |
| `export_query` | Save query results as JSON or CSV |

## Security

- **Read-only by default** — `sqlite3` connects with `?mode=ro` URI
- **SQL injection prevented** — all inputs use `?` parameterized queries
- **Dangerous ops blocked** — DROP, ALTER, TRUNCATE, ATTACH rejected at all times
- **Path restricted** — only databases under `~/Projects/` are accessible
- **Row limits** — queries capped at 1000 rows to prevent OOM
- **WAL mode** — concurrent reads don't block Playground writes

## Default Database

```
~/Projects/local/agents-playground/src/memory.db
```

Expected schema:
- `episodes(id, state, action, observation, timestamp, metadata)`
- `keywords(id, episode_id, keyword, weight)`

## Architecture

```
AI Agent ↔ stdio ↔ MCP Server ↔ sqlite3 ↔ *.db files
                        ↕
                  SQL Validator (blocked patterns)
```

## Requirements

- Python 3.10+, `mcp[cli]`
- stdlib `sqlite3` only — no external packages
- No root required
