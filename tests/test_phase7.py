import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.network.mesh import WebRTCMeshRouter
from compute_res.network.signaling import SignalingServer

class TestPhase7MeshRouter(unittest.TestCase):
    def test_mesh_router_initialization(self):
        router = WebRTCMeshRouter(node_id="TestNode-01", swarm_id="test-swarm")
        self.assertEqual(router.node_id, "TestNode-01")
        self.assertEqual(router.swarm_id, "test-swarm")
        self.assertIsNotNone(router.crdt)

    def test_mesh_router_start(self):
        async def _test_mesh():
            server = SignalingServer(host="127.0.0.1", port=8797)
            await server.start()

            router = WebRTCMeshRouter(node_id="MeshNode-Alpha", swarm_id="alpha", signaling_url="ws://127.0.0.1:8797")
            await router.start()
            self.assertIsNotNone(router.signaling_client)

            if router.signaling_client:
                await router.signaling_client.close()
            await server.stop()

        asyncio.run(_test_mesh())

if __name__ == "__main__":
    unittest.main()
