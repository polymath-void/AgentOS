"""
ComputeRes Agent OS — Card Components
2D ASCII pixel-art characters + OS Manager permanent card.
"""
import os
import time
from textual.widgets import Static
from textual.reactive import reactive

# ── ASCII 2D Character Sprites (7 lines × ~10 cols) ─────────────────────────
SPRITES = {
    "OS-Manager": [
        "  [bold #00FFD0]┌─╥─┐[/bold #00FFD0]  ",
        "  [bold #00FFD0]│◈╫◈│[/bold #00FFD0]  ",
        "  [bold #00FFD0]└─╨─┘[/bold #00FFD0]  ",
        " [bold #00FFD0]╔══╧══╗[/bold #00FFD0] ",
        " [bold #00FFD0]║▓▓▓▓▓║[/bold #00FFD0] ",
        " [bold #00FFD0]╚══╤══╝[/bold #00FFD0] ",
        "  [bold #00FFD0]▐█ █▌[/bold #00FFD0]  ",
    ],
    "Claude": [
        "   [bold #FF6B6B]│▲│[/bold #FF6B6B]   ",
        "  [bold #FF6B6B]╔═══╗[/bold #FF6B6B]  ",
        "  [bold #FF6B6B]║◈ ◈║[/bold #FF6B6B]  ",
        "  [bold #FF6B6B]╚═▼═╝[/bold #FF6B6B]  ",
        " [bold #FF6B6B]╔═════╗[/bold #FF6B6B] ",
        " [bold #FF6B6B]╚══╤══╝[/bold #FF6B6B] ",
        "  [bold #FF6B6B]▐█ █▌[/bold #FF6B6B]  ",
    ],
    "Gemini": [
        "  [bold #38BDF8]╱   ╲[/bold #38BDF8]  ",
        " [bold #38BDF8]│◉   ◉│[/bold #38BDF8] ",
        " [bold #38BDF8]│  ▲  │[/bold #38BDF8] ",
        "  [bold #38BDF8]╲_▼_╱[/bold #38BDF8]  ",
        " [bold #38BDF8]╔═════╗[/bold #38BDF8] ",
        " [bold #38BDF8]╚══╤══╝[/bold #38BDF8] ",
        "  [bold #38BDF8]▐█ █▌[/bold #38BDF8]  ",
    ],
    "Copilot": [
        "  [bold #4ADE80]▄███▄[/bold #4ADE80]  ",
        " [bold #4ADE80]█▀▀▀▀▀█[/bold #4ADE80] ",
        " [bold #4ADE80]█ ◈◈◈ █[/bold #4ADE80] ",
        " [bold #4ADE80]█▄▄▄▄▄█[/bold #4ADE80] ",
        "  [bold #4ADE80]╔═══╗[/bold #4ADE80]  ",
        " [bold #4ADE80]▐╔═══╗▌[/bold #4ADE80] ",
        "  [bold #4ADE80]█   █[/bold #4ADE80]  ",
    ],
    "Cursor": [
        "   [bold #FACC15]▲[/bold #FACC15]     ",
        "  [bold #FACC15]▐◆▌[/bold #FACC15]   ",
        " [bold #FACC15]╔═════╗[/bold #FACC15] ",
        " [bold #FACC15]║ ─▶─ ║[/bold #FACC15] ",
        " [bold #FACC15]╚══╤══╝[/bold #FACC15] ",
        "  [bold #FACC15]▐▀▀▀▌[/bold #FACC15]  ",
        " [bold #FACC15]▐█   █▌[/bold #FACC15] ",
    ],
    "GPT-4": [
        "  [bold #F472B6]~~~~~[/bold #F472B6]  ",
        "  [bold #F472B6]╔═══╗[/bold #F472B6]  ",
        "  [bold #F472B6]║●─●║[/bold #F472B6]  ",
        "  [bold #F472B6]║ ≋ ║[/bold #F472B6]  ",
        "  [bold #F472B6]╚═╤═╝[/bold #F472B6]  ",
        " [bold #F472B6]▄╔═╧═╗▄[/bold #F472B6] ",
        " [bold #F472B6]▀╚═══╝▀[/bold #F472B6] ",
    ],
    "Llama": [
        "   [bold #FB923C]╭─╮[/bold #FB923C]   ",
        "  [bold #FB923C]╭╯◕╰╮[/bold #FB923C]  ",
        "  [bold #FB923C]│ ω │[/bold #FB923C]  ",
        "  [bold #FB923C]╰───╯[/bold #FB923C]  ",
        " [bold #FB923C]╔═════╗[/bold #FB923C] ",
        " [bold #FB923C]║ ~~~ ║[/bold #FB923C] ",
        " [bold #FB923C]╚█   █╝[/bold #FB923C] ",
    ],
    "Mistral": [
        "  [bold #A78BFA]≋≋≋≋≋[/bold #A78BFA]  ",
        " [bold #A78BFA]╔═════╗[/bold #A78BFA] ",
        " [bold #A78BFA]║ ◐◑  ║[/bold #A78BFA] ",
        " [bold #A78BFA]╚══╤══╝[/bold #A78BFA] ",
        " [bold #A78BFA]≋╔═╧═╗≋[/bold #A78BFA] ",
        " [bold #A78BFA]≋║   ║≋[/bold #A78BFA] ",
        " [bold #A78BFA]≋╚═══╝≋[/bold #A78BFA] ",
    ],
    "SwarmWorker": [
        "  [bold #94A3B8]⬡⬡⬡[/bold #94A3B8]   ",
        " [bold #94A3B8]⬡ ◉ ⬡[/bold #94A3B8]  ",
        "  [bold #94A3B8]⬡⬡⬡[/bold #94A3B8]   ",
        "  [bold #94A3B8]╔═╗[/bold #94A3B8]    ",
        "  [bold #94A3B8]║░║[/bold #94A3B8]    ",
        " [bold #94A3B8]╔╩═╩╗[/bold #94A3B8]  ",
        " [bold #94A3B8]╚═══╝[/bold #94A3B8]  ",
    ],
}

AGENT_STYLES = {
    "OS-Manager":  {"color": "#00FFD0", "role": "OS Performance Monitor",  "desk": "Control Hub"},
    "Claude":      {"color": "#FF6B6B", "role": "Architect Engine",        "desk": "Desk A"},
    "Gemini":      {"color": "#38BDF8", "role": "Vector Memory Oracle",    "desk": "Desk B"},
    "Copilot":     {"color": "#4ADE80", "role": "IDE Sidecar Bridge",      "desk": "Desk C"},
    "Cursor":      {"color": "#FACC15", "role": "CRDT AST Mutator",        "desk": "Desk D"},
    "GPT-4":       {"color": "#F472B6", "role": "Reasoning Engine",        "desk": "Desk E"},
    "Llama":       {"color": "#FB923C", "role": "Local Inference Node",    "desk": "Desk F"},
    "Mistral":     {"color": "#A78BFA", "role": "Compact Swarm Node",      "desk": "Desk G"},
    "SwarmWorker": {"color": "#94A3B8", "role": "Dynamic Swarm Node",      "desk": "Desk ?"},
}

STATUS_STYLES = {
    "IDLE":       ("grey42",       "○"),
    "MONITORING": ("bold #00FFD0", "◈"),
    "WORKING":    ("bold yellow",  "◐"),
    "SPEAKING":   ("bold cyan",    "◉"),
    "EXECUTING":  ("bold green",   "●"),
    "TOOL":       ("bold magenta", "▶"),
    "ERROR":      ("bold red",     "✖"),
    "DONE":       ("bold blue",    "✔"),
}


def _bar(used: int, total: int, width: int = 12) -> str:
    if total == 0:
        return "░" * width
    filled = max(0, min(int((used / total) * width), width))
    color = "green" if filled < width * 0.6 else ("yellow" if filled < width * 0.85 else "red")
    return f"[{color}]{'█' * filled}{'░' * (width - filled)}[/{color}]"


def _get_sprite(name: str) -> list:
    return SPRITES.get(name, SPRITES["SwarmWorker"])


# ═══════════════════════════════════════════════════════════════
#  OS Manager Card — permanent, always on the floor
# ═══════════════════════════════════════════════════════════════
class OSManagerCard(Static):
    """
    Permanent OS Monitor agent — always present on the Office Floor.
    Shows live system metrics: CPU, RAM, disk, kernel IPC, agent count.
    Never decays or gets removed.
    """
    ram_used_mb    = reactive(0)
    ram_total_mb   = reactive(512)
    disk_used_pct  = reactive(0)
    cpu_load       = reactive("—")
    agent_count    = reactive(0)
    events_total   = reactive(0)
    kernel_online  = reactive(False)

    def render(self) -> str:
        sprite = "\n".join(_get_sprite("OS-Manager"))
        k_dot  = "[bold #00FFD0]●[/bold #00FFD0]" if self.kernel_online else "[bold red]✖[/bold red]"
        k_str  = "ONLINE" if self.kernel_online else "OFFLINE"
        ram_bar  = _bar(self.ram_used_mb, self.ram_total_mb, 10)
        disk_bar = _bar(self.disk_used_pct, 100, 10)

        return "\n".join([
            sprite,
            f"[bold #00FFD0] OS-Manager[/bold #00FFD0]",
            f" [dim]OS Performance Monitor · Control Hub[/dim]",
            f" [dim]{'─' * 24}[/dim]",
            f" [bold #00FFD0]◈ MONITORING[/bold #00FFD0]",
            f" RAM: {ram_bar} [white]{self.ram_used_mb}[/white][dim]/{self.ram_total_mb}MB[/dim]",
            f" Disk: {disk_bar} [dim]{self.disk_used_pct}%[/dim]",
            f" Load: [cyan]{self.cpu_load}[/cyan]  "
              f"Agents: [bold white]{self.agent_count}[/bold white]",
            f" Kernel: {k_dot} [dim]{k_str}[/dim]  "
              f"Events: [dim]{self.events_total}[/dim]",
        ])


# ═══════════════════════════════════════════════════════════════
#  Dynamic Agent Card
# ═══════════════════════════════════════════════════════════════
class AgentCard(Static):
    """Dynamically mounted desk card for active swarm agents."""
    agent_status     = reactive("IDLE")
    active_task      = reactive("Awaiting intent...")
    interaction_count = reactive(0)
    fuel_consumed    = reactive(0)
    skills_run       = reactive(0)

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name       = name
        info = AGENT_STYLES.get(name, AGENT_STYLES["SwarmWorker"])
        self.color            = info["color"]
        self.role             = info["role"]
        self.desk             = info["desk"]
        self.last_active_time = time.time()
        self.session_start    = time.time()

    def _uptime(self) -> str:
        secs = int(time.time() - self.session_start)
        h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
        return f"{h}h{m:02d}m" if h else f"{m:02d}m{s:02d}s"

    def render(self) -> str:
        style, dot   = STATUS_STYLES.get(self.agent_status, ("white", "○"))
        status_badge = f"[{style}]{dot} {self.agent_status}[/{style}]"
        sprite       = "\n".join(_get_sprite(self.agent_name))
        task_text    = (self.active_task[:27] + "...") if len(self.active_task) > 30 else self.active_task
        fuel_bar     = _bar(min(self.fuel_consumed, 50000), 50000, 10)

        return "\n".join([
            sprite,
            f"[bold {self.color}] {self.agent_name}[/bold {self.color}]",
            f" [dim]{self.role} · {self.desk}[/dim]",
            f" [dim]{'─' * 24}[/dim]",
            f" {status_badge}",
            f" [italic #C9D1D9]{task_text}[/italic #C9D1D9]",
            f" {fuel_bar} [dim]↺{self.interaction_count} ⏱{self._uptime()} ⚗{self.skills_run}[/dim]",
        ])


# ═══════════════════════════════════════════════════════════════
#  Metric Header Cards
# ═══════════════════════════════════════════════════════════════
class FuelEngineCard(Static):
    capacity  = reactive(1_000_000)
    used_fuel = reactive(0)
    burn_rate = reactive(0)
    ram_mb    = reactive(0)

    def render(self) -> str:
        used_pct = (self.used_fuel / self.capacity) * 100 if self.capacity else 0
        fuel_bar = _bar(self.used_fuel, self.capacity, 14)
        ram_bar  = _bar(self.ram_mb, 512, 8)
        return (
            f"[bold #58A6FF]⚡ WASM Fuel[/bold #58A6FF]\n"
            f" {fuel_bar} [yellow]{used_pct:.1f}%[/yellow]\n"
            f" Used [white]{self.used_fuel:,}[/white][dim]/{self.capacity:,}[/dim]\n"
            f" Burn [cyan]{self.burn_rate:,}/s[/cyan] RAM {ram_bar}[green]{self.ram_mb}MB[/green]"
        )


class HyperbolicDBCard(Static):
    indexed_vectors = reactive(0)
    tree_depth      = reactive(12)
    latency_ms      = reactive(0.0)
    queries         = reactive(0)

    def render(self) -> str:
        dist_bar = _bar(int(min(self.latency_ms / 10.0, 0.99) * 100), 100, 8)
        return (
            f"[bold #D2A8FF]🧠 Hyperbolic DB[/bold #D2A8FF]\n"
            f" Vectors [bold white]{self.indexed_vectors:,}[/bold white] Depth [cyan]{self.tree_depth}[/cyan]\n"
            f" Latency [green]{self.latency_ms:.2f}ms[/green] {dist_bar}\n"
            f" Queries [dim]{self.queries:,}[/dim]  Metric [italic]d_H[/italic]"
        )


class SkillsHubCard(Static):
    total_skills    = reactive(0)
    top_niche       = reactive("—")
    fts_ready       = reactive(False)

    def render(self) -> str:
        fts_color = "#4ADE80" if self.fts_ready else "#94A3B8"
        fts_label = "FTS5 ●" if self.fts_ready else "FTS5 ○"
        return (
            f"[bold #4ADE80]⚗️  SkillsHub[/bold #4ADE80]\n"
            f" Skills [bold white]{self.total_skills}[/bold white] registered\n"
            f" Top [cyan]{self.top_niche}[/cyan]\n"
            f" [{fts_color}]{fts_label}[/{fts_color}] [dim]Indexed[/dim]"
        )


class KernelStatusCard(Static):
    kernel_status   = reactive("CHECKING")
    active_agents   = reactive(0)
    events_pushed   = reactive(0)
    uptime_str      = reactive("—")

    def render(self) -> str:
        k_color = "#4ADE80" if self.kernel_status == "ONLINE" else ("#FACC15" if self.kernel_status == "CHECKING" else "#FF6B6B")
        k_dot   = "●" if self.kernel_status == "ONLINE" else ("◐" if self.kernel_status == "CHECKING" else "✖")
        return (
            f"[bold #FB923C]🌐 Kernel[/bold #FB923C]\n"
            f" [{k_color}]{k_dot} {self.kernel_status}[/{k_color}] Up [dim]{self.uptime_str}[/dim]\n"
            f" Agents [bold white]{self.active_agents}[/bold white] online\n"
            f" Events [dim]{self.events_pushed}[/dim] pushed"
        )
