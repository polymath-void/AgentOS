import asyncio
import zmq
import zmq.asyncio

async def trigger_dynamic():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5557")
    
    print("MCP Client: Connecting to AgentOS Kernel...")
    
    # Send raw code dynamically without writing a physical script to the tools directory
    dynamic_code = """
import os
def run(name="World"):
    system_info = os.uname()
    return f"Hello {name}! Dynamically executed on {system_info.sysname} {system_info.machine} via AgentOS."
"""
    
    intent = {
        "code": dynamic_code,
        "args": {
            "name": "Architect"
        }
    }
    
    print(f"MCP Client: Sending Intent -> dynamic python string...")
    await socket.send_json(intent)
    
    response = await socket.recv_json()
    print(f"MCP Client: Received Response from OS -> {response}")

if __name__ == "__main__":
    asyncio.run(trigger_dynamic())
