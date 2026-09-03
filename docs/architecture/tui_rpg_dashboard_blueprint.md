# ComputeRes OpenClaw Telemetry Dashboard Architecture Blueprint

## 1. Executive Summary
This document defines the production-grade architecture of the **ComputeRes OpenClaw Telemetry Dashboard** (`compute_res/telemetry/tui.py`). The dashboard provides a high-fidelity, real-time, terminal-native environment for observing, orchestrating, and inspecting decentralized AI swarm node activities, WASM fuel consumption, hyperbolic vector memory queries, and dynamic skill executions.

---

## 2. Technology Stack & Frameworks
- **UI Framework**: [Textual](https://textual.textualize.io/) (Python) – Native CSS layout engine, reactive component lifecycle, async workers, and keyboard/mouse navigation.
- **Visual Formatting**: [Rich](https://github.com/Textualize/rich) – Terminal markup, progress bars, tables, syntax highlighting, and color styling.
- **IPC Telemetry Transport**: ZeroMQ (`pyzmq.asyncio`) – Asynchronous PUB/SUB socket bound to `tcp://127.0.0.1:5562` for non-blocking stream ingestion.
- **Asynchronous Execution**: Python `asyncio` with Textual `@work` background tasks.

---

## 3. 3-Tab Architecture & Layout Specification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ComputeRes OpenClaw Frontend │ Decentralized Swarm Telemetry                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  [🏢 Virtual Office]    [💻 Skill Workbench]    [⚙️ System Console]           │
├─────────────────────────────────────────────────────────────────────────────┤
│ ⚡ WASM Fuel Engine & Capacity         │ 🧠 Hyperbolic Vector DB Telemetry  │
│ Capacity: 1,000,000 | Used: 142,500    │ Indexed Vectors: 14,280 | Depth: 12 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🏢 Virtual Office Grid Box (Dynamic Interacted Agents Only)                │
│ ┌───────────────────────────────────┬─────────────────────────────────────┐ │
│ │ 🤖 Claude (Architect Engine)       │ 🦉 Gemini (Vector Memory)           │ │
│ │ Status: WORKING                   │ Status: SPEAKING                    │ │
│ └───────────────────────────────────┴─────────────────────────────────────┘ │
├─────────────────────────────────────┬───────────────────────────────────────┤
│ 📊 ZeroMQ Intent Stream             │ 💬 Live Swarm Dialogue Feed           │
│ > execute_dynamic_python...         │ [Claude]: Re-routing ZeroMQ broker... │
└─────────────────────────────────────┴───────────────────────────────────────┘
```

### 3.1 Tab 1: 🏢 Virtual Office (Swarm Runtime & Telemetry)
The main operational view for monitoring swarm nodes and real-time execution telemetry.

1. **Top Telemetry Header Bar**:
   - **WASM Fuel Engine Card (`FuelEngineCard`)**: Tracks Total Fuel Capacity (1,000,000 Fuel), Used Fuel, Burn Rate (fuel/sec), and Bounded RAM Usage (512 MB).
   - **Hyperbolic Vector DB Card (`HyperbolicDBCard`)**: Displays Indexed Vectors count (14,280+), AST Tree Depth (12), Search Latency (ms), and Poincaré Ball distance metric ($d_H$).
2. **Virtual Office Floor Grid Box (`#active_agents_grid_box`)**:
   - Styled responsive grid container (`layout: grid; grid-size: 2; height: 1fr; border: round #38BDF8; background: #0D1117;`).
   - **Dynamic Interacted Agent Mounting**: Starts completely clean with an empty placeholder. Agent cards (`AgentCard`) are instantiated and mounted **ONLY when ZMQ telemetry receives active agent intents**, and idle agents dynamically unmount over time to keep the dashboard responsive and fresh.
   - **Vibrant Agent Palette**:
     - **Claude**: `#FF6B6B` (Architect Engine)
     - **Gemini**: `#38BDF8` (Bright Cyan – High Visibility contrast on dark backgrounds)
     - **Copilot**: `#4ADE80` (IDE Sidecar Bridge)
     - **Cursor**: `#FACC15` (CRDT AST Mutator)
     - **SwarmWorker**: `#C084FC` (Dynamic Swarm Node)
3. **Split Telemetry & Dialogue Feed**:
   - **Left Panel (35%)**: Real-time ZeroMQ intent stream log (`#telemetry_stream_log`).
   - **Right Panel (65%)**: Rich formatted live swarm dialogue feed (`#dialogue_log`).

---

### 3.2 Tab 2: 💻 Skill Workbench
The interactive workspace for editing skills and cataloging registered system tools.

1. **Active Skill Editor (`TextArea`)** (45% Width):
   - Full code editor widget with Python/YAML syntax highlighting for editing dynamic WASM skill executables. Fits perfectly to screen with `height: 1fr;`.
2. **Registered Tools & Skills Catalog (`DataTable`)** (55% Width):
   - Interactive table listing all native ComputeRes tools and registered MCP capabilities:
     - `execute_dynamic_python` (Core WASM Execution Sandbox)
     - `hyperbolic_vector_search` (Poincaré Ball Memory Indexer)
     - `crdt_ast_mutate` (Concurrent Multi-Agent AST File Mutator)
     - `wasm_fuel_sandbox` (Capability & RAM Bounding Oracle)
     - `webrtc_swarm_route` (Decentralized Peer-to-Peer Mesh)
     - `mcp_supabase_execute_sql` & `mcp_supabase_list_tables` (Supabase MCP Integration)
     - `compute_res_core_skill` (Core Workflow Skill)
   - Features `zebra_stripes = True`, row cursor highlighting, and layout refresh on `TabbedContent.TabActivated` events.
3. **Mermaid Flowchart Generator (`#mermaid_pane`)**:
   - Visual log rendering Mermaid syntax diagrams for multi-agent workflow pipelines.

---

### 3.3 Tab 3: ⚙️ System Console
- Low-level system event log capturing raw ZMQ socket frames (`tcp://127.0.0.1:5562`), IPC broker routing messages, and thread worker lifecycle events.

---

## 4. ZeroMQ Async Event Pipeline & Reactive Lifecycle

```
[ComputeRes Kernel / MCP Gateway]
              │ (PUB tcp://127.0.0.1:5562)
              ▼
    [listen_swarm_telemetry Worker]
              │
              ├──► Parse Intent Payload (JSON)
              ├──► Update FuelEngineCard & HyperbolicDBCard
              ├──► Query #active_agents_grid_box Container
              │         │
              │         ├── If Agent absent: Mount new AgentCard dynamically
              │         ├── If Agent present: Update reactive agent_status & active_task
              │         └── If Ambient/Idle: Dynamically unmount idle AgentCards to clear space
              │
              └──► Append formatted line to dialogue_log & telemetry_stream_log
```

---

## 5. Design Tokens & Styling Guide
- **Background**: `#0B0E14` (Deep Space Dark)
- **Container Surfaces**: `#161B22` / `#0D1117`
- **Borders**: `#30363D` (Muted), `#38BDF8` (Cyan Accent), `#58A6FF` (Blue Accent), `#D2A8FF` (Purple Accent)
- **Typography**: Rich bold/italic text markup with semantic color badges (`[bold cyan]● SPEAKING[/bold cyan]`, `[bold green]● EXECUTING[/bold green]`).
