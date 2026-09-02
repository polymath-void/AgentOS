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
            "Claude": Agent("Claude", "🤖", "red", 12, 10),
            "Gemini": Agent("Gemini", "🦉", "blue", 65, 14)
        }
        self.mock_agents = [
            Agent("QA Bot", "⚙️", "green", 15, 4),
            Agent("Deploy Bot", "⚙️", "yellow", 65, 5),
            Agent("Sec Bot", "⚙️", "magenta", 40, 17)
        ]
        self.collab_lines = []
        self.set_interval(0.1, self.tick)
        
    def tick(self) -> None:
        changed = False
        for agent in self.agents.values():
            if agent.move():
                changed = True
                
        for mock in self.mock_agents:
            if random.random() > 0.9:
                mock.target_x = max(1, min(78, mock.x + random.randint(-10, 10)))
                mock.target_y = max(1, min(18, mock.y + random.randint(-5, 5)))
            if mock.move():
                changed = True
                
        if changed:
            self.refresh(layout=True)

    def render(self) -> str:
        width = 80
        height = 20
        
        # Base dotted floor
        grid = [['[bright_black]·[/]' for _ in range(width)] for _ in range(height)]
        
        # Draw Boundary
        for x in range(width):
            grid[0][x] = '[blue]═[/]'
            grid[height-1][x] = '[blue]═[/]'
        for y in range(height):
            grid[y][0] = '[blue]║[/]'
            grid[y][width-1] = '[blue]║[/]'
        grid[0][0] = '[blue]╔[/]'
        grid[0][width-1] = '[blue]╗[/]'
        grid[height-1][0] = '[blue]╚[/]'
        grid[height-1][width-1] = '[blue]╝[/]'
        
        # Draw Server Racks (Top Left)
        for y in range(2, 6):
            for x in range(4, 12):
                grid[y][x] = '[cyan]█[/]' if random.random() > 0.2 else '[white]█[/]'
            for x in range(16, 24):
                grid[y][x] = '[cyan]█[/]' if random.random() > 0.2 else '[white]█[/]'

        # Draw Lounge (Top Right)
        self._draw_box(grid, 55, 2, 75, 6, "[yellow]Lounge Area[/]", "yellow")
        if grid[4][60] == '[bright_black]·[/]': grid[4][60] = '🛋'
        if grid[4][61] == '[bright_black]·[/]': grid[4][61] = '️'
        if grid[4][70] == '[bright_black]·[/]': grid[4][70] = '☕'
        
        # Draw Claude Desk (Left Middle)
        self._draw_box(grid, 5, 8, 25, 13, "[red]Architect Desk[/]", "red")
        grid[10][10] = '💻'
        grid[10][11] = ' '
        grid[10][20] = '🪴'
        grid[10][21] = ' '
        
        # Draw Gemini Desk (Right Bottom)
        self._draw_box(grid, 55, 12, 75, 17, "[blue]Vector Memory[/]", "blue")
        grid[14][60] = '💻'
        grid[14][61] = ' '
        grid[14][70] = '🪴'
        grid[14][71] = ' '
        
        # Draw Central Meeting Pod
        cx, cy = 40, 12
        pod_w, pod_h = 24, 8
        self._draw_box(grid, cx - pod_w//2, cy - pod_h//2, cx + pod_w//2, cy + pod_h//2, "[magenta]Collab Pod[/]", "magenta")
        # Holo-table inside pod
        for x in range(cx - 4, cx + 5):
            grid[cy][x] = '[bold cyan]═[/]'
        grid[cy][cx] = '🌀'
        grid[cy][cx+1] = ' '

        # Draw Collaboration Line
        if self.collab_lines:
            c1, c2 = self.agents["Claude"], self.agents["Gemini"]
            for x in range(min(c1.x, c2.x) + 2, max(c1.x, c2.x)):
                if 0 < x < width and 0 < c1.y < height:
                    if grid[c1.y][x] == '[bright_black]·[/]':
                        grid[c1.y][x] = '[green]┈[/]'

        # Overlay Agents
        for mock in self.mock_agents:
            if 0 < mock.x < width - 2 and 0 < mock.y < height - 1:
                grid[mock.y][mock.x] = mock.get_avatar()
                grid[mock.y][mock.x+1] = ''

        for agent in self.agents.values():
            ax, ay = agent.x, agent.y
            if 0 < ax < width - 2 and 0 < ay < height - 1:
                # Add background color to highlight main agents
                bg_color = "on grey15"
                symbol = agent.symbol
                emoji = {"idle": "💤", "working": "⠷", "speaking": "💬", "tool": "🛠️"}.get(agent.status, "💤")
                grid[ay][ax] = f"[{agent.color} {bg_color}] {symbol} [/]{emoji}"
                grid[ay][ax+1] = '' 

        lines = ["".join(filter(None, row)) for row in grid]
        return "\n".join(lines)
        
    def _draw_box(self, grid, x1, y1, x2, y2, title, color="white"):
        if not (0 <= x1 < x2 < len(grid[0]) and 0 <= y1 < y2 < len(grid)): return
        for x in range(x1, x2 + 1):
            grid[y1][x] = f'[{color}]─[/]'
            grid[y2][x] = f'[{color}]─[/]'
        for y in range(y1, y2 + 1):
            grid[y][x1] = f'[{color}]│[/]'
            grid[y][x2] = f'[{color}]│[/]'
        grid[y1][x1] = f'[{color}]╭[/]'
        grid[y1][x2] = f'[{color}]╮[/]'
        grid[y2][x1] = f'[{color}]╰[/]'
        grid[y2][x2] = f'[{color}]╯[/]'
        t_str = f" {title} "
        if x1 + 2 + 18 < x2:
            grid[y1][x1+2] = t_str
            for i in range(x1+3, x1+3+15):
                grid[y1][i] = ''

class DashboardApp(App):
    CSS = """
    Screen { background: $surface; }
    #header { height: 3; content-align: center middle; background: $boost; border-bottom: heavy $accent; }
    .map_container { height: 22; padding: 1; align: center middle; }
    .bottom_panel { height: 12; border-top: solid $primary; padding: 1; }
    .fuel_box { width: 30%; }
    .dialogue_box { width: 40%; border-left: solid $secondary; padding-left: 2; }
    #telemetry_log { width: 30%; border-left: solid $secondary; }
    #event_stream { height: 1fr; border: solid $secondary; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]AgentOS OpenClaw Frontend[/bold cyan] | Digital Twin Office", id="header")
        
        with TabbedContent():
            with TabPane("🏢 Virtual Office"):
                with Vertical():
                    self.office_map = OfficeMap(classes="map_container")
                    yield self.office_map
                    
                    with Horizontal(classes="bottom_panel"):
                        with Vertical(classes="fuel_box"):
                            yield Static("📊 [bold]Agent Telemetry[/bold]")
                            yield Label("Tokyo-Prime Fuel:")
                            yield ProgressBar(total=1000, id="fuel_tokyo", show_eta=False)
                        with Vertical(classes="dialogue_box"):
                            yield Static("💬 [bold]Live Agent Dialogues[/bold]\n")
                            self.dialogue_label = Label("[red]Claude[/]: Awaiting...\n[blue]Gemini[/]: Awaiting...", id="agent_dialogues")
                            yield self.dialogue_label
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
                    
                    code = payload.get("code", "").lower()
                    if "summit" in code or "claude" in code:
                        c.target_x, c.target_y = 35, 12
                        c.status = "working"
                        c.dialogue = "Processing Summit Payload!"
                        g.target_x, g.target_y = 45, 12
                        g.status = "speaking"
                        g.dialogue = "Joining swarm pod."
                        self.office_map.collab_lines = [True]
                    else:
                        c.target_x, c.target_y = 12, 10
                        c.status = "idle"
                        c.dialogue = "Awaiting intent..."
                        g.target_x, g.target_y = 65, 14
                        g.status = "tool"
                        g.dialogue = "Vectorizing..."
                        self.office_map.collab_lines = []
                        
                    self.dialogue_label.update(f"[red]Claude[/]: {c.dialogue}\n[blue]Gemini[/]: {g.dialogue}")
                else:
                    if random.random() > 0.8:
                        c = self.office_map.agents["Claude"]
                        g = self.office_map.agents["Gemini"]
                        c.target_x, c.target_y = 12, 10
                        g.target_x, g.target_y = 65, 14
                        c.status, g.status = "idle", "idle"
                        c.dialogue, g.dialogue = "Awaiting...", "Awaiting..."
                        self.office_map.collab_lines = []
                        self.dialogue_label.update(f"[red]Claude[/]: {c.dialogue}\n[blue]Gemini[/]: {g.dialogue}")
                        
            except Exception as e:
                self.event_stream.write(f"Error: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
