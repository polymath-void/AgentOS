from pydantic import BaseModel
from typing import Dict, Any, List

class StateActionObservation(BaseModel):
    state_vector: List[float]
    action_taken: str
    observation_result: str
    reward: float
    metadata: Dict[str, Any]
