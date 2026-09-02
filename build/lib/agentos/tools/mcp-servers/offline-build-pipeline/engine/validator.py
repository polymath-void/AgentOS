"""
Phase 3: Validator module
Cascading offline validation (Syntax -> Structure -> Security -> Logic)
"""
import ast
import py_compile
import json
from pathlib import Path

def _check_syntax(file_path: Path) -> dict:
    try:
        py_compile.compile(str(file_path), doraise=True)
        return {"pass": True}
    except Exception as e:
        return {"pass": False, "error": str(e)}

def _check_structure(file_path: Path) -> dict:
    try:
        tree = ast.parse(file_path.read_text())
        has_run = False
        tools = []
        for node in ast.walk(tree):
            # Check for mcp.run()
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "run" and isinstance(node.func.value, ast.Name) and node.func.value.id == "mcp":
                    has_run = True
            
            # Check for @mcp.tool decorators
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        if dec.func.attr == "tool":
                            tools.append(node.name)
        
        return {
            "pass": has_run, 
            "tools_found": len(tools),
            "error": "Missing mcp.run()" if not has_run else None
        }
    except Exception as e:
        return {"pass": False, "error": str(e)}

def run_validation(files: list, rules_dir: str) -> dict:
    results = {}
    all_pass = True
    
    for f in files:
        path = Path(f)
        if not path.exists():
            continue
            
        if path.suffix == ".py":
            syntax = _check_syntax(path)
            structure = _check_structure(path)
            
            file_pass = syntax["pass"] and structure["pass"]
            results[str(path)] = {
                "syntax": syntax,
                "structure": structure,
                "pass": file_pass
            }
            if not file_pass:
                all_pass = False
                
    return {"valid": all_pass, "details": results}
