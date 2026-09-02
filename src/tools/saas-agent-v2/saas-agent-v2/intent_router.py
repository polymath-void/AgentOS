"""
intent_router.py — Classify user intent and auto-route to best AgentCard.

Strategy:
  1. Extract keywords/patterns from task
  2. Score against pre-seeded cards' scope_tags
  3. Return best-fit card ID + confidence
  4. If no good match (confidence < 0.6), use System Agent fallback
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import AgentCard, IntentClassification

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Intent keywords (used for classification)
# ---------------------------------------------------------------------------

INTENT_PATTERNS: dict[str, tuple[list[str], list[str]]] = {
    "MEDIA": (
        ["play", "music", "song", "video", "youtube", "spotify", "stream", "watch"],
        ["radio", "podcast"],
    ),
    "CALLS": (
        ["call", "dial", "phone", "ring", "missed call", "contact"],
        [],
    ),
    "SMS": (
        ["sms", "text", "message", "whatsapp", "send message"],
        [],
    ),
    "FILES": (
        ["file", "folder", "directory", "copy", "move", "delete", "list", "find", "search"],
        [],
    ),
    "EMAIL": (
        ["email", "mail", "inbox", "unread", "send email", "summarize mail"],
        [],
    ),
    "CALENDAR": (
        ["calendar", "event", "meeting", "schedule", "appointment", "reminder"],
        [],
    ),
    "NOTES": (
        ["note", "journal", "write", "remember", "save note"],
        [],
    ),
    "SYSTEM": (
        ["brightness", "wifi", "network", "battery", "notification", "volume", "shutdown"],
        [],
    ),
    "OTHER": (
        [],
        [],
    ),
}

# Scope tag → card name mapping (pre-seeded cards)
SCOPE_TAG_TO_CARD_NAME: dict[str, str] = {
    "media": "Media Control",
    "calls": "Call Manager",
    "sms": "SMS Manager",
    "files": "File Manager",
    "email": "Email Assistant",
    "calendar": "Calendar Assistant",
    "notes": "Notes Manager",
    "system": "System Control",
}


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

def classify_intent(task: str) -> str:
    """
    Classify a task into one of the intent categories.
    Returns the intent name (e.g. "MEDIA", "CALLS").
    """
    task_lower = task.lower()

    # Score each intent based on keyword matches
    scores: dict[str, float] = {}

    for intent, (positive_words, negative_words) in INTENT_PATTERNS.items():
        positive_score = sum(1 for word in positive_words if word in task_lower)
        negative_score = sum(1 for word in negative_words if word in task_lower)
        score = positive_score - negative_score
        scores[intent] = score

    # Return highest-scoring intent (or OTHER if tie at zero)
    best_intent = max(scores, key=scores.get)
    return best_intent if scores[best_intent] > 0 else "OTHER"


def score_card_match(task: str, card: AgentCard) -> float:
    """
    Score how well a card matches the task (0–1).
    Based on scope_tags and card name.
    """
    task_lower = task.lower()
    card_name_lower = card.name.lower()

    score = 0.0

    # Match card name in task
    if card_name_lower in task_lower:
        score += 0.3

    # Match scope tags
    for tag in card.scope_tags:
        if tag.lower() in task_lower:
            score += 0.35

    # Intent match (bonus if card name contains intent keyword)
    intent = classify_intent(task)
    intent_keywords = INTENT_PATTERNS.get(intent, ([], []))[0]
    for keyword in intent_keywords:
        if keyword in card_name_lower:
            score += 0.2

    return min(score, 1.0)


def route_to_card(task: str, available_cards: list[AgentCard]) -> tuple[AgentCard | None, float]:
    """
    Pick the best card for a task.

    Returns (best_card, confidence_score).
    If confidence < 0.5, returns (None, score) — caller should use System Agent fallback.
    """
    if not available_cards:
        return None, 0.0

    scores: dict[AgentCard, float] = {}
    for card in available_cards:
        scores[card] = score_card_match(task, card)

    best_card = max(available_cards, key=lambda c: scores[c])
    confidence = scores[best_card]

    logger.debug(
        f"intent_router: task={task[:50]!r} → card={best_card.name} (confidence={confidence:.2f})"
    )

    return best_card, confidence


# ---------------------------------------------------------------------------
# For v2: Return IntentClassification object
# ---------------------------------------------------------------------------

def classify_with_recommendation(
    task: str,
    available_cards: list[AgentCard],
) -> IntentClassification:
    """
    Full classification with card recommendation.
    Returns IntentClassification object for API serialization.
    """
    from models import IntentClassification

    intent = classify_intent(task)
    best_card, confidence = route_to_card(task, available_cards)

    return IntentClassification(
        detected_intent=intent,
        recommended_card_id=best_card.id if best_card else None,
        confidence=confidence,
        reasoning=(
            f"Detected intent: {intent}. "
            + (
                f"Best match: {best_card.name} (confidence {confidence:.0%})."
                if best_card
                else "No strong match; use manual card selection or System Agent."
            )
        ),
    )
