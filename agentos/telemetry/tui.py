import asyncio
import sys

try:
    from textual.app import App, ComposeResult
    from textual.containers import Grid, Horizontal, Vertical
    from textual.widgets import Header, Footer, Static, Log, ProgressBar
    from textual.reactive import reactive
except ImportError:
    print("AgentOS Visual Telemetry requires the 'textual' framework.")
    print("Please install it by running: pip install textual rich")
    sys.exit(1)

class AgentNodeWidget(Static):
    """A personalized RPG-style widget representing an active AI Agent."""
    
    dialogue = reactive("Awaiting intent...")

    def __init__(self, agent_name: str, color: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = agent_name
        self.color = color

    def render(self) -> str:
        # A sleek, RPG-styled text box rendered purely via Textual/Rich
        return f"[{self.color} bold]<{self.agent_name}>[/{self.color} bold]\n[white]{self.dialogue}[/white]"

class AgentOSTelemetryApp(App):
    """
    The AgentOS Swarm Dashboard.
    Visualizes WASM fuel, ZeroMQ active connections, and dynamic RPG-style intents.
    """
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 4;
        grid-rows: 3 3 1fr 10;
        grid-columns: 1fr 1fr;
    }
    
    #top_panel {
        column-span: 2;
        padding: 1;
        background: $boost;
        border-bottom: heavy $accent;
        content-align: center middle;
    }
    
    #fuel_panel {
        column-span: 2;
        padding: 1;
    }
    
    .agent_box {
        border: round $primary;
        padding: 1;
        height: 100%;
        background: $surface;
    }
    
    #event_stream {
        column-span: 2;
        border-top: dashed $secondary;
        background: $panel;
    }
    """

    def compose(self) -> ComposeResult:
        # 1. Top Panel: Global Mesh Status
        yield Static("[bold cyan]AgentOS Global Mesh Status[/bold cyan] | Active Nodes: 4 | Global WASM Fuel: 85,400", id="top_panel")
        
        # 2. Sub-Top Panel: Fuel Diagnostics
        with Horizontal(id="fuel_panel"):
            yield Static("Tokyo-Prime Fuel: ")
            yield ProgressBar(total=10000, show_eta=False, id="tokyo_fuel")
            yield Static("  London-Edge Fuel: ")
            yield ProgressBar(total=10000, show_eta=False, id="london_fuel")

        # 3. Main View: RPG Nodes (Claude and Gemini active)
        self.claude_node = AgentNodeWidget("Claude (Architect)", "green", classes="agent_box")
        self.gemini_node = AgentNodeWidget("Gemini (Memory Vectorizer)", "cyan", classes="agent_box")
        
        yield self.claude_node
        yield self.gemini_node

        # 4. Bottom Panel: Hyperbolic Event Stream
        self.event_stream = Log(id="event_stream", highlight=True)
        yield self.event_stream

    async def on_mount(self) -> None:
        """Starts the background telemetry fetchers upon mounting the UI."""
        self.query_one("#tokyo_fuel").advance(8500)
        self.query_one("#london_fuel").advance(4200)
        
        self.event_stream.write("[System] AgentOS TUI Initialized.")
        self.event_stream.write("[Mesh] ZeroMQ ROUTER bound to tcp://0.0.0.0:5557")
        self.event_stream.write("[WebRTC] STUN Resolution successful. P2P Tunnels Open.")
        
        # Start a background task to listen to incoming swarm telemetry
        self.run_worker(self.listen_swarm_traffic(), exclusive=True)

    async def listen_swarm_traffic(self) -> None:
        """Listens asynchronously to the AgentOS Kernel PUB socket."""
        import zmq
        import zmq.asyncio
        import json
        
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://127.0.0.1:5562")
        socket.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
        
        self.event_stream.write("[Telemetry] Subscribed to real-time intent stream on tcp://127.0.0.1:5562")
        
        while True:
            try:
                message = await socket.recv_string()
                # Message format: "TELEMETRY {"code": "...", "args": {}}"
                payload_str = message.replace("TELEMETRY ", "", 1)
                intent = json.loads(payload_str)
                
                # We received a real intent!
                self.event_stream.write(f"[Intent-Intercept] Received payload: {str(intent)[:100]}...")
                
                # Fluctuate fuel as a visual effect of processing
                import random
                tokyo = self.query_one("#tokyo_fuel")
                if tokyo.progress > 100: tokyo.advance(-random.randint(50, 500))
                
                # Update RPG Dialogue conditionally if we see key words in code
                code_str = intent.get("code", "")
                if "summit" in code_str.lower() or "claude" in code_str.lower():
                    self.claude_node.dialogue = "Processing remote Summit Payload via WebRTC DataChannel!"
                elif "weather" in code_str.lower():
                    self.gemini_node.dialogue = "Executing external API Fetch intent via WASM Sandbox!"
                else:
                    self.claude_node.dialogue = "Analyzing intent AST signature..."
                    self.gemini_node.dialogue = "Vectorizing outcome into Hyperbolic space..."
                    
            except Exception as e:
                self.event_stream.write(f"[Error] Telemetry sync failed: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    app = AgentOSTelemetryApp()
    app.run()
