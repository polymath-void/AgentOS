# SaaS-Agent v2 — Production Deployment Guide

**Deterministic execution-based personal OS agent** for rooted Android/Linux with auto-routing, 3 execution modes, and pre-seeded domain cards.

## Quick Start

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/saas-agent-v2.git
cd saas-agent-v2

# 2. Install
bash install.sh

# 3. Activate venv
source venv/bin/activate

# 4. Set API key
export GEMINI_API_KEY="your-gemini-api-key"

# 5. Start server
python main.py

# 6. Open browser
# http://localhost:8000
```

## Architecture

| Layer | Technology |
|---|---|
| UI | PWA (HTML5 + Service Worker) — installable from Chrome |
| Backend | FastAPI + Pydantic |
| LLM | Google Gemini 2.5 Flash (google-genai >= 1.0) |
| Persistence | SQLite (`.saas_agent/cards.db`) |
| Auto-routing | Intent classifier + pre-seeded domain cards |
| Tool execution | Tier-based fallback (Root→ADB→Local→Cloud) |

## Core Features

### 3 Execution Modes

1. **Function Calling** — Actions (play, call, files, system control)
2. **JSON Structured** — Data retrieval (call logs, file lists)
3. **Summarization** — Email/notification digest (1M token window)

### Pre-seeded Domain Cards (auto-routing)

- **System Agent** — Default router (classifies intent → routes to specialized card)
- **Media Control** — Play YouTube videos/music
- **Call Manager** — Make calls, fetch call logs
- **File Manager** — List, read, write, search, sync files
- **Email Assistant** — Fetch, summarize, send emails
- **Calendar Assistant** — Check events, schedule meetings
- **Notes Manager** — Write/read timestamped notes
- **System Control** — Brightness, WiFi, notifications, monitoring

### Tool Execution Tiers

```
Tier 1: Root (su -c) — system settings, calls, notifications
Tier 2: ADB (adb shell) — Android remote commands
Tier 3: Local tools — mpv, gcalcli, jrnl
Tier 4: Cloud APIs — YouTube, Gmail, Google Calendar
```

## Chat Interface

**Left panel:** Chat with agent (auto card routing or manual selection)
**Right panel:** Card management (list, create, delete, select)

User can:
- Chat naturally: agent auto-picks best card
- Select a card manually
- Create new cards on-the-fly via "Create Card" modal

## Environment Variables

```bash
export GEMINI_API_KEY="your-api-key"           # Required
export GEMINI_MODEL="gemini-2.5-flash"         # Default
export SAAS_AGENT_HOST="0.0.0.0"               # Bind address
export SAAS_AGENT_PORT="8000"                  # Port
export SAAS_AGENT_CARD_STORE="~/.saas_agent/cards.db"  # DB path
export LOG_LEVEL="INFO"                        # Log level
```

## File Structure

```
saas-agent-v2/
├── .github/workflows/test.yml      # CI/CD pipeline
├── .gitignore
├── README_PRODUCTION.md            # This file
├── requirements.txt
├── install.sh
├── models.py                       # Pydantic schemas
├── dependency_manager.py           # Auto-install tools
├── intent_router.py                # Intent classification
├── tool_registry.py                # All 20+ tool definitions
├── tool_executor.py                # Execute tools with tier fallback
├── card_store.py                   # SQLite + pre-seeded cards
├── gemini_engine.py                # 3 execution modes
├── main.py                         # FastAPI server
└── static/
    ├── app.html                    # PWA + chat + dashboard
    ├── manifest.json               # PWA manifest
    └── sw.js                       # Service worker
```

## API Endpoints

```
POST  /chat                 # Chat endpoint (auto-routing)
GET   /cards                # List all cards
POST  /cards                # Create card from prompt
GET   /cards/{id}           # Get card
DELETE /cards/{id}          # Delete card
GET   /health               # Health check + tool status
GET   /                     # Serve PWA
```

## Auto-install Dependencies

On startup, `dependency_manager.py` checks for required tools and installs missing ones:

- `mpv` — video/audio player
- `yt-dlp` — YouTube downloader
- `gcalcli` — Google Calendar CLI
- `jrnl` — note-taking
- `curl`, `jq`, `sqlite3` — utilities
- `rclone` — cloud sync

Fallback graceful warnings if tools can't be installed.

## Card Creation Flow

User describes a task → Gemini generates system_prompt → Card is saved and immediately available.

Example:
```
User: "Create a card called 'WiFi Manager' that controls WiFi and shows network status"
Agent: [Calls create_agent_card with AI-generated system_prompt]
Result: New card appears in dashboard, ready to use
```

## Permissions & Safety

- **Root access:** Requires Magisk/su (optional, degrades gracefully if not available)
- **ADB:** Connects to Android device (optional)
- **OAuth:** Gmail/Google Calendar require browser auth on first use
- **Constraints:** Agent cannot modify `/system`, `/proc`, `/dev` — uses overlays in `/data/local` or `~/.config`

## GitHub Actions CI/CD

Pipeline runs on:
- Push to `main` or `develop`
- Pull requests

Checks:
- Python syntax
- Module imports
- Linting (flake8)

## Deployment

### Local Termux

```bash
bash install.sh
source venv/bin/activate
export GEMINI_API_KEY="..."
python main.py
```

Server listens on `http://localhost:8000`.

### Remote Server

```bash
# Install on Ubuntu/Debian
sudo apt update && sudo apt install python3-pip python3-venv
bash install.sh
export GEMINI_API_KEY="..."
python main.py --host 0.0.0.0
```

### Docker (optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV GEMINI_API_KEY=""
CMD ["python", "main.py"]
```

## Troubleshooting

### `grpcio` compile errors on Termux

Solution: `pkg install python-grpcio` before `pip install -r requirements.txt`.

### GeminiEngine initialization fails

Check `GEMINI_API_KEY` is set and valid.

### Tool execution fails

Check `/var/log/saas-agent.log` or increase `LOG_LEVEL=DEBUG`.

## Security

- Never commit `.env` or `GEMINI_API_KEY` to git
- Use `.gitignore` to exclude sensitive files
- Store tokens in `~/.config/saas-agent/` (user-private directory)
- Audit logging enabled by default

## Production Checklist

- [ ] API key stored in secure vault (not git)
- [ ] Firewall rules: only allow trusted IPs
- [ ] HTTPS reverse proxy (nginx/caddy) if exposed
- [ ] Database backups enabled (SQLite WAL mode)
- [ ] Logging to file + rotation setup
- [ ] Health checks configured
- [ ] Monitoring/alerting enabled
- [ ] GitHub Actions CI/CD passing

## Support & Contribution

Issues, PRs, and feature requests welcome!

---

**Built with:** FastAPI, Pydantic v2, Google Gemini 2.5 Flash, SQLite

**License:** MIT
