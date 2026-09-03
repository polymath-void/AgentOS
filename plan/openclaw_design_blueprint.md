# OpenClaw Office Paradigm for ComputeRes

## 1. Core Metaphor Integration
To make the multi-agent system feel more tangible, ComputeRes will adopt the OpenClaw visual metaphor, translating it to our Textual/Rich TUI environment:

*   **Agent** = **Digital Employee**: Each running LLM agent is an entity with a state and persona.
*   **Office** = **Agent Runtime**: The terminal UI screen is the physical office space where all employees reside.
*   **Desk** = **Session Context**: The dedicated memory and working space for a single agent.
*   **Meeting Pod** = **Collaboration Context**: A shared context where multiple agents participate in a sub-task or swarm discussion.

## 2. Virtual Office Implementation (Textual/Rich TUI)

The central component will be the `OfficeMap` widget, a 2D canvas (using `textual.widgets.DataTable` or a custom Grid widget) that visually represents the virtual office.

### 2D Floor Plan Elements

*   **Agent Avatars with Status**:
    *   Agents will be represented by Emoji or Unicode characters (e.g., `🤖`, `🦉`, `💻`).
    *   **Animations/Status**: By updating the character at an interval, we can simulate animations.
        *   *Idle*: Agent sits at their desk (e.g., `[ 💤 ]`).
        *   *Working*: Spinning braille loading indicator (e.g., `[ ⠷ ]`).
        *   *Speaking*: Speech bubble indicator (e.g., `[ 💬 ]`).
        *   *Tool Calling*: Hammer/Wrench (e.g., `[ 🛠️ ]`).
*   **Meeting Pods**:
    *   Visualized as bounded areas on the map using `rich.box` drawing characters (e.g., `╭──────╮`).
    *   When an agent enters a swarm conversation, their avatar dynamically moves from their Desk to the Meeting Pod area on the map.
*   **Collaboration Lines**:
    *   When `send_message` is invoked, temporary ASCII/Unicode lines (e.g., `┈`, `┊`, `⤡`) are drawn connecting the sender and receiver's grid coordinates, acting as visual tracers for message routing.

### Extruded UI Elements

*   **Speech Bubbles**: 
    *   When an agent speaks (outputs text), a Textual `Tooltip` or an absolutely positioned `Panel` will appear adjacent to their avatar.
    *   The content will be parsed via `rich.markdown.Markdown` for live markdown rendering.
*   **Side Panels**:
    *   The UI will feature a sidebar containing `Token/Activity charts`.
    *   Using sparklines or `textual-plotext`, we can graph LLM API latency, token consumption rates, and task completion metrics in real-time.

## 3. Skill Workbench

The Skill Workbench will be a dedicated Textual `Screen` for developing and inspecting agent tools.

*   **Skill Editor**: A `TextArea` widget with syntax highlighting (YAML/Python) for editing `.md` skill configurations and python scripts.
*   **Mermaid Flowcharts**: By parsing the skill workflow, ComputeRes can generate Mermaid markdown. This will be rendered in the terminal using a terminal image viewer integration (like `chafa` or `timg`) or converted to an ASCII-art flowchart (via tools like `graph-easy`).
*   **Visual Input Forms**: Using Textual `Input`, `Select`, and `Checkbox` widgets to allow users to interactively test a skill before deploying it to an agent.
