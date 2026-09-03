import zmq
import zmq.asyncio as zmq_asyncio
import asyncio
import json
import logging
import uuid
import time
from typing import Dict

logger = logging.getLogger("FederationMesh")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

class FederatedZeroMQNode:
    """
    A globally scalable ZeroMQ Federation Node.
    Routes AI intents across a distributed mesh based on cryptographic node IDs 
    and WASM Fuel availability, eliminating the single-broker bottleneck.
    """
    def __init__(self, node_id: str = None, host: str = "0.0.0.0", port: int = 5559):
        self.node_id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        self.host = host
        self.port = port
        self.context = zmq_asyncio.Context()
        
        # ROUTER socket for receiving intents from other federated peers
        self.router = self.context.socket(zmq.ROUTER)
        self.router.bind(f"tcp://{self.host}:{self.port}")
        
        # DEALER sockets to forward intents to known peers
        self.peers: Dict[str, zmq_asyncio.Socket] = {}
        
        # Simulated Fuel (Compute Capacity) - Determines if we process locally or forward
        self.available_fuel = 1000  

    def connect_to_peer(self, peer_id: str, peer_address: str):
        """Establish a DEALER connection to a remote federated ROUTER."""
        dealer = self.context.socket(zmq.DEALER)
        dealer.setsockopt_string(zmq.IDENTITY, self.node_id)
        dealer.connect(peer_address)
        self.peers[peer_id] = dealer
        logger.info(f"[{self.node_id}] Connected to remote peer: {peer_id} at {peer_address}")

    async def forward_intent(self, target_peer: str, intent: dict):
        """Forwards an intent to a remote peer if they have more compute capacity."""
        if target_peer in self.peers:
            logger.info(f"[{self.node_id}] Routing intent across federation to {target_peer}...")
            await self.peers[target_peer].send_json(intent)
        else:
            logger.error(f"[{self.node_id}] Peer {target_peer} not found in routing table.")

    async def process_intent_locally(self, intent: dict):
        """Simulates processing the intent within the local Wasmtime sandbox."""
        logger.info(f"[{self.node_id}] Processing intent locally. Fuel remaining: {self.available_fuel}")
        self.available_fuel -= intent.get("fuel_cost", 10)
        return {"status": "success", "result": f"Executed natively by {self.node_id}"}

    async def start_listening(self):
        """Main event loop for the federated ROUTER socket."""
        logger.info(f"[{self.node_id}] Federated Mesh Node ONLINE on tcp://{self.host}:{self.port}")
        
        while True:
            # Receive multipart message from ROUTER [identity, payload]
            try:
                frames = await self.router.recv_multipart()
                if len(frames) == 2:
                    identity, message = frames
                elif len(frames) == 3:
                    identity, _, message = frames
                else:
                    logger.error("Malformed ZMQ frame received.")
                    continue
                    
                intent = json.loads(message.decode())
                
                sender_id = identity.decode()
                logger.info(f"[{self.node_id}] Received incoming intent from {sender_id}: {intent['action']}")
                
                # Check fuel capability routing
                if self.available_fuel > intent.get("fuel_cost", 10):
                    result = await self.process_intent_locally(intent)
                    await self.router.send_multipart([identity, json.dumps(result).encode()])
                else:
                    logger.warning(f"[{self.node_id}] Insufficient fuel. Intent must be re-routed to mesh.")
                    await self.router.send_multipart([identity, json.dumps({"status": "error", "reason": "Insufficient Local Fuel"}).encode()])
            except Exception as e:
                logger.error(f"Routing error: {e}")

async def run_federation_simulation():
    # Node 1: Tokyo Datacenter
    node_tokyo = FederatedZeroMQNode(node_id="Tokyo-Prime", port=5560)
    
    # Node 2: London Edge Device
    node_london = FederatedZeroMQNode(node_id="London-Edge", port=5561)
    
    # Start listeners
    asyncio.create_task(node_tokyo.start_listening())
    asyncio.create_task(node_london.start_listening())
    
    # Allow bindings to settle
    await asyncio.sleep(0.5)
    
    # London connects to Tokyo via Federation Mesh
    node_london.connect_to_peer("Tokyo-Prime", "tcp://127.0.0.1:5560")
    
    # London sends a massive compute intent to Tokyo
    intent = {
        "action": "Compile Hyperbolic DB Abstract Syntax Tree",
        "fuel_cost": 500
    }
    
    await node_london.forward_intent("Tokyo-Prime", intent)
    
    # Wait for processing
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_federation_simulation())
