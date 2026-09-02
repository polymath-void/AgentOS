import asyncio
import os
import sys
import threading
import time

# Add src to python path securely using absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

# Import AgentOS Subsystems
from orchestration.ipc_bus import IPCBroker
from orchestration.mcp_bridge import MCPBridgeDaemon
from orchestration.registry import SkillRegistry
from p2p.webrtc_node import WebRTCNode
from orchestration.agent import BaseAgent

async def boot_sequence():
    print("=" * 60)
    print(" [AgentOS Kernel] Initiating System Boot Sequence...")
    print("=" * 60)
    
    # 1. Start ZeroMQ IPC Broker
    print("[AgentOS Kernel] [1/5] Mounting ZeroMQ IPC Broker...")
    broker = IPCBroker()
    threading.Thread(target=broker.start, daemon=True).start()
    await asyncio.sleep(1) # Allow broker to bind
    print("                      -> IPC Broker Online (tcp://*:5555)")

    # 2. Start MCP Bridge Daemon (mcpd)
    print("[AgentOS Kernel] [2/5] Initializing MCP Bridge Daemon...")
    mcp_daemon = MCPBridgeDaemon()
    threading.Thread(target=mcp_daemon.start, daemon=True).start()
    await asyncio.sleep(1)
    print("                      -> MCP Servers Mounted.")

    # 3. Load Tool Registry
    print("[AgentOS Kernel] [3/5] Scanning Virtual Filesystem for Tools...")
    registry = SkillRegistry(tools_dir=os.path.join(os.path.dirname(__file__), "src/tools"))
    registry.scan_and_load()
    tools_loaded = len(registry.list_tools())
    print(f"                      -> {tools_loaded} unified tools/skills hot-loaded.")

    # 4. Initialize P2P Mesh Node
    print("[AgentOS Kernel] [4/5] Initializing WebRTC P2P Mesh daemon...")
    node = WebRTCNode(node_id="AgentOS-Prime")
    await node.connect(signaling_server_url="ws://localhost:8080")
    print("                      -> Mesh established.")

    # Import IPCBus for mounting
    from orchestration.ipc_bus import IPCBus

    # 5. Spawn the Prime Agent
    print("[AgentOS Kernel] [5/5] Awakening Prime Agent Entity...")
    prime_agent = BaseAgent(
        name="Antigravity-Prime",
        role="System Supervisor",
        system_prompt="You are the absolute master of AgentOS. Coordinate the swarm."
    )
    
    # Mount Prime Agent to IPC Bus
    ipc_client = IPCBus()
    ipc_client.connect()
    
    def prime_agent_handler(payload):
        task = payload.get("task", "Empty task")
        response = prime_agent.execute(task)
        return {"response": response}
        
    ipc_client.start_reply_server(target="prime_agent", handler=prime_agent_handler)
    print("                      -> Prime Agent mounted to IPC Bus (target='prime_agent').")
    
    time.sleep(1)
    print("\n" + "=" * 60)
    print(f" [{prime_agent.name}] AGENT OS IS ONLINE.")
    print(" Core, Scripts, and Tools are mounted and ready to execute.")
    print("=" * 60)
    
    # Keep kernel alive
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(boot_sequence())
    except KeyboardInterrupt:
        print("\n[AgentOS Kernel] System shutting down safely. Goodbye.")
