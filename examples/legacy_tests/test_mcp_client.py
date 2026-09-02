import asyncio
import zmq
import zmq.asyncio
import sys

async def trigger_organizer():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5557")
    
    print("MCP Client: Connecting to AgentOS Kernel...")
    
    intent = {
        "tool": "file_organizer",
        "args": {
            "target_dir": "/data/data/com.termux/files/home/storage/shared"
        }
    }
    
    print(f"MCP Client: Sending Intent -> {intent}")
    await socket.send_json(intent)
    
    response = await socket.recv_json()
    print(f"MCP Client: Received Response from OS -> {response}")

if __name__ == "__main__":
    asyncio.run(trigger_organizer())
