import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compute_res.core.sandbox import WASMSandboxRunner

async def run_first_breath_simulation():
    print("\n--- INITIATING FIRST BREATH SIMULATION ---\n")
    runner = WASMSandboxRunner()
    code = "def run(x, y): return x * y"
    res = await runner.execute_python_sandboxed(code, args={"x": 6, "y": 7})
    print(f"[Sandbox Output]: {res}")
    print("\n--- FIRST BREATH SIMULATION COMPLETE ---\n")

if __name__ == "__main__":
    asyncio.run(run_first_breath_simulation())
