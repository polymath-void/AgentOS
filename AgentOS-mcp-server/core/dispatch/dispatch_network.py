import sys
import subprocess
import json
from pathlib import Path

# Add project paths for integration
sys.path.append("/data/data/com.termux/files/home/Projects/local/nano-neural-mesh")
sys.path.append("/data/data/com.termux/files/home/teamwork_projects/skills_verification")

class DispatchNetwork:
    def __init__(self, tools_manager):
        self.tools_manager = tools_manager
        print("DispatchNetwork initialized.")

    def route_task(self, task_type, payload):
        print(f"Routing task: {task_type}")
        
        if task_type == "mesh":
            print(f"Dispatching to Fabric (Mesh): {payload}")
            
        elif task_type == "verify":
            print(f"Dispatching to Verification Harness: {payload}")
            test_harness = "/data/data/com.termux/files/home/teamwork_projects/skills_verification/tests/run_e2e_tests.py"
            result = subprocess.run(["python3", test_harness], capture_output=True, text=True)
            print(f"Verification Result: {result.stdout}")
            
        elif task_type == "register_tool":
            name = payload.get("name")
            desc = payload.get("description")
            script = payload.get("script")
            print(f"Registering tool: {name}")
            
            # Register schema, script, and mirror
            self.tools_manager.register_tool(name, desc, script)
            print(f"Tool {name} registered with mirror.")
            
        elif task_type == "execute":
            name = payload.get("name")
            args = payload.get("args")
            mode = payload.get("mode", "simulate")
            
            print(f"Executing tool: {name} in {mode} mode.")
            
            if mode == "simulate":
                script_path = Path(self.tools_manager.tools_dir) / "mirrors" / f"{name}.sh"
            else:
                script_path = Path(self.tools_manager.tools_dir) / f"{name}.sh"
                
            if not script_path.exists():
                return f"Error: Script {script_path} not found."
            
            result = subprocess.run(["bash", str(script_path), json.dumps(args)], capture_output=True, text=True)
            print(f"Result ({mode}): {result.stdout}")
            
        else:
            print(f"Unsupported task type: {task_type}")
