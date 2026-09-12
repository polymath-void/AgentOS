import math
from typing import List, Dict, Any

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class VectorManager:
    """
    Real Cosine-Similarity K-Nearest Neighbor (KNN) Vector Memory Store.
    """
    def __init__(self):
        self.index: List[Dict[str, Any]] = []

    def store(self, vector: List[float], payload_id: str, metadata: Dict[str, Any] = None):
        self.index.append({
            "id": payload_id,
            "vector": vector,
            "metadata": metadata or {}
        })

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        scored = []
        for item in self.index:
            score = cosine_similarity(query_vector, item["vector"])
            scored.append({
                "id": item["id"],
                "score": round(score, 4),
                "metadata": item["metadata"]
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
