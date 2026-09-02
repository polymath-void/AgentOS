# Native AI Engine Bridge — MCP Server

Manages the Wake→Execute→Sleep lifecycle of the native_ai_engine binary,
allowing AI agents to invoke the local phi-3-mini model through the WASM bridge.

## Quick Start

```bash
pip install "mcp[cli]"
python3 server.py
```

## Tools

| Tool | Description |
|:-----|:------------|
| `wake_engine` | Start engine via Magisk `su -c start` |
| `execute_prompt` | Send prompt to phi-3 via WASM shared memory |
| `sleep_engine` | Graceful TCP shutdown + `su -c stop` |
| `prompt_and_sleep` | Atomic: wake → execute → sleep in one call |
| `engine_status` | PID, CPU, memory, uptime of running engine |
| `model_info` | Model path, quantization, file size, mmap status |

## Safety

- atexit handler guarantees engine shutdown on server exit
- Only whitelisted `su` commands (`start/stop native_ai_engine`)
- Single-threaded execution — concurrent prompts are rejected
- Configurable timeout (default 60s) prevents infinite hangs

## Architecture

```
AI Agent ↔ stdio ↔ MCP Server ↔ TCP:57160 ↔ WASM Bridge ↔ phi-3-mini
                                    ↕
                              su -c start/stop
```

## Requirements

- Magisk root, `native_ai_engine` overlay deployed
- Model at `~/models/phi-3-mini-q4.gguf`
- Python 3.10+, `mcp[cli]`
