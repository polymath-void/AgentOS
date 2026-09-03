from core.config import Settings, get_logger
from core.mesh import NeuralMesh
from core.engine import WasmEngine
from core.spawner import NanoNodeSpawner
import uuid

logger = get_logger()

def main():
    logger.info("Booting Distributed Cognitive Swarm...")
    
    mesh = NeuralMesh()
    engine = WasmEngine()
    module = engine.load_module(Settings.PAYLOAD_PATH)
    spawner = NanoNodeSpawner(engine, module)
    
    node_ids = []
    total_spawn_time = 0
    
    # Mass instantiation of the swarm
    for _ in range(50):
        instance, duration = spawner.duplicate_node()
        nid = f"nano-{uuid.uuid4().hex[:4]}"
        mesh.attach_node(nid, instance)
        node_ids.append(nid)
        total_spawn_time += duration
        
    avg_spawn = total_spawn_time / 50
    logger.info(f"Swarm instantiated. 50 nodes duplicated. Avg time: {avg_spawn:.2f} ns/node")
    
    # Run Cognitive Epochs (Reasoning Complexity)
    for epoch in range(1, Settings.EPOCHS + 1):
        logger.info(f"--- Initiating Cognitive Epoch {epoch} ---")
        # Generate a synthetic input vector (e.g., environmental data)
        synthetic_vector = [0.1 * epoch, 0.5 * epoch, 0.9]
        
        # The primary node triggers the broadcast, forcing the entire network
        # to execute their WASM cognitive cycles and update their internal weights.
        mesh.broadcast(node_ids[0], synthetic_vector)
        
    logger.info(f"Final Global Swarm State Hash: {mesh.global_state_hash}")

if __name__ == "__main__":
    main()
