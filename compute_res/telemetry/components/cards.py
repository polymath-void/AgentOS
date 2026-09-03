from textual.widgets import Static
from textual.reactive import reactive
import time

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
        self.last_active_time = time.time()

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
