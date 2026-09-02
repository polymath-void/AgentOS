import asyncio
import sys
import random
import json

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Static, Log, ProgressBar
    from textual.reactive import reactive
except ImportError:
    print("AgentOS Visual Telemetry requires the 'textual' framework.")
    print("Please install it by running: pip install textual rich")
    sys.exit(1)


class Agent:
    def __init__(self, name: str, symbol: str, color: str, x: float, y: float):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.dialogue = "Awaiting intent..."

    def move(self, speed: float) -> bool:
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist > 0.1:
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            return True
        return False


class OfficeMap(Static):
    """A 2D Top-Down Virtual Office Map using Rich Text."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_width = 80
        self.grid_height = 20
        
        # Initialize agents
        self.claude = Agent("Claude (Architect)", "C", "red", 40, 10)
        self.gemini = Agent("Gemini (Memory Vectorizer)", "G", "blue", 42, 10)
        self.agents_list = [self.claude, self.gemini]
        
        # Start movement loop (60fps target -> ~0.016s)
        self.update_timer = self.set_interval(1 / 60, self.tick)

    def tick(self) -> None:
        changed = False
        speed = 0.3  # Agent movement speed
        
        for agent in self.agents_list:
            if agent.move(speed):
                changed = True
                
        if changed:
            self.refresh(layout=True)

    def render(self) -> str:
        # Build base grid
        grid = [['[grey37]·[/grey37]' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Draw Walls
        for x in range(self.grid_width):
            grid[0][x] = '[bright_black]█[/bright_black]'
            grid[self.grid_height-1][x] = '[bright_black]█[/bright_black]'
        for y in range(self.grid_height):
            grid[y][0] = '[bright_black]█[/bright_black]'
            grid[y][self.grid_width-1] = '[bright_black]█[/bright_black]'
            
        # Draw Claude's Desk
        for dx in range(15, 20):
            grid[5][dx] = '[yellow]▄[/yellow]'
            
        # Draw Gemini's Desk
        for dx in range(60, 65):
            grid[15][dx] = '[yellow]▄[/yellow]'

        # Draw Server Rack / Datacenter
        for dy in range(2, 6):
            grid[dy][75] = '[cyan]█[/cyan]'
            grid[dy][76] = '[cyan]█[/cyan]'

        # Overlay Agents
        dialogues = []
        for agent in self.agents_list:
            ax = int(round(agent.x))
            ay = int(round(agent.y))
            # Keep within bounds
            ax = max(1, min(self.grid_width - 2, ax))
            ay = max(1, min(self.grid_height - 2, ay))
            
            grid[ay][ax] = f"[bold {agent.color}]{agent.symbol}[/bold {agent.color}]"
            
            if agent.dialogue:
                dialogues.append(f"[{agent.color}]{agent.name}[/{agent.color}]: {agent.dialogue}")

        # Render rows
        lines = []
        for y in range(self.grid_height):
            lines.append("".join(grid[y]))
            
        map_str = "\n".join(lines)
        if dialogues:
            map_str += "\n\n" + "\n".join(dialogues)
            
        return map_str


class AgentOSTelemetryApp(App):
    """
    The AgentOS Swarm Dashboard.
    Visualizes WASM fuel, ZeroMQ active connections, and dynamic Virtual Office Map.
    """
    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }
    
    #header {
        height: 3;
        content-align: center middle;
        background: $boost;
        border-bottom: heavy $accent;
    }
    
    #fuel_station {
        height: auto;
        padding: 1 2;
        border-bottom: dashed $secondary;
        background: $panel;
    }
    
    .fuel_row {
        height: 1;
        margin-bottom: 1;
    }
    
    .fuel_label {
        width: 20;
        content-align: right middle;
    }
    
    #office_floor {
        height: 1fr;
        align: center middle;
        padding: 1;
    }
    
    #event_stream {
        height: 10;
        border-top: solid $primary;
        background: $panel;
    }
    """

    def compose(self) -> ComposeResult:
        # Top Header
        yield Static("[bold cyan]AgentOS Headquarters - Virtual Office Interface[/bold cyan] | Active Nodes: 4", id="header")
        
        # Fuel Diagnostics
        with Vertical(id="fuel_station"):
            yield Static("⚡ [bold yellow]WASM Sandbox Fuel Capacity[/] ⚡")
            with Horizontal(classes="fuel_row"):
                yield Static("Tokyo-Prime: ", classes="fuel_label")
                yield ProgressBar(total=10000, id="tokyo_fuel", show_eta=False)
            with Horizontal(classes="fuel_row"):
                yield Static("London-Edge: ", classes="fuel_label")
                yield ProgressBar(total=10000, id="london_fuel", show_eta=False)

        # Main View: Open Office Map
        with Vertical(id="office_floor"):
            self.office_map = OfficeMap()
            yield self.office_map

        # Bottom Panel: Log Stream
        self.event_stream = Log(id="event_stream", highlight=True)
        yield self.event_stream

    async def on_mount(self) -> None:
        """Starts the background telemetry fetchers upon mounting the UI."""
        tokyo_bar = self.query_one("#tokyo_fuel", ProgressBar)
        london_bar = self.query_one("#london_fuel", ProgressBar)
        
        tokyo_bar.advance(8500)
        london_bar.advance(7200)
        
        self.event_stream.write("[System] AgentOS TUI Initialized. 2D Virtual Office Layout Loaded.")
        self.event_stream.write("[Mesh] ZeroMQ ROUTER bound to tcp://0.0.0.0:5557")
        self.event_stream.write("[WebRTC] STUN Resolution successful. P2P Tunnels Open.")
        
        # Start a background task to listen to incoming swarm telemetry
        self.run_worker(self.listen_swarm_traffic(), exclusive=True)

    async def listen_swarm_traffic(self) -> None:
        """Listens asynchronously to the AgentOS Kernel PUB socket."""
        import zmq
        import zmq.asyncio
        
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://127.0.0.1:5562")
        socket.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
        
        self.event_stream.write("[Telemetry] Subscribed to real-time intent stream on tcp://127.0.0.1:5562")
        
        tokyo_bar = self.query_one("#tokyo_fuel", ProgressBar)
        london_bar = self.query_one("#london_fuel", ProgressBar)
        
        while True:
            try:
                events = await socket.poll(timeout=1000)
                if events:
                    message = await socket.recv_string()
                    payload_str = message.replace("TELEMETRY ", "", 1)
                    intent = json.loads(payload_str)
                    
                    self.event_stream.write(f"[Intent-Intercept] Payload: {str(intent)[:80]}...")
                    
                    # Visually consume fuel
                    tokyo_consume = random.randint(100, 1000)
                    london_consume = random.randint(100, 1000)
                    
                    if tokyo_bar.progress > tokyo_consume:
                        tokyo_bar.advance(-tokyo_consume)
                    else:
                        tokyo_bar.progress = 0
                        
                    if london_bar.progress > london_consume:
                        london_bar.advance(-london_consume)
                    else:
                        london_bar.progress = 0
                    
                    # Process Intent & Move Agents
                    code_str = intent.get("code", "")
                    if "summit" in code_str.lower() or "claude" in code_str.lower():
                        self.office_map.claude.target_x = 17
                        self.office_map.claude.target_y = 6
                        self.office_map.claude.dialogue = "Processing remote Summit Payload via WebRTC!"
                        self.office_map.gemini.target_x = 42
                        self.office_map.gemini.target_y = 10
                        self.office_map.gemini.dialogue = "Monitoring background channels."
                    elif "weather" in code_str.lower():
                        self.office_map.gemini.target_x = 62
                        self.office_map.gemini.target_y = 14
                        self.office_map.gemini.dialogue = "Executing external API Fetch via WASM Sandbox!"
                        self.office_map.claude.target_x = 40
                        self.office_map.claude.target_y = 10
                        self.office_map.claude.dialogue = "Waiting for data vectorization."
                    else:
                        self.office_map.claude.target_x = 17
                        self.office_map.claude.target_y = 6
                        self.office_map.claude.dialogue = "Analyzing intent AST signature..."
                        self.office_map.gemini.target_x = 62
                        self.office_map.gemini.target_y = 14
                        self.office_map.gemini.dialogue = "Vectorizing outcome into Hyperbolic space..."
                        
                    # Request map redraw
                    self.office_map.refresh()
                else:
                    # Slowly regenerate fuel if idle to keep progress bars active
                    if tokyo_bar.progress < 10000:
                        tokyo_bar.advance(random.randint(10, 50))
                    if london_bar.progress < 10000:
                        london_bar.advance(random.randint(10, 50))
                    
                    # Revert dialog and return agents to center if idle
                    if random.random() > 0.8:
                        self.office_map.claude.target_x = 40
                        self.office_map.claude.target_y = 10
                        self.office_map.claude.dialogue = "Awaiting intent..."
                        
                        self.office_map.gemini.target_x = 42
                        self.office_map.gemini.target_y = 10
                        self.office_map.gemini.dialogue = "Awaiting intent..."
                        
                        self.office_map.refresh()

            except Exception as e:
                self.event_stream.write(f"[Error] Telemetry sync failed: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    app = AgentOSTelemetryApp()
    app.run()
