import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.sdk.client import ComputeResClient

class TestPhase3SDK(unittest.TestCase):
    def test_sdk_instantiation(self):
        client = ComputeResClient(broker_url="tcp://127.0.0.1:5557")
        self.assertEqual(client.broker_url, "tcp://127.0.0.1:5557")
        self.assertEqual(client.timeout_ms, 25000)

if __name__ == "__main__":
    unittest.main()
