"""
ComputeRes OpenClaw — Agent & Metric Card Components
Office Workspace Design System
"""
import time
import math
from textual.widgets import Static
from textual.reactive import reactive

# ── Agent Style Registry ────────────────────────────────────────────────────
AGENT_STYLES = {
    "Claude":        {"icon": "◈", "color": "#FF6B6B", "border": "#FF6B6B", "role": "Architect Engine",       "desk": "🖥️  Desk A"},
    "Gemini":        {"icon": "◉", "color": "#38BDF8", "border": "#38BDF8", "role": "Vector Memory Oracle",   "desk": "🖥️  Desk B"},
    "Copilot":       {"icon": "◆", "color": "#4ADE80", "border": "#4ADE80", "role": "IDE Sidecar Bridge",     "desk": "🖥️  Desk C"},
    "Cursor":        {"icon": "▲", "color": "#FACC15", "border": "#FACC15", "role": "CRDT AST Mutator",       "desk": "🖥️  Desk D"},
    "GPT-4":         {"icon": "◐", "color": "#F472B6", "border": "#F472B6", "role": "Reasoning Engine",       "desk": "🖥️  Desk E"},
    "Llama":         {"icon": "◑", "color": "#FB923C", "border": "#FB923C", "role": "Local Inference Node",   "desk": "🖥️  Desk F"},
    "Mistral":       {"icon": "◒", "color": "#A78BFA", "border": "#A78BFA", "role": "Compact Swarm Node",     "desk": "🖥️  Desk G"},
    "SwarmWorker":   {"icon": "⬡", "color": "#94A3B8", "border": "#475569", "role": "Dynamic Swarm Node",     "desk": "🖥️  Desk ?"},
}

STATUS_STYLES = {
    "IDLE":      ("grey42",     "○"),
    "WORKING":   ("bold yellow","◐"),
    "SPEAKING":  ("bold cyan",  "◉"),
    "EXECUTING": ("bold green", "●"),
    "TOOL":      ("bold magenta","▶"),
    "ERROR":     ("bold red",   "✖"),
    "DONE":      ("bold blue",  "✔"),
}

def _bar(used: int, total: int, width: int = 18) -> str:
    """Render a compact ASCII progress bar."""
    if total == 0:
        return f"[{'─' * width}]"
    filled = int((used / total) * width)
    filled = max(0, min(filled, width))
    bar_color = "green" if filled < width * 0.6 else ("yellow" if filled < width * 0.85 else "red")
    bar_str = "█" * filled + "░" * (width - filled)
    return f"[{bar_color}]{bar_str}[/{bar_color}]"


class AgentCard(Static):
    """
    Office Desk Card — represents a single AI agent's active workstation.
    Dynamically mounted when telemetry arrives, auto-unmounts after prolonged idle.
    """
    agent_status = reactive("IDLE")
    active_task  = reactive("Awaiting intent...")
    interaction_count = reactive(0)
    skills_used  = reactive(0)
    fuel_consumed = reactive(0)

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = name
        info = AGENT_STYLES.get(name, AGENT_STYLES["SwarmWorker"])
        self.icon  = info["icon"]
        self.color = info["color"]
        self.role  = info["role"]
        self.desk  = info["desk"]
        self.last_active_time = time.time()
        self.session_start = time.time()

    def _uptime(self) -> str:
        secs = int(time.time() - self.session_start)
        h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
        if h > 0:
            return f"{h}h {m:02d}m"
        return f"{m:02d}m {s:02d}s"

    def render(self) -> str:
        style, dot = STATUS_STYLES.get(self.agent_status, ("white", "○"))
        status_badge = f"[{style}]{dot} {self.agent_status}[/{style}]"

        # Fuel mini-bar (relative to interactions as proxy)
        fuel_pct = min(self.fuel_consumed, 50000)
        fuel_bar = _bar(fuel_pct, 50000, 12)

        # Truncate task to fit card width
        task_text = self.active_task
        if len(task_text) > 35:
            task_text = task_text[:32] + "..."

        header    = f"[bold {self.color}] {self.icon}  {self.agent_name}[/bold {self.color}]"
        role_line = f"[dim]    {self.role}[/dim]"
        desk_line = f"[dim]    {self.desk}[/dim]"
        sep       = f"[dim]   {'─' * 28}[/dim]"
        stat_line = f"   Status:  {status_badge}"
        task_line = f"   Intent:  [italic #C9D1D9]{task_text}[/italic #C9D1D9]"
        meta_line = (
            f"   Fuel: {fuel_bar}  "
            f"[dim]↺ {self.interaction_count}  ⏱ {self._uptime()}[/dim]"
        )

        return "\n".join([header, role_line, desk_line, sep, stat_line, task_line, meta_line])


class FuelEngineCard(Static):
    """WASM Fuel Engine & Capacity telemetry card."""
    capacity   = reactive(1_000_000)
    used_fuel  = reactive(142_500)
    burn_rate  = reactive(2_400)
    ram_mb     = reactive(128)

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
    """Hyperbolic Vector DB telemetry card."""
    indexed_vectors = reactive(14_280)
    tree_depth      = reactive(12)
    latency_ms      = reactive(1.4)
    queries         = reactive(0)

    def render(self) -> str:
        # Poincaré ball metaphor: latency as distance from origin
        dist = min(self.latency_ms / 10.0, 0.99)
        dist_bar = _bar(int(dist * 100), 100, 10)
        return (
            f"[bold #D2A8FF]🧠 Hyperbolic DB[/bold #D2A8FF]\n"
            f" Vectors: [bold white]{self.indexed_vectors:,}[/bold white]  "
            f"Depth: [cyan]{self.tree_depth}[/cyan]\n"
            f" Latency: [green]{self.latency_ms:.2f}ms[/green] {dist_bar}\n"
            f" Queries: [dim]{self.queries:,}[/dim]  Metric: [italic]d_H[/italic]"
        )


class SkillsHubCard(Static):
    """SkillsHub DB registry telemetry card."""
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
            f" Forks: [dim]{self.adaptations}[/dim]  "
            f"[dim]FTS5 Indexed[/dim]"
        )


class KernelStatusCard(Static):
    """ComputeRes Kernel & Event Gateway status card."""
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
