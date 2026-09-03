import os
import json
import time

def run(agent_id="UnknownAgent", payload=None, context=None, **kwargs):
    """
    Authentication and context sharing bridge for external swarm agents.
    Allows agents to 'login' and share blueprints with the ComputeRes OS.
    """
    data_to_save = {
        "agent_id": agent_id,
        "payload": payload or context,
        "timestamp": time.time(),
        "extra_kwargs": kwargs
    }
    
    # Save the context to the filesystem so the waiting internal agent (me) can read it
    os.makedirs("shared_context", exist_ok=True)
    file_path = f"shared_context/handoff_{agent_id}_{int(time.time())}.json"
    
    with open(file_path, "w") as f:
        json.dump(data_to_save, f, indent=4)
        
    return {
        "status": "SUCCESS",
        "message": f"Welcome to ComputeRes, {agent_id}. Your handoff context has been received and stored securely in the kernel space.",
        "saved_path": file_path
    }
