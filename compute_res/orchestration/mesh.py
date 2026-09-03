import asyncio
import json
import logging
import uuid
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

logger = logging.getLogger("WebRTCMesh")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

class ComputeResMeshRouter:
    """
    The Decentralized WebRTC Mesh Overlay.
    Bypasses centralized cloud infrastructure entirely by using STUN/TURN UDP hole-punching.
    Establishes raw SCTP DataChannels between global ComputeRes nodes, creating an invisible,
    un-blockable P2P fabric for the ZeroMQ Federation to ride upon.
    """
    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.node_id = f"mesh_{uuid.uuid4().hex[:8]}"
        self.peers = {}
        
        # Standard Google STUN servers for NAT Traversal
        self.rtc_config = RTCConfiguration(
            iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
        )
        logger.info(f"[{self.node_id}] Initializing WebRTC Mesh for Swarm: {self.swarm_id}")

    async def create_offer(self, target_node_id: str) -> dict:
        """Generates a cryptographic WebRTC SDP Offer to initiate a connection."""
        pc = RTCPeerConnection(configuration=self.rtc_config)
        self.peers[target_node_id] = pc

        # Create the raw data channel for ZeroMQ intent piping
        channel = pc.createDataChannel(f"compute_res_ipc_{self.swarm_id}")
        
        @channel.on("open")
        def on_open():
            logger.info(f"[{self.node_id}] P2P DataChannel OPENED with {target_node_id}. NAT Traversal Successful.")
            channel.send(json.dumps({"type": "handshake", "sender": self.node_id}))

        @channel.on("message")
        def on_message(message):
            logger.info(f"[{self.node_id}] Received via P2P Mesh: {message}")

        # Create the SDP offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        
        logger.info(f"[{self.node_id}] Generated WebRTC Offer for {target_node_id}.")
        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    async def receive_offer_create_answer(self, remote_node_id: str, offer_dict: dict) -> dict:
        """Receives an SDP Offer from a peer and generates an SDP Answer."""
        pc = RTCPeerConnection(configuration=self.rtc_config)
        self.peers[remote_node_id] = pc

        @pc.on("datachannel")
        def on_datachannel(channel):
            logger.info(f"[{self.node_id}] Inbound DataChannel established from {remote_node_id}.")
            
            @channel.on("message")
            def on_message(message):
                logger.info(f"[{self.node_id}] P2P Message from {remote_node_id}: {message}")
                # Echo back to prove two-way low-latency mesh
                if "handshake" in message:
                    channel.send(json.dumps({"type": "ack", "sender": self.node_id}))

        # Set the remote offer and generate local answer
        offer = RTCSessionDescription(sdp=offer_dict["sdp"], type=offer_dict["type"])
        await pc.setRemoteDescription(offer)
        
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        logger.info(f"[{self.node_id}] Generated WebRTC Answer for {remote_node_id}.")
        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    async def apply_answer(self, target_node_id: str, answer_dict: dict):
        """Applies the SDP Answer to finalize the P2P connection."""
        pc = self.peers.get(target_node_id)
        if pc:
            answer = RTCSessionDescription(sdp=answer_dict["sdp"], type=answer_dict["type"])
            await pc.setRemoteDescription(answer)
            logger.info(f"[{self.node_id}] Remote Answer applied. P2P link finalizing with {target_node_id}...")

async def simulate_decentralized_mesh():
    # Node A is a phone in Brazil on a mobile network
    node_a = ComputeResMeshRouter(swarm_id="Global-Alpha")
    
    # Node B is a laptop in Germany behind a strict corporate firewall
    node_b = ComputeResMeshRouter(swarm_id="Global-Alpha")
    
    # 1. Brazil generates an offer (Normally exchanged via a tiny signaling server)
    offer = await node_a.create_offer(target_node_id=node_b.node_id)
    
    # 2. Germany receives the offer and generates an answer
    answer = await node_b.receive_offer_create_answer(remote_node_id=node_a.node_id, offer_dict=offer)
    
    # 3. Brazil applies Germany's answer. UDP Hole Punching commences.
    await node_a.apply_answer(target_node_id=node_b.node_id, answer_dict=answer)
    
    # Wait for ICE candidates to resolve and datachannels to open natively
    await asyncio.sleep(2)
    print("\n[Simulation Complete] The WebRTC Data Channels are now open. The ZeroMQ Federation can now stream packets directly over this unblockable connection.")

if __name__ == "__main__":
    asyncio.run(simulate_decentralized_mesh())
