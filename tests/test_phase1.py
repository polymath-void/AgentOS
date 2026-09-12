import os
import sys
import unittest
import asyncio

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.core.manifest import ModuleManifest, load_manifest, validate_manifest_dict
from compute_res.core.sandbox import WASMSandboxRunner

class TestPhase1Foundation(unittest.TestCase):
    def test_manifest_validation(self):
        valid_dict = {"name": "test_skill", "version": "1.0.0", "fuel_limit": 50000}
        self.assertTrue(validate_manifest_dict(valid_dict))

        invalid_dict = {"version": "1.0.0"}
        self.assertFalse(validate_manifest_dict(invalid_dict))

    def test_manifest_object(self):
        manifest = ModuleManifest(name="test_skill", fuel_limit=200000)
        self.assertEqual(manifest.name, "test_skill")
        self.assertEqual(manifest.fuel_limit, 200000)
        self.assertIn("filesystem:read", manifest.permissions)

    def test_python_ast_sandbox(self):
        runner = WASMSandboxRunner()
        code = """
def run(x, y):
    return x + y
"""
        res = asyncio.run(runner.execute_python_sandboxed(code, args={"x": 10, "y": 20}))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["result"], 30)
        self.assertEqual(res["engine"], "ast_sandbox")

if __name__ == "__main__":
    unittest.main()
