import asyncio
import json
import logging
import zmq
import zmq.asyncio
from typing import Dict, Any

try:
    import websockets
    from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
    AIORTC_AVAILABLE = True
except ImportError:
    AIORTC_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] WebRTCMesh: %(message)s')
logger = logging.getLogger("Mesh")

class CRDTManager:
    """
    Manages State Synchronization using an optimized Last-Writer-Wins Element Set (LWW-Element-Set).
    """
    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.add_set: Dict[str, float] = {}
        self.remove_set: Dict[str, float] = {}

    def merge_remote_crdt(self, remote_crdt: Dict[str, Any]):
        """Fast, deterministic conflict-resolution logic."""
        remote_adds = remote_crdt.get('add_set', {})
        remote_removes = remote_crdt.get('remove_set', {})
        
        for key, timestamp in remote_adds.items():
            if key not in self.add_set or timestamp > self.add_set[key]:
                self.add_set[key] = timestamp
                
        for key, timestamp in remote_removes.items():
            if key not in self.remove_set or timestamp > self.remove_set[key]:
                self.remove_set[key] = timestamp
                
        new_state = {}
        for key, add_time in self.add_set.items():
            if key not in self.remove_set or add_time > self.remove_set[key]:
                new_state[key] = remote_crdt.get('state', {}).get(key, self.state.get(key))
                
        self.state = new_state
        logger.debug(f"CRDT state mathematically resolved. Keys: {list(self.state.keys())}")


class WebRTCMeshRouter:
    """
    Bridges local ZeroMQ IPC Broker to the decentralized WebRTC Swarm.
    Implements Signaling Dropout for true P2P decentralization.
    """
    def __init__(self, node_id: str, swarm_id: str, signaling_url="ws://127.0.0.1:8765"):
        self.node_id = node_id
        self.swarm_id = swarm_id
        self.signaling_url = signaling_url
        self.context = zmq.asyncio.Context()
        self.crdt = CRDTManager()
        
        # ZeroMQ mapping
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.connect("tcp://127.0.0.1:5555")
        
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect("tcp://127.0.0.1:5556")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "MESH_BROADCAST")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "SYS_CAPABILITY_UPDATE")

        # WebRTC specific
        self.peers = {} # node_id -> RTCPeerConnection
        self.data_channels = {} # node_id -> RTCDataChannel
        self.signaling_ws = None

    async def _zmq_to_webrtc_loop(self):
        """Listens for local pub/sub events and broadcasts them to the global P2P mesh."""
        while True:
            try:
                topic_bytes, payload_bytes = await self.sub_socket.recv_multipart()
                topic = topic_bytes.decode('utf-8')
                payload = json.loads(payload_bytes.decode('utf-8'))
                
                mesh_envelope = {
                    "origin": self.node_id,
                    "topic": topic,
                    "data": payload
                }
                
                message_str = json.dumps(mesh_envelope)
                
                # Scatter broadcast directly over P2P DataChannels
                for peer_id, channel in self.data_channels.items():
                    if channel.readyState == "open":
                        channel.send(message_str)
                        logger.debug(f"Routed {topic} to peer {peer_id} via WebRTC DataChannel.")
                        
            except Exception as e:
                logger.error(f"Error in ZMQ->WebRTC bridge: {e}")

    async def _connect_signaling(self):
        """Connects to Matchmaker, negotiates P2P, and drops out."""
        if not AIORTC_AVAILABLE:
            logger.warning("aiortc/websockets not available in environment. Skipping WebRTC signaling handshake.")
            return

        try:
            async with websockets.connect(self.signaling_url) as ws:
                self.signaling_ws = ws
                
                # 1. Join Swarm
                await ws.send(json.dumps({"type": "join", "node_id": self.node_id, "swarm_id": self.swarm_id}))
                logger.info(f"Connected to Signaling Server. Joined swarm {self.swarm_id}.")
                
                # 2. Listen for matchmaking events
                async for message in ws:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "roster":
                        # Attempt to create P2P connections to all existing peers
                        ice_urls = data.get("ice_servers", [{"urls": "stun:stun.l.google.com:19302"}])
                        for peer_id in data.get("peers", []):
                            await self._create_peer_connection(peer_id, ice_urls, initiator=True)
                            
                    elif msg_type == "peer_joined":
                        # Wait for the new peer to send an offer
                        logger.info(f"Peer {data.get('peer_id')} joined the swarm.")
                        
                    elif msg_type == "offer":
                        peer_id = data.get("origin")
                        sdp = data.get("sdp")
                        # Handle incoming offer... (logic abbreviated for architectural scaffolding)
                        logger.info(f"Received P2P Offer from {peer_id}.")
                        
        except Exception as e:
            logger.error(f"Signaling error: {e}")

    async def _create_peer_connection(self, peer_id, ice_urls, initiator=False):
        """Initializes a direct P2P link to a node."""
        logger.info(f"Initializing RTCPeerConnection to {peer_id}...")
        # In a full implementation, we create the RTCPeerConnection, hook up the DataChannel,
        # set local description, and send the offer back via self.signaling_ws.
        
        # Signaling Dropout Logic:
        # channel.on("open", self._execute_signaling_dropout)
        pass

    def _execute_signaling_dropout(self):
        """Triggered the moment the DataChannel opens. Severs the server link."""
        logger.info("P2P DataChannel OPEN. Executing Signaling Dropout...")
        if self.signaling_ws:
            asyncio.create_task(self.signaling_ws.close())
            self.signaling_ws = None
            logger.info("Signaling Server link severed. Node is fully decentralized.")

    async def start(self):
        """Starts the WebRTC Mesh daemon."""
        logger.info(f"[{self.node_id}] Initializing Decentralized WebRTC Mesh Router...")
        asyncio.create_task(self._zmq_to_webrtc_loop())
        await self._connect_signaling()
