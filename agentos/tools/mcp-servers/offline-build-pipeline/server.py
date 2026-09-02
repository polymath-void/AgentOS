#!/usr/bin/env python3
"""
Offline Build Pipeline — MCP Server

Orchestrates a token-efficient build pipeline by pulling context once,
generating code offline via Jinja2, validating syntax/logic offline,
and leveraging the local phi-3-mini engine for AI reviews.

Transport: stdio
"""

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import engine
sys.path.insert(0, str(Path(__file__).parent))

from engine import hydrator, executor, transferer

logger = logging.getLogger("offline-pipeline")
logger.setLevel(logging.DEBUG)

mcp = FastMCP(
    "offline-build-pipeline",
    description="Token-efficient offline build and AI review pipeline.",
)

# In-memory store for manifest state across tool calls
_MANIFESTS = {}

@mcp.tool()
def hydrate_context(task_id: str, project_root: str, design_spec: str) -> dict:
    """
    Phase 1: Hydrate. Pulls all context at once and generates a task manifest.
    """
    manifest = hydrator.hydrate(task_id, project_root, design_spec)
    _MANIFESTS[task_id] = manifest
    return manifest

@mcp.tool()
def execute_offline(task_id: str) -> dict:
    """
    Phase 2: Offline Execute. Runs Jinja2 template engine.
    """
    manifest = _MANIFESTS.get(task_id)
    if not manifest:
        return {"error": f"No manifest found for task_id: {task_id}. Call hydrate_context first."}
    
    templates_dir = str(Path(__file__).parent / "templates")
    results = executor.execute_work_items(manifest, templates_dir)
    _MANIFESTS[task_id]["execution_results"] = results
    return {"status": "executed", "results": results}

@mcp.tool()
def get_validation_context(task_id: str) -> dict:
    """
    Phase 3: Context for Main Agent.
    Packages the diffs and files so the normal agent model can perform validation.
    """
    manifest = _MANIFESTS.get(task_id)
    if not manifest:
        return {"error": "Manifest not found"}
    
    results = manifest.get("execution_results", [])
    files = [r["target"] for r in results if r["status"] == "success"]
    
    # Normally we would collect the diffs here to send to the main agent
    return {
        "files_to_review": files,
        "message": "Please read these files and perform syntax, security, and logic validation using your own capabilities."
    }

@mcp.tool()
def transfer_result(task_id: str) -> dict:
    """
    Phase 4: Transfer. Packages final clean output.
    """
    manifest = _MANIFESTS.get(task_id)
    if not manifest:
        return {"error": "Manifest not found"}
        
    files = [r["target"] for r in manifest.get("execution_results", [])]
    
    return transferer.package_results(task_id, files)

if __name__ == "__main__":
    mcp.run(transport="stdio")
