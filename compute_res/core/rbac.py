import logging
from typing import Dict, Set, List, Optional

logger = logging.getLogger("ComputeRes_RBAC")

class RBACEngine:
    """
    Enterprise Role-Based Access Control (RBAC) Engine for ComputeRes OS.
    Restricts agent capabilities, WASM skill execution, and system permissions.
    """
    DEFAULT_ROLES = {
        "admin": {"filesystem:read", "filesystem:write", "network:outbound", "wasm:execute", "skill:publish", "kernel:admin"},
        "agent": {"filesystem:read", "network:outbound", "wasm:execute", "skill:publish"},
        "guest": {"wasm:execute"}
    }

    def __init__(self):
        self.roles: Dict[str, Set[str]] = {k: set(v) for k, v in self.DEFAULT_ROLES.items()}
        self.agent_roles: Dict[str, str] = {}

    def assign_role(self, agent_id: str, role: str):
        if role not in self.roles:
            raise ValueError(f"Role '{role}' is not defined in RBAC policy.")
        self.agent_roles[agent_id] = role
        logger.info(f"Assigned role '{role}' to agent '{agent_id}'.")

    def check_permission(self, agent_id: str, required_permission: str) -> bool:
        role = self.agent_roles.get(agent_id, "guest")
        allowed = required_permission in self.roles.get(role, set())
        if not allowed:
            logger.warning(f"Access DENIED for agent '{agent_id}' (role: '{role}') requesting '{required_permission}'.")
        return allowed

    def authorize_manifest(self, agent_id: str, manifest_permissions: List[str]) -> bool:
        for perm in manifest_permissions:
            if not self.check_permission(agent_id, perm):
                return False
        return True
