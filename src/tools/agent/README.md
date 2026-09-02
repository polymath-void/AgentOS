<div align="center">
  <pre>
  ____       _                       _   _    
 |  _ \ ___ | |_   _ _ __ ___   __ _| |_| |__ 
 | |_) / _ \| | | | | '_ ` _ \ / _` | __| '_ \
 |  __/ (_) | | |_| | | | | | | (_| | |_| | | 
 |_|   \___/|_|\__, |_| |_| |_|\__,_|\__|_| |_
               |___/                          
  </pre>
  
  **A highly-optimized, native Rust Autonomous Agent Swarm designed explicitly for Termux and edge computing.**
  
  [![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white)](#)
  [![Termux](https://img.shields.io/badge/termux-000000?style=for-the-badge&logo=termux&logoColor=white)](#)
  [![Ratatui](https://img.shields.io/badge/TUI-Ratatui-blue?style=for-the-badge)](#)
</div>

---

## 🌌 What is Polymath-Void?

**Polymath-Void** (or simply **Polymath Swarm**) is a next-generation, deeply hierarchical AI Agent architecture written purely in Rust. It utilizes a state-of-the-art **Terminal UI (TUI)** built on Ratatui to deliver a highly interactive, animated, and responsive dashboard natively within Termux or any Linux terminal.

Instead of running a single bloated agent, Polymath uses a **Recursive Swarm Architecture**. It enforces a strict **Zen Metacognition Protocol**, aggressively breaking down complex problems across four distinct autonomous tiers:

`Polymath (Main) -> Master Agent -> Sub Agent -> Micro Agent`

By combining SQLite-backed Long-Term Memory, dynamic prompt distillation, and aggressive context pruning, Polymath is arguably the most efficient and robust AI swarm available for edge environments.

---

## ✨ Core Features (SEO Optimized)
- **Native Ratatui TUI Dashboard**: A stunning, glitch-free terminal interface with auto-scrolling, animated telemetry, and real-time swarm tracking.
- **Recursive Swarm Intelligence**: Tasks are mathematically delegated down a rigid 4-tier chain to prevent hallucination and improve execution accuracy.
- **Zen Metacognition Protocol**: Forces agents into a "Step-Back, Chain-of-Thought, Critique" loop before writing code or executing tools.
- **Persistent SQLite Memory**: Automatically archives successful problem resolutions and context into a local `polymath_agent_memory.db` for instant recall on future boots.
- **Interactive Command Deck**: Use `/slash` commands with predictive typing to instantly configure APIs, toggle models, change themes, or limit recursive depth on the fly.
- **Customizable Theming Engine**: Hot-swap aesthetic colorways natively (`Matrix`, `Dracula`, `Synthwave`).

---

## 🚀 Installation Guide

Because Polymath-Void is written in Rust, it is highly portable. It is deeply optimized for **Android Termux**, but will easily compile on macOS, Linux, and Windows WSL.

### 1. Prerequisites
Ensure you have Rust and essential build tools installed.
```bash
# On Termux
pkg update && pkg upgrade
pkg install rust binutils openssl-dev sqlite
```

### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-username/polymath-void-agent.git
cd polymath-void-agent

# Make the boot script executable
chmod +x start.sh
```

### 3. Launch the Swarm
Instead of dealing with noisy compilation logs, launch the app directly via the provided boot script to experience the animated boot sequence:
```bash
sh start.sh
```

---

## 📖 User Guide

### Setting up your API Key
Once you boot the TUI, you can dynamically securely cache your API key without ever leaving the dashboard.
Type the following into the command deck:
```
/config api YOUR_GEMINI_API_KEY
```
*Note: This automatically creates a `.env` file in the root directory. Polymath will remember this key on your next boot.*

### Slash Commands & Configurations
As you type `/` in the input bar, a smart auto-complete box will hover above your cursor. Use the **Up/Down Arrows** to navigate, and **Tab/Enter** to apply configurations.

| Command | Description |
|---|---|
| `/config theme matrix` | Switches the dashboard to Hacker Green. |
| `/config theme dracula` | Switches the dashboard to Neon Pink & White. |
| `/config theme synthwave` | Switches the dashboard to Hot Magenta & Cyan. |
| `/config max_depth <num>` | Caps the agent's recursive spawning depth (default: 3). |
| `/config prune_memory <bool>` | Toggles aggressive LT memory context pruning to save tokens. |
| `/config timeout <secs>` | Adjusts the API network timeout limit. |
| `/config local_model <bool>` | Toggles routing to an experimental local `.gguf` model. |

### Global Alias (Optional but Recommended)
To boot Polymath from anywhere on your device, append this alias to your `.bashrc`:
```bash
echo 'alias polymath="sh /data/data/com.termux/files/home/Projects/local/agent/start.sh"' >> ~/.bashrc
source ~/.bashrc
```
Now, simply typing `polymath` will spawn the void swarm instantly!

---
*Architected for the Edge. Built in Rust.*
