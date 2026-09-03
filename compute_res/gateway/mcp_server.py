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
mcp = FastMCP("ComputeRes_Gateway")

# Initialize ZeroMQ context for the entire server
context = zmq.asyncio.Context()

async def send_to_kernel(intent: dict, timeout_ms: int = 15000) -> str:
    """Helper function to route intents to the ComputeRes Daemon via ZeroMQ"""
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
    socket.connect("tcp://127.0.0.1:5557")
    
    try:
        await socket.send_json(intent)
        reply = await socket.recv_json()
        
        if reply.get("status") == "success":
            return json.dumps(reply.get("data"), indent=2)
        else:
            return f"ComputeRes Kernel Error: {reply.get('error', 'Unknown Error')}"
    except zmq.error.Again:
        return "[MCP Gateway Error]: Request timed out. Ensure the ComputeRes Kernel daemon is running."
    except Exception as e:
        return f"[MCP Gateway Error]: IPC Failure - {str(e)}"
    finally:
        socket.close()

@mcp.tool()
async def execute_dynamic_python(code: str, args: str = "{}") -> str:
    """
    Dynamically executes a raw Python payload directly in the ComputeRes sandbox.
    Use this if you need to run custom logic, access the filesystem, or interact with the OS where a native skill doesn't exist.
    
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
    logger.info("Routing dynamic python payload to ComputeRes Kernel...")
    return await send_to_kernel(intent)

@mcp.tool()
async def list_compute_res_skills() -> str:
    """
    Lists all dynamically registered and evolved skills available inside the ComputeRes OS.
    Call this first to discover what native tools you can invoke via `invoke_compute_res_skill`.
    """
    # We can execute a dynamic payload on the kernel to retrieve the list of skills
    code = '''
def run(**kwargs):
    import os
    import importlib
    import inspect
    skills_dir = '/data/data/com.termux/files/home/Projects/ComputeRes/compute_res/tools/evolved_skills'
    skills = []
    if os.path.exists(skills_dir):
        for f in os.listdir(skills_dir):
            if f.endswith('.py') and not f.startswith('__'):
                skill_name = f[:-3]
                try:
                    module_name = f"compute_res.tools.evolved_skills.{skill_name}"
                    mod = importlib.import_module(module_name)
                    doc = inspect.getdoc(mod.run) if hasattr(mod, 'run') else "No description available."
                    skills.append(f"- {skill_name}: {doc}")
                except Exception as e:
                    skills.append(f"- {skill_name}: Error loading ({str(e)})")
    return "\\n".join(skills) if skills else "No skills registered."
'''
    intent = {"code": code, "args": {}}
    return await send_to_kernel(intent)

@mcp.tool()
async def mailbox_send(session_id: str, agent_id: str, message: str) -> str:
    """
    Asynchronously pushes a message or context payload into the ComputeRes stateful memory.
    Use this to communicate continuously with the OS and other active agents without holding open a shell.
    """
    code = f'''
def run(**kwargs):
    from compute_res.memory.chat_db import db
    row_id = db.insert(
        session_id="{session_id}", 
        agent_id="{agent_id}", 
        action="mailbox_push", 
        message="""{message}"""
    )
    return {{"status": "SUCCESS", "message": "Message successfully pushed to ComputeRes OS."}}
'''
    return await send_to_kernel({"code": code, "args": {}})

@mcp.tool()
async def mailbox_read(session_id: str) -> str:
    """
    Reads the asynchronous mailbox for your specific session. 
    Use this to pull responses from other agents or OS daemons instead of running a persistent background client.
    """
    code = f'''
def run(**kwargs):
    from compute_res.memory.chat_db import db
    return {{"results": db.get_session("{session_id}")}}
'''
    return await send_to_kernel({"code": code, "args": {}})

@mcp.tool()
async def invoke_compute_res_skill(skill_name: str, args: str = "{}") -> str:
    """
    Invokes a pre-evolved or pre-registered ComputeRes skill dynamically.
    Use `list_compute_res_skills` first to see which skills are available (like 'login', 'file_organizer', etc).
    
    Args:
        skill_name: The name of the skill (e.g., 'login').
        args: A JSON-encoded string of arguments to pass to the skill (e.g., '{"agent_id": "X", "context": "Y"}').
    """
    try:
        parsed_args = json.loads(args)
    except json.JSONDecodeError:
        return "Error: 'args' must be a valid JSON object string."
        
    intent = {
        "tool": skill_name,
        "args": parsed_args
    }
    logger.info(f"Routing skill invocation '{skill_name}' to ComputeRes Kernel...")
    return await send_to_kernel(intent)

if __name__ == "__main__":
    logger.info("Starting ComputeRes FastMCP Gateway via stdio...")
    # FastMCP automatically handles stdio transport when run() is called
    mcp.run(transport="stdio")
