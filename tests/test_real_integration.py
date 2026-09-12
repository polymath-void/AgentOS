import os
import sys
import time
import json
import asyncio
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.core.manifest import ModuleManifest, validate_manifest_dict
from compute_res.core.sandbox import WASMSandboxRunner
from compute_res.memory.crdt_sync import StateCRDT
from compute_res.memory.vector_mgr import VectorManager
from compute_res.memory.chat_db import ChatMemoryDB
from compute_res.core.rbac import RBACEngine
from compute_res.core.audit import AuditLogger
from compute_res.sdk.client import ComputeResClient

class TestRealWorldIntegration(unittest.TestCase):
    def test_01_manifest_module(self):
        manifest = ModuleManifest(name="real_image_proc", fuel_limit=5000000)
        m_dict = manifest.to_dict()
        self.assertTrue(validate_manifest_dict(m_dict))
        self.assertEqual(m_dict["name"], "real_image_proc")
        self.assertEqual(m_dict["fuel_limit"], 5000000)
        print("\n✅ [1/7 Real Manifest Test]: Manifest schema created and validated.")

    def test_02_sandbox_execution(self):
        runner = WASMSandboxRunner()
        code = """
def run(numbers):
    # Real mathematical data processing inside AST sandbox
    evens = [x for x in numbers if x % 2 == 0]
    total = sum(evens)
    return {"evens": evens, "sum": total, "count": len(evens)}
"""
        res = asyncio.run(runner.execute_python_sandboxed(code, args={"numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["result"]["sum"], 30)
        self.assertEqual(res["result"]["evens"], [2, 4, 6, 8, 10])
        print(f"✅ [2/7 Real Sandbox Test]: Executed in {res['execution_time_ms']} ms -> Sum: {res['result']['sum']}")

    def test_03_crdt_p2p_state_sync(self):
        node_a = StateCRDT("Node-Alpha")
        node_b = StateCRDT("Node-Beta")

        node_a.set_key("temperature", 24.5)
        node_a.set_key("status", "ACTIVE")
        node_b.set_key("temperature", 26.1)
        node_b.set_key("load", 0.42)

        # Merge Node-B state into Node-A
        node_a.merge(node_b.to_dict())

        self.assertEqual(node_a.get_key("status"), "ACTIVE")
        self.assertEqual(node_a.get_key("load"), 0.42)
        self.assertIn("Node-Alpha", node_a.active_nodes.read())
        self.assertIn("Node-Beta", node_a.active_nodes.read())
        print("✅ [3/7 Real CRDT Sync Test]: Merged P2P state across Node-Alpha and Node-Beta.")

    def test_04_vector_knn_search(self):
        vm = VectorManager()

        # Store 3 real multi-dimensional embedding vectors
        vm.store(vector=[1.0, 0.0, 0.0], payload_id="vector_x", metadata={"topic": "space"})
        vm.store(vector=[0.0, 1.0, 0.0], payload_id="vector_y", metadata={"topic": "finance"})
        vm.store(vector=[0.9, 0.1, 0.0], payload_id="vector_similar_x", metadata={"topic": "aerospace"})

        # Search query close to vector_x ([1.0, 0.0, 0.0])
        results = vm.search(query_vector=[0.95, 0.05, 0.0], top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "vector_x")
        self.assertGreater(results[0]["score"], 0.99)
        self.assertEqual(results[1]["id"], "vector_similar_x")
        print(f"✅ [4/7 Real KNN Vector Test]: Top match '{results[0]['id']}' Cosine Similarity: {results[0]['score']}")

    def test_05_fts5_memory_database(self):
        test_db_path = os.path.expanduser("~/.compute_res/real_test_db.db")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        db = ChatMemoryDB(db_path=test_db_path)
        db.insert("session_001", "Agent-Swarm-1", "dispatch", "Deploying WASM skill module with 5000000 fuel")
        db.insert("session_001", "Agent-Swarm-2", "report", "WASM execution completed in 1.2ms without errors")

        # FTS5 search query
        results = db.search("WASM fuel")
        self.assertEqual(len(results), 1)
        self.assertIn("Deploying WASM", results[0]["message"])

        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        print("✅ [5/7 Real FTS5 Search Test]: Found matching interaction log via FTS5 index.")

    def test_06_rbac_security(self):
        rbac = RBACEngine()
        rbac.assign_role("WorkerAgent", "agent")
        rbac.assign_role("RootAdmin", "admin")

        self.assertTrue(rbac.check_permission("WorkerAgent", "wasm:execute"))
        self.assertFalse(rbac.check_permission("WorkerAgent", "kernel:admin"))
        self.assertTrue(rbac.check_permission("RootAdmin", "kernel:admin"))
        print("✅ [6/7 Real RBAC Security Test]: Role-based authorization enforced cleanly.")

    def test_07_live_kernel_sdk_ipc(self):
        async def _test_live():
            client = ComputeResClient()
            code = "def run(a, b): return a * b"
            res = await client.execute_dynamic_code(code, args={"a": 7, "b": 8})
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["data"], 56)
            print(f"✅ [7/7 Real Live Kernel IPC Test]: Live ZeroMQ Kernel executed 7 * 8 = {res['data']}")

        asyncio.run(_test_live())

if __name__ == "__main__":
    unittest.main()
