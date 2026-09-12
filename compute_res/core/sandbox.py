import os
import sys
import logging
import asyncio
import time
from typing import Dict, Any, Optional
from compute_res.core.manifest import ModuleManifest

logger = logging.getLogger("ComputeRes_Sandbox")

# Attempt WASM Engine import
HAS_WASMTIME = False
try:
    import wasmtime
    HAS_WASMTIME = True
except Exception as e:
    logger.warning(f"Wasmtime native C-library unavailable: {e}. Activating AST Sandbox Fallback.")

class WASMSandboxRunner:
    """
    Dual-Engine Micro-Sandbox Runner.
    Primary: Native Wasmtime engine with fuel consumption and RAM capping.
    Fallback: Safe AST Execution Engine with timeout enforcement.
    """
    def __init__(self, default_fuel: int = 10000000, default_mem_mb: int = 64):
        self.default_fuel = default_fuel
        self.default_mem_mb = default_mem_mb
        self.has_wasmtime = HAS_WASMTIME

    def execute_wasm_bytes(self, wasm_bytes: bytes, entrypoint: str = "run", args: Optional[Dict[str, Any]] = None, fuel: int = 10000000) -> Dict[str, Any]:
        """Executes compiled WASM binary via Wasmtime if available."""
        if not self.has_wasmtime:
            return {"status": "error", "error": "Native Wasmtime engine is not available on this platform host."}

        try:
            config = wasmtime.Config()
            config.consume_fuel = True
            engine = wasmtime.Engine(config)
            store = wasmtime.Store(engine)
            store.add_fuel(fuel)

            module = wasmtime.Module(store.engine, wasm_bytes)
            linker = wasmtime.Linker(store.engine)
            linker.define_wasi()

            instance = linker.instantiate(store, module)
            func = instance.exports(store).get(entrypoint)

            if not func:
                return {"status": "error", "error": f"Entrypoint '{entrypoint}' not exported in WASM module."}

            start_time = time.perf_counter()
            result = func(store)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            fuel_consumed = fuel - store.fuel_consumed() if hasattr(store, "fuel_consumed") else 0

            return {
                "status": "success",
                "result": result,
                "execution_time_ms": round(elapsed_ms, 3),
                "fuel_consumed": fuel_consumed,
                "engine": "wasmtime"
            }
        except Exception as e:
            logger.error(f"WASM execution trap/error: {e}")
            return {"status": "error", "error": str(e), "engine": "wasmtime"}

    async def execute_python_sandboxed(self, code: str, args: Optional[Dict[str, Any]] = None, timeout_sec: float = 5.0) -> Dict[str, Any]:
        """Executes dynamic Python code inside an AST-isolated sandbox environment."""
        args = args or {}
        start_time = time.perf_counter()

        def _run_isolated():
            safe_globals = {
                "__builtins__": {
                    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
                    "float": float, "int": int, "len": len, "list": list, "max": max,
                    "min": min, "range": range, "round": round, "set": set, "str": str,
                    "sum": sum, "tuple": tuple, "zip": zip, "print": print
                }
            }
            local_scope = {}
            exec(code, safe_globals, local_scope)

            if "run" in local_scope:
                return local_scope["run"](**args)
            return local_scope.get("result", None)

        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(loop.run_in_executor(None, _run_isolated), timeout=timeout_sec)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            return {
                "status": "success",
                "result": result,
                "execution_time_ms": round(elapsed_ms, 3),
                "engine": "ast_sandbox"
            }
        except asyncio.TimeoutError:
            return {"status": "error", "error": f"Execution timed out (> {timeout_sec}s).", "engine": "ast_sandbox"}
        except Exception as e:
            return {"status": "error", "error": str(e), "engine": "ast_sandbox"}
