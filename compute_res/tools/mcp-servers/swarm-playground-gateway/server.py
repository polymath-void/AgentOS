#!/usr/bin/env python3
"""
ComputeRes Gateway — MCP Server (Pure Python Stdio)

Exposes the ComputeRes unified operating system via MCP,
allowing external AI agents to send direct commands to the Prime Agent
via the ZeroMQ IPC Bus.

Zero-dependency standard library implementation to bypass Android Rust bounds.
"""

import json
import sys
import os

# Inject ComputeRes src into path to import IPC Bus
sys.path.insert(0, '/data/data/com.termux/files/home/Projects/ComputeRes/compute_res')
try:
    from compute_res.orchestration.ipc_bus import IPCBus
except ImportError:
    IPCBus = None

def dispatch_to_os(task_string: str) -> dict:
    """Send a command directly to the ComputeRes Prime Agent via IPC."""
    if not IPCBus:
        return {"error": "IPCBus module not found. Is ComputeRes installed correctly?"}
        
    ipc = IPCBus()
    ipc.connect()
    
    # Retry loop to handle ZeroMQ REQ/REP Dealer round-robin load balancing
    for _ in range(5):
        try:
            reply = ipc.request(target="prime_agent", payload={"task": task_string}, timeout=15.0)
            if reply.get("status") == "success":
                return {"response": reply.get("data", {}).get("response", "No response content.")}
            elif reply.get("message") == "Target mismatch":
                continue 
            else:
                return {"error": f"Prime Agent failed: {reply.get('message')}"}
        except Exception as e:
            return {"error": f"IPC Request failed: {e}"}
            
    return {"error": "Failed to route to Prime Agent (Max retries exceeded)."}

def handle_request(req: dict) -> dict:
    """Handle an incoming JSON-RPC request."""
    method = req.get("method")
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {"name": "compute_res-gateway", "version": "1.0.0"}
        }
    
    elif method == "tools/list":
        return {
            "tools": [
                {
                    "name": "execute_os_command",
                    "description": "Execute a high-level orchestration command on the ComputeRes Prime Agent.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"command": {"type": "string"}},
                        "required": ["command"]
                    }
                },
                {
                    "name": "get_os_status",
                    "description": "Check if the ComputeRes IPC Bus is online and responding.",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            ]
        }
        
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "execute_os_command":
            res = dispatch_to_os(args.get("command", ""))
            return {"content": [{"type": "text", "text": json.dumps(res)}], "isError": "error" in res}
            
        elif tool_name == "get_os_status":
            res = dispatch_to_os("SYSTEM_STATUS_CHECK")
            is_err = "error" in res
            status_obj = {"status": "offline" if is_err else "online", "details": res}
            return {"content": [{"type": "text", "text": json.dumps(status_obj)}], "isError": is_err}
            
        else:
            return {"content": [{"type": "text", "text": f"Tool not found: {tool_name}"}], "isError": True}
            
    return {}

def main():
    """Pure stdio JSON-RPC event loop."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            if req_id is not None:
                result = handle_request(req)
                resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
                print(json.dumps(resp), flush=True)
        except Exception:
            pass

if __name__ == "__main__":
    main()
