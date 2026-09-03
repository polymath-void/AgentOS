# Agent Rules

- **Documentation Obligation:** Agents MUST update `CONTEXT.MD` and `AGENTS.MD` with any new knowledge, architectural changes, or workflow improvements immediately following the execution of tasks.
- **Project Memory:** Maintain project-specific memory in the designated private project memory folder (not committed).
- **Communication:** Provide high-signal output, minimize filler, and follow the established lifecycle (Research -> Strategy -> Execution).
- **Compliance:** All agents are bound by the project mandates in `GEMINI.md`.
- **Workflow:** Implemented ReAct orchestrator loop for Gemini tool calls using Rust/tokio.
- **Workflow:** Implemented dual-layer memory system (SQLite for long-term facts, sliding buffer for short-term chat context).
- **Workflow:** Implemented Dynamic Tool Factory allowing self-authoring and registering of new tools at runtime.
- **Workflow:** Implemented Recursive Swarm Delegation Router (Master -> Sub-Agent -> Micro-Agent) with programmatic Validation Gateway for complex task management.
- **Workflow:** Implemented Skill Adapting Architecture via `learn_skill` for permanent methodology storage.
- **Workflow:** Implemented Context Ingestion Engine (Web, RSS, Workspace, Git) for environmental awareness.
