"""
database.py — Multi-tenant SQLite database for SaaS-Agent v2.

Tables:
  - users: User accounts with server-side API key storage
  - user_cards: Cards scoped to individual users
  - chat_history: Per-user conversation persistence

Design:
  - WAL mode for concurrent reads
  - Foreign keys enforced
  - Thread-safe with lock
"""

from __future__ import annotations

import logging
import os
import sqlite3
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(
    os.environ.get("SAAS_AGENT_DB", str(Path.home() / ".saas_agent" / "saas_agent.db"))
)

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    """Get or create the database connection (singleton)."""
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _conn.execute("PRAGMA journal_mode=WAL;")
        _conn.execute("PRAGMA foreign_keys=ON;")
        _conn.row_factory = sqlite3.Row
        _init_schema(_conn)
        logger.info(f"database: opened at {DB_PATH}")
    return _conn


def get_lock() -> threading.Lock:
    """Expose the lock for external callers that need atomic operations."""
    return _lock


def _init_schema(conn: sqlite3.Connection) -> None:
    """Create tables if they don't exist."""
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                display_name TEXT DEFAULT '',
                gemini_api_key TEXT DEFAULT '',
                preferred_model TEXT DEFAULT 'gemini-2.5-flash',
                plan TEXT DEFAULT 'free' CHECK(plan IN ('free', 'pro', 'enterprise')),
                messages_today INTEGER DEFAULT 0,
                messages_reset_date TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_cards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                card_data TEXT NOT NULL,
                is_system_card INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT DEFAULT 'default',
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                card_id TEXT,
                model_used TEXT DEFAULT '',
                tool_results TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_user_cards_user ON user_cards(user_id);
            CREATE INDEX IF NOT EXISTS idx_chat_user_session ON chat_history(user_id, session_id);
        """)
    logger.info("database: schema initialized")


def close() -> None:
    """Close the database connection."""
    global _conn
    with _lock:
        if _conn:
            _conn.close()
            _conn = None
            logger.info("database: closed")
