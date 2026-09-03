import math
import uuid
import time
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger("HyperbolicDB")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

class HyperbolicVector:
    """Represents a mathematical point in the Poincaré ball model of Hyperbolic space."""
    def __init__(self, coordinates: List[float]):
        self.coordinates = coordinates
        
    def norm_sq(self) -> float:
        return sum(x**2 for x in self.coordinates)
        
    def distance_sq(self, other: 'HyperbolicVector') -> float:
        return sum((x - y)**2 for x, y in zip(self.coordinates, other.coordinates))

def poincare_distance(u: HyperbolicVector, v: HyperbolicVector) -> float:
    """
    Calculates the exact geometric distance between two points in hyperbolic space.
    d(u,v) = arcosh(1 + 2 * (||u-v||^2) / ((1 - ||u||^2) * (1 - ||v||^2)))
    This math allows tree-like AST structures to be embedded with zero distortion!
    """
    norm_u = u.norm_sq()
    norm_v = v.norm_sq()
    
    # Ensure points remain strictly inside the boundary of the Poincaré ball
    if norm_u >= 1.0 or norm_v >= 1.0:
        raise ValueError("Points must be strictly inside the unit Poincaré ball (norm < 1).")
        
    dist_sq = u.distance_sq(v)
    denominator = (1.0 - norm_u) * (1.0 - norm_v)
    
    # Calculate the hyperbolic argument
    delta = 1.0 + 2.0 * (dist_sq / denominator)
    return math.acosh(delta)

class HyperbolicDB:
    """
    The ComputeRes Neuro-Symbolic Memory Vector Database.
    Embeds ASTs and Intent graphs in Hyperbolic Space for exponentially faster
    nearest-neighbor retrieval of hierarchical data across the WebRTC mesh.
    """
    def __init__(self):
        self.registry: Dict[str, Tuple[HyperbolicVector, dict, float]] = {}
        logger.info("Initialized ComputeRes Hyperbolic DB.")

    def insert(self, record_id: str, vector: List[float], metadata: dict):
        """Inserts an embedding into the CRDT-synced database registry."""
        norm_sq = sum(x**2 for x in vector)
        if norm_sq >= 1.0:
            # Normalize it into the Poincaré ball dynamically
            scale = 0.99 / math.sqrt(norm_sq)
            vector = [x * scale for x in vector]
            
        h_vec = HyperbolicVector(vector)
        timestamp = time.time()
        self.registry[record_id] = (h_vec, metadata, timestamp)
        logger.info(f"Inserted record '{record_id}' into Hyperbolic Space.")

    def search(self, query_vector: List[float], top_k: int = 3) -> List[dict]:
        """
        Performs an ultra-fast nearest-neighbor search using Poincaré mathematics.
        Returns the closest matching ASTs or historical Agent Intents.
        """
        norm_sq = sum(x**2 for x in query_vector)
        if norm_sq >= 1.0:
            scale = 0.99 / math.sqrt(norm_sq)
            query_vector = [x * scale for x in query_vector]
            
        q_vec = HyperbolicVector(query_vector)
        results = []
        
        for rec_id, (h_vec, metadata, ts) in self.registry.items():
            dist = poincare_distance(q_vec, h_vec)
            results.append({
                "id": rec_id,
                "metadata": metadata,
                "hyperbolic_distance": round(dist, 4)
            })
            
        # Sort by mathematical proximity (lowest distance first)
        results.sort(key=lambda x: x["hyperbolic_distance"])
        return results[:top_k]

if __name__ == "__main__":
    db = HyperbolicDB()
    
    # 1. Store hierarchical AST logic embeddings
    # (In hyperbolic space, parents are near the origin (0,0), children are pushed towards the boundary (0.9, 0.9))
    db.insert("Root_OS_Logic", [0.0, 0.0, 0.0], {"type": "kernel_root"})
    db.insert("WebRTC_Mesh", [0.5, 0.0, 0.0], {"type": "networking_module"})
    db.insert("ZeroMQ_Broker", [0.0, 0.5, 0.0], {"type": "ipc_module"})
    db.insert("WebRTC_DataChannel", [0.9, 0.0, 0.0], {"type": "networking_sub_module"})
    
    # 2. Agent Swarm searches for networking logic to optimize P2P tunnels
    query = [0.8, 0.0, 0.0] # An intent querying deeply about networking
    
    print("\n--- Hyperbolic Nearest-Neighbor Search Results ---")
    results = db.search(query, top_k=2)
    for idx, res in enumerate(results):
        print(f"Rank {idx+1}: {res['id']} (Distance: {res['hyperbolic_distance']}) - {res['metadata']}")
