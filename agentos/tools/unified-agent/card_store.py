"""
card_store.py — SQLite-backed persistence layer for AgentCards.

Design decisions:
  - Single SQLite file at CARD_STORE_PATH (env-overridable).
  - JSON-serialised AgentCard blobs in one table — no ORM overhead.
  - Thread-safe via SQLite WAL mode + check_same_thread=False with a module-level lock.
  - A hard-coded SYSTEM_AGENT_ID constant is the fallback card always present.
  - All public functions raise CardStoreError on failure — callers handle gracefully.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from models import AgentCard

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CARD_STORE_PATH: Path = Path(
    os.environ.get("SAAS_AGENT_CARD_STORE", str(Path.home() / ".saas_agent" / "cards.db"))
)

SYSTEM_AGENT_ID: str = "00000000-0000-0000-0000-000000000001"

SYSTEM_AGENT_CARD = AgentCard(
    id=SYSTEM_AGENT_ID,
    name="System Agent",
    description="Default general-purpose agent. Can create and manage other AgentCards.",
    system_prompt=(
        "You are a powerful local system agent running on a ROOTED Android device (Nothing Phone 2a) "
        "inside Termux. You have full root access via `su`. You have access to shell execution, "
        "file I/O, clipboard, and HTTP tools.\n\n"

        "## Device Context\n"
        "- OS: Android (rooted, Magisk), shell: bash inside Termux\n"
        "- Root: always available via `su -c '<cmd>'` — set require_root=true for any system-level command\n"
        "- Android settings API: `settings put system <key> <value>` (requires root)\n"
        "- Android brightness range: 0–255 (integer). Convert user percentages: value = round(pct * 255 / 100)\n"
        "- Auto-brightness toggle: `settings put system screen_brightness_mode 0` = manual, 1 = auto\n\n"

        "## System Command Reference (always use require_root=true for these)\n"
        "| Task                        | Command                                                        |\n"
        "|-----------------------------|----------------------------------------------------------------|\n"
        "| Set brightness to N (0-255) | settings put system screen_brightness N                        |\n"
        "| Disable auto-brightness     | settings put system screen_brightness_mode 0                   |\n"
        "| Enable auto-brightness      | settings put system screen_brightness_mode 1                   |\n"
        "| Set volume (media, 0-15)    | media volume --stream 3 --set N                                |\n"
        "| Clear notifications         | service call notification 1                                    |\n"
        "| Get battery level           | dumpsys battery \\| grep level                                  |\n"
        "| List running apps           | dumpsys activity \\| grep -E 'mCurrentFocus'                    |\n"
        "| Toggle WiFi off/on          | svc wifi disable / svc wifi enable                             |\n"
        "| Toggle data off/on          | svc data disable / svc data enable                             |\n"
        "| Reboot device               | reboot                                                         |\n\n"

        "## Execution Rules\n"
        "1. For ANY command that touches Android system settings, hardware, or /system paths: "
        "   ALWAYS set require_root=true in run_shell_command arguments. Never omit this.\n"
        "2. When setting brightness: ALWAYS first disable auto-brightness "
        "   (settings put system screen_brightness_mode 0) as a separate tool call BEFORE "
        "   setting the brightness value. Auto-brightness will override manual values if left on.\n"
        "3. Convert user-friendly values to Android API values before running commands:\n"
        "   - Brightness %  → round(pct * 255 / 100)\n"
        "   - Volume %      → round(pct * 15 / 100)\n"
        "4. When a user describes a recurring task, create a new AgentCard via create_agent_card "
        "   with a precise system prompt for that task domain.\n"
        "5. Always return a clear reply stating what commands were run and what the outcome was.\n"
        "6. Never guess at command syntax — use the reference table above for Android system tasks.\n\n"

        "Respond ONLY with valid JSON matching the AgentResponse schema."
    ),
    tools=[],  # empty = all tools
)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class CardStoreError(Exception):
    """Raised for any card_store operation failure."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    """Return (or create) the module-level SQLite connection."""
    global _conn
    if _conn is None:
        CARD_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(CARD_STORE_PATH), check_same_thread=False)
        _conn.execute("PRAGMA journal_mode=WAL;")
        _conn.execute("PRAGMA foreign_keys=ON;")
        _conn.row_factory = sqlite3.Row
        _init_schema(_conn)
        logger.info("card_store: opened DB at %s", CARD_STORE_PATH)
    return _conn


def _init_schema(conn: sqlite3.Connection) -> None:
    """Create the cards table and task_history table if they don't exist, then seed System Agent."""
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_cards (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                data        TEXT NOT NULL,   -- full JSON-serialised AgentCard
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_history (
                id          TEXT PRIMARY KEY,
                task        TEXT NOT NULL,
                card_name   TEXT NOT NULL,
                status      TEXT NOT NULL,
                data        TEXT NOT NULL,   -- full JSON-serialised TaskExecutionResult
                created_at  TEXT NOT NULL
            );
            """
        )
    # Seed System Agent if absent
    row = conn.execute(
        "SELECT id FROM agent_cards WHERE id = ?", (SYSTEM_AGENT_ID,)
    ).fetchone()
    if row is None:
        _upsert_card(conn, SYSTEM_AGENT_CARD)
        logger.info("card_store: seeded System Agent card.")



def _upsert_card(conn: sqlite3.Connection, card: AgentCard) -> None:
    """Insert or replace a card row."""
    now = datetime.now(timezone.utc).isoformat()
    data = card.model_dump_json()
    with conn:
        conn.execute(
            """
            INSERT INTO agent_cards (id, name, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name       = excluded.name,
                data       = excluded.data,
                updated_at = excluded.updated_at;
            """,
            (card.id, card.name, data, now, now),
        )


def _row_to_card(row: sqlite3.Row) -> AgentCard:
    """Deserialise a DB row back to an AgentCard."""
    return AgentCard.model_validate_json(row["data"])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_card(card_id: str) -> AgentCard | None:
    """
    Retrieve a card by UUID.
    Returns None if not found (caller falls back to System Agent).
    """
    with _lock:
        conn = _get_conn()
        row = conn.execute(
            "SELECT data FROM agent_cards WHERE id = ?", (card_id,)
        ).fetchone()
    if row is None:
        return None
    try:
        return _row_to_card(row)
    except Exception as exc:
        raise CardStoreError(f"Failed to deserialise card {card_id}: {exc}") from exc


def get_system_agent() -> AgentCard:
    """Always returns the System Agent card (creates it if missing)."""
    card = get_card(SYSTEM_AGENT_ID)
    if card is None:
        # Defensive: re-seed if somehow deleted
        save_card(SYSTEM_AGENT_CARD)
        return SYSTEM_AGENT_CARD
    return card


def save_card(card: AgentCard) -> AgentCard:
    """
    Persist a new or updated AgentCard.
    Touches updated_at before writing.
    Returns the saved card.
    """
    card.touch()
    with _lock:
        conn = _get_conn()
        try:
            _upsert_card(conn, card)
        except sqlite3.Error as exc:
            raise CardStoreError(f"Failed to save card '{card.name}': {exc}") from exc
    logger.info("card_store: saved card id=%s name=%r", card.id, card.name)
    return card


def delete_card(card_id: str) -> bool:
    """
    Delete a card by UUID.
    Returns True if deleted, False if not found.
    Raises CardStoreError if attempting to delete the System Agent.
    """
    if card_id == SYSTEM_AGENT_ID:
        raise CardStoreError("The System Agent card cannot be deleted.")
    with _lock:
        conn = _get_conn()
        try:
            cursor = conn.execute(
                "DELETE FROM agent_cards WHERE id = ?", (card_id,)
            )
            conn.commit()
        except sqlite3.Error as exc:
            raise CardStoreError(f"Failed to delete card {card_id}: {exc}") from exc
    deleted = cursor.rowcount > 0
    if deleted:
        logger.info("card_store: deleted card id=%s", card_id)
    return deleted


def list_cards() -> list[dict]:
    """
    Return a lightweight summary list of all cards:
    [{"id": ..., "name": ..., "description": ..., "created_at": ...}, ...]
    """
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT data FROM agent_cards ORDER BY created_at ASC"
        ).fetchall()
    result = []
    for row in rows:
        try:
            card = _row_to_card(row)
            result.append(
                {
                    "id": card.id,
                    "name": card.name,
                    "description": card.description,
                    "tools": card.tools,
                    "created_at": card.created_at.isoformat(),
                }
            )
        except Exception as exc:
            logger.warning("card_store: skipping corrupt row — %s", exc)
    return result


def resolve_card(card_id: str | None) -> AgentCard:
    """
    Resolve a card_id to an AgentCard, falling back to the System Agent.
    This is the single entry point used by main.py.
    """
    if card_id is None:
        return get_system_agent()
    card = get_card(card_id)
    if card is None:
        logger.warning(
            "card_store: card_id=%s not found, falling back to System Agent.", card_id
        )
        return get_system_agent()
    return card


# ---------------------------------------------------------------------------
# Task Execution History API
# ---------------------------------------------------------------------------


def save_task_history(result_data: dict) -> None:
    """
    Persist a task execution summary to SQLite.
    """
    task_id = result_data.get("task_id", "")
    task = result_data.get("task", "")
    card_name = result_data.get("card_name", "System Agent")
    status = result_data.get("status", "completed")
    created_at = result_data.get("created_at", datetime.now(timezone.utc).isoformat())
    raw_json = json.dumps(result_data)

    with _lock:
        conn = _get_conn()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO task_history (id, task, card_name, status, data, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        status = excluded.status,
                        data   = excluded.data;
                    """,
                    (task_id, task, card_name, status, raw_json, created_at),
                )
            logger.info("card_store: saved task execution history id=%s", task_id)
        except sqlite3.Error as exc:
            logger.error("card_store: failed to save task history — %s", exc)


def get_task_history(limit: int = 20) -> list[dict]:
    """
    Return recent task execution summaries ordered by latest first.
    """
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            """
            SELECT data FROM task_history
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    history = []
    for row in rows:
        try:
            record = json.loads(row["data"])
            history.append(record)
        except Exception as exc:
            logger.warning("card_store: skipping corrupt task history row — %s", exc)
    return history


def get_total_tasks_count() -> int:
    """Return total number of executed tasks recorded in history."""
    with _lock:
        conn = _get_conn()
        row = conn.execute("SELECT COUNT(*) AS cnt FROM task_history").fetchone()
        return row["cnt"] if row else 0


def close() -> None:
    """Close the DB connection (call on app shutdown)."""
    global _conn
    with _lock:
        if _conn is not None:
            _conn.close()
            _conn = None
            logger.info("card_store: connection closed.")

