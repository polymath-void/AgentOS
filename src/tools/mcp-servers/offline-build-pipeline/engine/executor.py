"""
Phase 2: Executor module
Uses Jinja2 to render templates based on work items in the manifest.
"""
import os
from pathlib import Path
try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    # Fallback if jinja2 is not installed, though it should be in the requirements
    Environment, FileSystemLoader = None, None

def execute_work_items(manifest: dict, templates_dir: str) -> list:
    if not Environment:
        return [{"error": "jinja2 not installed"}]
        
    env = Environment(loader=FileSystemLoader(templates_dir))
    results = []
    
    project_root = Path(manifest["project_root"])
    project_root.mkdir(parents=True, exist_ok=True)
    
    for item in manifest.get("work_items", []):
        if item["type"] == "generate_code":
            template = env.get_template(item["template"] + ".j2")
            rendered = template.render(**item.get("spec", {}))
            
            target_path = project_root / item["target"]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(rendered)
            
            results.append({
                "id": item["id"],
                "target": str(target_path),
                "status": "success"
            })
            
    return results
