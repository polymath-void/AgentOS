import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compute_res.memory.chat_db import ChatMemoryDB

class TestPhase8MemoryAndFTS5(unittest.TestCase):
    def test_fts5_insert_and_search(self):
        test_db_path = os.path.expanduser("~/.compute_res/test_interactions.db")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        db = ChatMemoryDB(db_path=test_db_path)
        row_id = db.insert(
            session_id="sess_123",
            agent_id="Agent-Alpha",
            action="deploy_wasm",
            message="Successfully compiled Rust binary to WASM with fuel metering"
        )
        self.assertGreater(row_id, 0)

        # Retrieve session
        session_logs = db.get_session("sess_123")
        self.assertEqual(len(session_logs), 1)

        # Perform FTS5 full-text search
        search_results = db.search("WASM fuel")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]["agent_id"], "Agent-Alpha")

        if os.path.exists(test_db_path):
            os.remove(test_db_path)

if __name__ == "__main__":
    unittest.main()
