# Project Context

- **Goal:** Build a production-grade native aarch64 binary.
- **Technology:** Rust, tokio.
- **Current Status:** Recursive Swarm Architecture with Validation Gateway implemented.
- **Architecture:** Single binary, no bloated interpreters.
- **Dependencies:** 
  - `tokio` (runtime)
  - `reqwest` (HTTP)
  - `serde`/`serde_json` (serialization)
  - `dotenvy` (config)
  - `rusqlite` (persistent storage)
  - `scraper` (HTML parsing)
  - `rss` (RSS parsing)
  - `ignore` (file system traversal)
  - IPC broker integration (VoidTerm)
- **Tooling:** Dynamic Tool Factory (~/.polymath_agent/tools/)
- **Orchestration:** Recursive Swarm Delegation Router (Master -> Sub-Agent -> Micro-Agent) with programmatic Validation Gateway.
- **Cognition:** Skill Adapting Architecture via `learn_skill` and persistent SQLite storage.
- **Environment:** Context Ingestion Engine (Web, RSS, Workspace, Git).
