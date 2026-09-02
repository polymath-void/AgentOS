
from core.dispatch.dispatch_network import DispatchNetwork
from plugins.tools_manager import ToolsManager

def main():
    tools = ToolsManager("/data/data/com.termux/files/home/Projects/AgentOS/agent-os-hub/plugins")
    dispatch = DispatchNetwork(tools)
    
    # Simulate
    dispatch.route_task("execute", {"name": "web_search", "args": "google.com", "mode": "simulate"})
    
    # Execute
    dispatch.route_task("execute", {"name": "web_search", "args": "google.com", "mode": "execute"})

if __name__ == "__main__":
    main()
