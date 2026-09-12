import asyncio
import json
import logging
from typing import Dict, Set, Any
import websockets

logger = logging.getLogger("ComputeRes_WSGateway")

class WebSocketTelemetryGateway:
    """
    Live WebSocket Telemetry & Event Push Gateway for ComputeRes OS.
    Streams real-time WASM fuel metrics, CRDT updates, and kernel telemetry
    to connected browser dashboards and external UI clients.
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 8766):
        self.host = host
        self.port = port
        self.subscribers: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None

    async def register(self, websocket: Any):
        self.subscribers.add(websocket)
        logger.info(f"Telemetry subscriber connected from {websocket.remote_address}")

    async def unregister(self, websocket: Any):
        self.subscribers.discard(websocket)
        logger.info("Telemetry subscriber disconnected.")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcasts a telemetry payload to all connected subscribers."""
        if not self.subscribers:
            return

        payload = json.dumps({
            "event": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        })

        disconnected = set()
        for ws in self.subscribers:
            try:
                await ws.send(payload)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(ws)

        for ws in disconnected:
            self.subscribers.discard(ws)

    async def handle_connection(self, websocket: Any, path: str = None):
        await self.register(websocket)
        try:
            async for message in websocket:
                # Handle client ping or subscription requests if needed
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def start(self):
        self.server = await websockets.serve(self.handle_connection, self.host, self.port)
        logger.info(f"WebSocket Telemetry Gateway online at ws://{self.host}:{self.port}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket Telemetry Gateway stopped.")
