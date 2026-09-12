import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compute_res.sdk.client import ComputeResClient

async def test_live_connection():
    print("\n--- INITIATING LIVE KERNEL TEST ---")
    
    client = ComputeResClient()
    print("[LLM Client] Connecting to ComputeRes Gateway via ZeroMQ...")
    
    code = "def run(**kwargs): return {'status': 'ONLINE', 'os': 'ComputeRes 1.0.0'}"
    response = await client.execute_dynamic_code(code)
    
    print("\n[LLM Client] Received Response from OS:")
    print(response)
    print("\n--- LIVE TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_live_connection())
