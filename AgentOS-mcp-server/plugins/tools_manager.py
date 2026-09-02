
import os
import json
import subprocess
from pathlib import Path

class ToolsManager:
    def __init__(self, tools_dir):
        self.tools_dir = Path(tools_dir)
        if not self.tools_dir.exists():
            os.makedirs(self.tools_dir)
        print(f"ToolsManager initialized at {self.tools_dir}")

    def load_dynamic_schemas(self):
        schemas = []
        for file in self.tools_dir.glob("*.json"):
            with open(file, 'r') as f:
                try:
                    schemas.append(json.load(f))
                except json.JSONDecodeError:
                    print(f"Error loading schema: {file}")
        return schemas

    def register_tool(self, name, description, script):
        tool_schema = {"name": name, "description": description}
        with open(self.tools_dir / f"{name}.json", 'w') as f:
            json.dump(tool_schema, f)
            
        # Create actual script
        script_path = self.tools_dir / f"{name}.sh"
        with open(script_path, 'w') as f:
            f.write(script)
        subprocess.run(["chmod", "+x", str(script_path)])
        
        # Create mirror script
        mirror_path = self.tools_dir / "mirrors" / f"{name}.sh"
        with open(mirror_path, 'w') as f:
            f.write(f"#!/bin/bash\necho 'SIMULATED: {name} with args: $1'")
        subprocess.run(["chmod", "+x", str(mirror_path)])
        
        print(f"Tool {name} registered with mirror.")
