"""
auth.py — JWT authentication for SaaS-Agent v2.

Features:
  - User registration with email/password
  - JWT token generation and validation (PyJWT)
  - Password hashing with PBKDF2-SHA256 (zero C deps, works on Termux)
  - FastAPI dependency injection for protected routes
  - Server-side API key management per user
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

import database

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "72"))

# Plan limits
PLAN_LIMITS = {
    "free": {"messages_per_day": 50, "max_cards": 5},
    "pro": {"messages_per_day": 10000, "max_cards": 100},
    "enterprise": {"messages_per_day": 100000, "max_cards": 1000},
}

security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """User registration request."""
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(default="", max_length=64)


class LoginRequest(BaseModel):
    """User login request."""
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=1)


class ApiKeyUpdate(BaseModel):
    """Update user's Gemini API key."""
    api_key: str = Field(..., min_length=1, max_length=512)
    model: str = Field(default="gemini-2.5-flash", max_length=64)


class UserProfile(BaseModel):
    """Public user profile (no secrets)."""
    id: str
    email: str
    display_name: str
    plan: str
    has_api_key: bool
    preferred_model: str
    created_at: str


class TokenResponse(BaseModel):
    """Auth response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


# ---------------------------------------------------------------------------
# Password Hashing — PBKDF2-SHA256 (pure Python, no C compilation)
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-SHA256 with random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000)
    return f"{salt}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against stored PBKDF2 hash."""
    try:
        salt, key_hex = stored_hash.split("$", 1)
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000)
        return hmac.compare_digest(new_key.hex(), key_hex)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT Token Management
# ---------------------------------------------------------------------------


def create_token(user_id: str, email: str) -> str:
    """Create a JWT access token."""
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + (JWT_EXPIRY_HOURS * 3600),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------


def create_user(email: str, password: str, display_name: str = "") -> dict:
    """Register a new user. Raises HTTPException if email exists."""
    conn = database.get_conn()
    lock = database.get_lock()

    with lock:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ? COLLATE NOCASE", (email.lower(),)
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=409, detail="Email already registered."
            )

        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        pw_hash = hash_password(password)

        conn.execute(
            """INSERT INTO users
               (id, email, password_hash, display_name, plan, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'free', ?, ?)""",
            (user_id, email.lower(), pw_hash, display_name or email.split("@")[0], now, now),
        )
        conn.commit()

    logger.info("auth: registered user %s", email.lower())
    return {
        "id": user_id,
        "email": email.lower(),
        "display_name": display_name or email.split("@")[0],
        "plan": "free",
        "has_api_key": False,
        "preferred_model": "gemini-2.5-flash",
        "created_at": now,
    }


def authenticate_user(email: str, password: str) -> dict | None:
    """Verify email/password and return user dict, or None if invalid."""
    conn = database.get_conn()
    row = conn.execute(
        """SELECT id, email, password_hash, display_name, plan,
                  gemini_api_key, preferred_model, created_at
           FROM users WHERE email = ? COLLATE NOCASE""",
        (email.lower(),),
    ).fetchone()

    if not row or not verify_password(password, row["password_hash"]):
        return None

    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row["display_name"],
        "plan": row["plan"],
        "has_api_key": bool(row["gemini_api_key"]),
        "preferred_model": row["preferred_model"],
        "created_at": row["created_at"],
    }


def get_user_by_id(user_id: str) -> dict | None:
    """Fetch user by ID (used for token validation)."""
    conn = database.get_conn()
    row = conn.execute(
        """SELECT id, email, display_name, plan, gemini_api_key,
                  preferred_model, messages_today, messages_reset_date, created_at
           FROM users WHERE id = ?""",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def update_user_api_key(user_id: str, api_key: str, model: str = "") -> None:
    """Store user's Gemini API key server-side."""
    conn = database.get_conn()
    lock = database.get_lock()
    now = datetime.now(timezone.utc).isoformat()

    with lock:
        if model:
            conn.execute(
                "UPDATE users SET gemini_api_key=?, preferred_model=?, updated_at=? WHERE id=?",
                (api_key, model, now, user_id),
            )
        else:
            conn.execute(
                "UPDATE users SET gemini_api_key=?, updated_at=? WHERE id=?",
                (api_key, now, user_id),
            )
        conn.commit()
    logger.info("auth: updated API key for user %s", user_id)


def check_rate_limit(user: dict) -> None:
    """Check if user has exceeded daily message limit. Resets at midnight UTC."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = database.get_conn()
    lock = database.get_lock()

    # Reset counter if new day
    if user.get("messages_reset_date") != today:
        with lock:
            conn.execute(
                "UPDATE users SET messages_today=0, messages_reset_date=? WHERE id=?",
                (today, user["id"]),
            )
            conn.commit()
        user["messages_today"] = 0

    plan = user.get("plan", "free")
    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])["messages_per_day"]

    if user.get("messages_today", 0) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily message limit reached ({limit}/day on {plan} plan). Upgrade to Pro for more.",
        )


def increment_message_count(user_id: str) -> None:
    """Increment daily message counter for a user."""
    conn = database.get_conn()
    lock = database.get_lock()
    with lock:
        conn.execute(
            "UPDATE users SET messages_today = messages_today + 1 WHERE id = ?",
            (user_id,),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Chat History
# ---------------------------------------------------------------------------


def save_chat_message(
    user_id: str,
    role: str,
    content: str,
    card_id: str = "",
    model_used: str = "",
    tool_results: str = "[]",
    session_id: str = "default",
) -> None:
    """Persist a chat message."""
    conn = database.get_conn()
    lock = database.get_lock()
    now = datetime.now(timezone.utc).isoformat()
    with lock:
        conn.execute(
            """INSERT INTO chat_history
               (user_id, session_id, role, content, card_id, model_used, tool_results, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, session_id, role, content, card_id, model_used, tool_results, now),
        )
        conn.commit()


def get_chat_history(user_id: str, session_id: str = "default", limit: int = 50) -> list[dict]:
    """Retrieve recent chat history for a user."""
    conn = database.get_conn()
    rows = conn.execute(
        """SELECT role, content, card_id, model_used, tool_results, created_at
           FROM chat_history
           WHERE user_id = ? AND session_id = ?
           ORDER BY created_at DESC LIMIT ?""",
        (user_id, session_id, limit),
    ).fetchall()
    return [dict(r) for r in reversed(rows)]


# ---------------------------------------------------------------------------
# FastAPI Dependencies
# ---------------------------------------------------------------------------


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """FastAPI dependency: require authenticated user."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in.",
        )

    payload = decode_token(credentials.credentials)
    user = get_user_by_id(payload["sub"])

    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    """FastAPI dependency: optional authentication (for public + auth endpoints)."""
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return get_user_by_id(payload["sub"])
    except HTTPException:
        return None
