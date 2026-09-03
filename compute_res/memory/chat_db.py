import sqlite3
import time
import os

DB_PATH = "/data/data/com.termux/files/home/Projects/ComputeRes/compute_res/memory/interactions.db"

class ChatMemoryDB:
    """
    Fast, FTS5-indexed SQLite database for storing swarm chats, intents, and agent interactions.
    Separates standard text/chat data from the Hyperbolic vector DB.
    """
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Standard table for interactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    action TEXT,
                    message TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            # FTS5 table for lightning-fast full-text search
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS interactions_fts 
                USING fts5(message, content='interactions', content_rowid='id')
            ''')
            
            # Triggers to keep FTS table in sync automatically
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS interactions_ai AFTER INSERT ON interactions BEGIN
                    INSERT INTO interactions_fts(rowid, message) VALUES (new.id, new.message);
                END;
            ''')
            
            # Index for fast session isolation
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON interactions(session_id)')
            
            # Table for Webhook Subscriptions (The Event Gateway)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS webhooks (
                    session_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    callback_url TEXT NOT NULL,
                    PRIMARY KEY (session_id, agent_id)
                )
            ''')
            conn.commit()

    def insert(self, session_id: str, agent_id: str, action: str, message: str) -> int:
        """Inserts a new chat message/interaction."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions (session_id, agent_id, action, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, agent_id, action, message, time.time()))
            conn.commit()
            return cursor.lastrowid

    def get_session(self, session_id: str) -> list:
        """Retrieves all interactions for a specific project/session in chronological order."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM interactions WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def search(self, query: str) -> list:
        """Performs a full-text search across all interactions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT interactions.* FROM interactions 
                JOIN interactions_fts ON interactions.id = interactions_fts.rowid 
                WHERE interactions_fts MATCH ? 
                ORDER BY rank
            ''', (query,))
            return [dict(row) for row in cursor.fetchall()]
            
    def register_webhook(self, session_id: str, agent_id: str, callback_url: str):
        """Registers a callback URL for an agent to receive push events."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO webhooks (session_id, agent_id, callback_url)
                VALUES (?, ?, ?)
            ''', (session_id, agent_id, callback_url))
            conn.commit()

    def get_webhooks(self) -> list:
        """Retrieves all registered webhooks."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM webhooks')
            return [dict(row) for row in cursor.fetchall()]

# Global instance for skills to use
db = ChatMemoryDB()
