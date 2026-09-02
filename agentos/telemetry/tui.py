import asyncio
import sys
import json
import random

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Static, Log, ProgressBar, TabbedContent, TabPane, Label
    from textual.reactive import reactive
except ImportError:
    print("AgentOS Visual Telemetry requires the 'textual' framework.")
    sys.exit(1)

class AgentAvatar(Static):
    """An absolutely positioned agent avatar that smoothly animates across the screen."""
    
    status = reactive("idle")
    
    def __init__(self, name: str, icon: str, color: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = name
        self.icon = icon
        self.agent_color = color

    def render(self) -> str:
        emojis = {"idle": "💤", "working": "⠷", "speaking": "💬", "tool": "🛠️"}
        return f"[{self.agent_color} on grey15] {self.icon} [/]{emojis.get(self.status, '💤')}"

    def move_to(self, target_x_pct: float, target_y_pct: float):
        """Move using smooth layout offsets (percentage of parent)."""
        parent_width = self.parent.size.width if self.parent else 80
        parent_height = self.parent.size.height if self.parent else 20
        
        target_x = int(parent_width * target_x_pct)
        target_y = int(parent_height * target_y_pct)
        
        # Smoothly animate the textual widget offset
        self.animate("offset", (target_x, target_y), duration=1.5, easing="in_out_cubic")

class Desk(Static):
    pass

class MeetingPod(Static):
    pass

class VirtualOffice(Container):
    """The central environment utilizing the Golden Ratio (1:1.618) for spatial division."""
    
    def compose(self) -> ComposeResult:
        yield Desk("💻 Architect Desk", id="desk_claude", classes="office_prop")
        yield Desk("💻 Vector Memory", id="desk_gemini", classes="office_prop")
        yield MeetingPod("🌀 Holographic Collab Pod", id="collab_pod", classes="office_prop")
        
        # The main agents
        self.claude = AgentAvatar("Claude", "🤖", "red", id="agent_claude")
        self.gemini = AgentAvatar("Gemini", "🦉", "blue", id="agent_gemini")
        yield self.claude
        yield self.gemini

        # Mock Agents for ambient busyness
        self.mocks = [
            AgentAvatar("QA", "⚙️", "green", id="mock_1", classes="mock_agent"),
            AgentAvatar("Sec", "⚙️", "yellow", id="mock_2", classes="mock_agent"),
            AgentAvatar("Deploy", "⚙️", "magenta", id="mock_3", classes="mock_agent"),
        ]
        for m in self.mocks:
            yield m

    def on_mount(self) -> None:
        # Initial positions
        self.claude.styles.offset = (5, 5)
        self.gemini.styles.offset = (50, 15)
        for m in self.mocks:
            m.styles.offset = (random.randint(10, 60), random.randint(2, 18))
            
        self.set_interval(2.0, self.wander_mocks)
        
    def wander_mocks(self) -> None:
        for m in self.mocks:
            if random.random() > 0.5:
                # Randomly animate mock agents
                target_x = random.uniform(0.1, 0.9)
                target_y = random.uniform(0.1, 0.9)
                m.move_to(target_x, target_y)

class DashboardApp(App):
    CSS = """
    Screen { background: $surface; }
    #header { height: 3; content-align: center middle; background: $boost; border-bottom: heavy $accent; }
    
    VirtualOffice {
        height: 1fr;
        width: 1fr;
        background: #0D1117; /* GitHub Dark theme background */
        border: solid $secondary;
    }
    
    .office_prop {
        position: absolute;
        content-align: center middle;
        border: round $primary;
        background: $panel;
        opacity: 0.8;
    }
    
    #desk_claude {
        offset: 5% 15%;
        width: 25%;
        height: 25%;
        border: round red;
    }
    
    #desk_gemini {
        offset: 70% 60%;
        width: 25%;
        height: 25%;
        border: round blue;
    }
    
    #collab_pod {
        /* Golden ratio placement */
        offset: 38% 30%;
        width: 24%;  
        height: 40%;
        border: double magenta;
        background: #2E1A33;
    }

    AgentAvatar {
        position: absolute;
        width: 6;
        height: 1;
        content-align: center middle;
    }
    
    .mock_agent {
        opacity: 0.5;
    }

    .bottom_panel { 
        height: 12; 
        border-top: solid $primary; 
        background: $panel;
    }
    
    .telemetry_box { width: 35%; padding: 1; }
    .dialogue_box { width: 65%; border-left: solid $secondary; padding: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]AgentOS Native Frontend[/bold cyan] | 2D Spatial UI Architecture", id="header")
        
        with Vertical():
            self.office = VirtualOffice()
            yield self.office
            
            with Horizontal(classes="bottom_panel"):
                with Vertical(classes="telemetry_box"):
                    yield Static("📊 [bold]System Telemetry[/bold]")
                    yield Label("WASM Sandbox Prime:")
                    yield ProgressBar(total=1000, id="fuel_tokyo", show_eta=False)
                    yield Label("Edge Node Replica:")
                    yield ProgressBar(total=1000, id="fuel_london", show_eta=False)
                    self.event_stream = Log(id="event_stream", highlight=True, classes="small_log")
                    yield self.event_stream
                    
                with Vertical(classes="dialogue_box"):
                    yield Static("💬 [bold]Live Intent Stream[/bold]")
                    self.dialogue_label = Label("[grey50]Awaiting neural intercept...[/]", id="agent_dialogues")
                    yield self.dialogue_label

    async def on_mount(self) -> None:
        self.query_one("#fuel_tokyo", ProgressBar).advance(800)
        self.query_one("#fuel_london", ProgressBar).advance(700)
        self.event_stream.write("TUI Node initialized.")
        self.run_worker(self.listen_swarm_traffic(), exclusive=True)

    async def listen_swarm_traffic(self) -> None:
        import zmq
        import zmq.asyncio
        
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://127.0.0.1:5562")
        socket.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
        
        self.event_stream.write("Subscribed to ZMQ:5562")
        tokyo_bar = self.query_one("#fuel_tokyo", ProgressBar)
        
        c = self.office.claude
        g = self.office.gemini
        
        # Move them to desks initially
        c.move_to(0.1, 0.2)
        g.move_to(0.75, 0.65)
        
        while True:
            try:
                events = await socket.poll(timeout=1000)
                if events:
                    msg = await socket.recv_string()
                    payload = json.loads(msg.replace("TELEMETRY ", "", 1))
                    
                    code = payload.get("code", "").lower()
                    self.event_stream.write(f"INTENT: {code[:40]}")
                    
                    if tokyo_bar.progress > 50: tokyo_bar.advance(-50)
                    else: tokyo_bar.progress = 1000
                    
                    if "summit" in code or "claude" in code:
                        # Move to Collaboration Pod (Center)
                        c.status = "working"
                        c.move_to(0.40, 0.40) 
                        c_dialogue = "Processing Summit Payload in shared context."
                        
                        g.status = "speaking"
                        g.move_to(0.50, 0.40)
                        g_dialogue = "Joining swarm collaboration pod."
                    else:
                        # Return to Desks
                        c.status = "idle"
                        c.move_to(0.1, 0.2)
                        c_dialogue = "Analyzing AST signatures."
                        
                        g.status = "tool"
                        g.move_to(0.75, 0.65)
                        g_dialogue = "Vectorizing outcome via sandbox."
                        
                    self.dialogue_label.update(
                        f"[red]🤖 Claude (Architect)[/]: {c_dialogue}\n"
                        f"[blue]🦉 Gemini (Vector)[/]: {g_dialogue}"
                    )
                else:
                    if random.random() > 0.8:
                        c.status = "idle"
                        g.status = "idle"
                        c.move_to(0.1, 0.2)
                        g.move_to(0.75, 0.65)
                        self.dialogue_label.update(
                            f"[red]🤖 Claude[/]: [grey50]Awaiting intent...[/]\n"
                            f"[blue]🦉 Gemini[/]: [grey50]Awaiting intent...[/]"
                        )
                        
            except Exception as e:
                self.event_stream.write(f"Error: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
