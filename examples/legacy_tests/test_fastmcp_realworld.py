import asyncio
import json
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def run_real_world_experiment():
    print("AI Agent: Initializing MCP Client...")
    
    # 1. Define the FastMCP Server Subprocess Parameters
    server_params = StdioServerParameters(
        command="python3",
        args=["compute_res/gateway/mcp_server.py"],
        env=None
    )
    
    print("AI Agent: Booting ComputeRes FastMCP Gateway via stdio...")
    
    # 2. Connect to the Server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("AI Agent: MCP Session Initialized Successfully.")
            
            # 3. Discover Tools
            tools_response = await session.list_tools()
            print(f"AI Agent: Discovered ComputeRes Tools: {[t.name for t in tools_response.tools]}")
            
            # 4. Construct a highly complex Real-World Payload (Local LAN Scanner & Reporter)
            print("AI Agent: Formulating dynamic payload for Network Reconnaissance...")
            payload_code = r"""
def run():
    import os
    import socket
    import subprocess
    try:
        # Step 1: Find the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Step 2: Extract routing and interface info
        kernel_info = subprocess.check_output(['uname', '-a']).decode('utf-8')
        
        # Step 3: Write a physical intelligence report to the Android Device
        report_path = os.path.expanduser("~/storage/shared/Documents/ComputeRes_Network_Intel.txt")
        
        with open(report_path, "w") as f:
            f.write("=== AGENT-OS NETWORK INTEL ===\\n")
            f.write(f"Host IP: {local_ip}\\n")
            f.write(f"Kernel Info:\\n{kernel_info}\\n")
            f.write("Status: Secure.\\n")
            
        return f"Successfully extracted network telemetry ({local_ip}) and wrote physical report to {report_path}"
    except Exception as e:
        return f"Payload Failed: {str(e)}"
"""
            
            # 5. Execute the dynamic capability via MCP
            print("AI Agent: Injecting payload into ComputeRes execute_dynamic_python tool...")
            result = await session.call_tool(
                name="execute_dynamic_python",
                arguments={
                    "code": payload_code,
                    "args": "{}"
                }
            )
            
            # 6. Output the result
            print(f"\nAI Agent: Received Execution Result from ComputeRes:")
            print(f"-> {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_real_world_experiment())
