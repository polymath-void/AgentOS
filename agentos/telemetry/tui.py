import asyncio
import sys
import random
import json

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Static, Log, ProgressBar, TabbedContent, TabPane, TextArea, Label, DataTable
    from textual.reactive import reactive
except ImportError:
    print("AgentOS Visual Telemetry requires the 'textual' framework.")
    print("Please install it by running: pip install textual rich")
    sys.exit(1)

class Agent:
    def __init__(self, name: str, symbol: str, color: str, x: int, y: int):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.status = "idle"  # idle, working, speaking, tool
        self.dialogue = ""

    def get_avatar(self) -> str:
        emojis = {"idle": "💤", "working": "⠷", "speaking": "💬", "tool": "🛠️"}
        return f"[bold {self.color}]{self.symbol}[/]{emojis.get(self.status, '💤')}"

    def move(self) -> bool:
        if self.x < self.target_x:
            self.x += 1
            return True
        elif self.x > self.target_x:
            self.x -= 1
            return True
        elif self.y < self.target_y:
            self.y += 1
            return True
        elif self.y > self.target_y:
            self.y -= 1
            return True
        return False

class OfficeMap(Static):
    """The OpenClaw Virtual Office Floor Plan."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agents = {
            "Claude": Agent("Claude", "🤖", "red", 6, 3),
            "Gemini": Agent("Gemini", "🦉", "blue", 45, 3)
        }
        self.collab_lines = []
        self.set_interval(0.1, self.tick)
        
    def tick(self) -> None:
        changed = False
        for agent in self.agents.values():
            if agent.move():
                changed = True
        if changed:
            self.refresh(layout=True)

    def render(self) -> str:
        width = max(30, self.size.width)
        height = max(10, self.size.height) - 4
        
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw Boundary
        for x in range(width):
            grid[0][x] = '─'
            grid[height-1][x] = '─'
        for y in range(height):
            grid[y][0] = '│'
            grid[y][width-1] = '│'
        grid[0][0] = '╭'
        grid[0][width-1] = '╮'
        grid[height-1][0] = '╰'
        grid[height-1][width-1] = '╯'
        
        # Draw Claude Desk
        self._draw_box(grid, 2, 2, 10, 4, "[bright_black]Claude Desk[/]")
        
        # Draw Gemini Desk
        g_desk_x = width - 12
        if g_desk_x > 12:
            self._draw_box(grid, g_desk_x, 2, width - 4, 4, "[bright_black]Gemini Desk[/]")
        
        # Draw Meeting Pod
        pod_w = 20
        pod_h = 6
        cx = width // 2
        cy = height // 2
        if cx - pod_w//2 > 0 and cy - pod_h//2 > 0:
            self._draw_box(grid, cx - pod_w//2, cy - pod_h//2, cx + pod_w//2, cy + pod_h//2, "[magenta]Meeting Pod[/]")

        # Draw Collaboration Line
        if self.collab_lines:
            c1, c2 = self.agents["Claude"], self.agents["Gemini"]
            # simple straight line between them roughly
            for x in range(min(c1.x, c2.x) + 2, max(c1.x, c2.x)):
                if 0 < x < width and 0 < c1.y < height:
                    if grid[c1.y][x] == ' ':
                        grid[c1.y][x] = '[green]┈[/]'

        # Overlay Agents & Dialogues
        dialogues = []
        for agent in self.agents.values():
            ax, ay = agent.x, agent.y
            if 0 < ax < width - 2 and 0 < ay < height - 1:
                grid[ay][ax] = agent.get_avatar()
                grid[ay][ax+1] = '' # Emoji width comp
            if agent.dialogue:
                dialogues.append(f"[{agent.color}]{agent.name}[/]: {agent.dialogue}")

        # Render
        lines = ["".join(filter(None, row)) for row in grid]
        out = "\n".join(lines)
        if dialogues:
            out += "\n\n" + "\n".join(dialogues[-2:])
        return out
        
    def _draw_box(self, grid, x1, y1, x2, y2, title):
        if not (0 <= x1 < x2 < len(grid[0]) and 0 <= y1 < y2 < len(grid)): return
        for x in range(x1, x2 + 1):
            grid[y1][x] = '─'
            grid[y2][x] = '─'
        for y in range(y1, y2 + 1):
            grid[y][x1] = '│'
            grid[y][x2] = '│'
        grid[y1][x1] = '╭'
        grid[y1][x2] = '╮'
        grid[y2][x1] = '╰'
        grid[y2][x2] = '╯'
        # title
        t_str = f" {title} "
        if x1 + 2 + 15 < x2:
            grid[y1][x1+2] = t_str
            for i in range(x1+3, x1+3+12):
                grid[y1][i] = ''

class DashboardApp(App):
    CSS = """
    Screen { background: $surface; }
    #header { height: 3; content-align: center middle; background: $boost; border-bottom: heavy $accent; }
    .side_panel { width: 35%; border-left: solid $primary; padding: 1; }
    .map_container { width: 65%; padding: 1; }
    #event_stream { height: 1fr; border: solid $secondary; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]AgentOS OpenClaw Frontend[/bold cyan] | Digital Twin Office", id="header")
        
        with TabbedContent():
            with TabPane("🏢 Virtual Office"):
                with Horizontal():
                    with Vertical(classes="map_container"):
                        self.office_map = OfficeMap()
                        yield self.office_map
                    with Vertical(classes="side_panel"):
                        yield Static("📊 [bold]Agent Telemetry[/bold]\n")
                        yield Label("Tokyo-Prime Fuel:")
                        yield ProgressBar(total=1000, id="fuel_tokyo", show_eta=False)
                        yield Label("\nLondon-Edge Fuel:")
                        yield ProgressBar(total=1000, id="fuel_london", show_eta=False)
                        self.telemetry_log = Log(id="telemetry_log")
                        yield self.telemetry_log
                        
            with TabPane("💻 Skill Workbench"):
                with Horizontal():
                    self.skill_editor = TextArea(
                        "name: example_skill\ntype: workflow\n---\ndef run():\n    return 'Hello World'", 
                        language="python"
                    )
                    yield self.skill_editor
                    yield Log(id="mermaid_preview")
                    
            with TabPane("⚙️ Console"):
                self.event_stream = Log(id="event_stream", highlight=True)
                yield self.event_stream

    async def on_mount(self) -> None:
        self.query_one("#fuel_tokyo", ProgressBar).advance(800)
        self.query_one("#fuel_london", ProgressBar).advance(700)
        self.query_one("#mermaid_preview", Log).write("graph TD;\n    A-->B;\n    A-->C;\n    B-->D;\n    C-->D;")
        self.event_stream.write("[System] OpenClaw Dashboard Online.")
        self.run_worker(self.listen_swarm_traffic(), exclusive=True)

    async def listen_swarm_traffic(self) -> None:
        import zmq
        import zmq.asyncio
        
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://127.0.0.1:5562")
        socket.setsockopt_string(zmq.SUBSCRIBE, "TELEMETRY")
        
        self.event_stream.write("[Telemetry] Subscribed to 5562")
        self.telemetry_log.write("Awaiting ZeroMQ Swarm Intents...\n")
        
        tokyo_bar = self.query_one("#fuel_tokyo", ProgressBar)
        
        while True:
            try:
                events = await socket.poll(timeout=1000)
                if events:
                    msg = await socket.recv_string()
                    payload = json.loads(msg.replace("TELEMETRY ", "", 1))
                    
                    self.event_stream.write(f"Intercept: {str(payload)[:80]}")
                    self.telemetry_log.write(f"> {payload.get('code', 'unknown')[:30]}")
                    
                    if tokyo_bar.progress > 50: tokyo_bar.advance(-50)
                    else: tokyo_bar.progress = 1000
                    
                    c = self.office_map.agents["Claude"]
                    g = self.office_map.agents["Gemini"]
                    
                    cx = self.office_map.size.width // 2
                    cy = max(3, self.office_map.size.height // 2)
                    
                    code = payload.get("code", "").lower()
                    if "summit" in code or "claude" in code:
                        c.target_x, c.target_y = cx - 5, cy
                        c.status = "working"
                        c.dialogue = "Processing Summit Payload!"
                        g.target_x, g.target_y = cx + 5, cy
                        g.status = "speaking"
                        g.dialogue = "Joining swarm pod."
                        self.office_map.collab_lines = [True]
                    else:
                        c.target_x, c.target_y = 6, 3
                        c.status = "idle"
                        c.dialogue = ""
                        g.target_x, g.target_y = max(10, self.office_map.size.width - 8), 3
                        g.status = "tool"
                        g.dialogue = "Vectorizing..."
                        self.office_map.collab_lines = []
                        
                    self.office_map.refresh()
                else:
                    if random.random() > 0.8:
                        c = self.office_map.agents["Claude"]
                        g = self.office_map.agents["Gemini"]
                        c.target_x, c.target_y = 6, 3
                        g.target_x, g.target_y = max(10, self.office_map.size.width - 8), 3
                        c.status, g.status = "idle", "idle"
                        c.dialogue, g.dialogue = "Awaiting...", "Awaiting..."
                        self.office_map.collab_lines = []
                        self.office_map.refresh()
            except Exception as e:
                self.event_stream.write(f"Error: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
