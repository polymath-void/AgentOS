# 🚀 SaaS-Agent v2 — Complete Quickstart

**From zero to production deployment in 5 steps.**

---

## 📦 What You Have

**13 files organized into a production-ready package:**

```
saas-agent-v2/
├── .github/workflows/test.yml          # CI/CD (GitHub Actions)
├── .gitignore                          # Git ignore rules
├── DEPLOYMENT_CHECKLIST.md             # Pre-push verification
├── GIT_SETUP_GUIDE.md                  # Git + GitHub instructions
├── README_PRODUCTION.md                # Main documentation
├── QUICKSTART.md                       # This file
├── requirements.txt                    # Python dependencies
├── install.sh                          # Auto-install script
│
├── models.py                           # Pydantic schemas (all types)
├── dependency_manager.py               # Auto-install mpv, yt-dlp, etc.
├── intent_router.py                    # Intent classification + auto-routing
├── tool_registry.py                    # 20+ tool definitions
├── tool_executor.py                    # Execute tools (3-tier fallback)
├── card_store.py                       # SQLite persistence + 7 pre-seeded cards
├── gemini_engine.py                    # Gemini 3 modes (function call, JSON, summarization)
├── main.py                             # FastAPI server + PWA serving
│
└── static/
    ├── app.html                        # PWA (chat + card dashboard, installable)
    ├── manifest.json                   # PWA metadata
    └── sw.js                           # Service Worker (offline support)
```

---

## ⚡ 5-Minute Setup

### Step 1: Download & Navigate

```bash
# Extract the saas-agent-v2 folder to your preferred location
cd saas-agent-v2
```

### Step 2: Install Dependencies

```bash
# Termux / Linux / macOS
bash install.sh

# This will:
# - Update package manager (pkg update on Termux)
# - Create Python virtual environment
# - Install google-genai, fastapi, uvicorn, pydantic, httpx
# - Auto-install system tools (mpv, yt-dlp, gcalcli, etc.)
# - Verify imports
```

### Step 3: Set API Key

```bash
# Get your Gemini API key from: https://aistudio.google.com/app/apikey
export GEMINI_API_KEY="your-actual-api-key-here"

# Optional: Save to ~/.bashrc / ~/.zshrc for persistence
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Start Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run
python main.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Press CTRL+C to quit
```

### Step 5: Open in Browser

```bash
# On your device:
http://localhost:8000

# Or from mobile/remote:
http://<your-device-ip>:8000
```

**Done!** 🎉 Chat with the agent. Create cards. Automate tasks.

---

## 🎯 What You Can Do Now

### Chat with Agent

```
You: "play world cup fifa song"
Agent: [Plays video on YouTube via yt-dlp + mpv]

You: "set my brightness to 70"
Agent: [Disables auto-brightness, sets to 70%]

You: "show me my recent missed calls"
Agent: [Queries call_log, returns missed calls]
```

### Create Custom Cards

**In the UI (right panel):**

1. Click "+ Create Card"
2. Enter name: "WiFi Manager"
3. Enter description: "Control WiFi and show network status"
4. Click "Create"
5. Agent auto-generates system_prompt → Card is live immediately

### Auto-Routing

- No need to manually select cards
- Agent classifies intent → picks best card automatically
- User can also select card manually from dashboard

---

## 🔧 Configuration

| Env Var | Default | Purpose |
|---------|---------|---------|
| `GEMINI_API_KEY` | *(required)* | Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | LLM model |
| `SAAS_AGENT_HOST` | `0.0.0.0` | Server bind address |
| `SAAS_AGENT_PORT` | `8000` | Server port |
| `SAAS_AGENT_CARD_STORE` | `~/.saas_agent/cards.db` | SQLite DB path |
| `LOG_LEVEL` | `INFO` | Python log level |

```bash
# Example: Bind to localhost, port 9000
export SAAS_AGENT_HOST="127.0.0.1"
export SAAS_AGENT_PORT="9000"
python main.py
```

---

## 📱 PWA Installation

The web app is installable on mobile & desktop:

### Chrome / Edge

1. Open `http://your-device:8000`
2. Address bar → **Install** button appears
3. Click → App installs to home screen
4. Works offline (cached app shell via Service Worker)

### Firefox / Safari

- Works as web app (limited offline support)
- Bookmark to home screen

---

## 🔌 API Endpoints

```
POST  /chat                    # Chat with agent (auto-routing)
GET   /health                  # Server status + tool availability
GET   /cards                   # List all cards
POST  /cards                   # Create card from prompt
GET   /cards/{id}              # Get single card
DELETE /cards/{id}             # Delete card
GET   /                        # Serve PWA
GET   /docs                    # Auto-generated API docs (Swagger)
```

**Example chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "task": "tell me about my battery",
    "card_id": null,
    "local_context": {}
  }'
```

---

## 🚀 Deploy to Production (GitHub)

### 1. Create GitHub Repo

```bash
# On GitHub.com:
# - New repo: saas-agent-v2
# - Add description, license, etc.
# Copy the HTTPS URL
```

### 2. Push to GitHub

```bash
git init
git add .
git commit -m "🚀 Initial commit: SaaS-Agent v2"
git remote add origin https://github.com/YOUR_USERNAME/saas-agent-v2.git
git branch -M main
git push -u origin main
```

### 3. Monitor CI/CD

- Go to **Actions** tab on GitHub
- Watch tests run automatically
- Green checkmark = all tests passed ✅

### 4. Share & Collaborate

Now your code is:
- ✅ Version controlled
- ✅ Backed up on GitHub
- ✅ Tested automatically
- ✅ Ready for contributions

For full git instructions, see **GIT_SETUP_GUIDE.md**.

---

## 🛡️ Pre-Production Checklist

Before pushing to production:

```bash
# 1. Run local tests
python -m py_compile *.py           # Syntax check
python -c "from main import app"    # Import check

# 2. Verify no secrets
grep -r "gemini-" *.py              # Should be empty
grep -r "api_key" *.py              # Should be empty

# 3. Check git status
git status                          # Should be clean

# 4. Test endpoints
curl http://localhost:8000/health   # Should return ok
```

Full checklist: **DEPLOYMENT_CHECKLIST.md**

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README_PRODUCTION.md** | Comprehensive reference (architecture, API, deployment) |
| **GIT_SETUP_GUIDE.md** | Step-by-step git + GitHub instructions |
| **DEPLOYMENT_CHECKLIST.md** | Pre-push verification items |
| **QUICKSTART.md** | This file — get running in 5 minutes |

---

## ⚙️ Architecture at a Glance

```
User Input (Chat UI)
       ↓
   Intent Router (classifies intent → picks card)
       ↓
   Gemini Engine (3 modes: function calling, JSON, summarization)
       ↓
   Tool Executor (tier fallback: root → ADB → local → cloud)
       ↓
   Output (reply + executed actions)
```

**3 Execution Modes:**

1. **Function Calling** (default) — Execute actions (play, call, files)
2. **JSON Structured** — Return structured data (call logs, file lists)
3. **Summarization** — Digest & summarize (email, notifications)

**7 Pre-seeded Domain Cards:**

1. System Agent (router)
2. Media Control (YouTube, music)
3. Call Manager (calls, call logs)
4. File Manager (read, write, sync)
5. Email Assistant (fetch, summarize)
6. Calendar Assistant (events, scheduling)
7. Notes Manager (write, read)
8. System Control (brightness, WiFi, notifications)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: google` | Run `bash install.sh` and activate venv |
| `GEMINI_API_KEY not set` | `export GEMINI_API_KEY="your-key"` |
| `Port 8000 already in use` | `export SAAS_AGENT_PORT=9000` |
| `grpcio compile error (Termux)` | `pkg install python-grpcio` before pip install |
| Service Worker not registering | Use HTTPS or localhost (http://127.0.0.1 works) |
| GitHub Actions failing | Check `.github/workflows/test.yml` logs in Actions tab |

---

## 📞 Next Steps

1. **Explore the UI** — Chat, create cards, automate tasks
2. **Read README_PRODUCTION.md** — Learn full architecture
3. **Follow GIT_SETUP_GUIDE.md** — Push to GitHub
4. **Run DEPLOYMENT_CHECKLIST.md** — Verify everything before production
5. **Monitor logs** — `tail -f logs/saas-agent.log` (optional setup)

---

## 🎓 Learning Resources

- **FastAPI docs** → `http://localhost:8000/docs`
- **Pydantic v2** → https://docs.pydantic.dev/
- **Google Gemini** → https://ai.google.dev/
- **Android ADB** → https://developer.android.com/studio/command-line/adb

---

## 🤝 Contributing

Want to extend SaaS-Agent? All files are modular:

- Add tools: Edit `tool_registry.py` + `tool_executor.py`
- Add execution modes: Extend `gemini_engine.py`
- Add pre-seeded cards: Edit `card_store.py`
- Improve UI: Edit `static/app.html`

---

## 📄 License

MIT — Use freely, modify, deploy.

---

**You now have a production-ready, git-integrated personal OS agent!** 

🚀 Deploy with confidence. Automate with power. Monitor with visibility.

**Ready?** Start the server and chat with your agent! 🤖
