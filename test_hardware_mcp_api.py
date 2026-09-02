import asyncio
import zmq
import zmq.asyncio
import json

async def trigger_full_system_insight():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5557")
    
    print("MCP Client: Connecting to AgentOS Kernel...")
    
    dynamic_code = """
def run():
    import os
    import subprocess
    import json
    sys_data = {}
    
    # 1. OS Info
    try:
        uname_out = subprocess.check_output(['uname', '-a']).decode('utf-8').strip()
        android_ver = subprocess.check_output(['getprop', 'ro.build.version.release']).decode('utf-8').strip()
        sys_data['os'] = f"Android {android_ver} | Kernel: {uname_out}"
    except Exception as e:
        sys_data['os'] = str(e)
        
    # 2. Battery Info via Termux API
    try:
        battery_out = subprocess.check_output(['termux-battery-status']).decode('utf-8')
        battery = json.loads(battery_out)
        sys_data['battery'] = f"{battery.get('percentage')}% ({battery.get('status')}) | Temp: {battery.get('temperature')}°C | Health: {battery.get('health')}"
    except Exception as e:
        sys_data['battery'] = f"Unavailable: {e}"
        
    # 3. Hardware & CPU
    try:
        cores = 0
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('processor'):
                    cores += 1
                    
        model = subprocess.check_output(['getprop', 'ro.product.model']).decode('utf-8').strip()
        manufacturer = subprocess.check_output(['getprop', 'ro.product.manufacturer']).decode('utf-8').strip()
        chipset = subprocess.check_output(['getprop', 'ro.board.platform']).decode('utf-8').strip()
        
        sys_data['hardware'] = f"{manufacturer} {model}"
        sys_data['cpu'] = f"{cores} Cores | Platform: {chipset.upper()}"
    except Exception as e:
        sys_data['hardware'] = f"Unavailable: {e}"
        
    # 4. GPU Info
    try:
        gpu_egl = subprocess.check_output(['getprop', 'ro.hardware.egl']).decode('utf-8').strip()
        sys_data['gpu'] = f"ARM {gpu_egl.capitalize()}" if gpu_egl else "Unknown"
    except Exception:
        sys_data['gpu'] = "Unavailable"
        
    return sys_data
"""
    
    intent = {
        "code": dynamic_code,
        "args": {}
    }
    
    print(f"MCP Client: Sending Complete System Insight Script to AgentOS...")
    await socket.send_json(intent)
    
    response = await socket.recv_json()
    print(f"MCP Client: Received Response from OS ->")
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(trigger_full_system_insight())
