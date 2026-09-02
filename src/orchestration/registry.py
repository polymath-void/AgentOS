import os
import ast
import json
import zmq
import importlib.util
from typing import Dict, Any, List

class SkillRegistry:
    def __init__(self, tools_dir: str):
        self.tools_dir = tools_dir
        self.registry: Dict[str, Any] = {}
        self.schemas: List[Dict[str, Any]] = []
        
        # ZeroMQ capability publisher
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.connect("tcp://127.0.0.1:5555")

    def parse_ast_schema(self, filepath: str, module_name: str) -> List[Dict[str, Any]]:
        """Parses Python AST to automatically generate MCP Tool JSON Schemas."""
        schemas = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Ignore private or standard main functions
                    if node.name.startswith("_") or node.name == "main":
                        continue
                        
                    docstring = ast.get_docstring(node) or f"Auto-generated skill from {module_name}"
                    
                    properties = {}
                    required = []
                    for arg in node.args.args:
                        arg_name = arg.arg
                        # Simple type inference fallback
                        properties[arg_name] = {"type": "string", "description": f"Argument {arg_name}"}
                        required.append(arg_name)
                        
                    schema = {
                        "name": f"{module_name}_{node.name}",
                        "description": docstring,
                        "inputSchema": {
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }
                    }
                    schemas.append(schema)
        except Exception as e:
            print(f"[Registry] AST Parse Error on {filepath}: {e}")
        return schemas

    def scan_and_load(self):
        """Recursively scan the tools directory and register available tools."""
        new_schemas = []
        for root, dirs, files in os.walk(self.tools_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('venv', 'venv_safe', '__pycache__', 'env', 'node_modules')]
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    module_name = file[:-3]
                    filepath = os.path.join(root, file)
                    
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, filepath)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            self.registry[module_name] = module
                            
                            # Parse AST for capabilities
                            extracted_schemas = self.parse_ast_schema(filepath, module_name)
                            if extracted_schemas:
                                new_schemas.extend(extracted_schemas)
                                
                            print(f"[Registry] Successfully loaded tool: {module_name} from {filepath}")
                    except Exception as e:
                        print(f"[Registry] Error loading {filepath}: {e}")
        
        self.schemas = new_schemas
        self.broadcast_capabilities()

    def broadcast_capabilities(self):
        """Broadcasts the newly parsed capabilities over the ZeroMQ Swarm Bus."""
        payload = json.dumps({"capabilities": self.schemas})
        self.pub_socket.send_multipart([b"SYS_CAPABILITY_UPDATE", payload.encode('utf-8')])
        print(f"[Registry] Broadcasted {len(self.schemas)} capabilities to Swarm.")

    def get_tool(self, name: str):
        return self.registry.get(name)

    def list_tools(self):
        return list(self.registry.keys())
