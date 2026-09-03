import sqlite3
import json
from typing import List, Dict, Any, Optional

class SQLiteAdapter:
    """
    SQLite persistent storage adapter for episodic memory.
    """
    
    def __init__(self, db_path: str = "memory.db"):
        """
        Initializes the SQLite database connection and creates the necessary tables.
        
        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Creates the memory table if it does not exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT,
                content TEXT,
                metadata TEXT
            )
        ''')
        self.conn.commit()

    def insert(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Inserts a new memory episode.
        
        Args:
            role (str): The role of the speaker (e.g., 'user', 'assistant').
            content (str): The content of the memory.
            metadata (dict, optional): Additional metadata associated with the memory.
            
        Returns:
            int: The ID of the inserted row.
        """
        cursor = self.conn.cursor()
        metadata_str = json.dumps(metadata) if metadata else None
        cursor.execute(
            'INSERT INTO memory (role, content, metadata) VALUES (?, ?, ?)',
            (role, content, metadata_str)
        )
        self.conn.commit()
        return cursor.lastrowid

    def select(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieves memory episodes ordered by their creation time.
        
        Args:
            limit (int): The maximum number of records to retrieve.
            offset (int): The number of records to skip.
            
        Returns:
            List[Dict[str, Any]]: A list of memory episodes.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, timestamp, role, content, metadata FROM memory ORDER BY id ASC LIMIT ? OFFSET ?',
            (limit, offset)
        )
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            record = dict(row)
            if record.get('metadata'):
                try:
                    record['metadata'] = json.loads(record['metadata'])
                except json.JSONDecodeError:
                    pass
            results.append(record)
            
        return results

    def close(self):
        """Closes the database connection."""
        self.conn.close()
