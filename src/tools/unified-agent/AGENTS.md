# Unified Agent Architecture — Contextual Agentic Workflows Task Executor

The Unified Agent is a local LLM control plane and agentic execution platform for Termux/Android and Linux environments. It compiles complex user requests into **Contextual Agentic Workflows** featuring step-by-step variable propagation, condition evaluation, and agentic self-healing.

---

## Agents Overview

The Unified Agent system leverages a tiered agent architecture to manage tasks efficiently:

### 1. System Agent (Default)
The primary orchestrator that handles general, unclassified tasks. It has full access to the core tool registry and is responsible for overall workflow synthesis, managing global system state, and delegating specialized tasks.

### 2. Specialized AgentCards
These are domain-specific agents created and managed via the Agent Factory. Each `AgentCard` consists of a custom system prompt and a specific tool whitelist. Examples include:
- **Maintenance Agents:** Focused on cleaning files, managing logs, or clearing app data.
- **Diagnostics Agents:** Focused on analyzing system performance, process monitoring, or log inspection.
- **Utility Agents:** Focused on specific tasks like network connectivity, file manipulation, or user notifications.

By isolating functionality into specialized `AgentCards`, the system reduces prompt complexity, increases task accuracy, and improves execution safety.

---

## Core Concepts

### 1. Contextual Agentic Workflow Engine (`workflow_engine.py`)
Replaces flat static script arrays with an adaptive execution pipeline:
- **Variable Chaining:** Steps can store stdout into context variables (`capture_var: "ip"`) and pass them to subsequent steps (`${ip}`).
- **Condition Evaluation:** Pre-execution checks skip unnecessary or unmet steps dynamically.
- **Agentic Self-Healing (`auto-heal`):** When a step encounters an unexpected error or missing binary, the `WorkflowEngine` triggers `GeminiEngine.heal_step()` to diagnose the failure output and execute compensatory recovery actions in real-time.
- **Unified Tool & Root Dispatch:** Seamlessly routes raw shell commands (with `su` root support), file I/O, clipboard, and card management.

### 2. AgentCards & Factory Pattern
`AgentCards` are domain-specialized agent configurations persisted in SQLite (`~/.saas_agent/cards.db`).
- Contains custom system instructions and tool whitelists.
- **Factory Pattern:** The System Agent can create new domain-specialized `AgentCards` dynamically during workflow execution.

### 3. Gemini Engine & Multi-Model Routing (`gemini_engine.py`)
- **`gemini-2.5-flash`**: Used for complex workflow synthesis, structural system modifications, and self-healing analysis.
- **`gemini-2.5-flash-lite`**: Used for routine execution and high-frequency tasks.
- **Failover & Quota Protection:** Automated 429 rate-limit recovery and cross-model fallback routing.

### 4. Persistence & Task History (`card_store.py`)
- SQLite database (`~/.saas_agent/cards.db`) using WAL mode and thread locks.
- Persists `agent_cards` and execution history logs in `task_history`.
- Powers `/tasks/history` and `/state` API endpoints.

---

## Technical Stack

| Component | Technology |
|---|---|
| Control Plane | FastAPI (Python 3.11+) |
| LLM Engine | Google Gemini (`google-genai` SDK) |
| Workflow Engine | `WorkflowEngine` (Contextual variable chaining + Self-healing) |
| Persistence | SQLite (`~/.saas_agent/cards.db`) |
| CLI Client | Bash (`agent_cli.sh`) |
| Environment | Linux / Termux (Rooted Android) |
