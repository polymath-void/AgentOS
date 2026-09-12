import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.gateway.websocket_gateway import WebSocketTelemetryGateway
import websockets
import json

class TestPhase6WebSocketGateway(unittest.TestCase):
    def test_websocket_gateway(self):
        async def _run_test():
            gw = WebSocketTelemetryGateway(host="127.0.0.1", port=8798)
            await gw.start()

            async with websockets.connect("ws://127.0.0.1:8798") as client:
                await gw.broadcast_event("FUEL_METRIC", {"fuel_used": 1500, "node": "Node-Alpha"})
                msg = await client.recv()
                data = json.loads(msg)
                self.assertEqual(data["event"], "FUEL_METRIC")
                self.assertEqual(data["data"]["fuel_used"], 1500)

            await gw.stop()

        asyncio.run(_run_test())

if __name__ == "__main__":
    unittest.main()
