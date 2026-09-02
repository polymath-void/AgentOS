import sys
import os
sys.path.insert(0, '/data/data/com.termux/files/home/Projects/AgentOS/src/tools/mcp-servers/swarm-playground-gateway')
import server

print("[Test] Pinging AgentOS via MCP Gateway methods...")
status = server.get_os_status()
print(f"Status: {status}")

print("[Test] Executing OS Command via MCP Gateway...")
response = server.execute_os_command("Deploy exploratory swarm node.")
print(f"Response: {response}")
