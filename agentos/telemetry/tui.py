import asyncio
import sys
import json
import random
from typing import Dict, Any

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
        Header,
        Footer,
        DataTable
    )
    from textual.reactive import reactive
except ImportError:
    print("AgentOS Visual Telemetry requires the 'textual' framework.")
    print("Please install it by running: pip install textual rich")
    sys.exit(1)


class AgentCard(Static):
    """A clean, well-aligned widget representing an Agent Workstation in the Virtual Office."""
    
    agent_status = reactive("IDLE")
    active_task = reactive("Awaiting intent...")

    def __init__(self, name: str, icon: str, role: str, color: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = name
        self.icon = icon
        self.role = role
        self.color = color

    def render(self) -> str:
        status_colors = {
            "IDLE": "grey50",
            "WORKING": "yellow",
            "SPEAKING": "cyan",
            "EXECUTING": "green",
            "TOOL": "magenta",
        }
        status_badge = f"[{status_colors.get(self.agent_status, 'white')}]● {self.agent_status}[/]"
        
        return (
            f"[bold {self.color}]{self.icon} {self.agent_name}[/bold {self.color}]\n"
            f"[dim]{self.role}[/dim]\n\n"
            f"Status: {status_badge}\n"
            f"Task: [italic]{self.active_task[:35]}[/italic]"
        )


class PodCard(Static):
    """Widget representing the Central Holographic Collaboration Pod."""
    
    pod_status = reactive("STANDBY")
    active_summit = reactive("No active swarm consensus")

    def render(self) -> str:
        color = "magenta" if self.pod_status != "STANDBY" else "grey50"
        return (
            f"[bold magenta]🌀 Central Collaboration Pod[/bold magenta]\n"
            f"[dim]Holographic Swarm Link[/dim]\n\n"
            f"State: [{color}]● {self.pod_status}[/{color}]\n"
            f"Context: [italic]{self.active_summit[:40]}[/italic]"
        )


class SystemNodeCard(Static):
    """Widget displaying active edge infrastructure and mock worker statuses."""

    node_count = reactive(4)
    active_workers = reactive("QA, Security, Deployer")

    def render(self) -> str:
        return (
            f"[bold green]🖥️ Swarm Infrastructure[/bold green]\n"
            f"[dim]ZeroMQ + WASM Edge Mesh[/dim]\n\n"
            f"Active Edge Nodes: [bold cyan]{self.node_count}[/bold cyan]\n"
            f"Daemons: [dim]{self.active_workers}[/dim]"
        )


class DashboardApp(App):
    """Production-Grade AgentOS OpenClaw Telemetry Dashboard."""

    TITLE = "AgentOS OpenClaw Telemetry"
    SUB_TITLE = "Real-Time Decentralized AI Swarm Dashboard"

    CSS = """
    Screen {
        background: #0B0E14;
        color: #C9D1D9;
    }

    #header_title {
        height: 3;
        content-align: center middle;
        background: #161B22;
        color: #58A6FF;
        border-bottom: solid #30363D;
        text-style: bold;
    }

    /* Grid Layout for Virtual Office */
    .office_grid {
        layout: grid;
        grid-size: 3 2;
        grid-columns: 1fr 1fr 1fr;
        grid-rows: 1fr 1fr;
        grid-gutter: 1;
        padding: 1;
        height: 55%;
    }

    AgentCard {
        background: #161B22;
        border: round #30363D;
        padding: 1 2;
        height: 100%;
    }

    #card_claude {
        border-title-color: #FF7B72;
        border: round #FF7B72;
    }

    #card_gemini {
        border-title-color: #79C0FF;
        border: round #79C0FF;
    }

    PodCard {
        background: #1C1226;
        border: double #D2A8FF;
        padding: 1 2;
        height: 100%;
    }

    SystemNodeCard {
        background: #0D1F17;
        border: round #56D364;
        padding: 1 2;
        height: 100%;
    }

    .bottom_section {
        height: 45%;
        border-top: heavy #30363D;
        background: #0B0E14;
    }

    .telemetry_panel {
        width: 35%;
        border-right: solid #30363D;
        padding: 1;
        background: #161B22;
    }

    .dialogue_panel {
        width: 65%;
        padding: 1;
        background: #0D1117;
    }

    #dialogue_log {
        height: 1fr;
        border: round #30363D;
        background: #090D12;
    }

    #event_log {
        height: 1fr;
        border: round #30363D;
        background: #090D12;
    }

    .progress_label {
        margin-top: 1;
        text-style: bold;
    }

    ProgressBar {
        padding: 0;
        margin-bottom: 1;
    }

    /* Tab 2: Skill Workbench */
    .workbench_container {
        height: 100%;
        padding: 1;
    }

    #editor_pane {
        width: 50%;
        border: round #58A6FF;
        margin-right: 1;
    }

    #mermaid_pane {
        width: 50%;
        border: round #D2A8FF;
        background: #0D1117;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]AgentOS OpenClaw Frontend[/bold cyan] │ Swarm Runtime Engine", id="header_title")
        
        with TabbedContent():
            with TabPane("🏢 Virtual Office", id="tab_office"):
                with Vertical():
                    # 3x2 Grid for layout alignment
                    with Grid(classes="office_grid"):
                        self.card_claude = AgentCard(
                            "Claude (Architect)", "🤖", "System & Swarm Design", "red", id="card_claude"
                        )
                        yield self.card_claude

                        self.card_pod = PodCard(id="card_pod")
                        yield self.card_pod

                        self.card_gemini = AgentCard(
                            "Gemini (Vector)", "🦉", "Episodic Memory DB", "blue", id="card_gemini"
                        )
                        yield self.card_gemini

                        self.card_copilot = AgentCard(
                            "Copilot (Sidecar)", "✈️", "VS Code Extension", "cyan", id="card_copilot"
                        )
                        yield self.card_copilot

                        self.card_nodes = SystemNodeCard(id="card_nodes")
                        yield self.card_nodes

                        self.card_cursor = AgentCard(
                            "Cursor (AST Engine)", "⚡", "CRDT File Mutator", "yellow", id="card_cursor"
                        )
                        yield self.card_cursor

                    # Telemetry & Dialogue Split Panel
                    with Horizontal(classes="bottom_section"):
                        with Vertical(classes="telemetry_panel"):
                            yield Static("📊 [bold #58A6FF]WASM & Swarm Fuel Metrics[/bold #58A6FF]")
                            yield Label("Tokyo Node WASM Fuel:", classes="progress_label")
                            self.bar_tokyo = ProgressBar(total=1000, id="fuel_tokyo", show_eta=False)
                            yield self.bar_tokyo

                            yield Label("London Replica WASM Fuel:", classes="progress_label")
                            self.bar_london = ProgressBar(total=1000, id="fuel_london", show_eta=False)
                            yield self.bar_london

                            yield Label("ZMQ Telemetry Event Stream:", classes="progress_label")
                            self.telemetry_stream = Log(id="telemetry_stream_log")
                            yield self.telemetry_stream

                        with Vertical(classes="dialogue_panel"):
                            yield Static("💬 [bold #D2A8FF]Live Swarm Intent & Dialogue Feed[/bold #D2A8FF]")
                            self.dialogue_log = Log(id="dialogue_log", highlight=True)
                            yield self.dialogue_log

            with TabPane("💻 Skill Workbench", id="tab_workbench"):
                with Horizontal(classes="workbench_container"):
                    self.skill_editor = TextArea(
                        "name: dynamic_swarm_intent\ntype: WASM_EXECUTABLE\n---\ndef run():\n    import os\n    return 'AgentOS Swarm Executed!'",
                        language="python",
                        id="editor_pane"
                    )
                    yield self.skill_editor

                    self.mermaid_preview = Log(id="mermaid_pane")
                    yield self.mermaid_preview

            with TabPane("⚙️ Console & Logs", id="tab_console"):
                self.console_log = Log(id="event_log", highlight=True)
                yield self.console_log

        yield Footer()

    async def on_mount(self) -> None:
        self.bar_tokyo.advance(850)
        self.bar_london.advance(720)

        self.dialogue_log.write("[bold green][System][/bold green] AgentOS Dashboard Initialized cleanly.\n")
        self.dialogue_log.write("[bold cyan][Info][/bold cyan] Listening for real-time ZMQ telemetry on tcp://127.0.0.1:5562\n")

        self.mermaid_preview.write("```mermaid\ngraph TD;\n    A[Agent Intent] --> B(ZeroMQ Broker);\n    B --> C{WASM Sandbox};\n    C -->|Approved| D[State Mutated];\n    C -->|Fuel Exhausted| E[Re-route Node];\n```")

        # Start ZMQ background listener
        self.run_worker(self.listen_swarm_telemetry(), exclusive=True)

    async def listen_swarm_telemetry(self) -> None:
        import zmq
        import zmq.asyncio

        context = zmq.asyncio.Context()
        socket = context.socket(zmq.SUB)
        
        try:
            socket.connect("tcp://127.0.0.1:5562")
            socket.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
            self.console_log.write("[ZMQ] Successfully connected to tcp://127.0.0.1:5562\n")
        except Exception as err:
            self.console_log.write(f"[ZMQ Error] Could not bind socket: {err}\n")

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
                    args = payload.get("args", {})

                    self.telemetry_stream.write(f"> {code_snippet[:35]}\n")
                    self.console_log.write(f"[TELEMETRY] Payload: {str(payload)[:80]}\n")

                    # Update Fuel level
                    if self.bar_tokyo.progress > 100:
                        self.bar_tokyo.advance(-30)
                    else:
                        self.bar_tokyo.progress = 1000

                    # Parse Intent Type and update agent status cleanly
                    code_lower = code_snippet.lower()
                    if "summit" in code_lower:
                        self.card_claude.agent_status = "WORKING"
                        self.card_claude.active_task = "Global Scaling Architecture"
                        
                        self.card_gemini.agent_status = "SPEAKING"
                        self.card_gemini.active_task = "Neuro-Symbolic Vector DB"
                        
                        self.card_cursor.agent_status = "EXECUTING"
                        self.card_cursor.active_task = "AST CRDT File Sync"

                        self.card_pod.pod_status = "ACTIVE SUMMIT"
                        self.card_pod.active_summit = "Decentralized Swarm Consensus"

                        self.dialogue_log.write("[bold red][Claude][/bold red]: Re-routing ZeroMQ broker across edge nodes.\n")
                        self.dialogue_log.write("[bold blue][Gemini][/bold blue]: Indexing episodic memory vectors into Hyperbolic DB.\n")
                    elif "web" in code_lower or "http" in code_lower:
                        self.card_copilot.agent_status = "WORKING"
                        self.card_copilot.active_task = "Deploying Memory-Resident Server"
                        
                        self.card_claude.agent_status = "TOOL"
                        self.card_claude.active_task = "Verifying HTTP Handler"

                        self.dialogue_log.write("[bold cyan][Copilot][/bold cyan]: Web Server live at port 8080.\n")
                    else:
                        self.card_claude.agent_status = "EXECUTING"
                        self.card_claude.active_task = f"Exec: {code_snippet[:25]}"

                        self.dialogue_log.write(f"[bold yellow][Swarm][/bold yellow]: Processing intent -> {code_snippet[:40]}\n")
                else:
                    # Ambient status refresh
                    if random.random() > 0.8:
                        self.card_claude.agent_status = "IDLE"
                        self.card_claude.active_task = "Awaiting intent..."
                        
                        self.card_gemini.agent_status = "IDLE"
                        self.card_gemini.active_task = "Idle memory indexing..."
                        
                        self.card_pod.pod_status = "STANDBY"
                        self.card_pod.active_summit = "No active swarm consensus"

            except Exception as e:
                self.console_log.write(f"[Listener Exception] {e}\n")
                await asyncio.sleep(2)


if __name__ == "__main__":
    app = DashboardApp()
    app.run()
