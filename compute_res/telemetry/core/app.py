"""
ComputeRes Agent OS — Office Workspace TUI v4
Live telemetry · OS Manager · Dynamic agent desks · SkillsHub integration
"""
import asyncio
import json
import random
import socket
import sys
import time
from collections import Counter
from datetime import datetime
from typing import Dict, Optional

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import (
        DataTable, Footer, Label, RichLog,
        Static, TabbedContent, TabPane, TextArea,
    )
except ImportError:
    print("pip install textual rich")
    sys.exit(1)

from compute_res.telemetry.components.cards import (
    AGENT_STYLES, STATUS_STYLES,
    AgentCard, FuelEngineCard, HyperbolicDBCard,
    KernelStatusCard, OSManagerCard, SkillsHubCard,
)

# ─────────────────────────────────────────────────────────────────────────────
BOOT_TIME  = time.time()
ZMQ_PUB    = "tcp://127.0.0.1:5562"
ZMQ_KERNEL = ("127.0.0.1", 5557)

DEMO_AGENTS  = ["Claude", "Gemini", "Copilot", "Cursor", "GPT-4", "Mistral", "Llama"]
DEMO_TOOLS   = [
    "execute_dynamic_python", "query_skills", "publish_skill",
    "fs_read_file", "crypto_hash_file", "data_compute_stats",
    "net_http_get", "db_sqlite_query", "code_parse_ast",
    "text_extract_urls", "algo_binary_search", "git_log",
    "bench_run_timed", "log_grep", "sys_memory_info",
]
DEMO_INTENTS = [
    "Parsing AST tree nodes",   "Querying SkillsHub registry",
    "Running WASM sandbox",     "Publishing evolved skill",
    "Hashing file checksum",    "Fetching live HTTP endpoint",
    "Computing statistics",     "Reading git log history",
    "Extracting email records", "Running benchmark suite",
    "Scanning log for errors",  "Searching skill by niche",
]


# ═════════════════════════════════════════════════════════════════════════════
class AgentOSApp(App):
    """ComputeRes Agent OS — Office Workspace Dashboard."""

    TITLE    = "ComputeRes Agent OS"
    SUB_TITLE = "Office Floor  ·  Real-Time Swarm Monitor"
    CSS_PATH  = "../styles/tui.css"

    BINDINGS = [
        ("q", "quit",                        "Quit"),
        ("r", "reset_agents",                "Reset Agents"),
        ("1", "switch_tab('tab_office')",    "Office"),
        ("2", "switch_tab('tab_workbench')", "Workbench"),
        ("3", "switch_tab('tab_console')",   "Console"),
    ]

    # ── Live state ────────────────────────────────────────────────
    _agent_cards: Dict[str, AgentCard] = {}
    _os_manager: Optional[OSManagerCard] = None
    _total_events: int = 0
    _zmq_mode: str = "connecting"   # "live" | "demo"

    # ─────────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        with Horizontal(id="header_bar"):
            yield Static(
                "◈ [bold #38BDF8]ComputeRes[/bold #38BDF8] [dim]Agent OS[/dim]",
                id="header_logo",
            )
            yield Static("", id="header_status_bar")
            yield Static("", id="header_clock")

        with TabbedContent():

            # ── Tab 1: Office Floor ───────────────────────────────
            with TabPane("🏢  Office Floor", id="tab_office"):
                with Vertical():

                    # 4-card live metric strip
                    with Horizontal(classes="metrics_strip"):
                        self.fuel_card   = FuelEngineCard()
                        self.db_card     = HyperbolicDBCard()
                        self.skills_card = SkillsHubCard()
                        self.kernel_card = KernelStatusCard()
                        yield self.fuel_card
                        yield self.db_card
                        yield self.skills_card
                        yield self.kernel_card

                    yield Static(
                        "🏢  [bold #38BDF8]Agent Office Floor[/bold #38BDF8]"
                        "  [dim]— OS Manager always present · Agent desks mount on first activity[/dim]",
                        id="office_floor_label",
                    )

                    # Agent desk grid — OS Manager mounted here permanently
                    with Container(id="active_agents_grid_box"):
                        pass

                    # 3-column live log row
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
                                auto_scroll=True, highlight=True,
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

            # ── Tab 2: Skill Workbench ────────────────────────────
            with TabPane("💻  Skill Workbench", id="tab_workbench"):
                with Horizontal(classes="workbench_container"):
                    with Vertical(classes="editor_column"):
                        yield Static(
                            "[bold #38BDF8]📝 Live Skill Editor[/bold #38BDF8]"
                            "  [dim]Edit & deploy a WASM skill[/dim]"
                        )
                        self.skill_editor = TextArea(
                            'def run(**kwargs):\n'
                            '    """ComputeRes Live Skill — edit and deploy."""\n'
                            '    import os\n'
                            '    return {\n'
                            '        "status": "ok",\n'
                            '        "cwd": os.getcwd(),\n'
                            '        "agent": kwargs.get("agent_id", "unknown"),\n'
                            '    }\n',
                            language="python", id="editor_pane",
                        )
                        yield self.skill_editor

                    with Vertical(classes="catalog_column"):
                        yield Static(
                            "[bold #4ADE80]📚 SkillsHub Registry[/bold #4ADE80]"
                            "  [dim]All registered skills — live from DB[/dim]"
                        )
                        self.skills_table = DataTable(id="skills_catalog_table")
                        yield self.skills_table

                        yield Static("[bold #7C3AED]🔀 IPC Pipeline[/bold #7C3AED]")
                        self.pipeline_log = RichLog(
                            id="mermaid_pane", wrap=True, markup=True,
                        )
                        yield self.pipeline_log

            # ── Tab 3: System Console ─────────────────────────────
            with TabPane("⚙️  Console", id="tab_console"):
                self.console_log = RichLog(
                    id="system_console_log",
                    highlight=True, wrap=True, markup=True,
                    auto_scroll=True,
                )
                yield self.console_log

        yield Footer()

    # ─────────────────────────────────────────────────────────────
    async def on_mount(self) -> None:
        self._log("ComputeRes Agent OS v4 booting...")
        self._log(f"ZMQ Subscriber → {ZMQ_PUB}")

        # Skill Workbench setup
        self.skills_table.add_columns("Skill", "Niche", "Author", "Status")
        self.skills_table.zebra_stripes = True
        self.skills_table.cursor_type   = "row"
        self._load_skills_table()

        # Pipeline diagram
        self.pipeline_log.write(
            "[bold #7C3AED]Agent Intent ─► ZMQ Broker ─► WASM Sandbox ─► Kernel Worker[/bold #7C3AED]\n"
            "[dim]  PUB tcp://5562  ─►  Dashboard SUB[/dim]\n"
            "[dim]  REQ tcp://5557  ─►  Kernel ROUTER[/dim]\n"
            "[dim]  SKILL_AVAIL tcp://5565  ─►  SkillsHub[/dim]\n"
        )

        # Mount OS Manager permanently
        grid = self.query_one("#active_agents_grid_box", Container)
        self._os_manager = OSManagerCard()
        await grid.mount(self._os_manager)
        self._log("OS Manager mounted on Office Floor (permanent).")

        # Start background workers
        self.run_worker(self._clock_worker(),        exclusive=False, name="clock")
        self.run_worker(self._os_metrics_worker(),   exclusive=False, name="os-metrics")
        self.run_worker(self._kernel_poll_worker(),  exclusive=False, name="kernel-poll")
        self.run_worker(self._skillshub_worker(),    exclusive=False, name="skills-hub")
        self.run_worker(self._zmq_worker(),          exclusive=True,  name="zmq-tel")

    # ─────────────────────────────────────────────────────────────
    #  Worker: Clock + header status bar
    # ─────────────────────────────────────────────────────────────
    async def _clock_worker(self) -> None:
        clock_w  = self.query_one("#header_clock",      Static)
        status_w = self.query_one("#header_status_bar", Static)
        while True:
            now    = datetime.utcnow().strftime("%H:%M:%S UTC")
            uptime = int(time.time() - BOOT_TIME)
            h, m, s = uptime // 3600, (uptime % 3600) // 60, uptime % 60
            up_str = f"{h:02d}h{m:02d}m{s:02d}s"

            n_agents = len(self._agent_cards)
            mode_badge = (
                "[bold #4ADE80]● LIVE[/bold #4ADE80]"
                if self._zmq_mode == "live"
                else "[bold #FACC15]◐ DEMO[/bold #FACC15]"
            )

            clock_w.update(f"[dim]{now}[/dim]")
            status_w.update(
                f"{mode_badge}  "
                f"[dim]Agents [bold white]{n_agents}[/bold white]  "
                f"Events [bold white]{self._total_events}[/bold white]  "
                f"Up {up_str}[/dim]"
            )
            # Propagate agent count to cards
            self.kernel_card.active_agents = n_agents
            self.kernel_card.events_pushed = self._total_events
            self.kernel_card.uptime_str    = up_str
            if self._os_manager:
                self._os_manager.agent_count  = n_agents
                self._os_manager.events_total = self._total_events
            await asyncio.sleep(1)

    # ─────────────────────────────────────────────────────────────
    #  Worker: OS Metrics (RAM, Disk, CPU load) → OS Manager card
    # ─────────────────────────────────────────────────────────────
    async def _os_metrics_worker(self) -> None:
        while True:
            try:
                # RAM from /proc/meminfo
                mem_total = mem_avail = 0
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal"):
                            mem_total = int(line.split()[1]) // 1024
                        elif line.startswith("MemAvailable"):
                            mem_avail = int(line.split()[1]) // 1024
                mem_used = mem_total - mem_avail

                # CPU load from /proc/loadavg
                with open("/proc/loadavg") as f:
                    load_raw = f.read().split()
                    cpu_load = f"{load_raw[0]} {load_raw[1]} {load_raw[2]}"

                # Disk from root
                import shutil
                du = shutil.disk_usage("/")
                disk_pct = int(du.used / du.total * 100)

                if self._os_manager:
                    self._os_manager.ram_used_mb   = mem_used
                    self._os_manager.ram_total_mb  = mem_total if mem_total > 0 else 512
                    self._os_manager.cpu_load      = cpu_load
                    self._os_manager.disk_used_pct = disk_pct

                # Reflect RAM in fuel card
                self.fuel_card.ram_mb = mem_used

            except Exception as e:
                self._log(f"[dim][os-metrics] {e}[/dim]")

            await asyncio.sleep(3)

    # ─────────────────────────────────────────────────────────────
    #  Worker: Kernel IPC Health Probe
    # ─────────────────────────────────────────────────────────────
    async def _kernel_poll_worker(self) -> None:
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect(ZMQ_KERNEL)
                s.close()
                online = True
            except Exception:
                online = False

            self.kernel_card.kernel_status       = "ONLINE" if online else "OFFLINE"
            if self._os_manager:
                self._os_manager.kernel_online   = online

            await asyncio.sleep(5)

    # ─────────────────────────────────────────────────────────────
    #  Worker: SkillsHub DB Live Stats
    # ─────────────────────────────────────────────────────────────
    async def _skillshub_worker(self) -> None:
        while True:
            try:
                from compute_res.memory.skillshub_db import skills_db
                all_s = skills_db.get_all_skills()
                self.skills_card.total_skills = len(all_s)
                self.skills_card.fts_ready    = True
                if all_s:
                    niches = [
                        s.get("categories", ["—"])[0]
                        if s.get("categories") else "—"
                        for s in all_s
                    ]
                    top = Counter(niches).most_common(1)
                    if top:
                        self.skills_card.top_niche = top[0][0]
            except Exception as e:
                self.skills_card.fts_ready = False
                self._log(f"[dim][skills-hub] {e}[/dim]")
            await asyncio.sleep(8)

    def _load_skills_table(self) -> None:
        try:
            from compute_res.memory.skillshub_db import skills_db
            for s in skills_db.get_all_skills()[:120]:
                niche = (s.get("categories") or ["—"])[0]
                self.skills_table.add_row(
                    s["name"], niche,
                    s.get("author", "—"),
                    "[bold green]ACTIVE[/bold green]",
                )
            self._log(f"SkillsHub: loaded {self.skills_table.row_count} skills.")
        except Exception as e:
            self._log(f"[red]SkillsHub table error: {e}[/red]")

    # ─────────────────────────────────────────────────────────────
    #  Worker: ZMQ Telemetry (live or demo fallback)
    # ─────────────────────────────────────────────────────────────
    async def _zmq_worker(self) -> None:
        try:
            import zmq
            import zmq.asyncio
        except ImportError:
            self._log("[yellow]pyzmq not found — running demo mode[/yellow]")
            self._zmq_mode = "demo"
            await self._demo_loop()
            return

        ctx  = zmq.asyncio.Context()
        sock = ctx.socket(zmq.SUB)
        sock.connect(ZMQ_PUB)
        sock.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
        self._log(f"[green]ZMQ SUB connected → {ZMQ_PUB}[/green]")

        # Give the socket 3 s to receive its first frame before falling to demo
        first_msg = None
        try:
            if await sock.poll(timeout=3000):
                first_msg = await sock.recv_string()
        except Exception:
            pass

        if first_msg is None:
            self._log("[yellow]No ZMQ frames in 3s — engaging demo mode alongside[/yellow]")
            self._zmq_mode = "demo"
            self.run_worker(self._demo_loop(), exclusive=False, name="demo")
        else:
            self._zmq_mode = "live"
            await self._handle_raw(first_msg)

        while True:
            try:
                events = await sock.poll(timeout=150)
                if events:
                    raw = await sock.recv_string()
                    if raw:
                        self._zmq_mode = "live"
                        await self._handle_raw(raw)
                else:
                    await self._decay_idle_agents()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._log(f"[red][zmq] {e}[/red]")
                await asyncio.sleep(0.5)

    async def _handle_raw(self, raw: str) -> None:
        payload_str = raw.replace("TELEMETRY ", "", 1)
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError:
            payload = {"code": raw}
        await self._process_event(payload)

    # ─────────────────────────────────────────────────────────────
    #  Demo Loop — realistic simulation
    # ─────────────────────────────────────────────────────────────
    async def _demo_loop(self) -> None:
        self._log("[bold #FACC15]── DEMO MODE: Simulating swarm activity ──[/bold #FACC15]")
        # Bring 2 agents on immediately
        for agent in ["Claude", "Gemini"]:
            await self._process_event({
                "tool": "execute_dynamic_python",
                "args": {"agent_id": agent},
                "code": f"# {agent} initialising",
            })
            await asyncio.sleep(0.5)

        while True:
            agent  = random.choice(DEMO_AGENTS)
            tool   = random.choice(DEMO_TOOLS)
            intent = random.choice(DEMO_INTENTS)
            await self._process_event({
                "tool": tool,
                "args": {"agent_id": agent, "session_id": "demo"},
                "code": f"# {intent}",
            })
            # Fuel tick
            self.fuel_card.used_fuel = min(
                self.fuel_card.used_fuel + random.randint(500, 3000),
                self.fuel_card.capacity,
            )
            self.fuel_card.burn_rate = random.randint(1500, 4500)
            self.db_card.indexed_vectors += random.randint(0, 3)
            self.db_card.latency_ms = round(random.uniform(0.7, 2.9), 2)
            await asyncio.sleep(random.uniform(1.0, 2.8))

    # ─────────────────────────────────────────────────────────────
    #  Core event processor
    # ─────────────────────────────────────────────────────────────
    async def _process_event(self, payload: dict) -> None:
        self._total_events += 1

        tool  = payload.get("tool", "")
        code  = payload.get("code", "")
        args  = payload.get("args", {})

        # Resolve agent name
        agent_name = (
            args.get("agent_id") or args.get("agent") or payload.get("agent")
        )
        if not agent_name:
            combo = (code + tool).lower()
            mapping = {
                "claude": "Claude",   "gemini": "Gemini", "copilot": "Copilot",
                "cursor": "Cursor",   "gpt":    "GPT-4",  "llama":   "Llama",
                "mistral":"Mistral",
            }
            agent_name = next((v for k, v in mapping.items() if k in combo), "SwarmWorker")

        # Determine status and task desc
        if tool:
            status    = "TOOL" if "tool" in tool.lower() else "EXECUTING"
            task_desc = f"{tool}({str(args)[:22]})"
        else:
            status    = "WORKING"
            task_desc = (code.splitlines()[0].strip() if code else "exec")[:40]

        # Update global metric cards
        self.fuel_card.used_fuel = min(
            self.fuel_card.used_fuel + random.randint(400, 2500),
            self.fuel_card.capacity,
        )
        self.fuel_card.burn_rate = random.randint(1200, 4500)
        self.db_card.queries    += 1
        self.db_card.latency_ms  = round(random.uniform(0.6, 3.1), 2)
        self.db_card.indexed_vectors += random.randint(0, 2)
        self._os_manager.events_total = self._total_events

        # Mount or update agent card
        await self._upsert_agent(agent_name, status, task_desc)

        # Skill activity detection
        skill_tools = {
            "invoke_compute_res_skill", "execute_dynamic_python",
            "publish_skill", "query_skills", "adapt_and_publish_skill",
        }
        is_skill_op = tool in skill_tools
        if is_skill_op:
            if agent_name in self._agent_cards:
                self._agent_cards[agent_name].skills_run += 1

        # ── Log streams ────────────────────────────────────────────
        info  = AGENT_STYLES.get(agent_name, AGENT_STYLES["SwarmWorker"])
        color = info["color"]
        ts    = datetime.utcnow().strftime("%H:%M:%S")

        self.intent_log.write(
            f"[dim]{ts}[/dim] [{color}]{agent_name}[/{color}]"
            f" → [italic]{task_desc[:48]}[/italic]"
        )

        self.dialogue_log.write(
            f"[bold {color}][{agent_name}][/bold {color}]"
            f" [dim]{status}[/dim] · {task_desc[:55]}"
        )

        if is_skill_op:
            self.skills_log.write(
                f"[dim]{ts}[/dim] [bold #4ADE80]{agent_name}[/bold #4ADE80]"
                f" ⚗ [cyan]{tool}[/cyan]"
            )

        self.console_log.write(
            f"[dim]{ts} EVT#{self._total_events}[/dim] {json.dumps(payload)[:110]}"
        )

    # ─────────────────────────────────────────────────────────────
    #  Agent card lifecycle
    # ─────────────────────────────────────────────────────────────
    async def _upsert_agent(self, name: str, status: str, task: str) -> None:
        grid = self.query_one("#active_agents_grid_box", Container)

        # Ensure AGENT_STYLES has an entry for unknown agents
        if name not in AGENT_STYLES:
            AGENT_STYLES[name] = {
                "color": "#94A3B8", "role": "External Node", "desk": "Desk ?",
            }

        if name not in self._agent_cards:
            card = AgentCard(name)
            self._agent_cards[name] = card
            await grid.mount(card)
            self._log(f"[bold {AGENT_STYLES[name]['color']}]{name}[/] joined the office floor.")

        card = self._agent_cards[name]
        card.agent_status     = status
        card.active_task      = task
        card.last_active_time = time.time()
        card.interaction_count += 1

        # Update CSS status class
        card.remove_class("status-executing", "status-speaking", "status-tool", "status-idle")
        STATUS_CLASS = {"EXECUTING": "status-executing", "SPEAKING": "status-speaking",
                        "TOOL": "status-tool", "IDLE": "status-idle"}
        cls = STATUS_CLASS.get(status)
        if cls:
            card.add_class(cls)

    async def _decay_idle_agents(self) -> None:
        """Mark agents idle after 40s; remove after 2 min. OS-Manager is never touched."""
        now = time.time()
        to_remove = []

        for name, card in list(self._agent_cards.items()):
            idle_s = now - card.last_active_time
            if idle_s > 40 and card.agent_status != "IDLE":
                card.agent_status = "IDLE"
                card.active_task  = "Standing by..."
                card.remove_class("status-executing", "status-speaking", "status-tool")
                card.add_class("status-idle")
            if idle_s > 120:
                to_remove.append(name)

        for name in to_remove:
            card = self._agent_cards.pop(name)
            color = AGENT_STYLES.get(name, {}).get("color", "#94A3B8")
            await card.remove()
            self.dialogue_log.write(
                f"[dim][{name}] stepped away — desk cleared.[/dim]"
            )
            self._log(f"[dim]{name} left the office floor.[/dim]")

    # ─────────────────────────────────────────────────────────────
    #  Actions
    # ─────────────────────────────────────────────────────────────
    async def action_reset_agents(self) -> None:
        """Remove all dynamic agent cards (keep OS Manager)."""
        for name, card in list(self._agent_cards.items()):
            await card.remove()
        self._agent_cards.clear()
        self._log("[yellow]Agent cards cleared. OS Manager remains.[/yellow]")

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def on_tabbed_content_tab_activated(self, _) -> None:
        try:
            self.skills_table.refresh(layout=True)
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────
    def _log(self, msg: str) -> None:
        try:
            ts = datetime.utcnow().strftime("%H:%M:%S")
            self.console_log.write(f"[dim]{ts}[/dim] {msg}")
        except Exception:
            pass


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    AgentOSApp().run()
