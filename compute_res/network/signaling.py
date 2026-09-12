import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
import websockets

logger = logging.getLogger("ComputeRes_Signaling")

class SignalingServer:
    """
    WebSocket Signaling Server for WebRTC SDP & ICE Candidate Exchange.
    Enables decentralized nodes to discover peers and negotiate WebRTC connections.
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Dict[str, Any] = {}
        self.server = None

    async def register(self, node_id: str, websocket: Any):
        self.clients[node_id] = websocket
        logger.info(f"Node '{node_id}' registered with Signaling Server.")

    async def unregister(self, node_id: str):
        if node_id in self.clients:
            del self.clients[node_id]
            logger.info(f"Node '{node_id}' unregistered from Signaling Server.")

    async def handle_message(self, websocket: Any, path: Optional[str] = None):
        node_id = None
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "register":
                    node_id = data.get("node_id")
                    await self.register(node_id, websocket)
                    await websocket.send(json.dumps({"type": "registered", "node_id": node_id}))

                elif msg_type in ("offer", "answer", "candidate"):
                    target_id = data.get("target_id")
                    if target_id in self.clients:
                        await self.clients[target_id].send(message)
                    else:
                        await websocket.send(json.dumps({"type": "error", "error": f"Target node '{target_id}' not online."}))

                elif msg_type == "list_nodes":
                    active_nodes = [nid for nid in self.clients.keys() if nid != node_id]
                    await websocket.send(json.dumps({"type": "nodes_list", "nodes": active_nodes}))

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if node_id:
                await self.unregister(node_id)

    async def start(self):
        self.server = await websockets.serve(self.handle_message, self.host, self.port)
        logger.info(f"Signaling Server online at ws://{self.host}:{self.port}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Signaling Server stopped.")


class SignalingClient:
    """
    Signaling Client used by ComputeRes WebRTC Mesh Router to exchange WebRTC SDPs.
    """
    def __init__(self, server_url: str = "ws://127.0.0.1:8765", node_id: str = "Node-Default"):
        self.server_url = server_url
        self.node_id = node_id
        self.websocket = None
        self.on_message_callback: Optional[Callable[[Dict[str, Any]], None]] = None

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.server_url)
            await self.websocket.send(json.dumps({"type": "register", "node_id": self.node_id}))
            resp = await self.websocket.recv()
            logger.info(f"Signaling client connected to {self.server_url}: {resp}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to signaling server {self.server_url}: {e}")
            return False

    async def send_signal(self, target_id: str, msg_type: str, payload: Dict[str, Any]):
        if not self.websocket:
            return False
        msg = {
            "type": msg_type,
            "sender_id": self.node_id,
            "target_id": target_id,
            "payload": payload
        }
        await self.websocket.send(json.dumps(msg))
        return True

    async def listen(self):
        if not self.websocket:
            return
        try:
            async for message in self.websocket:
                data = json.loads(message)
                if self.on_message_callback:
                    if asyncio.iscoroutinefunction(self.on_message_callback):
                        await self.on_message_callback(data)
                    else:
                        self.on_message_callback(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Signaling websocket connection closed.")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
