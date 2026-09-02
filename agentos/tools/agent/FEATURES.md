# Functionality & Architectural Overview

The Polymath-Void Agent is structured to handle high-concurrency, latency-sensitive tasks in restricted environments.

## Core Modules

| Module | Functionality |
| :--- | :--- |
| `src/main.rs` | Entry point, orchestrator lifecycle management (Tokio runtime), and UI/Agent IPC. |
| `src/ui/` | Ratatui-based responsive terminal UI with Swarm Telemetry. |
| `src/memory/` | Dual-layer persistence: SQLite (Long-term) + sliding buffer (Short-term context) + `PromptCompiler` for local distillation. |
| `src/tools/` | Dynamic Tool Factory for self-authoring and registering capabilities at runtime. |
| `context_daemon.py` | Python sidecar for sub-millisecond local codebase indexing and querying via FastAPI. |

## Slash Command Reference

| Command | Action |
| :--- | :--- |
| `/config local_model <true/false>` | Toggles local edge inference. Triggers background download if necessary. |
| `/config trust <true/false>` | Toggles security/execution permissions. |
| `/editor` | Opens a system editor for complex prompt construction. |
| `/agents` | Lists currently active swarm agents. |
| `/plan` | Initializes the multi-step planning workflow. |
| `/implement` | Executes the implemented solution plan. |
