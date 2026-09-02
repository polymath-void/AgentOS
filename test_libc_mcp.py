import asyncio
import zmq
import zmq.asyncio
import json

async def trigger_raw_computing():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5557")
    
    print("MCP Client: Connecting to AgentOS Kernel...")
    
    # Send highly advanced raw code that utilizes ctypes to talk directly to the Bionic C Library
    dynamic_code = """
def run():
    import ctypes
    # 1. Load Android's Bionic C Library dynamically in memory
    libc = ctypes.CDLL("libc.so")
    
    # 2. Define the Linux sysinfo struct
    class SysInfo(ctypes.Structure):
        _fields_ = [
            ("uptime", ctypes.c_long),
            ("loads", ctypes.c_ulong * 3),
            ("totalram", ctypes.c_ulong),
            ("freeram", ctypes.c_ulong),
            ("sharedram", ctypes.c_ulong),
            ("bufferram", ctypes.c_ulong),
            ("totalswap", ctypes.c_ulong),
            ("freeswap", ctypes.c_ulong),
            ("procs", ctypes.c_ushort),
            ("pad", ctypes.c_ushort),
            ("totalhigh", ctypes.c_ulong),
            ("freehigh", ctypes.c_ulong),
            ("mem_unit", ctypes.c_uint),
            ("_f", ctypes.c_char * 20)
        ]
        
    sys_info = SysInfo()
    
    # 3. Call the kernel syscall directly from memory, bypassing the OS filesystem completely
    result = libc.sysinfo(ctypes.byref(sys_info))
    
    if result == 0:
        # 4. Extract and calculate raw data natively
        mem_unit = sys_info.mem_unit
        total_ram_mb = (sys_info.totalram * mem_unit) // (1024 * 1024)
        free_ram_mb = (sys_info.freeram * mem_unit) // (1024 * 1024)
        
        # In Linux, load average is divided by 2^16 (65536)
        load_1m = sys_info.loads[0] / 65536.0
        load_5m = sys_info.loads[1] / 65536.0
        load_15m = sys_info.loads[2] / 65536.0
        
        return {
            "kernel_syscall_status": "Success",
            "uptime_seconds": sys_info.uptime,
            "processes_running": sys_info.procs,
            "raw_memory": f"{total_ram_mb - free_ram_mb} MB used / {total_ram_mb} MB total",
            "kernel_load_average": f"{load_1m:.2f} (1m), {load_5m:.2f} (5m), {load_15m:.2f} (15m)"
        }
    else:
        return {"error": "Failed to execute sysinfo syscall"}
"""
    
    intent = {
        "code": dynamic_code,
        "args": {}
    }
    
    print(f"MCP Client: Sending Bare-Metal C-Types Script to AgentOS...")
    await socket.send_json(intent)
    
    response = await socket.recv_json()
    print(f"MCP Client: Received Response from OS ->")
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(trigger_raw_computing())
