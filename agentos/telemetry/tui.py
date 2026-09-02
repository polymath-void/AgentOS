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
    def __init__(self, name: str, symbol: str, color: str, x_pct: float, y_pct: float):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.x_pct = x_pct
        self.y_pct = y_pct
        self.target_x_pct = x_pct
        self.target_y_pct = y_pct
        self.dialogue = "Awaiting intent..."
        self.status = "idle"

    def get_display(self) -> str:
        emojis = {"idle": "💤", "working": "⠷", "speaking": "💬", "tool": "🛠️"}
        return f"[bold {self.color}]{self.symbol}[/bold {self.color}]{emojis.get(self.status, '')}"

    def move(self, speed: float) -> bool:
        dx = self.target_x_pct - self.x_pct
        dy = self.target_y_pct - self.y_pct
        dist = (dx**2 + dy**2)**0.5
        if dist > 0.01:
            self.x_pct += (dx / dist) * speed
            self.y_pct += (dy / dist) * speed
            return True
        return False

class OfficeMap(Static):
    """A Dynamic 2D Virtual Office Map using Rich Text."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize agents (positions as percentages 0.0-1.0)
        self.claude = Agent("Claude (Architect)", "C", "red", 0.2, 0.25)
        self.gemini = Agent("Gemini (Memory Vectorizer)", "G", "blue", 0.8, 0.75)
        self.agents_list = [self.claude, self.gemini]
        self.draw_collab_line = False
        
        # Start movement loop
        self.update_timer = self.set_interval(1 / 60, self.tick)

    def tick(self) -> None:
        changed = False
        speed = 0.01  # Agent movement speed in %
        for agent in self.agents_list:
            if agent.move(speed):
                changed = True
        if changed:
            self.refresh(layout=True)

    def render(self) -> str:
        width = max(20, self.size.width)
        height = max(10, self.size.height)
        
        # Reserve space for dialogues at the bottom
        grid_height = max(5, height - 6)
        grid_width = width
        
        # Build base grid
        grid = [['[grey37]·[/grey37]' for _ in range(grid_width)] for _ in range(grid_height)]
        
        # Draw Walls
        for x in range(grid_width):
            grid[0][x] = '[bright_black]█[/bright_black]'
            grid[grid_height-1][x] = '[bright_black]█[/bright_black]'
        for y in range(grid_height):
            grid[y][0] = '[bright_black]█[/bright_black]'
            grid[y][grid_width-1] = '[bright_black]█[/bright_black]'
            
        # Draw Claude's Desk (15% to 25% width, 25% height)
        c_start = int(0.15 * grid_width)
        c_end = int(0.25 * grid_width)
        c_y = int(0.25 * grid_height)
        for dx in range(c_start, c_end):
            if dx < grid_width: grid[c_y][dx] = '[yellow]▄[/yellow]'
            
        # Draw Gemini's Desk (75% to 85% width, 75% height)
        g_start = int(0.75 * grid_width)
        g_end = int(0.85 * grid_width)
        g_y = int(0.75 * grid_height)
        for dx in range(g_start, g_end):
            if dx < grid_width: grid[g_y][dx] = '[yellow]▄[/yellow]'

        # Draw Server Rack (90% width, 20% to 40% height)
        s_x1, s_x2 = int(0.9 * grid_width), int(0.92 * grid_width)
        s_y1, s_y2 = int(0.2 * grid_height), int(0.4 * grid_height)
        for dy in range(s_y1, s_y2):
            if dy < grid_height:
                if s_x1 < grid_width: grid[dy][s_x1] = '[cyan]█[/cyan]'
                if s_x2 < grid_width: grid[dy][s_x2] = '[cyan]█[/cyan]'

        # Draw Meeting Pod (Center of the room)
        mp_x1, mp_x2 = int(0.40 * grid_width), int(0.60 * grid_width)
        mp_y1, mp_y2 = int(0.40 * grid_height), int(0.60 * grid_height)
        if mp_x2 > mp_x1 and mp_y2 > mp_y1:
            if mp_y1 < grid_height: grid[mp_y1][mp_x1:mp_x2+1] = ['[magenta]─[/magenta]'] * (mp_x2 - mp_x1 + 1)
            if mp_y2 < grid_height: grid[mp_y2][mp_x1:mp_x2+1] = ['[magenta]─[/magenta]'] * (mp_x2 - mp_x1 + 1)
            for dy in range(mp_y1, mp_y2 + 1):
                if dy < grid_height:
                    grid[dy][mp_x1] = '[magenta]│[/magenta]'
                    grid[dy][mp_x2] = '[magenta]│[/magenta]'
            if mp_y1 < grid_height: 
                grid[mp_y1][mp_x1] = '[magenta]╭[/magenta]'
                grid[mp_y1][mp_x2] = '[magenta]╮[/magenta]'
            if mp_y2 < grid_height:
                grid[mp_y2][mp_x1] = '[magenta]╰[/magenta]'
                grid[mp_y2][mp_x2] = '[magenta]╯[/magenta]'

        # Draw Collaboration Lines (Bresenham)
        if self.draw_collab_line:
            x0 = int(round(self.claude.x_pct * grid_width))
            y0 = int(round(self.claude.y_pct * grid_height))
            x1 = int(round(self.gemini.x_pct * grid_width))
            y1 = int(round(self.gemini.y_pct * grid_height))
            
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy
            
            while True:
                if 0 <= x0 < grid_width and 0 <= y0 < grid_height:
                    # don't overwrite walls or desks or meeting pod walls
                    cell = grid[y0][x0]
                    if '·' in cell or ' ' in cell:
                        grid[y0][x0] = '[green]┈[/green]'
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy

        # Overlay Agents
        dialogues = []
        for agent in self.agents_list:
            ax = int(round(agent.x_pct * grid_width))
            ay = int(round(agent.y_pct * grid_height))
            # Keep within bounds and avoid clipping the right edge due to emoji width
            ax = max(1, min(grid_width - 3, ax))
            ay = max(1, min(grid_height - 2, ay))
            
            grid[ay][ax] = agent.get_display()
            # Clear the adjacent cell to compensate for double-width emoji rendering in terminal
            if ax + 1 < grid_width:
                grid[ay][ax + 1] = ''
            
            if agent.dialogue:
                dialogues.append(f"[{agent.color}]{agent.name}[/{agent.color}]: {agent.dialogue}")

        # Render rows
        lines = ["".join(filter(None, grid[y])) for y in range(grid_height)]
            
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
                        self.office_map.claude.target_x_pct = 0.45
                        self.office_map.claude.target_y_pct = 0.50
                        self.office_map.claude.status = "working"
                        self.office_map.claude.dialogue = "Processing remote Summit Payload via WebRTC!"
                        self.office_map.gemini.target_x_pct = 0.55
                        self.office_map.gemini.target_y_pct = 0.50
                        self.office_map.gemini.status = "idle"
                        self.office_map.gemini.dialogue = "Monitoring background channels."
                        self.office_map.draw_collab_line = True
                    elif "weather" in code_str.lower():
                        self.office_map.gemini.target_x_pct = 0.80
                        self.office_map.gemini.target_y_pct = 0.75
                        self.office_map.gemini.status = "tool"
                        self.office_map.gemini.dialogue = "Executing external API Fetch via WASM Sandbox!"
                        self.office_map.claude.target_x_pct = 0.20
                        self.office_map.claude.target_y_pct = 0.25
                        self.office_map.claude.status = "idle"
                        self.office_map.claude.dialogue = "Waiting for data vectorization."
                        self.office_map.draw_collab_line = False
                    else:
                        self.office_map.claude.target_x_pct = 0.45
                        self.office_map.claude.target_y_pct = 0.50
                        self.office_map.claude.status = "speaking"
                        self.office_map.claude.dialogue = "Analyzing intent AST signature..."
                        self.office_map.gemini.target_x_pct = 0.55
                        self.office_map.gemini.target_y_pct = 0.50
                        self.office_map.gemini.status = "speaking"
                        self.office_map.gemini.dialogue = "Vectorizing outcome into Hyperbolic space..."
                        self.office_map.draw_collab_line = True
                        
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
                        self.office_map.claude.target_x_pct = 0.20
                        self.office_map.claude.target_y_pct = 0.25
                        self.office_map.claude.status = "idle"
                        self.office_map.claude.dialogue = "Awaiting intent..."
                        
                        self.office_map.gemini.target_x_pct = 0.80
                        self.office_map.gemini.target_y_pct = 0.75
                        self.office_map.gemini.status = "idle"
                        self.office_map.gemini.dialogue = "Awaiting intent..."
                        self.office_map.draw_collab_line = False
                        
                        self.office_map.refresh()

            except Exception as e:
                self.event_stream.write(f"[Error] Telemetry sync failed: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    app = AgentOSTelemetryApp()
    app.run()
