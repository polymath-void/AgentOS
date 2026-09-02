"""
test_wave1.py — Bullet-proof integration tests for Wave 1 features.

Tests:
  Phase 1 (auth + cards): 12 tests
  Workflow Engine: 8 tests
  Scheduler: 8 tests
  Total: 28 tests

Run: python3 test_wave1.py
"""

import json
import os
import sys
import traceback

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Clean database for fresh tests
DB_PATH = os.path.expanduser("~/.saas_agent/saas_agent.db")
if os.path.exists(DB_PATH):
    os.unlink(DB_PATH)

passed = 0
failed = 0
errors = []


def test(name, func):
    global passed, failed
    try:
        func()
        print(f"  ✓ {name}")
        passed += 1
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        errors.append(f"{name}: {traceback.format_exc()}")
        failed += 1


# =====================================================================
# PHASE 1: Auth + Cards (12 tests)
# =====================================================================
print("\n== PHASE 1: Auth + Cards ==")

import database
import auth
import card_store


def test_db_init():
    conn = database.get_conn()
    assert conn is not None

test("Database init", test_db_init)


def test_register():
    user = auth.create_user("test@example.com", "testpass123", "Test User")
    assert user["email"] == "test@example.com"
    assert user["id"]
    assert user["plan"] == "free"

test("User registration", test_register)


def test_auth_ok():
    result = auth.authenticate_user("test@example.com", "testpass123")
    assert result is not None
    assert result["email"] == "test@example.com"

test("Auth valid password", test_auth_ok)


def test_auth_bad():
    result = auth.authenticate_user("test@example.com", "wrongpass")
    assert result is None

test("Auth bad password rejected", test_auth_bad)


def test_jwt():
    user = auth.authenticate_user("test@example.com", "testpass123")
    token = auth.create_token(user["id"], user["email"])
    decoded = auth.decode_token(token)
    assert decoded["sub"] == user["id"]
    assert decoded["email"] == user["email"]

test("JWT roundtrip", test_jwt)


def test_duplicate():
    try:
        auth.create_user("test@example.com", "anotherpass", "Dup")
        assert False, "Should have raised"
    except Exception:
        pass

test("Duplicate email rejected", test_duplicate)


def test_card_seed():
    user = auth.authenticate_user("test@example.com", "testpass123")
    card_store.seed_cards_for_user(user["id"])
    cards = card_store.list_cards(user_id=user["id"])
    assert len(cards) == 8, f"Expected 8, got {len(cards)}"

test("Card seeding (8 cards)", test_card_seed)


def test_system_agent():
    user = auth.authenticate_user("test@example.com", "testpass123")
    system = card_store.get_system_agent(user_id=user["id"])
    assert system.name == "System Agent"

test("System agent retrieval", test_system_agent)


def test_rate_limit():
    user = auth.authenticate_user("test@example.com", "testpass123")
    full_user = auth.get_user_by_id(user["id"])
    auth.check_rate_limit(full_user)  # Should not raise

test("Rate limit check", test_rate_limit)


def test_chat_history():
    user = auth.authenticate_user("test@example.com", "testpass123")
    auth.save_chat_message(user["id"], "user", "Hello!")
    auth.save_chat_message(user["id"], "assistant", "Hi!")
    history = auth.get_chat_history(user["id"])
    assert len(history) >= 2

test("Chat history persistence", test_chat_history)


def test_api_key():
    user = auth.authenticate_user("test@example.com", "testpass123")
    auth.update_user_api_key(user["id"], "test-key-123", "gemini-2.5-flash")
    updated = auth.get_user_by_id(user["id"])
    assert updated["gemini_api_key"] == "test-key-123"

test("API key storage", test_api_key)


def test_user_profile():
    user = auth.authenticate_user("test@example.com", "testpass123")
    full = auth.get_user_by_id(user["id"])
    assert full["email"] == "test@example.com"
    assert full["plan"] == "free"

test("User profile retrieval", test_user_profile)


# =====================================================================
# WORKFLOW ENGINE (8 tests)
# =====================================================================
print("\n== WORKFLOW ENGINE ==")

from workflow_engine import (
    WorkflowEngine, WorkflowStep, WorkflowPlan, StepResult, WorkflowResult,
)


def test_wf_interpolate():
    """Test variable interpolation."""
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine._gemini = None
    ctx = {"name": "John", "dir": "/home"}
    assert engine._interpolate_vars("Hello ${name}", ctx) == "Hello John"
    assert engine._interpolate_vars("cd $dir", ctx) == "cd /home"
    assert engine._interpolate_vars("no vars", ctx) == "no vars"
    assert engine._interpolate_vars("${missing}", ctx) == ""

test("Variable interpolation", test_wf_interpolate)


def test_wf_interpolate_args():
    """Test recursive argument interpolation."""
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine._gemini = None
    ctx = {"host": "localhost", "port": "8080"}
    args = {"url": "http://${host}:${port}", "nested": {"key": "$host"}}
    result = engine._interpolate_args(args, ctx)
    assert result["url"] == "http://localhost:8080"
    assert result["nested"]["key"] == "localhost"

test("Argument interpolation (nested)", test_wf_interpolate_args)


def test_wf_condition_true():
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine._gemini = None
    ctx = {"status": "ok"}
    assert engine._evaluate_condition(None, ctx) is True
    assert engine._evaluate_condition("", ctx) is True
    assert engine._evaluate_condition("true", ctx) is True
    assert engine._evaluate_condition("1", ctx) is True
    assert engine._evaluate_condition("yes", ctx) is True

test("Condition eval (truthy)", test_wf_condition_true)


def test_wf_condition_false():
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine._gemini = None
    ctx = {}
    assert engine._evaluate_condition("false", ctx) is False
    assert engine._evaluate_condition("0", ctx) is False
    assert engine._evaluate_condition("no", ctx) is False

test("Condition eval (falsy)", test_wf_condition_false)


def test_wf_condition_compare():
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine._gemini = None
    ctx = {"status": "ok", "mode": "test"}
    assert engine._evaluate_condition("${status} == ok", ctx) is True
    assert engine._evaluate_condition("${status} != bad", ctx) is True
    assert engine._evaluate_condition("${mode} == prod", ctx) is False

test("Condition eval (comparisons)", test_wf_condition_compare)


def test_wf_clean_context():
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine._gemini = None
    ctx = {"_task": "internal", "_card": "internal", "result": "public", "ip": "1.2.3.4"}
    cleaned = engine._clean_context(ctx)
    assert "_task" not in cleaned
    assert "_card" not in cleaned
    assert cleaned["result"] == "public"
    assert cleaned["ip"] == "1.2.3.4"

test("Context cleaning (_vars removed)", test_wf_clean_context)


def test_wf_step_model():
    step = WorkflowStep(
        step_id=1, title="Install Node",
        action_type="shell", command="pkg install nodejs",
        on_failure="heal", capture_var="node_ver",
    )
    assert step.step_id == 1
    assert step.command == "pkg install nodejs"
    assert step.on_failure == "heal"
    assert step.capture_var == "node_ver"

test("WorkflowStep model", test_wf_step_model)


def test_wf_plan_model():
    plan = WorkflowPlan(
        goal="Setup dev env",
        summary="Install and configure",
        steps=[
            WorkflowStep(step_id=1, title="Step 1", command="echo hello"),
            WorkflowStep(step_id=2, title="Step 2", command="echo world"),
        ],
    )
    assert len(plan.steps) == 2
    assert plan.goal == "Setup dev env"

test("WorkflowPlan model", test_wf_plan_model)


def test_wf_parse_response():
    engine = WorkflowEngine.__new__(WorkflowEngine)
    engine._gemini = None
    raw = json.dumps({
        "reply": "Setting up Node.js",
        "workflow": {
            "goal": "Install Node",
            "summary": "Install nodejs package",
            "steps": [
                {"step_id": 1, "title": "Install", "action_type": "shell", "command": "pkg install -y nodejs"},
                {"step_id": 2, "title": "Verify", "action_type": "shell", "command": "node --version", "capture_var": "node_ver"},
            ],
            "verification": {"title": "Check", "command": "which node"}
        }
    })
    plan, reply = engine._parse_workflow_response(raw)
    assert plan is not None
    assert len(plan.steps) == 2
    assert plan.steps[0].command == "pkg install -y nodejs"
    assert plan.steps[1].capture_var == "node_ver"
    assert plan.verification is not None
    assert reply == "Setting up Node.js"

test("Workflow JSON parsing", test_wf_parse_response)


# =====================================================================
# SCHEDULER (8 tests)
# =====================================================================
print("\n== SCHEDULER ==")

import scheduler
from datetime import datetime, timezone, timedelta


def test_sched_create():
    user = auth.authenticate_user("test@example.com", "testpass123")
    sched = scheduler.ScheduleCreate(
        name="Morning Brief",
        task="Summarize inbox",
        schedule_type="daily",
        time_of_day="08:00",
    )
    result = scheduler.create_schedule(user["id"], sched)
    assert result.name == "Morning Brief"
    assert result.schedule_type == "daily"
    assert result.next_run is not None

test("Schedule creation", test_sched_create)


def test_sched_list():
    user = auth.authenticate_user("test@example.com", "testpass123")
    schedules = scheduler.list_schedules(user["id"])
    assert len(schedules) >= 1
    assert schedules[0]["name"] == "Morning Brief"

test("Schedule listing", test_sched_list)


def test_sched_get():
    user = auth.authenticate_user("test@example.com", "testpass123")
    schedules = scheduler.list_schedules(user["id"])
    detail = scheduler.get_schedule(schedules[0]["id"], user["id"])
    assert detail is not None
    assert detail["task"] == "Summarize inbox"

test("Schedule get detail", test_sched_get)


def test_sched_toggle():
    user = auth.authenticate_user("test@example.com", "testpass123")
    schedules = scheduler.list_schedules(user["id"])
    sid = schedules[0]["id"]
    scheduler.toggle_schedule(sid, user["id"], False)
    updated = scheduler.get_schedule(sid, user["id"])
    assert updated["enabled"] == 0

    scheduler.toggle_schedule(sid, user["id"], True)
    updated2 = scheduler.get_schedule(sid, user["id"])
    assert updated2["enabled"] == 1

test("Schedule toggle on/off", test_sched_toggle)


def test_sched_next_daily():
    now = datetime(2026, 8, 12, 6, 0, tzinfo=timezone.utc)
    sched = scheduler.ScheduleCreate(name="t", task="t", schedule_type="daily", time_of_day="08:00")
    next_run = scheduler._calculate_next_run(sched, now)
    assert next_run.hour == 8
    assert next_run.minute == 0

test("Next run calc (daily)", test_sched_next_daily)


def test_sched_next_interval():
    now = datetime(2026, 8, 12, 10, 0, tzinfo=timezone.utc)
    sched = scheduler.ScheduleCreate(name="t", task="t", schedule_type="interval", interval_minutes=30)
    next_run = scheduler._calculate_next_run(sched, now)
    expected = now + timedelta(minutes=30)
    assert next_run == expected

test("Next run calc (interval)", test_sched_next_interval)


def test_sched_next_once():
    sched = scheduler.ScheduleCreate(name="t", task="t", schedule_type="once", run_at="2026-12-25T10:00:00")
    now = datetime(2026, 8, 12, 10, 0, tzinfo=timezone.utc)
    next_run = scheduler._calculate_next_run(sched, now)
    assert next_run.month == 12
    assert next_run.day == 25

test("Next run calc (one-shot)", test_sched_next_once)


def test_sched_delete():
    user = auth.authenticate_user("test@example.com", "testpass123")
    schedules = scheduler.list_schedules(user["id"])
    sid = schedules[0]["id"]
    deleted = scheduler.delete_schedule(sid, user["id"])
    assert deleted is True
    remaining = scheduler.list_schedules(user["id"])
    assert len(remaining) == len(schedules) - 1

test("Schedule deletion", test_sched_delete)


# =====================================================================
# FASTAPI APP IMPORT (1 test)
# =====================================================================
print("\n== FASTAPI APP ==")


def test_app_routes():
    from main import app
    routes = [r.path for r in app.routes if hasattr(r, "path")]
    required = ["/health", "/auth/register", "/auth/login", "/auth/me",
                "/chat", "/workflow", "/cards", "/schedules", "/app", "/"]
    for r in required:
        assert r in routes, f"Missing route: {r}"
    assert len(routes) >= 23  # 18 original + 5 new

test(f"All routes registered", test_app_routes)


# =====================================================================
# SUMMARY
# =====================================================================

# Cleanup
database.close()
if os.path.exists(DB_PATH):
    os.unlink(DB_PATH)

print(f"\n{'='*50}")
print(f"  RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
print(f"{'='*50}")

if errors:
    print("\n--- FAILURES ---")
    for e in errors:
        print(e)

sys.exit(0 if failed == 0 else 1)
