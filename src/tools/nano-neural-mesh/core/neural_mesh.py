import json
from uuid import uuid4

class NeuralMesh:
    def __init__(self):
        self.nodes = {}
        self.active_mesh = True
        print("[MESH] Neural Mesh Core Initialized. Ready for nanosecond node attachment.")
        
    def attach_node(self, instance):
        node_id = f"nano-node-{uuid4().hex[:8]}"
        self.nodes[node_id] = instance
        print(f"[MESH] Attached new execution node: {node_id}")
        return node_id
        
    def broadcast(self, sender_id, payload):
        """Seamlessly route data to all duplicated nodes via simulated synapses."""
        if not self.active_mesh:
            return
            
        print(f"[MESH] Broadcast from {sender_id}: {payload}")
        for nid, node in self.nodes.items():
            if nid != sender_id:
                # In a real environment, node.receive() triggers the WASM memory buffer
                print(f"[MESH]   -> Routing to {nid}")

    def get_node_count(self):
        return len(self.nodes)
