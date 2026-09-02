import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.client.mcp_client import AgentOSClient

async def test_live_connection():
    print("\n--- INITIATING LIVE KERNEL TEST ---")
    
    # Instantiate the Standalone Client (Simulating an external LLM)
    client = AgentOSClient()
    
    print("[LLM Client] Connecting to AgentOS Gateway via ZeroMQ...")
    
    # We will simulate the LLM issuing an intent to execute a tool.
    tool_intent = "system_diagnostic"
    args = {"verbose": True}
    
    print(f"[LLM Client] Executing Intent: {tool_intent} | Args: {args}")
    
    # Send the request to the running kernel
    response = await client.execute_tool(tool_name=tool_intent, arguments=args)
    
    print("\n[LLM Client] Received Response from OS:")
    print(response)
    print("\n--- LIVE TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_live_connection())
