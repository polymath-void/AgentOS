# SaaS-Agent

Local LLM control plane and execution agent. Runs on Linux / rooted Android (Termux).

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic v2 |
| LLM | Google Gemini 2.5 Flash (google-generativeai SDK) |
| Persistence | SQLite (`~/.saas_agent/cards.db`) |
| Client | Bash (`agent_cli.sh`) |

## Use Cases

The Unified Agent is designed to bridge the gap between high-level natural language instructions and low-level system operations in constrained environments (Termux/Android/Linux).

- **Automated System Administration:** Perform routine maintenance like clearing caches, managing processes, monitoring disk usage, or toggling system services via natural language.
- **Dynamic Workflow Automation:** Chain complex sequences of commands where the output of one step (e.g., finding a process ID) is used as an input for the next (e.g., killing that specific process).
- **Self-Healing Infrastructure:** Automatically detect when a command fails (e.g., file not found, permission denied), analyze the error, and execute a repair step (e.g., requesting root permissions or locating an alternative file path).
- **Personalized Agent Factory:** Create, persist, and manage specialized "AgentCards"—domain-specific system prompts with restricted tool access—allowing you to build and switch between custom assistants for different operational domains (e.g., "Network Tool," "File Manager," "System Optimizer").
- **Constraint-Aware Execution:** Operate safely within mobile and server environments by utilizing a restricted tool registry and LLM-based verification of shell commands before execution.

---

## Setup

```bash
# 1. Install Python deps
pip install -r requirements.txt

# 2. Set your Gemini API key
export GEMINI_API_KEY="your-key-here"

# 3. Start the server
python main.py

# 4. In another terminal, make agent_cli executable
chmod +x agent_cli.sh
```

---

## Usage

```bash
# Run a task (System Agent by default)
./agent_cli.sh "list all running processes and show top 5 by CPU"

# Check server health
./agent_cli.sh --health

# List all saved AgentCards
./agent_cli.sh --list-cards

# Run a task with a specific AgentCard
./agent_cli.sh --card <uuid> "clear all notifications"

# Use a different backend URL
SAAS_AGENT_URL=http://192.168.1.10:8000 ./agent_cli.sh "check disk usage"
```

---

## Factory Pattern

The System Agent can create new specialised AgentCards on the fly:

```bash
./agent_cli.sh "Create a new agent card called Notification Cleaner \
  that clears all Android notifications using root shell commands"
```

The response will include the new card's UUID. Use it for all future
notification tasks — the card carries a specialised system prompt
so the LLM needs less instruction each time.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `SAAS_AGENT_HOST` | `127.0.0.1` | Server bind host |
| `SAAS_AGENT_PORT` | `8000` | Server bind port |
| `SAAS_AGENT_CARD_STORE` | `~/.saas_agent/cards.db` | SQLite DB path |
| `SAAS_AGENT_URL` | `http://127.0.0.1:8000` | CLI client target URL |
| `SAAS_AGENT_CARD` | *(empty)* | Default card UUID for CLI |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## File Map

```
saas-agent/
├── models.py          # Pydantic schemas (AgentCard, TaskRequest, AgentResponse)
├── tool_registry.py   # Tool definitions for Gemini function binding
├── card_store.py      # SQLite persistence layer for AgentCards
├── tool_executor.py   # Tool dispatch and execution
├── gemini_engine.py   # GeminiEngine: prompt assembly + LLM call + response parse
├── main.py            # FastAPI server + /execute pipeline
├── agent_cli.sh       # Bash client
└── requirements.txt
```

---

## API Reference

### `POST /execute`
```json
{
  "task": "string",
  "card_id": "uuid | null",
  "local_context": {}
}
```

### `GET /cards` — list all cards
### `GET /cards/{id}` — get one card
### `DELETE /cards/{id}` — delete a card
### `GET /health` — server status
