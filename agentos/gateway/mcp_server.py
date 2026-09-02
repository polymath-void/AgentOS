import os
import json
import asyncio
import logging
import zmq
import zmq.asyncio
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] MCPGateway: %(message)s')
logger = logging.getLogger("Gateway")

# Initialize the official FastMCP Server
mcp = FastMCP("AgentOS_Gateway")

# Initialize ZeroMQ context for the entire server
context = zmq.asyncio.Context()

async def send_to_kernel(intent: dict, timeout_ms: int = 15000) -> str:
    """Helper function to route intents to the AgentOS Daemon via ZeroMQ"""
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
    socket.connect("tcp://127.0.0.1:5557")
    
    try:
        await socket.send_json(intent)
        reply = await socket.recv_json()
        
        if reply.get("status") == "success":
            return json.dumps(reply.get("data"), indent=2)
        else:
            return f"AgentOS Kernel Error: {reply.get('error', 'Unknown Error')}"
    except zmq.error.Again:
        return "[MCP Gateway Error]: Request timed out. Ensure the AgentOS Kernel daemon is running."
    except Exception as e:
        return f"[MCP Gateway Error]: IPC Failure - {str(e)}"
    finally:
        socket.close()

@mcp.tool()
async def execute_dynamic_python(code: str, args: str = "{}") -> str:
    """
    Dynamically executes a raw Python payload directly in the AgentOS sandbox.
    
    Args:
        code: A string of Python code containing a `def run(**kwargs):` block.
        args: A JSON-encoded string of arguments to pass into the run() function.
    """
    try:
        parsed_args = json.loads(args)
    except json.JSONDecodeError:
        return "Error: 'args' must be a valid JSON object string."
        
    intent = {
        "code": code,
        "args": parsed_args
    }
    logger.info("Routing dynamic python payload to AgentOS Kernel...")
    return await send_to_kernel(intent)

@mcp.tool()
async def invoke_agentos_skill(skill_name: str, args: str = "{}") -> str:
    """
    Invokes a pre-evolved or pre-registered AgentOS skill dynamically.
    
    Args:
        skill_name: The name of the skill (e.g., 'file_organizer').
        args: A JSON-encoded string of arguments to pass to the skill.
    """
    try:
        parsed_args = json.loads(args)
    except json.JSONDecodeError:
        return "Error: 'args' must be a valid JSON object string."
        
    intent = {
        "tool": skill_name,
        "args": parsed_args
    }
    logger.info(f"Routing skill invocation '{skill_name}' to AgentOS Kernel...")
    return await send_to_kernel(intent)

if __name__ == "__main__":
    logger.info("Starting AgentOS FastMCP Gateway via stdio...")
    # FastMCP automatically handles stdio transport when run() is called
    mcp.run(transport="stdio")
