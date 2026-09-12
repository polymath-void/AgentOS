import time
import os
import sys
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.core.sandbox import WASMSandboxRunner
from compute_res.memory.crdt_sync import StateCRDT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ComputeRes_Benchmark")

def run_benchmarks():
    print("===================================================")
    print("🚀 ComputeRes Performance & Latency Benchmark Suite")
    print("===================================================")

    # Benchmark 1: AST Sandbox Cold Start & Execution Latency
    runner = WASMSandboxRunner()
    code = "def run(n): return sum(i * i for i in range(n))"

    start_t = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        asyncio.run(runner.execute_python_sandboxed(code, args={"n": 1000}))
    total_time_ms = (time.perf_counter() - start_t) * 1000
    avg_latency_ms = total_time_ms / iterations

    print(f"⚡ [Sandbox Execution]: {iterations} runs completed in {total_time_ms:.2f} ms")
    print(f"   Average Latency per Execution: {avg_latency_ms:.3f} ms")

    # Benchmark 2: CRDT State Merge Throughput
    crdt1 = StateCRDT("Node-Alpha")
    crdt2 = StateCRDT("Node-Beta")

    start_crdt = time.perf_counter()
    crdt_ops = 500
    for i in range(crdt_ops):
        crdt2.set_key(f"metric_{i}", i)
        crdt1.merge(crdt2.to_dict())

    crdt_time_ms = (time.perf_counter() - start_crdt) * 1000
    print(f"🔄 [CRDT State Sync]: {crdt_ops} key merges completed in {crdt_time_ms:.2f} ms")

    print("===================================================")
    print("✅ All Benchmarks Completed Successfully!")
    print("===================================================")

if __name__ == "__main__":
    run_benchmarks()
