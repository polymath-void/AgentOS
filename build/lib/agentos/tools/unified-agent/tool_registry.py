from __future__ import annotations

# Import or define all tools from previous agents here.
# For simplicity, we ensure all necessary tools are registered.

def get_tool_definitions() -> list[dict]:
    """
    Exhaustive list of tools available to the contextual agentic execution engine.
    """
    return [
        {
            "name": "run_shell_command",
            "description": "Executes a shell command. Use require_root=true for Android system settings, hardware, or /system paths.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The bash command to run."},
                    "timeout": {"type": "integer", "description": "Timeout in seconds.", "default": 30},
                    "require_root": {"type": "boolean", "description": "Execute via su with root privileges.", "default": False}
                },
                "required": ["command"]
            }
        },
        {
            "name": "read_file",
            "description": "Read file content up to max_bytes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or home-relative file path."},
                    "max_bytes": {"type": "integer", "description": "Maximum bytes to read.", "default": 8192}
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write or append text content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Target file path."},
                    "content": {"type": "string", "description": "Text content to write."},
                    "append": {"type": "boolean", "description": "Append instead of overwrite.", "default": False}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "get_clipboard",
            "description": "Get current text content from the system clipboard.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "set_clipboard",
            "description": "Set the system clipboard text content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to copy to clipboard."}
                },
                "required": ["content"]
            }
        },
        {
            "name": "create_agent_card",
            "description": "Create and persist a new specialised AgentCard configuration in SQLite.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Agent name."},
                    "system_prompt": {"type": "string", "description": "Specialised system prompt for the domain."},
                    "description": {"type": "string", "description": "Short description.", "default": ""},
                    "tools": {"type": "array", "items": {"type": "string"}, "description": "Allowed tools list. Empty = all.", "default": []}
                },
                "required": ["name", "system_prompt"]
            }
        },
        {
            "name": "list_agent_cards",
            "description": "List all saved AgentCards.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "delete_agent_card",
            "description": "Delete an AgentCard by its UUID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "card_id": {"type": "string", "description": "UUID of the card to delete."}
                },
                "required": ["card_id"]
            }
        },
        {
            "name": "http_get",
            "description": "Perform an HTTP GET request to a URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch."},
                    "headers": {"type": "object", "description": "Optional HTTP headers.", "default": {}},
                    "timeout": {"type": "integer", "description": "Timeout in seconds.", "default": 15}
                },
                "required": ["url"]
            }
        }
    ]


def filter_tools_for_card(allowed: list[str]) -> list[dict]:
    all_tools = get_tool_definitions()
    if not allowed:
        return all_tools
    allowed_set = set(allowed)
    return [t for t in all_tools if t["name"] in allowed_set]

