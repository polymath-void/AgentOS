import asyncio
import os
import sys

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sandbox.wasm_engine import WasmContainer, WasmTrapException
from src.oracle.consensus import SwarmOracle

async def run_first_breath_simulation():
    print("\n--- INITIATING FIRST BREATH SIMULATION ---\n")
    
    # 1. Boot Node B (The Edge Worker executing the tool)
    oracle = SwarmOracle(node_id="Node_B_Worker")
    
    # 2. Instantiate a strictly sandboxed WASM Container for a new tool
    container = WasmContainer(tool_name="write_distributed_log", initial_capabilities={})
    
    # 3. Simulate external AI Agent trying to write a file via MCP
    target_path = "/logs/first_breath.txt"
    print(f"\n[MCP Gateway] Received intent to execute tool 'write_distributed_log' on {target_path}\n")
    
    try:
        # 4. The tool executes and immediately TRAPS because it lacks FS_WRITE
        container.execute_mock_tool(intent="FS_WRITE", target_path=target_path)
    except WasmTrapException as e:
        print(f"\n[OS KERNEL] TRAP DETECTED: {e}")
        
        # 5. Trap pauses execution and invokes the Swarm Oracle
        print(f"[OS KERNEL] Invoking Swarm Consensus Oracle...\n")
        consensus_granted = await oracle.request_capability_consensus(
            capability=e.capability_requested,
            target_path=e.target_path
        )
        
        # 6. If Swarm approves, we mathematically inject the capability and resume
        if consensus_granted:
            print("\n[OS KERNEL] Consensus granted. Injecting capability and resuming WASM execution...\n")
            container.inject_capability(e.capability_requested, e.target_path)
            
            # Resume execution (it should succeed this time)
            result = container.execute_mock_tool(intent="FS_WRITE", target_path=target_path)
            print(f"\n[MCP Gateway] Execution Final Result: {result}\n")
        else:
            print("\n[OS KERNEL] Consensus denied. Terminating WASM Container.\n")
            
    print("--- FIRST BREATH SIMULATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_first_breath_simulation())
