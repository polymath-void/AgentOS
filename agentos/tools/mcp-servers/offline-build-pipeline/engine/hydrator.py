"""
Phase 1: Hydrator module
Responsible for pulling project context and creating the JSON task manifest.
"""
import os
import json
from pathlib import Path

def hydrate(task_id: str, project_root: str, design_spec: str) -> dict:
    """
    Pull context and build the initial task manifest.
    """
    spec_path = Path(design_spec).expanduser()
    spec_content = ""
    if spec_path.exists():
        spec_content = spec_path.read_text()
    
    # In a real implementation, this would use a local lightweight model or heuristics
    # to extract tools from the markdown spec. For this pipeline, we expect the 
    # orchestrator to pass the structured work items directly if possible, or we stub it.
    
    manifest = {
        "task_id": task_id,
        "project_root": str(Path(project_root).expanduser()),
        "context": {
            "design_spec_preview": spec_content[:1000]
        },
        "work_items": [],
        "status": "hydrated"
    }
    return manifest
