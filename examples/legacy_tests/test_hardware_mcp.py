import asyncio
import zmq
import zmq.asyncio
import json

async def trigger_optimized_hardware():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5557")
    
    print("MCP Client: Connecting to ComputeRes Kernel...")
    
    # Send highly optimized raw code to bypass Android 11+ /proc/ restrictions
    dynamic_code = """
def run():
    import os
    import subprocess
    hardware_data = {}
    
    # 1. CPU Load (Bypassing /proc/loadavg via uptime)
    try:
        uptime_out = subprocess.check_output(['uptime']).decode('utf-8')
        # uptime format: "22:31:18 up 55 min,  load average: 15.00, 15.15, 15.05"
        load_avg = uptime_out.split('load average:')[1].strip()
        hardware_data['cpu_load'] = f"Load Average: {load_avg}"
    except Exception as e:
        hardware_data['cpu_load'] = f"Unavailable: {e}"
        
    # 2. Memory Info (Fast parse from /proc/meminfo)
    try:
        mem_total = 0
        mem_free = 0
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) // 1024 # MB
                elif line.startswith('MemAvailable:') or line.startswith('MemFree:'):
                    mem_free = int(line.split()[1]) // 1024 # MB
        hardware_data['memory'] = f"{mem_total - mem_free} MB used / {mem_total} MB total"
    except Exception:
        hardware_data['memory'] = "Unavailable"
        
    # 3. CPU Cores & Arch (Bypassing /proc/cpuinfo via getprop)
    try:
        cores = 0
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('processor'):
                    cores += 1
                    
        model = subprocess.check_output(['getprop', 'ro.product.model']).decode('utf-8').strip()
        chipset = subprocess.check_output(['getprop', 'ro.board.platform']).decode('utf-8').strip()
        
        hardware_data['cpu_arch'] = f"{cores} Cores | Model: {model} | Chipset: {chipset.upper()}"
    except Exception as e:
        hardware_data['cpu_arch'] = f"Unavailable: {e}"
        
    return hardware_data
"""
    
    intent = {
        "code": dynamic_code,
        "args": {}
    }
    
    print(f"MCP Client: Sending Optimized Dynamic Script to ComputeRes...")
    await socket.send_json(intent)
    
    response = await socket.recv_json()
    print(f"MCP Client: Received Response from OS ->")
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(trigger_optimized_hardware())
