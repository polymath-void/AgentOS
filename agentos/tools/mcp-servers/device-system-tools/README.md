# Device System Tools — MCP Server

Android device monitoring and management via /proc and /sys virtual filesystems.
Works on Termux and standard Linux.

## Quick Start

```bash
pip install "mcp[cli]"
python3 server.py
```

## Tools

| Tool | Description |
|:-----|:------------|
| `battery_status` | Level, charging state, health, temperature, voltage |
| `thermal_status` | All thermal zone temperatures with throttling alerts |
| `cpu_usage` | Per-core and aggregate CPU utilization (sampled) |
| `memory_usage` | RAM and swap stats from /proc/meminfo |
| `storage_info` | Filesystem usage for key partitions |
| `process_list` | Top N processes by CPU or memory |
| `kill_process` | Kill by PID (root required, system PIDs protected) |
| `device_summary` | All-in-one health snapshot |

## Security

- Read-only by default (procfs/sysfs reads)
- `kill_process` protects PID 1, zygote, system_server, etc.
- Only SIGTERM (15) and SIGKILL (9) allowed
- No arbitrary command execution

## Architecture

```
AI Agent ↔ stdio ↔ MCP Server ↔ /proc/*, /sys/class/*
                                    ↕ (kill only)
                              su -c kill -<sig> <pid>
```

## Requirements

- Python 3.10+, `mcp[cli]`
- No root for monitoring; Magisk `su` only for `kill_process`
