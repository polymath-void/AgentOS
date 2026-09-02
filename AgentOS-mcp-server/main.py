
from core.dispatch.dispatch_network import DispatchNetwork
from orchestrator.polymath_bridge import PolymathBridge
from orchestrator.validation import ValidationHarness
from factory.deployment import AgentFactory
from plugins.tools_manager import ToolsManager

def main():
    print("Initializing Integrated Polymath Reasoning Centre...")
    # Initialize Core Components
    bridge = PolymathBridge()
    harness = ValidationHarness()
    factory = AgentFactory(bridge, harness)
    tools = ToolsManager("/data/data/com.termux/files/home/Projects/AgentOS/agent-os-hub/plugins")
    dispatch = DispatchNetwork(tools)
    dispatch.route_task("verify", {"test": "all"})
    
    print("Integrated Polymath Reasoning Centre Running.")

if __name__ == "__main__":
    main()
