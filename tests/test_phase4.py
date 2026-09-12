import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.core.rbac import RBACEngine
from compute_res.core.audit import AuditLogger

class TestPhase4EnterpriseSecurity(unittest.TestCase):
    def test_rbac_permissions(self):
        rbac = RBACEngine()
        rbac.assign_role("Agent-007", "agent")

        self.assertTrue(rbac.check_permission("Agent-007", "wasm:execute"))
        self.assertFalse(rbac.check_permission("Agent-007", "kernel:admin"))

        rbac.assign_role("Admin-001", "admin")
        self.assertTrue(rbac.check_permission("Admin-001", "kernel:admin"))

    def test_audit_logging(self):
        test_audit_dir = os.path.expanduser("~/.compute_res/test_audit")
        os.makedirs(test_audit_dir, exist_ok=True)
        test_audit_path = os.path.join(test_audit_dir, "test_audit.jsonl")

        if os.path.exists(test_audit_path):
            os.remove(test_audit_path)

        audit = AuditLogger(log_path=test_audit_path)
        audit.log_event("Agent-Alpha", "wasm_run", {"fuel_used": 4500})

        self.assertTrue(os.path.exists(test_audit_path))
        with open(test_audit_path, "r") as f:
            content = f.read()
            self.assertIn("Agent-Alpha", content)
            self.assertIn("wasm_run", content)

        if os.path.exists(test_audit_path):
            os.remove(test_audit_path)

if __name__ == "__main__":
    unittest.main()
