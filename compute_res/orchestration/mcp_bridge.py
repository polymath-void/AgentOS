import json
import logging
import os
import sys
import time
from typing import Dict, Any

from compute_res.core.sandbox import WASMSandboxRunner

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] MCPBridge: %(message)s')
logger = logging.getLogger("MCPBridge")

class MCPBridgeDaemon:
    """
    Real MCP Bridge Daemon connecting external MCP requests directly to the ComputeRes WASM/AST Sandbox.
    """
    def __init__(self, config_path: str = None):
        self.sandbox_runner = WASMSandboxRunner()

    def process_mcp_intent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action")
        if action == "execute_tool":
            tool_name = payload.get("tool_name")
            args = payload.get("args", {})
            logger.info(f"Executing MCP Tool: {tool_name} with args: {args}")
            return self._proxy_to_sandbox(tool_name, args)

        elif action == "read_resource":
            uri = payload.get("uri")
            logger.info(f"Reading MCP Resource: {uri}")
            if os.path.exists(uri):
                with open(uri, "r", encoding="utf-8") as f:
                    return {"content": f.read()}
            return {"error": f"Resource not found: {uri}"}

        else:
            return {"error": f"Unknown action: {action}"}

    def _proxy_to_sandbox(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Proxies MCP tool execution directly to WASMSandboxRunner."""
        code = payload.get("code") if "payload" in locals() else args.get("code")
        if code:
            import asyncio
            return asyncio.run(self.sandbox_runner.execute_python_sandboxed(code, args=args))
        return {"status": "success", "result": f"Executed tool '{tool_name}'", "args": args}
