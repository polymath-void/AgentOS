import asyncio
import json
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def run_weather_experiment():
    print("AI Agent: Initializing MCP Client for Weather Analysis...")
    
    server_params = StdioServerParameters(
        command="python3",
        args=["agentos/gateway/mcp_server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("AI Agent: MCP Session Initialized. Injecting Weather Analysis Payload...")
            
            payload_code = r"""
def run():
    import urllib.request
    import json
    import os
    
    cities = {
        "Tokyo": (35.6895, 139.6917),
        "Delhi": (28.6139, 77.2090),
        "Beijing": (39.9042, 116.4074),
        "Bangkok": (13.7563, 100.5018),
        "Jakarta": (-6.2088, 106.8456),
        "Manila": (14.5995, 120.9842),
        "Dubai": (25.2048, 55.2708),
        "Singapore": (1.3521, 103.8198)
    }
    
    results = {}
    
    try:
        # 1. Collect Data via Open-Meteo API
        for city, (lat, lon) in cities.items():
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation&timezone=Asia%2FTokyo"
            req = urllib.request.Request(url, headers={'User-Agent': 'AgentOS/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                current = data.get("current", {})
                results[city] = {
                    "temp": current.get("temperature_2m", 0),
                    "rain": current.get("precipitation", 0)
                }
                
        # 2. Analyze Critical Zones
        high_heat_zone = max(results.items(), key=lambda x: x[1]["temp"])
        high_rain_zone = max(results.items(), key=lambda x: x[1]["rain"])
        
        # 3. Generate the Report
        report_path = os.path.expanduser("~/storage/shared/Documents/AgentOS_Asia_Weather_Analysis.txt")
        with open(report_path, "w") as f:
            f.write("=== AGENT-OS ASIA WEATHER ANALYSIS ===\n\n")
            f.write("Raw Telemetry:\n")
            for city, data in results.items():
                f.write(f" - {city}: {data['temp']}°C, {data['rain']}mm Rain\n")
            
            f.write("\n=== CRITICAL ZONES ===\n")
            f.write(f"[WARNING] High Heat Zone: {high_heat_zone[0]} at {high_heat_zone[1]['temp']}°C\n")
            if high_rain_zone[1]['rain'] > 0:
                f.write(f"[WARNING] High Precipitation Zone: {high_rain_zone[0]} at {high_rain_zone[1]['rain']}mm\n")
            else:
                f.write("[INFO] No significant precipitation currently detected across major hubs.\n")
                
            f.write("\nStatus: Computed dynamically on edge via MCP ZeroMQ IPC.")
            
        return f"Weather analysis complete. High Heat: {high_heat_zone[0]}. Saved to {report_path}"
        
    except Exception as e:
        return f"Payload Failed: {str(e)}"
"""
            
            result = await session.call_tool(
                name="execute_dynamic_python",
                arguments={
                    "code": payload_code,
                    "args": "{}"
                }
            )
            
            print(f"\nAI Agent: Received Execution Result from AgentOS:")
            print(f"-> {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_weather_experiment())
