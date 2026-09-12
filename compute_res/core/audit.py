import time
import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("ComputeRes_Audit")

class AuditLogger:
    """
    Immutable Execution Audit Logger for Enterprise SOC2 & Security Compliance.
    Logs every WASM/AST execution, fuel consumption, and agent action.
    """
    def __init__(self, log_path: Optional[str] = None):
        if log_path is None:
            base_dir = os.path.expanduser("~/.compute_res/audit")
            os.makedirs(base_dir, exist_ok=True)
            log_path = os.path.join(base_dir, "audit_trail.jsonl")
        self.log_path = log_path

    def log_event(self, agent_id: str, action: str, details: Dict[str, Any], status: str = "SUCCESS"):
        record = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "agent_id": agent_id,
            "action": action,
            "status": status,
            "details": details
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit record: {e}")
