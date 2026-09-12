import asyncio
import json
import logging
from typing import Dict, Any, Optional

from compute_res.memory.crdt_sync import StateCRDT
from compute_res.network.signaling import SignalingClient

try:
    import websockets
    from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
    AIORTC_AVAILABLE = True
except ImportError:
    AIORTC_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] WebRTCMesh: %(message)s')
logger = logging.getLogger("Mesh")

class WebRTCMeshRouter:
    """
    Bridges local ZeroMQ IPC Broker to the decentralized WebRTC Swarm.
    Uses SignalingClient for P2P SDP negotiation and StateCRDT for conflict-free memory sync.
    """
    def __init__(self, node_id: str, swarm_id: str, signaling_url: str = "ws://127.0.0.1:8765"):
        self.node_id = node_id
        self.swarm_id = swarm_id
        self.signaling_url = signaling_url
        self.crdt = StateCRDT(node_id=node_id)

        self.peers: Dict[str, Any] = {}
        self.data_channels: Dict[str, Any] = {}
        self.signaling_client: Optional[SignalingClient] = None

    async def handle_incoming_signal(self, data: Dict[str, Any]):
        msg_type = data.get("type")
        sender_id = data.get("sender_id")
        payload = data.get("payload", {})

        if msg_type == "offer" and AIORTC_AVAILABLE:
            logger.info(f"Received P2P Offer from {sender_id}")
            pc = RTCPeerConnection()
            self.peers[sender_id] = pc

            @pc.on("datachannel")
            def on_datachannel(channel):
                self.data_channels[sender_id] = channel
                logger.info(f"P2P DataChannel connected with {sender_id}")

                @channel.on("message")
                def on_message(message):
                    try:
                        packet = json.loads(message)
                        if packet.get("type") == "crdt_sync":
                            self.crdt.merge(packet.get("crdt", {}))
                            logger.info(f"Merged CRDT state delta from peer {sender_id}")
                    except Exception as e:
                        logger.error(f"Error parsing P2P message: {e}")

            sdp = payload.get("sdp")
            if sdp:
                await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type="offer"))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                if self.signaling_client:
                    await self.signaling_client.send_signal(
                        sender_id, "answer", {"sdp": pc.localDescription.sdp}
                    )

        elif msg_type == "answer" and AIORTC_AVAILABLE:
            pc = self.peers.get(sender_id)
            if pc and payload.get("sdp"):
                await pc.setRemoteDescription(RTCSessionDescription(sdp=payload["sdp"], type="answer"))
                logger.info(f"Established P2P answer with {sender_id}")

    async def broadcast_crdt_sync(self):
        """Periodically syncs StateCRDT deltas across active P2P data channels."""
        while True:
            await asyncio.sleep(5)
            if not self.data_channels:
                continue

            sync_packet = json.dumps({
                "type": "crdt_sync",
                "crdt": self.crdt.to_dict()
            })

            for peer_id, channel in list(self.data_channels.items()):
                try:
                    if hasattr(channel, "readyState") and channel.readyState == "open":
                        channel.send(sync_packet)
                except Exception as e:
                    logger.warning(f"Failed to send P2P CRDT sync to {peer_id}: {e}")

    async def start(self):
        """Starts the WebRTC Mesh Router daemon."""
        logger.info(f"[{self.node_id}] Initializing Decentralized WebRTC Mesh Router...")

        if not AIORTC_AVAILABLE:
            logger.warning("aiortc/websockets unavailable. P2P WebRTC data channels running in fallback mode.")
            return

        self.signaling_client = SignalingClient(server_url=self.signaling_url, node_id=self.node_id)
        self.signaling_client.on_message_callback = self.handle_incoming_signal

        connected = await self.signaling_client.connect()
        if connected:
            asyncio.create_task(self.signaling_client.listen())
            asyncio.create_task(self.broadcast_crdt_sync())
