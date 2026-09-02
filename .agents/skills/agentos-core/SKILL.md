---
name: agentos-core
description: >-
  Standard Operating Procedure for utilizing the AgentOS framework. Instructs agents on how to dynamically compile and execute raw Python payloads into the ZeroMQ IPC Broker using the execute_dynamic_python MCP tool.
---

# AgentOS Core Execution SOP

AgentOS is a bare-metal execution hypervisor that allows AI agents to run continuous, stateful, or highly complex workflows on the physical edge device via the Model Context Protocol (MCP).

## 1. The Dynamic Injection Paradigm

You do not need to write deployment files or shell scripts to execute complex tasks. AgentOS exposes the `execute_dynamic_python` MCP tool. 

**Core Concept:** 
You formulate a raw string of Python code containing a `def run():` block. You pass this string into the `execute_dynamic_python` tool. AgentOS intercepts this string, compiles it dynamically using `exec()` within the local IPC Kernel, and executes it natively on the physical host hardware.

## 2. Writing Valid Payloads

When formulating your Python payload for injection, you MUST adhere to the following rules to ensure the ZeroMQ worker can execute it:

1. **The Entrypoint:** The code MUST contain a `def run():` function. This is what the kernel will invoke.
2. **Internal Imports:** All imports (`import os`, `import socket`, `import subprocess`) MUST be placed **inside** the `def run():` block. If they are placed outside, the isolated execution scope will fail to resolve them.
3. **Return Statements:** The `run()` function must return a string or a JSON-serializable dictionary. This is the output that will be routed back to you across the MCP mesh.
4. **Daemon Threads for Long-Running Tasks:** If you are deploying an HTTP server or a continuous monitoring loop, you must spawn a background `threading.Thread(target=..., daemon=True)` and return immediately. Do NOT block the `run()` function with infinite loops (`while True`), or you will hang the ZeroMQ worker processing your request.

## 3. Example Payload: Network Scanning

```python
def run():
    import socket
    import os
    
    # Payload Logic
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
        
    return f"Successfully extracted network telemetry: {local_ip}"
```

## 4. Troubleshooting
- `name 'xyz' is not defined`: You forgot to put your `import xyz` inside the `def run():` block.
- `[Errno 111] Connection refused`: The AgentOS Kernel daemon (`python3 agentos/orchestration/kernel.py`) is not running in the background. Start it before executing the tool.
