import time
import json
import uuid
import logging
from typing import Dict, Any, Set, Tuple

logger = logging.getLogger("ComputeRes_CRDT")

class LWWRegister:
    """Last-Write-Wins Register for single key-value state."""
    def __init__(self, value: Any = None, timestamp: float = 0.0, node_id: str = ""):
        self.value = value
        self.timestamp = timestamp or time.time()
        self.node_id = node_id

    def set(self, value: Any, node_id: str):
        self.value = value
        self.timestamp = time.time()
        self.node_id = node_id

    def merge(self, other: "LWWRegister"):
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp
            self.node_id = other.node_id
        elif other.timestamp == self.timestamp and other.node_id > self.node_id:
            self.value = other.value
            self.node_id = other.node_id

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value, "timestamp": self.timestamp, "node_id": self.node_id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LWWRegister":
        return cls(value=data.get("value"), timestamp=data.get("timestamp", 0.0), node_id=data.get("node_id", ""))


class ORSet:
    """Observed-Remove Set (Add-Win Set) for distributed elements."""
    def __init__(self):
        # Element -> Set of (tag_uuid, timestamp)
        self.add_set: Dict[Any, Set[Tuple[str, float]]] = {}
        self.remove_set: Dict[Any, Set[Tuple[str, float]]] = {}

    def add(self, element: Any) -> str:
        tag = str(uuid.uuid4())
        ts = time.time()
        if element not in self.add_set:
            self.add_set[element] = set()
        self.add_set[element].add((tag, ts))
        return tag

    def remove(self, element: Any):
        if element in self.add_set:
            if element not in self.remove_set:
                self.remove_set[element] = set()
            self.remove_set[element].update(self.add_set[element])

    def read(self) -> Set[Any]:
        result = set()
        for elem, add_tags in self.add_set.items():
            rem_tags = self.remove_set.get(elem, set())
            active_tags = add_tags - rem_tags
            if active_tags:
                result.add(elem)
        return result

    def merge(self, other: "ORSet"):
        for elem, tags in other.add_set.items():
            if elem not in self.add_set:
                self.add_set[elem] = set()
            self.add_set[elem].update(tags)

        for elem, tags in other.remove_set.items():
            if elem not in self.remove_set:
                self.remove_set[elem] = set()
            self.remove_set[elem].update(tags)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "add_set": {k: list(v) for k, v in self.add_set.items()},
            "remove_set": {k: list(v) for k, v in self.remove_set.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ORSet":
        orset = cls()
        orset.add_set = {k: set(tuple(x) for x in v) for k, v in data.get("add_set", {}).items()}
        orset.remove_set = {k: set(tuple(x) for x in v) for k, v in data.get("remove_set", {}).items()}
        return orset


class StateCRDT:
    """
    Unified Conflict-Free Replicated Data Store for ComputeRes Nodes.
    Synchronizes active nodes, swarm tasks, and shared memory keys across P2P WebRTC channels.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.registers: Dict[str, LWWRegister] = {}
        self.active_nodes = ORSet()
        self.active_nodes.add(node_id)

    def set_key(self, key: str, value: Any):
        if key not in self.registers:
            self.registers[key] = LWWRegister()
        self.registers[key].set(value, self.node_id)

    def get_key(self, key: str) -> Any:
        reg = self.registers.get(key)
        return reg.value if reg else None

    def merge(self, other_state_dict: Dict[str, Any]):
        # Merge Registers
        other_regs = other_state_dict.get("registers", {})
        for k, r_dict in other_regs.items():
            other_reg = LWWRegister.from_dict(r_dict)
            if k not in self.registers:
                self.registers[k] = other_reg
            else:
                self.registers[k].merge(other_reg)

        # Merge Active Nodes
        if "active_nodes" in other_state_dict:
            other_nodes = ORSet.from_dict(other_state_dict["active_nodes"])
            self.active_nodes.merge(other_nodes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "registers": {k: v.to_dict() for k, v in self.registers.items()},
            "active_nodes": self.active_nodes.to_dict()
        }
