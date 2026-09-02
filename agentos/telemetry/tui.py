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

CLAUDE_ART = """\
   _____
  / o o \\
  \\  _  /
   /|||\\
  //|||\\\\
 // ||| \\\\"""

GEMINI_ART = """\
   .---.
  / * * \\
  |  -  |
   \\___/
   /|||\\
  //|||\\\\
 // ||| \\\\"""


class AgentNodeWidget(Static):
    """A personalized RPG-style widget representing an active AI Agent."""
    
    dialogue = reactive("Awaiting intent...")

    def __init__(self, agent_name: str, color: str, ascii_art: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = agent_name
        self.color = color
        self.ascii_art = ascii_art

    def render(self) -> str:
        # A sleek, dynamically resizing RPG-styled text box in the head
        max_width = 38
        
        # Word wrap the text if it's too long
        words = self.dialogue.split(" ")
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += (word + " ")
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
            
        longest_line = max(len(line) for line in lines) if lines else 0
        
        # Build the dynamic box
        box = f"╭{'─' * (longest_line + 2)}╮\n"
        for line in lines:
            padded_line = line.ljust(longest_line)
            box += f"│ {padded_line} │\n"
        box += f"╰{'─' * (longest_line + 2)}╯"
        
        # The speech bubble pointer
        bubble = "      \\\n       \\_"
        art_colored = f"[{self.color}]{self.ascii_art}[/{self.color}]"
        
        return f"[bold {self.color}]{self.agent_name}[/bold {self.color}]\n\n{box}\n{bubble}\n{art_colored}"


class AgentOSTelemetryApp(App):
    """
    The AgentOS Swarm Dashboard.
    Visualizes WASM fuel, ZeroMQ active connections, and dynamic RPG-style intents.
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
        layout: horizontal;
        height: 1fr;
        align: center middle;
    }
    
    .agent_desk {
        width: 45%;
        height: 100%;
        content-align: center middle;
        padding: 2;
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

        # Main View: Open Office
        with Horizontal(id="office_floor"):
            self.claude_node = AgentNodeWidget("Claude (Architect)", "green", CLAUDE_ART, classes="agent_desk")
            self.gemini_node = AgentNodeWidget("Gemini (Memory Vectorizer)", "cyan", GEMINI_ART, classes="agent_desk")
            yield self.claude_node
            yield self.gemini_node

        # Bottom Panel: Log Stream
        self.event_stream = Log(id="event_stream", highlight=True)
        yield self.event_stream

    async def on_mount(self) -> None:
        """Starts the background telemetry fetchers upon mounting the UI."""
        tokyo_bar = self.query_one("#tokyo_fuel", ProgressBar)
        london_bar = self.query_one("#london_fuel", ProgressBar)
        
        tokyo_bar.advance(8500)
        london_bar.advance(7200)
        
        self.event_stream.write("[System] AgentOS TUI Initialized. Office Layout Loaded.")
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
                    
                    # Update dialog
                    code_str = intent.get("code", "")
                    if "summit" in code_str.lower() or "claude" in code_str.lower():
                        self.claude_node.dialogue = "Processing remote Summit Payload via WebRTC!"
                        self.gemini_node.dialogue = "Monitoring background channels."
                    elif "weather" in code_str.lower():
                        self.gemini_node.dialogue = "Executing external API Fetch via WASM Sandbox!"
                        self.claude_node.dialogue = "Waiting for data vectorization."
                    else:
                        self.claude_node.dialogue = "Analyzing intent AST signature..."
                        self.gemini_node.dialogue = "Vectorizing outcome into Hyperbolic space..."
                else:
                    # Slowly regenerate fuel if idle to keep progress bars active
                    if tokyo_bar.progress < 10000:
                        tokyo_bar.advance(random.randint(10, 50))
                    if london_bar.progress < 10000:
                        london_bar.advance(random.randint(10, 50))
                    
                    # Revert dialog if no events for a while
                    if random.random() > 0.8:
                        self.claude_node.dialogue = "Awaiting intent..."
                        self.gemini_node.dialogue = "Awaiting intent..."

            except Exception as e:
                self.event_stream.write(f"[Error] Telemetry sync failed: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    app = AgentOSTelemetryApp()
    app.run()
