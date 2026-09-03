"""
ComputeRes Agent OS — Agent Desk Card Components
2D ASCII pixel-art characters for each AI agent.
"""
import time
from textual.widgets import Static
from textual.reactive import reactive

# ── ASCII 2D Character Sprites ──────────────────────────────────────────────
# Each sprite is a list of Rich-markup lines, 10 chars wide.
# They use Unicode half-block chars (▀▄█▌▐░) for pixel-art look.

SPRITES = {
    # Claude — Red architect with square helmet & antenna
    "Claude": [
        "    [bold #FF6B6B]│▲│[/bold #FF6B6B]    ",
        "  [bold #FF6B6B]╔═══╗[/bold #FF6B6B]  ",
        "  [bold #FF6B6B]║◈ ◈║[/bold #FF6B6B]  ",
        "  [bold #FF6B6B]╚═▼═╝[/bold #FF6B6B]  ",
        " [bold #FF6B6B]╔═════╗[/bold #FF6B6B] ",
        " [bold #FF6B6B]╚══╤══╝[/bold #FF6B6B] ",
        "  [bold #FF6B6B]▐█ █▌[/bold #FF6B6B]  ",
    ],
    # Gemini — Cyan mystical owl with twin eyes
    "Gemini": [
        "  [bold #38BDF8]╱   ╲[/bold #38BDF8]  ",
        " [bold #38BDF8]│◉   ◉│[/bold #38BDF8] ",
        " [bold #38BDF8]│  ▲  │[/bold #38BDF8] ",
        "  [bold #38BDF8]╲_▼_╱[/bold #38BDF8]  ",
        " [bold #38BDF8]╔═════╗[/bold #38BDF8] ",
        " [bold #38BDF8]╚══╤══╝[/bold #38BDF8] ",
        "  [bold #38BDF8]▐█ █▌[/bold #38BDF8]  ",
    ],
    # Copilot — Green pilot with visor helmet
    "Copilot": [
        "  [bold #4ADE80]▄███▄[/bold #4ADE80]  ",
        " [bold #4ADE80]█▀▀▀▀▀█[/bold #4ADE80] ",
        " [bold #4ADE80]█ ◈◈◈ █[/bold #4ADE80] ",
        " [bold #4ADE80]█▄▄▄▄▄█[/bold #4ADE80] ",
        "  [bold #4ADE80]╔═══╗[/bold #4ADE80]  ",
        " [bold #4ADE80]▐╔═══╗▌[/bold #4ADE80] ",
        "  [bold #4ADE80]█   █[/bold #4ADE80]  ",
    ],
    # Cursor — Yellow lightning mutator, triangular head
    "Cursor": [
        "   [bold #FACC15] ▲ [/bold #FACC15]   ",
        "  [bold #FACC15]▐◆▌[/bold #FACC15]   ",
        " [bold #FACC15]╔═════╗[/bold #FACC15] ",
        " [bold #FACC15]║ ─▶─ ║[/bold #FACC15] ",
        " [bold #FACC15]╚══╤══╝[/bold #FACC15] ",
        "  [bold #FACC15]▐▀▀▀▌[/bold #FACC15]  ",
        " [bold #FACC15]▐█   █▌[/bold #FACC15] ",
    ],
    # GPT-4 — Pink neural net humanoid with halo ring
    "GPT-4": [
        "  [bold #F472B6]~~~~~[/bold #F472B6]  ",
        "  [bold #F472B6]╔═══╗[/bold #F472B6]  ",
        "  [bold #F472B6]║●─●║[/bold #F472B6]  ",
        "  [bold #F472B6]║ ≋ ║[/bold #F472B6]  ",
        "  [bold #F472B6]╚═╤═╝[/bold #F472B6]  ",
        " [bold #F472B6]▄╔═╧═╗▄[/bold #F472B6] ",
        " [bold #F472B6]▀╚═══╝▀[/bold #F472B6] ",
    ],
    # Llama — Orange local inference, rounded soft shape
    "Llama": [
        "   [bold #FB923C]╭─╮[/bold #FB923C]   ",
        "  [bold #FB923C]╭╯◕╰╮[/bold #FB923C]  ",
        "  [bold #FB923C]│ ω │[/bold #FB923C]  ",
        "  [bold #FB923C]╰───╯[/bold #FB923C]  ",
        " [bold #FB923C]╔═════╗[/bold #FB923C] ",
        " [bold #FB923C]║ ~~~ ║[/bold #FB923C] ",
        " [bold #FB923C]╚█   █╝[/bold #FB923C] ",
    ],
    # Mistral — Purple wind spirit, wavy cloak
    "Mistral": [
        "  [bold #A78BFA]≋≋≋≋≋[/bold #A78BFA]  ",
        " [bold #A78BFA]╔═════╗[/bold #A78BFA] ",
        " [bold #A78BFA]║ ◐◑ ║[/bold #A78BFA] ",
        " [bold #A78BFA]╚══╤══╝[/bold #A78BFA] ",
        " [bold #A78BFA]≋╔═╧═╗≋[/bold #A78BFA] ",
        " [bold #A78BFA]≋║   ║≋[/bold #A78BFA] ",
        " [bold #A78BFA]≋╚═══╝≋[/bold #A78BFA] ",
    ],
    # SwarmWorker — Grey hexagonal drone
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

# ── Agent Metadata ───────────────────────────────────────────────────────────
AGENT_STYLES = {
    "Claude":      {"color": "#FF6B6B", "role": "Architect Engine",     "desk": "Desk A"},
    "Gemini":      {"color": "#38BDF8", "role": "Vector Memory Oracle", "desk": "Desk B"},
    "Copilot":     {"color": "#4ADE80", "role": "IDE Sidecar Bridge",   "desk": "Desk C"},
    "Cursor":      {"color": "#FACC15", "role": "CRDT AST Mutator",     "desk": "Desk D"},
    "GPT-4":       {"color": "#F472B6", "role": "Reasoning Engine",     "desk": "Desk E"},
    "Llama":       {"color": "#FB923C", "role": "Local Inference Node", "desk": "Desk F"},
    "Mistral":     {"color": "#A78BFA", "role": "Compact Swarm Node",   "desk": "Desk G"},
    "SwarmWorker": {"color": "#94A3B8", "role": "Dynamic Swarm Node",   "desk": "Desk ?"},
}

STATUS_STYLES = {
    "IDLE":      ("grey42",       "○"),
    "WORKING":   ("bold yellow",  "◐"),
    "SPEAKING":  ("bold cyan",    "◉"),
    "EXECUTING": ("bold green",   "●"),
    "TOOL":      ("bold magenta", "▶"),
    "ERROR":     ("bold red",     "✖"),
    "DONE":      ("bold blue",    "✔"),
}


def _bar(used: int, total: int, width: int = 12) -> str:
    if total == 0:
        return f"[{'─' * width}]"
    filled = max(0, min(int((used / total) * width), width))
    color = "green" if filled < width * 0.6 else ("yellow" if filled < width * 0.85 else "red")
    return f"[{color}]{'█' * filled}{'░' * (width - filled)}[/{color}]"


def _get_sprite(name: str) -> list:
    return SPRITES.get(name, SPRITES["SwarmWorker"])


class AgentCard(Static):
    """
    Agent Workstation Desk Card with 2D ASCII character art.
    Dynamically mounted to the Office Floor when an agent activates.
    """
    agent_status    = reactive("IDLE")
    active_task     = reactive("Awaiting intent...")
    interaction_count = reactive(0)
    fuel_consumed   = reactive(0)

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = name
        info = AGENT_STYLES.get(name, AGENT_STYLES["SwarmWorker"])
        self.color = info["color"]
        self.role  = info["role"]
        self.desk  = info["desk"]
        self.last_active_time = time.time()
        self.session_start    = time.time()

    def _uptime(self) -> str:
        secs = int(time.time() - self.session_start)
        h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
        return f"{h}h{m:02d}m" if h else f"{m:02d}m{s:02d}s"

    def render(self) -> str:
        style, dot = STATUS_STYLES.get(self.agent_status, ("white", "○"))
        status_badge = f"[{style}]{dot} {self.agent_status}[/{style}]"

        sprite_lines = _get_sprite(self.agent_name)
        sprite = "\n".join(sprite_lines)

        task_text = self.active_task
        if len(task_text) > 30:
            task_text = task_text[:27] + "..."

        fuel_bar = _bar(min(self.fuel_consumed, 50000), 50000, 10)

        name_line = f"[bold {self.color}] {self.agent_name}[/bold {self.color}]"
        role_line = f" [dim]{self.role}[/dim]"
        desk_line = f" [dim]{self.desk}[/dim]"
        sep_line  = f" [dim]{'─' * 20}[/dim]"
        stat_line = f" {status_badge}"
        task_line = f" [italic #C9D1D9]{task_text}[/italic #C9D1D9]"
        meta_line = f" {fuel_bar} [dim]↺{self.interaction_count} ⏱{self._uptime()}[/dim]"

        return "\n".join([
            sprite,
            name_line, role_line, desk_line,
            sep_line,
            stat_line, task_line, meta_line,
        ])


class FuelEngineCard(Static):
    capacity  = reactive(1_000_000)
    used_fuel = reactive(142_500)
    burn_rate = reactive(2_400)
    ram_mb    = reactive(128)

    def render(self) -> str:
        used_pct = (self.used_fuel / self.capacity) * 100
        fuel_bar = _bar(self.used_fuel, self.capacity, 16)
        ram_bar  = _bar(self.ram_mb, 512, 10)
        return (
            f"[bold #58A6FF]⚡ WASM Fuel Engine[/bold #58A6FF]\n"
            f" {fuel_bar} [yellow]{used_pct:.1f}%[/yellow]\n"
            f" Used: [white]{self.used_fuel:,}[/white] / [dim]{self.capacity:,}[/dim]\n"
            f" Burn: [cyan]{self.burn_rate:,}/s[/cyan]  "
            f"RAM: {ram_bar}[green]{self.ram_mb}MB[/green]"
        )


class HyperbolicDBCard(Static):
    indexed_vectors = reactive(14_280)
    tree_depth      = reactive(12)
    latency_ms      = reactive(1.4)
    queries         = reactive(0)

    def render(self) -> str:
        dist_bar = _bar(int(min(self.latency_ms / 10.0, 0.99) * 100), 100, 10)
        return (
            f"[bold #D2A8FF]🧠 Hyperbolic DB[/bold #D2A8FF]\n"
            f" Vectors: [bold white]{self.indexed_vectors:,}[/bold white]  "
            f"Depth: [cyan]{self.tree_depth}[/cyan]\n"
            f" Latency: [green]{self.latency_ms:.2f}ms[/green] {dist_bar}\n"
            f" Queries: [dim]{self.queries:,}[/dim]  Metric: [italic]d_H[/italic]"
        )


class SkillsHubCard(Static):
    total_skills    = reactive(0)
    published_today = reactive(0)
    top_niche       = reactive("—")
    adaptations     = reactive(0)

    def render(self) -> str:
        return (
            f"[bold #4ADE80]⚗️  SkillsHub Registry[/bold #4ADE80]\n"
            f" Skills: [bold white]{self.total_skills}[/bold white]  "
            f"New: [green]+{self.published_today}[/green]\n"
            f" Top Niche: [cyan]{self.top_niche}[/cyan]\n"
            f" Forks: [dim]{self.adaptations}[/dim]  [dim]FTS5 Indexed[/dim]"
        )


class KernelStatusCard(Static):
    kernel_status   = reactive("ONLINE")
    active_webhooks = reactive(0)
    events_pushed   = reactive(0)
    uptime_str      = reactive("0m 00s")

    def render(self) -> str:
        k_color = "#4ADE80" if self.kernel_status == "ONLINE" else "#FF6B6B"
        k_dot   = "●" if self.kernel_status == "ONLINE" else "✖"
        return (
            f"[bold #FB923C]🌐 Kernel Gateway[/bold #FB923C]\n"
            f" [{k_color}]{k_dot} {self.kernel_status}[/{k_color}]  "
            f"Up: [dim]{self.uptime_str}[/dim]\n"
            f" Webhooks: [cyan]{self.active_webhooks}[/cyan]  "
            f"Pushed: [dim]{self.events_pushed}[/dim]\n"
            f" IPC: [dim]tcp://127.0.0.1:5557[/dim]"
        )
