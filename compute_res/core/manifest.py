import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ComputeRes_Manifest")

class ModuleManifest:
    """
    Standardized ComputeRes WASM & Skill Module Manifest (compute-res.json).
    Defines security bounds, fuel limits, RAM capping, and entrypoints.
    """
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        wasm_binary: Optional[str] = None,
        fuel_limit: int = 10000000,
        memory_limit_mb: int = 64,
        permissions: Optional[List[str]] = None,
        entrypoint: str = "run",
        description: str = ""
    ):
        self.name = name
        self.version = version
        self.wasm_binary = wasm_binary
        self.fuel_limit = fuel_limit
        self.memory_limit_mb = memory_limit_mb
        self.permissions = permissions or ["filesystem:read"]
        self.entrypoint = entrypoint
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "wasm_binary": self.wasm_binary,
            "fuel_limit": self.fuel_limit,
            "memory_limit_mb": self.memory_limit_mb,
            "permissions": self.permissions,
            "entrypoint": self.entrypoint,
            "description": self.description
        }

def validate_manifest_dict(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    if "name" not in data or not isinstance(data["name"], str):
        return False
    return True

def load_manifest(filepath: str) -> ModuleManifest:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Manifest file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not validate_manifest_dict(data):
        raise ValueError(f"Invalid compute-res.json schema in {filepath}")

    return ModuleManifest(
        name=data.get("name"),
        version=data.get("version", "1.0.0"),
        wasm_binary=data.get("wasm_binary"),
        fuel_limit=data.get("fuel_limit", 10000000),
        memory_limit_mb=data.get("memory_limit_mb", 64),
        permissions=data.get("permissions", ["filesystem:read"]),
        entrypoint=data.get("entrypoint", "run"),
        description=data.get("description", "")
    )
