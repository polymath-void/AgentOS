from typing import List, Dict, Any

class VectorManager:
    def __init__(self):
        self.index: List[Dict[str, Any]] = []
        
    def store(self, vector: List[float], sao_id: str):
        self.index.append({"id": sao_id, "vector": vector})
        
    def search(self, query: List[float], top_k: int = 5):
        # Mock KNN semantic search
        return self.index[:top_k]
