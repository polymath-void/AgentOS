"""
scheduler.py — Scheduled Autopilot for SaaS-Agent v2.

Allows users to create recurring or one-shot scheduled tasks.
Each schedule triggers a workflow execution at the specified time.

Features:
  - Cron-style scheduling (every minute, hourly, daily, weekly)
  - One-shot timers (run once at a specific time)
  - Per-user schedules stored in SQLite
  - Background thread executes due schedules
  - Thread-safe with proper locking

Examples:
  - "Every morning at 8am: summarize my inbox and check calendar"
  - "Every Friday at 5pm: generate weekly report"
  - "In 30 minutes: remind me to take a break"
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from pydantic import BaseModel, Field

import database

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schedule Models
# ---------------------------------------------------------------------------


class ScheduleCreate(BaseModel):
    """Request to create a new schedule."""
    name: str = Field(..., min_length=1, max_length=128)
    task: str = Field(..., min_length=1, max_length=4096, description="The task/prompt to execute")
    card_id: str | None = Field(default=None, description="Optional card ID to use")
    schedule_type: str = Field(
        default="daily",
        description="'once' | 'hourly' | 'daily' | 'weekly' | 'interval'"
    )
    # For 'once': specific ISO datetime
    run_at: str | None = Field(default=None, description="ISO datetime for one-shot (e.g. '2026-08-13T08:00:00')")
    # For recurring: time of day
    time_of_day: str | None = Field(default=None, description="HH:MM for daily/weekly (e.g. '08:00')")
    # For 'weekly': day of week (0=Mon, 6=Sun)
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    # For 'interval': minutes between runs
    interval_minutes: int | None = Field(default=None, ge=1, le=10080)
    enabled: bool = Field(default=True)


class ScheduleInfo(BaseModel):
    """Schedule information returned to the user."""
    id: str
    user_id: str
    name: str
    task: str
    card_id: str | None
    schedule_type: str
    run_at: str | None
    time_of_day: str | None
    day_of_week: int | None
    interval_minutes: int | None
    enabled: bool
    last_run: str | None
    next_run: str | None
    run_count: int
    created_at: str


# ---------------------------------------------------------------------------
# Schedule Database Operations
# ---------------------------------------------------------------------------


def _init_schedule_table() -> None:
    """Create schedules table if it doesn't exist."""
    conn = database.get_conn()
    lock = database.get_lock()
    with lock:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                task TEXT NOT NULL,
                card_id TEXT,
                schedule_type TEXT NOT NULL DEFAULT 'daily',
                run_at TEXT,
                time_of_day TEXT,
                day_of_week INTEGER,
                interval_minutes INTEGER,
                enabled INTEGER DEFAULT 1,
                last_run TEXT,
                next_run TEXT,
                run_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_schedules_user ON schedules(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_schedules_next ON schedules(next_run)")
        conn.commit()


def create_schedule(user_id: str, schedule: ScheduleCreate) -> ScheduleInfo:
    """Create a new schedule for a user."""
    _init_schedule_table()
    conn = database.get_conn()
    lock = database.get_lock()

    schedule_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    # Calculate next run time
    next_run = _calculate_next_run(schedule, now)

    with lock:
        conn.execute("""
            INSERT INTO schedules
            (id, user_id, name, task, card_id, schedule_type, run_at, time_of_day,
             day_of_week, interval_minutes, enabled, next_run, run_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            schedule_id, user_id, schedule.name, schedule.task, schedule.card_id,
            schedule.schedule_type, schedule.run_at, schedule.time_of_day,
            schedule.day_of_week, schedule.interval_minutes,
            1 if schedule.enabled else 0,
            next_run.isoformat() if next_run else None,
            now_iso,
        ))
        conn.commit()

    logger.info("scheduler: created '%s' for user %s (next: %s)", schedule.name, user_id, next_run)

    return ScheduleInfo(
        id=schedule_id, user_id=user_id, name=schedule.name,
        task=schedule.task, card_id=schedule.card_id,
        schedule_type=schedule.schedule_type, run_at=schedule.run_at,
        time_of_day=schedule.time_of_day, day_of_week=schedule.day_of_week,
        interval_minutes=schedule.interval_minutes, enabled=schedule.enabled,
        last_run=None, next_run=next_run.isoformat() if next_run else None,
        run_count=0, created_at=now_iso,
    )


def list_schedules(user_id: str) -> list[dict]:
    """List all schedules for a user."""
    _init_schedule_table()
    conn = database.get_conn()
    rows = conn.execute(
        "SELECT * FROM schedules WHERE user_id = ? ORDER BY created_at ASC",
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_schedule(schedule_id: str, user_id: str) -> dict | None:
    """Get a specific schedule."""
    _init_schedule_table()
    conn = database.get_conn()
    row = conn.execute(
        "SELECT * FROM schedules WHERE id = ? AND user_id = ?",
        (schedule_id, user_id),
    ).fetchone()
    return dict(row) if row else None


def delete_schedule(schedule_id: str, user_id: str) -> bool:
    """Delete a schedule."""
    conn = database.get_conn()
    lock = database.get_lock()
    with lock:
        cursor = conn.execute(
            "DELETE FROM schedules WHERE id = ? AND user_id = ?",
            (schedule_id, user_id),
        )
        conn.commit()
    return cursor.rowcount > 0


def toggle_schedule(schedule_id: str, user_id: str, enabled: bool) -> bool:
    """Enable or disable a schedule."""
    conn = database.get_conn()
    lock = database.get_lock()
    with lock:
        cursor = conn.execute(
            "UPDATE schedules SET enabled = ? WHERE id = ? AND user_id = ?",
            (1 if enabled else 0, schedule_id, user_id),
        )
        conn.commit()
    return cursor.rowcount > 0


def get_due_schedules() -> list[dict]:
    """Get all schedules that are due for execution."""
    _init_schedule_table()
    conn = database.get_conn()
    now = datetime.now(timezone.utc).isoformat()
    rows = conn.execute(
        "SELECT * FROM schedules WHERE enabled = 1 AND next_run IS NOT NULL AND next_run <= ?",
        (now,),
    ).fetchall()
    return [dict(r) for r in rows]


def mark_schedule_run(schedule_id: str, schedule_type: str, schedule_data: dict) -> None:
    """Update schedule after execution — set last_run and calculate next_run."""
    conn = database.get_conn()
    lock = database.get_lock()
    now = datetime.now(timezone.utc)

    if schedule_type == "once":
        next_run = None  # One-shot, don't reschedule
    else:
        sched = ScheduleCreate(
            name=schedule_data.get("name", ""),
            task=schedule_data.get("task", ""),
            schedule_type=schedule_type,
            time_of_day=schedule_data.get("time_of_day"),
            day_of_week=schedule_data.get("day_of_week"),
            interval_minutes=schedule_data.get("interval_minutes"),
        )
        next_run = _calculate_next_run(sched, now)

    with lock:
        conn.execute(
            """UPDATE schedules
               SET last_run = ?, next_run = ?, run_count = run_count + 1
               WHERE id = ?""",
            (now.isoformat(), next_run.isoformat() if next_run else None, schedule_id),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Next Run Calculation
# ---------------------------------------------------------------------------


def _calculate_next_run(schedule: ScheduleCreate, from_time: datetime) -> datetime | None:
    """Calculate the next execution time for a schedule."""
    if schedule.schedule_type == "once":
        if schedule.run_at:
            try:
                return datetime.fromisoformat(schedule.run_at).replace(tzinfo=timezone.utc)
            except ValueError:
                return from_time + timedelta(hours=1)
        return from_time + timedelta(hours=1)

    if schedule.schedule_type == "interval":
        mins = schedule.interval_minutes or 60
        return from_time + timedelta(minutes=mins)

    if schedule.schedule_type == "hourly":
        return from_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    if schedule.schedule_type == "daily":
        if schedule.time_of_day:
            try:
                hour, minute = map(int, schedule.time_of_day.split(":"))
                next_run = from_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= from_time:
                    next_run += timedelta(days=1)
                return next_run
            except (ValueError, IndexError):
                pass
        return from_time + timedelta(days=1)

    if schedule.schedule_type == "weekly":
        target_day = schedule.day_of_week or 0
        days_ahead = (target_day - from_time.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7  # Next week
        next_run = from_time + timedelta(days=days_ahead)
        if schedule.time_of_day:
            try:
                hour, minute = map(int, schedule.time_of_day.split(":"))
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except (ValueError, IndexError):
                pass
        return next_run

    return from_time + timedelta(hours=1)


# ---------------------------------------------------------------------------
# Background Scheduler Thread
# ---------------------------------------------------------------------------

_scheduler_thread: threading.Thread | None = None
_scheduler_stop = threading.Event()


def start_scheduler(workflow_engine, gemini_engine) -> None:
    """Start the background scheduler thread."""
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        return

    _scheduler_stop.clear()
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        args=(workflow_engine, gemini_engine),
        daemon=True,
        name="scheduler",
    )
    _scheduler_thread.start()
    logger.info("scheduler: background thread started")


def stop_scheduler() -> None:
    """Stop the background scheduler."""
    _scheduler_stop.set()
    logger.info("scheduler: stopped")


def _scheduler_loop(workflow_engine, gemini_engine) -> None:
    """Main scheduler loop — checks for due schedules every 30 seconds."""
    logger.info("scheduler: loop started, checking every 30s")

    while not _scheduler_stop.is_set():
        try:
            due = get_due_schedules()
            for sched in due:
                logger.info("scheduler: executing '%s' (id: %s)", sched["name"], sched["id"])
                try:
                    _execute_scheduled_task(sched, workflow_engine, gemini_engine)
                except Exception as exc:
                    logger.error("scheduler: failed to execute '%s': %s", sched["name"], exc)

                # Mark as run and calculate next
                mark_schedule_run(sched["id"], sched["schedule_type"], sched)
        except Exception as exc:
            logger.error("scheduler: loop error: %s", exc)

        _scheduler_stop.wait(timeout=30)


def _execute_scheduled_task(sched: dict, workflow_engine, gemini_engine) -> None:
    """Execute a scheduled task using the workflow engine."""
    import auth
    import card_store

    user_id = sched["user_id"]
    user = auth.get_user_by_id(user_id)
    if not user:
        logger.warning("scheduler: user %s not found, skipping", user_id)
        return

    api_key = user.get("gemini_api_key", "")
    if not api_key:
        logger.warning("scheduler: user %s has no API key, skipping", user_id)
        return

    # Resolve card
    card_id = sched.get("card_id")
    card = card_store.resolve_card(card_id, user_id=user_id)

    # Execute as workflow
    result = workflow_engine.execute_workflow(
        task=sched["task"],
        card=card,
        local_context={"device": "scheduled", "schedule_name": sched["name"]},
        user_api_key=api_key,
        user_model=user.get("preferred_model", "gemini-2.5-flash"),
    )

    # Save result to chat history
    auth.save_chat_message(
        user_id=user_id,
        role="assistant",
        content=f"⏰ Scheduled task '{sched['name']}' completed:\n{result.reply}\nStatus: {result.status} ({result.duration_ms}ms)",
        card_id=card.id,
        model_used=user.get("preferred_model", ""),
    )
    logger.info("scheduler: '%s' completed with status: %s", sched["name"], result.status)
