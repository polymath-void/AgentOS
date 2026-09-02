import asyncio
import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from core.dispatch.dispatch_network import DispatchNetwork
from plugins.tools_manager import ToolsManager

# Initialize the MCP Server
app = Server("agent-os-hub")

# Initialize AgentOS Engine Core
tools_dir = str(Path(__file__).parent / "plugins")
tools_manager = ToolsManager(tools_dir)
dispatch = DispatchNetwork(tools_manager)

# Load schemas dynamically
schemas = tools_manager.load_dynamic_schemas()

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Dynamically registers all AgentOS plugins as standard MCP tools."""
    mcp_tools = []
    for schema in schemas:
        mcp_tools.append(
            types.Tool(
                name=schema["name"],
                description=schema.get("description", f"Executes the {schema['name']} OS capability."),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "payload": {
                            "type": "string",
                            "description": "JSON string of arguments to pass to the script."
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["execute", "simulate"],
                            "description": "Execution mode (default: execute). Use 'simulate' to test safety."
                        }
                    }
                }
            )
        )
    return mcp_tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Routes the MCP tool call into the AgentOS DispatchNetwork."""
    # Ensure the tool exists in our loaded schemas
    if not any(s["name"] == name for s in schemas):
        raise ValueError(f"Unknown AgentOS tool: {name}")

    payload = arguments.get("payload", "{}")
    mode = arguments.get("mode", "execute")

    # The payload might be passed as a dict instead of string if the LLM auto-parses,
    # so we ensure it's a string for the bash script.
    if isinstance(payload, dict):
        payload = json.dumps(payload)

    # Route through the OS hub
    print(f"Routing MCP tool '{name}' to DispatchNetwork in '{mode}' mode...")
    task = {
        "name": name,
        "args": payload,
        "mode": mode
    }
    
    # Run the underlying agent-os-hub logic
    try:
        result = dispatch.route_task("execute", task)
        return [types.TextContent(type="text", text=str(result) if result else "Execution completed without output.")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"OS Execution Error: {str(e)}")]

async def main():
    print("Initializing Standard MCP Interface for AgentOS Hub...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
