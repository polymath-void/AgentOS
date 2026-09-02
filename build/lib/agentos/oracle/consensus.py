import asyncio
import uuid
import logging
import os

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] SwarmOracle: %(message)s')
logger = logging.getLogger("Oracle")

class SwarmOracle:
    """
    Coordinates Swarm-wide votes for capability escalation when a WASM container traps.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.active_votes = {} # Vote UUID -> State

    async def request_capability_consensus(self, capability: str, target_path: str, required_threshold=0.75) -> bool:
        """
        Pauses local execution, triggers a WebRTC broadcast, and waits for a supermajority vote.
        """
        vote_uuid = str(uuid.uuid4())
        logger.warning(f"[{vote_uuid}] Capability Request Initiated: {capability} on {target_path}")
        
        # 1. Initialize Vote State
        self.active_votes[vote_uuid] = {
            "capability": capability,
            "target": target_path,
            "votes": {"APPROVE": 1, "DENY": 0}, # Node self-approves to start
            "total_nodes_in_swarm": 3 # Hardcoded to 3 for the First Breath Simulation
        }
        
        logger.info(f"[{vote_uuid}] Broadcasting Vote Request to Global Swarm CRDT over ZeroMQ -> WebRTC...")
        
        # 2. In a real system, we publish over ZeroMQ here. For simulation, we yield to async loop to simulate network delay.
        await asyncio.sleep(0.5) 
        
        # 3. Process CRDT Votes (Simulated remote nodes responding)
        await self._simulate_remote_node_votes(vote_uuid)
        
        # 4. Tally
        state = self.active_votes[vote_uuid]
        total_votes = state["votes"]["APPROVE"] + state["votes"]["DENY"]
        approval_ratio = state["votes"]["APPROVE"] / max(total_votes, 1)
        
        logger.info(f"[{vote_uuid}] Vote Concluded. Approvals: {state['votes']['APPROVE']}, Denials: {state['votes']['DENY']}. Ratio: {approval_ratio:.2f}")
        
        if approval_ratio >= required_threshold:
            logger.info(f"[{vote_uuid}] SWARM SUPERMAJORITY ACHIEVED. Capability Granted.")
            return True
        else:
            logger.error(f"[{vote_uuid}] SWARM CONSENSUS FAILED. Capability Denied.")
            return False

    async def _simulate_remote_node_votes(self, vote_uuid: str):
        """Simulates other nodes in the WebRTC mesh receiving the CRDT and casting their votes."""
        # Simulate Node A (Gateway) voting APPROVE
        await asyncio.sleep(0.3)
        self.active_votes[vote_uuid]["votes"]["APPROVE"] += 1
        logger.debug(f"[{vote_uuid}] Received CRDT update: Node Gateway voted APPROVE")
        
        # Simulate Node C (Security Agent) analyzing heuristics and voting APPROVE
        await asyncio.sleep(0.4)
        self.active_votes[vote_uuid]["votes"]["APPROVE"] += 1
        logger.debug(f"[{vote_uuid}] Received CRDT update: Node SecurityOracle voted APPROVE")
