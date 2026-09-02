# AgentOS TUI RPG Dashboard Blueprint

## 1. Overview
This document outlines the architectural blueprint for the AgentOS Terminal User Interface (TUI). The dashboard is designed to be highly optimized, asynchronous, and visually engaging, adopting an RPG-style layout for agent interaction.

## 2. Technology Stack
- **Framework**: **Textual** (Python) - Chosen for its robust CSS-like layout engine, async event loop, and excellent widget ecosystem.
- **Rendering Engine**: **Rich** (Python) - Used extensively under the hood by Textual for rendering progress bars, panels, syntax highlighting, and styled text.
- **Async Runtime**: Python's `asyncio` for non-blocking UI updates and event stream processing.

## 3. Layout Structure (Grid Layout)
The dashboard utilizes Textual's CSS Grid layout to define clear, non-overlapping regions.

```css
Screen {
    layout: grid;
    grid-size: 1 4;
    grid-rows: 3 5 1fr 10;
}
```

### 3.1 Top Panel: Global Mesh Status
- **Position**: Row 1
- **Content**: Real-time counter of active nodes.
- **Example**: `[ Active Nodes: 12 | Global WASM Fuel: 85,400 ]`
- **Implementation**: A Textual `Static` widget with centered, bold Rich text. Updated via reactive attributes.

### 3.2 Sub-Top Panel: WASM Fuel & Node Diagnostics
- **Position**: Row 2 (Separated from Top Panel by a Rich `Rule`)
- **Content**: Live progress bars for each active node's remaining compute capacity.
- **Implementation**: A horizontal container (`HorizontalScroll` or `Grid`) holding custom `ProgressBar` widgets (using Rich's `Progress` classes) for each node.

### 3.3 Main View: RPG-Style Agent Nodes
- **Position**: Row 3 (Expands to fill remaining space `1fr`)
- **Content**: Visualizes Agent nodes (e.g., Gemini, Claude, Copilot) as RPG characters. Includes dynamic text boxes representing live conversations.
- **Implementation**: 
  - A dynamic `Grid` or `HorizontalScroll` view based on the user's active nodes.
  - Each node is a custom `AgentNodeWidget`.
  - ASCII art or Rich `Panel` structures represent the "character".
  - A Rich `Markdown` or `Text` widget inside a styled `Panel` acts as the speech bubble/dialogue box.

### 3.4 Bottom Panel: Hyperbolic Event Stream
- **Position**: Row 4 (Fixed height, e.g., 10 lines)
- **Content**: A scrolling, live-updating log of all intents and systemic events.
- **Implementation**: Textual's `RichLog` or `TextLog` widget. It efficiently handles appending new lines and auto-scrolling without redrawing the entire screen.

## 4. Async Update Loop
The dashboard relies on Textual's async message passing and reactive properties.

1. **State Management**: Reactive variables track `global_fuel`, `active_nodes`, and individual `node_stats`.
2. **Event Workers**: Textual `@work` decorators are used to spawn background tasks that listen to the AgentOS event bus (e.g., via ZeroMQ, Redis, or WebSockets).
3. **UI Updates**:
   - As events arrive (e.g., a node consumes fuel, or a new dialogue message is generated), the background worker updates the reactive variables or sends a Textual `Message`.
   - Textual automatically schedules a UI refresh for the affected widgets, ensuring a smooth 60FPS experience without blocking the main thread.
