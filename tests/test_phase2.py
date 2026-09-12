import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.network.signaling import SignalingServer, SignalingClient
from compute_res.memory.crdt_sync import LWWRegister, ORSet, StateCRDT

class TestPhase2NetworkAndCRDT(unittest.TestCase):
    def test_lww_register(self):
        reg1 = LWWRegister(value="alpha", timestamp=100.0, node_id="node1")
        reg2 = LWWRegister(value="beta", timestamp=200.0, node_id="node2")

        reg1.merge(reg2)
        self.assertEqual(reg1.value, "beta")
        self.assertEqual(reg1.node_id, "node2")

    def test_or_set(self):
        set1 = ORSet()
        set2 = ORSet()

        set1.add("node-A")
        set2.add("node-B")

        set1.merge(set2)
        self.assertEqual(set1.read(), {"node-A", "node-B"})

        set1.remove("node-A")
        self.assertEqual(set1.read(), {"node-B"})

    def test_state_crdt_merge(self):
        crdt1 = StateCRDT(node_id="Node-1")
        crdt2 = StateCRDT(node_id="Node-2")

        crdt1.set_key("status", "idle")
        crdt2.set_key("status", "running")

        crdt1.merge(crdt2.to_dict())
        self.assertEqual(crdt1.get_key("status"), "running")
        self.assertIn("Node-1", crdt1.active_nodes.read())
        self.assertIn("Node-2", crdt1.active_nodes.read())

    def test_signaling_server_client(self):
        async def _test_sig():
            server = SignalingServer(host="127.0.0.1", port=8799)
            await server.start()

            client1 = SignalingClient(server_url="ws://127.0.0.1:8799", node_id="Client-1")
            connected = await client1.connect()
            self.assertTrue(connected)

            await client1.close()
            await server.stop()

        asyncio.run(_test_sig())

if __name__ == "__main__":
    unittest.main()
