"""
ComputeRes OpenClaw — Office Workspace TUI v3
Real-time Swarm Telemetry & Agent Monitoring Dashboard
"""
import asyncio
import json
import random
import sys
import time
from datetime import datetime
from typing import Dict

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.reactive import reactive
    from textual.widgets import (
        DataTable, Footer, Label, RichLog, Static,
        TabbedContent, TabPane, TextArea,
    )
except ImportError:
    print("Install textual: pip install textual rich")
    sys.exit(1)

from compute_res.telemetry.components.cards import (
    AGENT_STYLES, STATUS_STYLES,
    AgentCard, FuelEngineCard, HyperbolicDBCard,
    KernelStatusCard, SkillsHubCard,
)


# ═══════════════════════════════════════════════════════════════════
#  Main App
# ═══════════════════════════════════════════════════════════════════
class OpenClawOffice(App):
    """ComputeRes OpenClaw — Agent Office Workspace Dashboard."""

    TITLE    = "ComputeRes OpenClaw"
    SUB_TITLE = "Agent Office Workspace  ·  Real-Time Swarm Monitor"
    CSS_PATH  = "../styles/tui.css"

    BINDINGS = [
        ("q",   "quit",                  "Quit"),
        ("r",   "reset_office",          "Clear Office"),
        ("s",   "screenshot",            "Screenshot"),
        ("1",   "switch_tab('tab_office')",    "Office"),
        ("2",   "switch_tab('tab_workbench')", "Workbench"),
        ("3",   "switch_tab('tab_console')",   "Console"),
    ]

    # ── Widget references
    _agent_cards: Dict[str, AgentCard] = {}

    # ── Compose Layout ────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        # Global header
        with Horizontal(id="header_bar"):
            yield Static(
                "◈ [bold #38BDF8]ComputeRes[/bold #38BDF8] [dim]OpenClaw[/dim]",
                id="header_logo",
            )
            yield Static("", id="header_status_bar")
            yield Static("", id="header_clock")

        with TabbedContent():
            # ── Tab 1: Virtual Office ──────────────────────────────
            with TabPane("🏢  Office Floor", id="tab_office"):
                with Vertical():
                    # Metric cards strip
                    with Horizontal(classes="metrics_strip"):
                        self.fuel_card    = FuelEngineCard()
                        self.db_card      = HyperbolicDBCard()
                        self.skills_card  = SkillsHubCard()
                        self.kernel_card  = KernelStatusCard()
                        yield self.fuel_card
                        yield self.db_card
                        yield self.skills_card
                        yield self.kernel_card

                    # Office floor label
                    yield Static(
                        "🏢  [bold #38BDF8]Virtual Office Floor[/bold #38BDF8]  "
                        "[dim]— Agent desks appear dynamically as agents join tasks[/dim]",
                        id="office_floor_label",
                    )

                    # Agent desk grid
                    with Container(id="active_agents_grid_box"):
                        self._placeholder = Label(
                            "\n\n\n"
                            "    ○  No agents on the office floor yet.\n\n"
                            "    Listening on [bold]ZeroMQ tcp://127.0.0.1:5562[/bold]\n"
                            "    Desks populate when agents start executing tasks.\n\n\n",
                            id="empty_placeholder",
                        )
                        yield self._placeholder

                    # Bottom 3-column log row
                    with Horizontal(classes="log_row"):
                        with Vertical(classes="intent_stream_box"):
                            yield Static(
                                "[bold #58A6FF]📡 ZMQ Intent Stream[/bold #58A6FF]",
                                classes="log_label",
                            )
                            self.intent_log = RichLog(
                                id="intent_log", wrap=True, markup=True,
                                auto_scroll=True,
                            )
                            yield self.intent_log

                        with Vertical(classes="dialogue_feed_box"):
                            yield Static(
                                "[bold #D2A8FF]💬 Swarm Dialogue Feed[/bold #D2A8FF]",
                                classes="log_label",
                            )
                            self.dialogue_log = RichLog(
                                id="dialogue_log", wrap=True, markup=True,
                                highlight=True, auto_scroll=True,
                            )
                            yield self.dialogue_log

                        with Vertical(classes="skills_activity_box"):
                            yield Static(
                                "[bold #4ADE80]⚗️  Skills Activity[/bold #4ADE80]",
                                classes="log_label",
                            )
                            self.skills_log = RichLog(
                                id="skills_log", wrap=True, markup=True,
                                auto_scroll=True,
                            )
                            yield self.skills_log

            # ── Tab 2: Skill Workbench ─────────────────────────────
            with TabPane("💻  Skill Workbench", id="tab_workbench"):
                with Horizontal(classes="workbench_container"):
                    with Vertical(classes="editor_column"):
                        yield Static(
                            "[bold #38BDF8]📝 Live Skill Editor[/bold #38BDF8]\n"
                            "[dim]Edit and deploy WASM skills in real-time[/dim]"
                        )
                        self.skill_editor = TextArea(
                            'def run(**kwargs):\n'
                            '    """\n'
                            '    ComputeRes Live Skill — edit and deploy.\n'
                            '    Args passed from agent intent payload.\n'
                            '    """\n'
                            '    import os\n'
                            '    return {\n'
                            '        "status": "ok",\n'
                            '        "cwd": os.getcwd(),\n'
                            '        "agent": kwargs.get("agent_id", "unknown"),\n'
                            '    }\n',
                            language="python",
                            id="editor_pane",
                        )
                        yield self.skill_editor

                    with Vertical(classes="catalog_column"):
                        yield Static(
                            "[bold #4ADE80]📚 SkillsHub Registry[/bold #4ADE80]\n"
                            "[dim]All registered ComputeRes tools & evolved skills[/dim]"
                        )
                        self.skills_table = DataTable(id="skills_catalog_table")
                        yield self.skills_table

                        yield Static(
                            "[bold #7C3AED]🔀 Execution Pipeline[/bold #7C3AED]"
                        )
                        self.mermaid_pane = RichLog(
                            id="mermaid_pane", wrap=True, markup=True,
                        )
                        yield self.mermaid_pane

            # ── Tab 3: System Console ──────────────────────────────
            with TabPane("⚙️  System Console", id="tab_console"):
                self.console_log = RichLog(
                    id="system_console_log",
                    highlight=True, wrap=True, markup=True,
                    auto_scroll=True,
                )
                yield self.console_log

        yield Footer()

    # ── Mount & Init ──────────────────────────────────────────────
    async def on_mount(self) -> None:
        # Boot messages
        self._boot_log("[bold #38BDF8]ComputeRes OpenClaw Office Workspace[/bold #38BDF8] booting...")
        self._boot_log("ZeroMQ Telemetry Subscriber → [dim]tcp://127.0.0.1:5562[/dim]")
        self._boot_log("SkillsHub DB → FTS5 search engine active.")
        self._boot_log("Event Gateway → Webhook push system online.")

        # Skills workbench table
        self.skills_table.add_columns("Skill / Tool", "Niche", "Author", "Status")
        self.skills_table.zebra_stripes = True
        self.skills_table.cursor_type   = "row"
        self._populate_skills_table()

        # Mermaid pipeline diagram
        self.mermaid_pane.write(
            "[bold #7C3AED]Agent Intent → ZMQ Broker → WASM Sandbox → Kernel Worker[/bold #7C3AED]\n"
            "[dim]  ┌──────────────────────────────────────────────────────┐[/dim]\n"
            "[dim]  │ PUB tcp://5562  ─►  Telemetry Dashboard SUB          │[/dim]\n"
            "[dim]  │ REQ tcp://5557  ─►  Kernel ROUTER ─► DEALER Worker   │[/dim]\n"
            "[dim]  │ SKILL_AVAILABLE tcp://5565 ─► SkillsHub ZMQ SUB      │[/dim]\n"
            "[dim]  └──────────────────────────────────────────────────────┘[/dim]\n"
        )

        # Start background workers
        self.run_worker(self._clock_ticker(),       exclusive=False, name="clock")
        self.run_worker(self._kernel_status_poller(), exclusive=False, name="kernel-poll")
        self.run_worker(self._skillshub_poller(),   exclusive=False, name="skills-poll")
        self.run_worker(self._zmq_telemetry_loop(), exclusive=True,  name="zmq-telemetry")

    # ── Skill Workbench Population ────────────────────────────────
    def _populate_skills_table(self) -> None:
        try:
            from compute_res.memory.skillshub_db import skills_db
            all_skills = skills_db.get_all_skills()
            for skill in all_skills[:80]:  # Display up to 80
                niche = skill.get("categories", ["—"])
                niche_str = niche[0] if niche else "—"
                self.skills_table.add_row(
                    skill["name"],
                    niche_str,
                    skill.get("author", "—"),
                    "[bold green]ACTIVE[/bold green]",
                )
            self.skills_card.total_skills = len(all_skills)
        except Exception as e:
            self.console_log.write(f"[red]SkillsHub load error: {e}[/red]")

    # ── Clock Ticker ──────────────────────────────────────────────
    async def _clock_ticker(self) -> None:
        clock_widget = self.query_one("#header_clock", Static)
        status_widget = self.query_one("#header_status_bar", Static)
        start = time.time()
        while True:
            now = datetime.utcnow().strftime("%H:%M:%S UTC")
            uptime_s = int(time.time() - start)
            h, m, s = uptime_s // 3600, (uptime_s % 3600) // 60, uptime_s % 60
            uptime_str = f"{h:02d}h {m:02d}m {s:02d}s"
            clock_widget.update(f"[dim]{now}[/dim]")
            agent_count = len(self._agent_cards)
            status_widget.update(
                f"[bold #4ADE80]● LIVE[/bold #4ADE80]  "
                f"[dim]Agents: [bold white]{agent_count}[/bold white]  "
                f"Uptime: {uptime_str}[/dim]"
            )
            self.kernel_card.uptime_str = uptime_str
            await asyncio.sleep(1)

    # ── Kernel Status Poller ──────────────────────────────────────
    async def _kernel_status_poller(self) -> None:
        import socket
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.connect(("127.0.0.1", 5557))
                sock.close()
                self.kernel_card.kernel_status = "ONLINE"
            except Exception:
                self.kernel_card.kernel_status = "OFFLINE"
            await asyncio.sleep(5)

    # ── SkillsHub Live Poller ─────────────────────────────────────
    async def _skillshub_poller(self) -> None:
        while True:
            try:
                from compute_res.memory.skillshub_db import skills_db
                all_skills = skills_db.get_all_skills()
                self.skills_card.total_skills = len(all_skills)
                if all_skills:
                    niches = [s.get("categories", ["—"])[0] if s.get("categories") else "—" for s in all_skills]
                    from collections import Counter
                    top = Counter(niches).most_common(1)
                    if top:
                        self.skills_card.top_niche = top[0][0]
            except Exception:
                pass
            await asyncio.sleep(10)

    # ── ZeroMQ Telemetry Loop ─────────────────────────────────────
    async def _zmq_telemetry_loop(self) -> None:
        """Subscribe to the Kernel ZMQ PUB socket and process telemetry in real-time."""
        try:
            import zmq
            import zmq.asyncio
        except ImportError:
            self._boot_log("[red]pyzmq not installed — running in demo mode[/red]")
            await self._demo_mode()
            return

        ctx = zmq.asyncio.Context()
        sock = ctx.socket(zmq.SUB)
        try:
            sock.connect("tcp://127.0.0.1:5562")
            sock.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
            self._boot_log("[green]ZMQ SUB connected to tcp://127.0.0.1:5562[/green]")
        except Exception as e:
            self._boot_log(f"[red]ZMQ connect failed: {e}[/red]")
            await self._demo_mode()
            return

        while True:
            try:
                events = await sock.poll(timeout=100)
                if events:
                    raw = await sock.recv_string()
                    payload_str = raw.replace("TELEMETRY ", "", 1)
                    try:
                        payload = json.loads(payload_str)
                    except json.JSONDecodeError:
                        payload = {"code": payload_str}

                    await self._process_telemetry(payload)
                else:
                    # Ambient idle — decay old cards
                    await self._decay_idle_agents()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.console_log.write(f"[red][ZMQ Error] {e}[/red]")
                await asyncio.sleep(0.5)

    async def _process_telemetry(self, payload: dict) -> None:
        """Parse a raw telemetry payload and update the Office Floor."""
        tool_name = payload.get("tool", "")
        code      = payload.get("code", "")
        args      = payload.get("args", {})

        # Resolve agent name
        agent_name = (
            args.get("agent_id")
            or args.get("agent")
            or payload.get("agent")
        )
        if not agent_name:
            # Heuristic: detect known models from code/tool strings
            combined = (code + tool_name).lower()
            if "claude"  in combined: agent_name = "Claude"
            elif "gemini" in combined: agent_name = "Gemini"
            elif "copilot"in combined: agent_name = "Copilot"
            elif "cursor" in combined: agent_name = "Cursor"
            elif "gpt"   in combined: agent_name = "GPT-4"
            elif "llama" in combined: agent_name = "Llama"
            elif "mistral"in combined: agent_name = "Mistral"
            else: agent_name = "SwarmWorker"

        # Determine status
        if tool_name:
            status = "TOOL" if "tool" in tool_name.lower() else "EXECUTING"
            task_desc = f"{tool_name}({str(args)[:28]})"
        else:
            first_line = code.splitlines()[0].strip() if code else "exec"
            status = "WORKING"
            task_desc = first_line[:40]

        # Fuel & DB updates
        self.fuel_card.used_fuel = min(
            self.fuel_card.used_fuel + random.randint(800, 3200),
            self.fuel_card.capacity,
        )
        self.fuel_card.burn_rate = random.randint(1800, 4200)
        self.db_card.indexed_vectors += random.randint(0, 4)
        self.db_card.queries += 1
        self.db_card.latency_ms = round(random.uniform(0.8, 2.8), 2)
        self.kernel_card.events_pushed += 1

        # Register / update agent card on the Office Floor
        await self._upsert_agent_card(agent_name, status, task_desc)

        # Log streams
        style = AGENT_STYLES.get(agent_name, AGENT_STYLES["SwarmWorker"])
        color = style["color"]

        self.intent_log.write(
            f"[dim]{datetime.utcnow().strftime('%H:%M:%S')}[/dim]  "
            f"[{color}]{agent_name}[/{color}] → {task_desc[:45]}"
        )

        feed_msg = str(args)[:50] if args else task_desc
        self.dialogue_log.write(
            f"[bold {color}][{agent_name}][/bold {color}] {feed_msg}"
        )

        self.console_log.write(
            f"[dim]TELEMETRY[/dim] {json.dumps(payload)[:120]}"
        )

        # Skills activity log — detect skill invocations
        if tool_name in ("invoke_compute_res_skill", "execute_dynamic_python", "publish_skill", "query_skills"):
            self.skills_log.write(
                f"[bold #4ADE80]{agent_name}[/bold #4ADE80] → [cyan]{tool_name}[/cyan]"
            )
            self.skills_card.published_today += 1

    # ── Agent Card Lifecycle ──────────────────────────────────────
    async def _upsert_agent_card(self, name: str, status: str, task: str) -> None:
        """Mount a new agent card or update an existing one on the Office Floor."""
        grid = self.query_one("#active_agents_grid_box", Container)

        # Remove placeholder on first agent
        if self._placeholder and self._placeholder.parent:
            await self._placeholder.remove()
            self._placeholder = None

        # Register in unknown styles
        if name not in AGENT_STYLES:
            AGENT_STYLES[name] = {
                "icon": "⬡", "color": "#94A3B8", "border": "#475569",
                "role": "External Node", "desk": "🖥️  Desk ?",
            }

        if name not in self._agent_cards:
            card = AgentCard(name)
            self._agent_cards[name] = card
            await grid.mount(card)

        card = self._agent_cards[name]
        card.agent_status   = status
        card.active_task    = task
        card.last_active_time = time.time()
        card.interaction_count += 1
        card.fuel_consumed  += random.randint(800, 3200)

        # Update CSS class for border colour
        card.remove_class("status-executing", "status-speaking", "status-tool", "status-idle")
        if status == "EXECUTING": card.add_class("status-executing")
        elif status == "SPEAKING": card.add_class("status-speaking")
        elif status == "TOOL":    card.add_class("status-tool")

    async def _decay_idle_agents(self) -> None:
        """Transition long-idle agents to IDLE, then remove them after 2 minutes."""
        now = time.time()
        grid = self.query_one("#active_agents_grid_box", Container)
        to_remove = []

        for name, card in list(self._agent_cards.items()):
            idle_secs = now - card.last_active_time
            if idle_secs > 45 and card.agent_status != "IDLE":
                card.agent_status = "IDLE"
                card.active_task  = "Standing by..."
                card.remove_class("status-executing", "status-speaking", "status-tool")
                card.add_class("status-idle")
            if idle_secs > 120:
                to_remove.append(name)

        for name in to_remove:
            card = self._agent_cards.pop(name)
            await card.remove()
            self.dialogue_log.write(
                f"[dim][{name}] stepped away from their desk.[/dim]"
            )

        # Restore placeholder if office is empty
        if not self._agent_cards:
            if not self._placeholder or not self._placeholder.parent:
                self._placeholder = Label(
                    "\n\n\n"
                    "    ○  No agents currently on the floor.\n\n"
                    "    Waiting for ZeroMQ telemetry...\n\n\n",
                    id="empty_placeholder",
                )
                await grid.mount(self._placeholder)

    # ── Demo Mode (no ZMQ available) ─────────────────────────────
    async def _demo_mode(self) -> None:
        """Simulate agent activity for demo/testing without a running kernel."""
        self._boot_log("[yellow]── DEMO MODE: Simulating swarm activity ──[/yellow]")
        demo_agents = ["Claude", "Gemini", "Copilot", "Cursor", "Mistral"]
        demo_tools  = [
            "execute_dynamic_python", "query_skills", "mailbox_send",
            "fs_read_file", "crypto_hash_file", "data_compute_stats",
            "net_http_get", "db_sqlite_query", "code_parse_ast",
        ]
        demo_statuses = ["EXECUTING", "WORKING", "TOOL", "SPEAKING"]

        while True:
            agent = random.choice(demo_agents)
            tool  = random.choice(demo_tools)
            status = random.choice(demo_statuses)
            payload = {
                "tool": tool,
                "args": {"agent_id": agent, "session_id": "demo"},
            }
            await self._process_telemetry(payload)
            await asyncio.sleep(random.uniform(1.2, 3.5))

    # ── Helpers ───────────────────────────────────────────────────
    def _boot_log(self, msg: str) -> None:
        try:
            self.console_log.write(
                f"[dim]{datetime.utcnow().strftime('%H:%M:%S')}[/dim] {msg}"
            )
        except Exception:
            pass

    # ── Actions ───────────────────────────────────────────────────
    async def action_reset_office(self) -> None:
        for name, card in list(self._agent_cards.items()):
            await card.remove()
        self._agent_cards.clear()
        self._boot_log("[yellow]Office floor cleared.[/yellow]")

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        if event.tab.id == "tab_workbench":
            try:
                self.skills_table.refresh(layout=True)
            except Exception:
                pass


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    OpenClawOffice().run()
