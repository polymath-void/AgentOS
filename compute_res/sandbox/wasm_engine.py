import os
import sys
import logging
from typing import Dict, Any, Optional

from compute_res.core.sandbox import WASMSandboxRunner

logger = logging.getLogger("ComputeRes_WASMEngine")

class WasmContainer:
    """
    Production WASM Container delegating directly to WASMSandboxRunner.
    """
    def __init__(self, tool_name: str = "default_tool", initial_capabilities: Optional[Dict[str, Any]] = None):
        self.tool_name = tool_name
        self.capabilities = initial_capabilities or {}
        self.runner = WASMSandboxRunner()

    def execute_code(self, code: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        import asyncio
        return asyncio.run(self.runner.execute_python_sandboxed(code, args=args))
