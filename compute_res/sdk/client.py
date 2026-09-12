import json
import asyncio
import logging
from typing import Dict, Any, Optional
import zmq
import zmq.asyncio

logger = logging.getLogger("ComputeRes_SDK")

class ComputeResClient:
    """
    High-Level Python Client SDK for ComputeRes AI Operating System.
    Connects to local or remote ComputeRes nodes via ZeroMQ IPC / MCP Protocol.
    """
    def __init__(self, broker_url: str = "tcp://127.0.0.1:5557", timeout_ms: int = 25000):
        self.broker_url = broker_url
        self.timeout_ms = timeout_ms
        self.context = zmq.asyncio.Context.instance()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


    async def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        socket = self.context.socket(zmq.REQ)
        socket.connect(self.broker_url)
        try:
            await socket.send_json(payload)
            reply = await asyncio.wait_for(socket.recv_json(), timeout=self.timeout_ms / 1000.0)
            return reply
        except asyncio.TimeoutError:
            return {"status": "error", "error": "ComputeRes client request timed out."}
        except Exception as e:
            return {"status": "error", "error": f"Client IPC failure: {str(e)}"}
        finally:
            socket.close(linger=0)

    async def execute_dynamic_code(self, code: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Submits dynamic Python code to the ComputeRes micro-sandbox."""
        payload = {
            "code": code,
            "args": args or {}
        }
        return await self._send_request(payload)

    async def execute_wasm(self, wasm_path: str, entrypoint: str = "run", args: Optional[Dict[str, Any]] = None, fuel: int = 10000000) -> Dict[str, Any]:
        """Submits a compiled WASM binary for sandboxed fuel-metered execution."""
        code = f'''
def run(**kwargs):
    from compute_res.core.sandbox import WASMSandboxRunner
    import os

    path = "{wasm_path}"
    if not os.path.exists(path):
        return {{"status": "error", "error": f"WASM binary file not found at {{path}}"}}

    with open(path, "rb") as f:
        wasm_bytes = f.read()

    runner = WASMSandboxRunner()
    return runner.execute_wasm_bytes(
        wasm_bytes=wasm_bytes,
        entrypoint="{entrypoint}",
        args={args or {}},
        fuel={fuel}
    )
'''
        return await self._send_request({"code": code, "args": {}})

    async def publish_skill(self, name: str, description: str, author: str, code: str) -> Dict[str, Any]:
        """Publishes a new dynamic skill into the ComputeRes SkillsHub."""
        code_payload = f'''
def run(**kwargs):
    from compute_res.memory.skillshub_db import skills_db
    import os
    safe_name = "{name}".replace(" ", "_").lower()
    evolved_dir = os.path.join(os.path.expanduser("~/.compute_res/tools/evolved_skills"))
    os.makedirs(evolved_dir, exist_ok=True)
    code_path = os.path.join(evolved_dir, f"{{safe_name}}.py")
    with open(code_path, "w") as f:
        f.write("""{code}""")
    skill_id = skills_db.publish_skill(
        name=safe_name,
        description="""{description}""",
        author="{author}",
        version="1.0.0",
        code_path=code_path
    )
    return {{"status": "success", "skill_id": skill_id}}
'''
        return await self._send_request({"code": code_payload, "args": {}})
