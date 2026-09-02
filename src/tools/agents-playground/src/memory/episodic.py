import time
import math
from typing import List, Dict, Any, Optional

class Event:
    """Represents a single episodic event or State-Action-Observation triplet."""
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None, role: str = "Swarm Event"):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

class EpisodicMemory:
    """
    Neuro-Symbolic Episodic Memory (Option 5).
    Logs State-Action-Observation triplets and retrieves experiences based on
    keyword/semantic term overlap and temporal recency decay.
    """
    def __init__(self):
        self.events: List[Event] = []

    def store_event(self, content: str, metadata: Optional[Dict[str, Any]] = None, role: str = "Swarm Event") -> Event:
        event = Event(content, metadata, role=role)
        self.events.append(event)
        return event

    def log_triplet(self, state: str, action: str, observation: str, success: bool = True, role: str = "Episode Logger") -> Event:
        """Logs a structured State-Action-Observation episode."""
        status_str = "SUCCESS" if success else "FAILURE"
        content = f"[{status_str}] State: {state} | Action: {action} | Obs: {observation}"
        meta = {"state": state, "action": action, "observation": observation, "success": success}
        return self.store_event(content=content, metadata=meta, role=role)

    def retrieve_events(self, query: str, limit: int = 10) -> List[Event]:
        if not self.events:
            return []
            
        query_terms = set(query.lower().split())
        scored_events = []
        current_time = time.time()
        
        for event in self.events:
            event_terms = set(event.content.lower().split())
            overlap = len(query_terms.intersection(event_terms))
            match_score = overlap / (math.log(len(event_terms) + 2)) if len(event_terms) > 0 else 0
            
            age = current_time - event.timestamp
            recency_score = 1.0 / (1.0 + age * 0.001)
            
            total_score = match_score + (recency_score * 0.1)
            scored_events.append((total_score, event))
            
        scored_events.sort(key=lambda x: x[0], reverse=True)
        return [e for score, e in scored_events[:limit]]
        
    def get_all_events(self) -> List[Event]:
        return self.events
