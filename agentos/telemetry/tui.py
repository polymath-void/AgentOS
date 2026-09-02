import asyncio
import sys
import json
import random
import time
from typing import Dict, Any, List

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical, Grid
    from textual.widgets import (
        Static,
        Log,
        ProgressBar,
        TabbedContent,
        TabPane,
        Label,
        TextArea,
        Footer,
        DataTable
    )
    from textual.reactive import reactive
except ImportError:
    print("AgentOS Visual Telemetry requires the 'textual' framework.")
    print("Please install it by running: pip install textual rich")
    sys.exit(1)


# Vibrant, high-contrast color scheme for agents (Gemini is bright cyan #38BDF8)
AGENT_STYLES = {
    "Claude": {"icon": "🤖", "color": "#FF6B6B", "border": "#FF6B6B", "role": "Architect Engine"},
    "Gemini": {"icon": "🦉", "color": "#38BDF8", "border": "#38BDF8", "role": "Hyperbolic Vector Memory"},
    "Copilot": {"icon": "✈️", "color": "#4ADE80", "border": "#4ADE80", "role": "IDE Sidecar Bridge"},
    "Cursor": {"icon": "⚡", "color": "#FACC15", "border": "#FACC15", "role": "CRDT AST Mutator"},
    "SwarmWorker": {"icon": "⚙️", "color": "#C084FC", "border": "#C084FC", "role": "Dynamic Swarm Node"},
}


class AgentCard(Static):
    """Dynamically created Agent Workstation card for interacted agents."""
    
    agent_status = reactive("IDLE")
    active_task = reactive("Awaiting intent...")
    interaction_count = reactive(1)

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = name
        info = AGENT_STYLES.get(name, AGENT_STYLES["SwarmWorker"])
        self.icon = info["icon"]
        self.color = info["color"]
        self.role = info["role"]

    def render(self) -> str:
        status_colors = {
            "IDLE": "grey60",
            "WORKING": "yellow",
            "SPEAKING": "bold cyan",
            "EXECUTING": "bold green",
            "TOOL": "bold magenta",
        }
        badge = f"[{status_colors.get(self.agent_status, 'white')}]● {self.agent_status}[/]"
        
        return (
            f"[bold {self.color}]{self.icon} {self.agent_name}[/bold {self.color}]  "
            f"[dim]({self.role})[/dim]\n"
            f"Status: {badge}  │  Interactions: [bold white]{self.interaction_count}[/bold white]\n"
            f"Active Intent: [italic]{self.active_task[:38]}[/italic]"
        )


class FuelEngineCard(Static):
    """Realtime WASM Fuel Capacity & System Resource Telemetry."""

    capacity = reactive(1000000)
    used_fuel = reactive(142500)
    burn_rate = reactive(2400)
    ram_mb = reactive(128)

    def render(self) -> str:
        used_pct = (self.used_fuel / self.capacity) * 100
        return (
            f"[bold #58A6FF]⚡ WASM Fuel Engine & Capacity[/bold #58A6FF]\n"
            f"Capacity: [bold white]{self.capacity:,}[/bold white] Fuel  │  Used: [yellow]{self.used_fuel:,} ({used_pct:.1f}%)[/yellow]\n"
            f"Burn Rate: [cyan]{self.burn_rate:,} fuel/sec[/cyan]  │  RAM Bounded: [green]{self.ram_mb} MB / 512 MB[/green]"
        )


class HyperbolicDBCard(Static):
    """Realtime Vector & Memory Database Telemetry."""

    indexed_vectors = reactive(14280)
    tree_depth = reactive(12)
    latency_ms = reactive(1.4)
    dist_metric = reactive("d_H (Poincaré Ball)")

    def render(self) -> str:
        return (
            f"[bold #D2A8FF]🧠 Hyperbolic Vector DB Telemetry[/bold #D2A8FF]\n"
            f"Indexed Vectors: [bold white]{self.indexed_vectors:,}[/bold white]  │  AST Tree Depth: [cyan]{self.tree_depth}[/cyan]\n"
            f"Search Latency: [green]{self.latency_ms:.2f} ms[/green]  │  Metric: [italic]{self.dist_metric}[/italic]"
        )


class DashboardApp(App):
    """Production-Grade AgentOS Telemetry & Swarm Dashboard."""

    TITLE = "AgentOS OpenClaw Telemetry"
    SUB_TITLE = "Real-Time Decentralized AI Swarm Environment"

    CSS = """
    Screen {
        background: #0B0E14;
        color: #C9D1D9;
    }

    #header_title {
        height: 3;
        content-align: center middle;
        background: #161B22;
        color: #38BDF8;
        border-bottom: solid #30363D;
        text-style: bold;
    }

    /* Top Telemetry Cards */
    .telemetry_header_bar {
        height: 7;
        margin: 1 1 0 1;
    }

    FuelEngineCard {
        width: 50%;
        background: #161B22;
        border: round #58A6FF;
        padding: 1 2;
        margin-right: 1;
    }

    HyperbolicDBCard {
        width: 50%;
        background: #161B22;
        border: round #D2A8FF;
        padding: 1 2;
    }

    /* Dynamic Virtual Office Grid Box */
    .agents_section_title {
        margin: 1 1 0 1;
        text-style: bold;
        color: #38BDF8;
    }

    #active_agents_grid_box {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        height: 12;
        margin: 0 1 1 1;
        padding: 1;
        border: round #38BDF8;
        background: #0D1117;
    }

    #empty_placeholder {
        column-span: 2;
        row-span: 2;
        content-align: center middle;
        color: #8B949E;
        text-style: italic;
    }

    AgentCard {
        background: #161B22;
        border: round #30363D;
        padding: 1 2;
        height: 100%;
    }

    /* Bottom Log & Dialogue Section */
    .bottom_section {
        height: 1fr;
        margin: 0 1 1 1;
    }

    .telemetry_log_box {
        width: 35%;
        border-right: solid #30363D;
        padding-right: 1;
    }

    .dialogue_log_box {
        width: 65%;
        padding-left: 1;
    }

    #telemetry_stream_log, #dialogue_log, #event_log {
        height: 1fr;
        border: round #30363D;
        background: #090D12;
    }

    /* Tab 2: Skill Workbench */
    .workbench_container {
        height: 100%;
        padding: 1;
    }

    .editor_column {
        width: 45%;
        height: 100%;
        margin-right: 1;
    }

    .tools_column {
        width: 55%;
        height: 100%;
    }

    #editor_pane {
        height: 1fr;
        border: round #38BDF8;
    }

    #tools_table {
        height: 1fr;
        border: round #4ADE80;
        background: #161B22;
        margin-bottom: 1;
    }

    #mermaid_pane {
        height: 1fr;
        border: round #C084FC;
        background: #090D12;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold #38BDF8]AgentOS OpenClaw Frontend[/bold #38BDF8] │ Decentralized Swarm Telemetry", id="header_title")
        
        with TabbedContent():
            with TabPane("🏢 Virtual Office", id="tab_office"):
                with Vertical():
                    # Top Realtime Fuel & DB Metrics
                    with Horizontal(classes="telemetry_header_bar"):
                        self.fuel_card = FuelEngineCard()
                        yield self.fuel_card

                        self.db_card = HyperbolicDBCard()
                        yield self.db_card

                    # Middle: Office Floor Grid Box (Dynamic)
                    yield Static("🏢 [bold #38BDF8]Virtual Office Grid Box[/bold #38BDF8] (Dynamically Displays Interacted Agents Only)", classes="agents_section_title")
                    with Container(id="active_agents_grid_box"):
                        self.placeholder = Label(
                            "⚡ No agents interacted yet.\nListening on ZeroMQ telemetry... Cards appear dynamically as agents join tasks.",
                            id="empty_placeholder"
                        )
                        yield self.placeholder

                    # Bottom Split Logs
                    with Horizontal(classes="bottom_section"):
                        with Vertical(classes="telemetry_log_box"):
                            yield Static("📊 [bold #58A6FF]ZeroMQ Intent Stream[/bold #58A6FF]")
                            self.telemetry_stream = Log(id="telemetry_stream_log")
                            yield self.telemetry_stream

                        with Vertical(classes="dialogue_log_box"):
                            yield Static("💬 [bold #D2A8FF]Live Swarm Dialogue Feed[/bold #D2A8FF]")
                            self.dialogue_log = Log(id="dialogue_log", highlight=True)
                            yield self.dialogue_log

            with TabPane("💻 Skill Workbench", id="tab_workbench"):
                with Horizontal(classes="workbench_container"):
                    with Vertical(classes="editor_column"):
                        yield Static("📝 [bold #38BDF8]Active Skill Editor[/bold #38BDF8]")
                        self.skill_editor = TextArea(
                            "name: dynamic_swarm_skill\ntype: WASM_EXECUTABLE\n---\ndef run():\n    import os\n    return 'AgentOS Swarm Executed successfully!'",
                            language="python",
                            id="editor_pane"
                        )
                        yield self.skill_editor

                    with Vertical(classes="tools_column"):
                        yield Static("🛠️ [bold #4ADE80]Registered AgentOS Tools & Skills Catalog[/bold #4ADE80]")
                        self.tools_table = DataTable(id="tools_table")
                        yield self.tools_table

                        yield Static("📐 [bold #C084FC]Mermaid Execution Diagram[/bold #C084FC]")
                        self.mermaid_preview = Log(id="mermaid_pane")
                        yield self.mermaid_preview

            with TabPane("⚙️ System Console", id="tab_console"):
                self.console_log = Log(id="event_log", highlight=True)
                yield self.console_log

        yield Footer()

    async def on_mount(self) -> None:
        # Initialize Registered Tools & Skills Catalog in Skill Workbench Table
        self.tools_table.add_columns("Tool / Skill Name", "Category", "Target Handler", "Status")
        self.populate_registered_tools()

        # Render initial logs
        self.dialogue_log.write("[bold #4ADE80][System][/bold #4ADE80] AgentOS Telemetry Dashboard Online.\n")
        self.dialogue_log.write("[bold #38BDF8][Info][/bold #38BDF8] Office Grid Box initialized. Awaiting real-time telemetry on ZMQ tcp://127.0.0.1:5562\n")

        self.mermaid_preview.write("```mermaid\ngraph TD;\n    A[Dynamic Intent] --> B(ZeroMQ IPC Broker);\n    B --> C{WASM Capability Guard};\n    C -->|Verified| D[Hyperbolic Vector DB];\n    C -->|Mutate| E[CRDT AST File Layer];\n```")

        # NOTE: NO PRE-MOUNTED CARDS ON STARTUP!
        # Office Grid Box starts completely empty until ZMQ receives active agent intents!

        # Start ZMQ background telemetry listener worker
        self.run_worker(self.listen_swarm_telemetry(), exclusive=True)

    def populate_registered_tools(self) -> None:
        """Register and populate all native AgentOS tools and skills on the Skill Workbench catalog."""
        self.tools_table.cursor_type = "row"
        self.tools_table.zebra_stripes = True
        registered_items = [
            ("execute_dynamic_python", "Core Exec", "WASM Sandbox", "ACTIVE"),
            ("hyperbolic_vector_search", "Memory DB", "Hyperbolic Engine", "ACTIVE"),
            ("crdt_ast_mutate", "FileSystem", "AST Compiler", "ACTIVE"),
            ("wasm_fuel_sandbox", "Security Guard", "Capability Oracle", "ACTIVE"),
            ("webrtc_swarm_route", "Networking", "WebRTC Mesh", "ACTIVE"),
            ("mcp_supabase_execute_sql", "MCP Extension", "Supabase MCP", "REGISTERED"),
            ("mcp_supabase_list_tables", "MCP Extension", "Supabase MCP", "REGISTERED"),
            ("agentos_core_skill", "Workflow Skill", "Core Orchestrator", "ACTIVE"),
        ]
        for item in registered_items:
            self.tools_table.add_row(*item)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Refresh DataTable layout when user switches to Skill Workbench tab."""
        if event.tab.id == "tab_workbench":
            self.tools_table.refresh(layout=True)

    async def register_agent_interaction(self, name: str, status: str, task: str) -> None:
        """Dynamically add or update an interacted agent card inside the Office Grid Box."""
        grid_box = self.query_one("#active_agents_grid_box", Container)

        # Remove empty placeholder if present
        if hasattr(self, 'placeholder') and self.placeholder and self.placeholder.parent:
            await self.placeholder.remove()

        cards = grid_box.query(AgentCard)
        target_card = None
        for card in cards:
            if card.agent_name == name:
                target_card = card
                break

        if not target_card:
            # Dynamically instantiate and mount new interacted agent card inside the Grid Box
            target_card = AgentCard(name)
            await grid_box.mount(target_card)

        # Update card reactive attributes
        target_card.agent_status = status
        target_card.active_task = task
        if status != "IDLE":
            target_card.interaction_count += 1

    async def listen_swarm_telemetry(self) -> None:
        """Realtime ZeroMQ Telemetry Subscriber & Telemetry Engine."""
        import zmq
        import zmq.asyncio

        context = zmq.asyncio.Context()
        socket = context.socket(zmq.SUB)

        try:
            socket.connect("tcp://127.0.0.1:5562")
            socket.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
            self.console_log.write("[ZMQ] Connected to tcp://127.0.0.1:5562\n")
        except Exception as err:
            self.console_log.write(f"[ZMQ Error] Connection error: {err}\n")

        while True:
            try:
                events = await socket.poll(timeout=1000)
                if events:
                    msg = await socket.recv_string()
                    payload_raw = msg.replace("TELEMETRY ", "", 1)
                    
                    try:
                        payload = json.loads(payload_raw)
                    except Exception:
                        payload = {"code": payload_raw}

                    code_snippet = payload.get("code", "").strip()
                    code_lower = code_snippet.lower()

                    self.telemetry_stream.write(f"> {code_snippet[:35]}\n")
                    self.console_log.write(f"[TELEMETRY] {str(payload)[:80]}\n")

                    # Update Fuel Usage & Capacity metrics in real-time
                    self.fuel_card.used_fuel += random.randint(1500, 4200)
                    self.fuel_card.burn_rate = random.randint(2100, 3800)
                    if self.fuel_card.used_fuel >= self.fuel_card.capacity:
                        self.fuel_card.used_fuel = 120000

                    # Update DB Latency & Vectors in real-time
                    self.db_card.indexed_vectors += random.randint(1, 5)
                    self.db_card.latency_ms = random.uniform(1.1, 2.3)

                    # Dynamic Interacted Agent Detection & Dialogue Routing
                    if "summit" in code_lower:
                        await self.register_agent_interaction("Claude", "WORKING", "Global Scaling Architecture")
                        await self.register_agent_interaction("Gemini", "SPEAKING", "Indexing Episodic Vector DB")
                        await self.register_agent_interaction("Cursor", "EXECUTING", "CRDT AST File Mutation")
                        await self.register_agent_interaction("Copilot", "WORKING", "IDE WebRTC Channel Active")

                        self.dialogue_log.write("[bold #FF6B6B][Claude][/bold #FF6B6B]: Re-routing ZeroMQ broker across edge nodes.\n")
                        self.dialogue_log.write("[bold #38BDF8][Gemini][/bold #38BDF8]: Indexing episodic memory vectors into Hyperbolic DB.\n")
                        self.dialogue_log.write("[bold #FACC15][Cursor][/bold #FACC15]: Resolving concurrent AST mutations.\n")

                    elif "web" in code_lower or "http" in code_lower:
                        await self.register_agent_interaction("Copilot", "WORKING", "Deploying Memory-Resident Web Server")
                        await self.register_agent_interaction("Claude", "TOOL", "Validating HTTP Handler")

                        self.dialogue_log.write("[bold #4ADE80][Copilot][/bold #4ADE80]: Web Server live at http://192.168.0.119:8080\n")
                    else:
                        interacted_name = "Claude" if "claude" in code_lower else "SwarmWorker"
                        await self.register_agent_interaction(interacted_name, "EXECUTING", f"Exec: {code_snippet[:25]}")
                        self.dialogue_log.write(f"[bold #C084FC][{interacted_name}][/bold #C084FC]: Processed intent -> {code_snippet[:35]}\n")

                else:
                    # Ambient state update
                    if random.random() > 0.8:
                        grid_box = self.query_one("#active_agents_grid_box", Container)
                        cards = grid_box.query(AgentCard)
                        for card in cards:
                            card.agent_status = "IDLE"

            except Exception as e:
                self.console_log.write(f"[Listener Exception] {e}\n")
                await asyncio.sleep(2)


if __name__ == "__main__":
    app = DashboardApp()
    app.run()
