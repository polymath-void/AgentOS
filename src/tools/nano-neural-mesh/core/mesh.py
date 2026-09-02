from core.config import get_logger
import hashlib
import time

logger = get_logger()

class NeuralMesh:
    def __init__(self):
        self.nodes = {}
        self.global_state_hash = "00000000"
        logger.info("Synaptic Mesh initialized. Ready for high-density cognitive routing.")
        
    def attach_node(self, node_id, instance):
        self.nodes[node_id] = instance
        
    def broadcast(self, sender_id, state_vector):
        # Simulate network propagation latency
        time.sleep(0.001)
        
        # Calculate cryptographic state hash of the current broadcast to ensure data integrity
        raw_state = f"{sender_id}:{state_vector}:{self.global_state_hash}"
        self.global_state_hash = hashlib.sha256(raw_state.encode()).hexdigest()[:12]
        
        logger.info(f"Broadcast [State: {self.global_state_hash}] initiating from {sender_id}")
        
        # Route to all connected nano-nodes for distributed processing
        active_synapses = 0
        for nid, node in self.nodes.items():
            if nid != sender_id:
                # Trigger the node's local cognitive cycle
                response = node.cognitive_cycle(state_vector, self.global_state_hash)
                active_synapses += 1
                
        logger.debug(f" -> Stabilized across {active_synapses} synaptic pathways.")
