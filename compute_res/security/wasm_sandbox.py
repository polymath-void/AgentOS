import logging
from typing import Dict, Any, Optional

from compute_res.core.sandbox import WASMSandboxRunner

logger = logging.getLogger("ComputeRes_WASMSecurity")

class WASMSecuritySandbox:
    """
    Production Security Sandbox wrapper around WASMSandboxRunner.
    """
    def __init__(self, fuel_limit: int = 10000000, memory_limit_mb: int = 64):
        self.fuel_limit = fuel_limit
        self.memory_limit_mb = memory_limit_mb
        self.runner = WASMSandboxRunner(default_fuel=fuel_limit, default_mem_mb=memory_limit_mb)

    def execute(self, code: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        import asyncio
        return asyncio.run(self.runner.execute_python_sandboxed(code, args=args))
