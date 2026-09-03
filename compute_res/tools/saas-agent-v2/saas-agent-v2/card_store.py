"""
card_store.py — Multi-tenant card persistence for SaaS-Agent v2.

Architecture:
  - Pre-seeded system cards are TEMPLATES (not stored per-user)
  - On first login, each user gets their own copy of system cards in user_cards table
  - User-created cards are private to that user
  - All operations are scoped to user_id
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

import database
from models import AgentCard

logger = logging.getLogger(__name__)

SYSTEM_AGENT_ID = "00000000-0000-0000-0000-000000000001"


class CardStoreError(Exception):
    """Card store operation error."""


# ---------------------------------------------------------------------------
# Pre-seeded domain card TEMPLATES
# ---------------------------------------------------------------------------

SYSTEM_AGENT_CARD = AgentCard(
    id=SYSTEM_AGENT_ID,
    name="System Agent",
    description="Default general-purpose agent. Routes tasks to specialized cards.",
    system_prompt=(
        "You are SystemOS Agent, a deterministic execution-based personal assistant on rooted Android/Linux.\n"
        "You have access to:\n"
        "  - Root shell (Magisk/su) for system-level control\n"
        "  - ADB for Android remote commands\n"
        "  - Cloud APIs (YouTube, Gmail, Calendar)\n"
        "  - Local tools (mpv, yt-dlp, gcalcli, jrnl)\n\n"
        "Your job:\n"
        "1. Classify the user's intent\n"
        "2. Route to the appropriate specialized card (Media Control, Call Manager, etc.)\n"
        "3. If no clear match, execute directly using available tools\n"
        "4. Always return structured JSON with [INTENT], [PLAN], [EXECUTION], [RESULT] blocks.\n\n"
        "Execution hierarchy:\n"
        "  Tier 1: Root (su) - system settings, calls, notifications\n"
        "  Tier 2: ADB - Android remote control\n"
        "  Tier 3: Local tools - mpv, gcalcli, jrnl\n"
        "  Tier 4: Cloud APIs - YouTube, Gmail, Calendar\n"
        "Never modify /system, /proc, /dev - use overlays in /data/local or ~/.config."
    ),
    tools=[],
    execution_mode="function_calling",
    scope_tags=["system", "router"],
    is_system_card=True,
)

PRESEEDED_CARDS = [
    SYSTEM_AGENT_CARD,
    AgentCard(
        id="10000000-0000-0000-0000-000000000001",
        name="Media Control",
        description="Play YouTube videos, music, streams.",
        system_prompt=(
            "You are a media specialist. Your only job: play music/videos.\n"
            "When user says 'play [query]', use play_youtube tool with that query.\n"
            "Always confirm what you're playing in the reply."
        ),
        tools=["play_youtube", "get_system_info"],
        execution_mode="function_calling",
        scope_tags=["media", "youtube", "music", "video"],
        is_system_card=True,
    ),
    AgentCard(
        id="10000000-0000-0000-0000-000000000002",
        name="Call Manager",
        description="Make calls, check call logs, retrieve missed calls.",
        system_prompt=(
            "You are a call management specialist.\n"
            "Tasks: place calls, fetch call logs, filter by type (MISSED, INCOMING, OUTGOING).\n"
            "Use place_call and get_call_logs tools. Always confirm action before executing."
        ),
        tools=["place_call", "get_call_logs"],
        execution_mode="function_calling",
        scope_tags=["calls", "phone", "contact"],
        is_system_card=True,
    ),
    AgentCard(
        id="10000000-0000-0000-0000-000000000003",
        name="File Manager",
        description="List, read, write, search, copy, sync files.",
        system_prompt=(
            "You are a file management specialist.\n"
            "Manage local files: list, read, write, search, copy, delete.\n"
            "Sync to cloud (S3, Google Drive) via rclone.\n"
            "Always confirm destructive operations (delete, overwrite)."
        ),
        tools=[
            "list_files", "read_file", "write_file", "search_files",
            "delete_file", "copy_file", "sync_cloud",
        ],
        execution_mode="function_calling",
        scope_tags=["files", "directory", "search", "sync"],
        is_system_card=True,
    ),
    AgentCard(
        id="10000000-0000-0000-0000-000000000004",
        name="Email Assistant",
        description="Check emails, summarize inbox, send emails.",
        system_prompt=(
            "You are an email specialist. Fetch, summarize, and send emails.\n"
            "Use get_emails, summarize_emails, send_email.\n"
            "Always respect privacy: summarize only, never expose full bodies unless asked.\n"
            "When summarizing, return 5-10 bullet points per email."
        ),
        tools=["get_emails", "summarize_emails", "send_email"],
        execution_mode="summarization",
        scope_tags=["email", "inbox", "mail"],
        is_system_card=True,
    ),
    AgentCard(
        id="10000000-0000-0000-0000-000000000005",
        name="Calendar Assistant",
        description="Check calendar, add events, schedule meetings.",
        system_prompt=(
            "You are a calendar specialist.\n"
            "Retrieve upcoming events, add new events, schedule meetings.\n"
            "When user says 'schedule meeting on [date] at [time]', use add_calendar_event.\n"
            "Always confirm event details before adding."
        ),
        tools=["get_calendar_events", "add_calendar_event"],
        execution_mode="function_calling",
        scope_tags=["calendar", "meeting", "event", "schedule"],
        is_system_card=True,
    ),
    AgentCard(
        id="10000000-0000-0000-0000-000000000006",
        name="Notes Manager",
        description="Write and read timestamped notes.",
        system_prompt=(
            "You are a note-taking specialist.\n"
            "Write notes with timestamps and tags. Read recent notes.\n"
            "When user says 'remember [text]' or 'write note', use write_note.\n"
            "Default tags: auto-extract from note text if relevant."
        ),
        tools=["write_note", "read_notes"],
        execution_mode="function_calling",
        scope_tags=["notes", "journal", "remember"],
        is_system_card=True,
    ),
    AgentCard(
        id="10000000-0000-0000-0000-000000000007",
        name="System Control",
        description="Brightness, WiFi, notifications, system monitoring.",
        system_prompt=(
            "You are a system control specialist.\n"
            "Control: brightness (0-100%), WiFi toggle, clear notifications.\n"
            "Monitor: battery, uptime, disk, memory.\n"
            "When user says 'set brightness to X%', use set_brightness.\n"
            "Always disable auto-brightness before setting manual brightness."
        ),
        tools=[
            "set_brightness", "toggle_wifi", "clear_notifications",
            "get_system_info", "run_shell_command",
        ],
        execution_mode="function_calling",
        scope_tags=["system", "control", "brightness", "wifi", "battery"],
        is_system_card=True,
    ),
]


# ---------------------------------------------------------------------------
# Multi-tenant card operations
# ---------------------------------------------------------------------------


def seed_cards_for_user(user_id: str) -> None:
    """Copy all pre-seeded card templates into user_cards for a new user."""
    conn = database.get_conn()
    lock = database.get_lock()

    with lock:
        # Check if user already has cards
        count = conn.execute(
            "SELECT COUNT(*) as cnt FROM user_cards WHERE user_id = ?", (user_id,)
        ).fetchone()["cnt"]

        if count > 0:
            return  # Already seeded

        now = datetime.now(timezone.utc).isoformat()
        for card in PRESEEDED_CARDS:
            # Give each user their own copy with a unique ID
            user_card_id = str(uuid.uuid4())
            card_copy = card.model_copy(update={"id": user_card_id})
            conn.execute(
                """INSERT INTO user_cards (id, user_id, card_data, is_system_card, created_at, updated_at)
                   VALUES (?, ?, ?, 1, ?, ?)""",
                (user_card_id, user_id, card_copy.model_dump_json(), now, now),
            )
        conn.commit()
    logger.info(f"card_store: seeded {len(PRESEEDED_CARDS)} cards for user {user_id}")


def get_card(card_id: str, user_id: str | None = None) -> AgentCard | None:
    """Get a card by ID, scoped to user."""
    conn = database.get_conn()

    if user_id:
        row = conn.execute(
            "SELECT card_data FROM user_cards WHERE id = ? AND user_id = ?",
            (card_id, user_id),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT card_data FROM user_cards WHERE id = ?", (card_id,)
        ).fetchone()

    if row:
        return AgentCard.model_validate_json(row["card_data"])
    return None


def get_system_agent(user_id: str | None = None) -> AgentCard:
    """Get the System Agent card for a user (or the template if no user)."""
    if user_id:
        conn = database.get_conn()
        row = conn.execute(
            """SELECT card_data FROM user_cards
               WHERE user_id = ? AND is_system_card = 1
               ORDER BY created_at ASC LIMIT 1""",
            (user_id,),
        ).fetchone()
        if row:
            return AgentCard.model_validate_json(row["card_data"])

    return SYSTEM_AGENT_CARD


def get_all_cards_for_user(user_id: str) -> list[AgentCard]:
    """Get all cards for a user as AgentCard objects."""
    conn = database.get_conn()
    rows = conn.execute(
        "SELECT card_data FROM user_cards WHERE user_id = ? ORDER BY created_at ASC",
        (user_id,),
    ).fetchall()

    cards = []
    for row in rows:
        try:
            cards.append(AgentCard.model_validate_json(row["card_data"]))
        except Exception as e:
            logger.warning(f"card_store: skipped corrupt card: {e}")
    return cards


def save_card(card: AgentCard, user_id: str | None = None) -> AgentCard:
    """Save a card (create or update) scoped to a user."""
    if not user_id:
        raise CardStoreError("user_id is required for saving cards.")

    card.touch()
    conn = database.get_conn()
    lock = database.get_lock()
    now = datetime.now(timezone.utc).isoformat()

    with lock:
        conn.execute(
            """INSERT INTO user_cards (id, user_id, card_data, is_system_card, created_at, updated_at)
               VALUES (?, ?, ?, 0, ?, ?)
               ON CONFLICT(id) DO UPDATE SET card_data=excluded.card_data, updated_at=excluded.updated_at""",
            (card.id, user_id, card.model_dump_json(), now, now),
        )
        conn.commit()
    logger.info(f"card_store: saved card '{card.name}' ({card.id}) for user {user_id}")
    return card


def delete_card(card_id: str, user_id: str | None = None) -> bool:
    """Delete a user-created card. Cannot delete system cards."""
    conn = database.get_conn()
    lock = database.get_lock()

    # Check if it's a system card
    row = conn.execute(
        "SELECT is_system_card FROM user_cards WHERE id = ?", (card_id,)
    ).fetchone()
    if row and row["is_system_card"]:
        raise CardStoreError("Cannot delete system cards.")

    with lock:
        if user_id:
            cursor = conn.execute(
                "DELETE FROM user_cards WHERE id = ? AND user_id = ?",
                (card_id, user_id),
            )
        else:
            cursor = conn.execute("DELETE FROM user_cards WHERE id = ?", (card_id,))
        conn.commit()
    return cursor.rowcount > 0


def list_cards(user_id: str | None = None) -> list[dict]:
    """List cards as summary dicts, scoped to user."""
    conn = database.get_conn()

    if user_id:
        rows = conn.execute(
            "SELECT card_data, is_system_card FROM user_cards WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT card_data, is_system_card FROM user_cards ORDER BY created_at ASC"
        ).fetchall()

    result = []
    for row in rows:
        try:
            card = AgentCard.model_validate_json(row["card_data"])
            result.append({
                "id": card.id,
                "name": card.name,
                "description": card.description,
                "scope_tags": card.scope_tags,
                "is_system": bool(row["is_system_card"]),
            })
        except Exception as e:
            logger.warning(f"card_store: skipped corrupt row: {e}")
    return result


def resolve_card(card_id: str | None, user_id: str | None = None) -> AgentCard:
    """Resolve a card ID to an AgentCard, with fallback to System Agent."""
    if card_id is None:
        return get_system_agent(user_id=user_id)

    card = get_card(card_id, user_id=user_id)
    if card is None:
        logger.warning(f"card_store: {card_id} not found, fallback to System Agent")
        return get_system_agent(user_id=user_id)
    return card


def close() -> None:
    """Close the database (delegates to database.py now)."""
    database.close()
