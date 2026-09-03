"""
models.py — SaaS-Agent v2 Pydantic schemas.

Covers:
  - AgentCard: persistent card identity + system_prompt + scope
  - TaskRequest: user task input (auto card selection or manual)
  - CardCreationRequest: user description → agent generates system_prompt
  - ChatMessage: stores chat history
  - ToolCall: function calling output
  - AgentResponse: structured output for all 3 modes
  - IntentClassification: intent + card recommendation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# AgentCard (v2: added mode preference + scope tags)
# ---------------------------------------------------------------------------

class AgentCard(BaseModel):
    """Persistent agent identity with execution mode hints."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID4 primary key.",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Card display name.",
    )
    description: str = Field(
        default="",
        max_length=512,
        description="One-liner describing what this card does.",
    )
    system_prompt: str = Field(
        ...,
        min_length=1,
        description="Full system prompt for this card.",
    )
    tools: list[str] = Field(
        default_factory=list,
        description="Whitelist of tool names. Empty = all tools.",
    )
    # v2 additions
    execution_mode: Literal["function_calling", "json_structured", "summarization"] = Field(
        default="function_calling",
        description="Preferred execution mode for Gemini.",
    )
    scope_tags: list[str] = Field(
        default_factory=list,
        description="Tags for intent matching (e.g. 'media', 'calls', 'calendar').",
    )
    is_system_card: bool = Field(
        default=False,
        description="If true, this is a pre-seeded system card (read-only edit).",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of creation.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last update.",
    )

    @field_validator("id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError as exc:
            raise ValueError(f"AgentCard.id must be a valid UUID4, got: {v!r}") from exc
        return v

    def touch(self) -> None:
        """Update updated_at to now."""
        self.updated_at = datetime.now(timezone.utc)

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}


# ---------------------------------------------------------------------------
# CardCreationRequest (v2: user describes task, agent generates prompt)
# ---------------------------------------------------------------------------

class CardCreationRequest(BaseModel):
    """Request to create a new card by natural language description."""

    user_description: str = Field(
        ...,
        min_length=10,
        max_length=2048,
        description="User's natural language description of what the card should do.",
    )
    suggested_name: str | None = Field(
        default=None,
        description="Optional: suggested card name. Agent can refine it.",
    )
    scope_tags: list[str] = Field(
        default_factory=list,
        description="Optional: user-suggested scope tags (media, calls, files, etc.).",
    )


# ---------------------------------------------------------------------------
# IntentClassification (v2: auto card routing)
# ---------------------------------------------------------------------------

class IntentClassification(BaseModel):
    """Model's classification of intent and recommended card."""

    detected_intent: str = Field(
        ...,
        description="Classified intent (MEDIA, CALLS, FILES, EMAIL, CALENDAR, NOTES, SYSTEM, OTHER).",
    )
    recommended_card_id: str | None = Field(
        default=None,
        description="UUID of the best-fit card, or None if no clear match.",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence score 0–1 that this card is the right choice.",
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of the classification.",
    )


# ---------------------------------------------------------------------------
# ChatMessage (v2: chat history)
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    """A single message in the chat history."""

    role: Literal["user", "assistant"] = Field(
        ...,
        description="'user' or 'assistant'.",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Message text.",
    )
    card_id: str | None = Field(
        default=None,
        description="If assistant, the card used to generate this response.",
    )
    tool_results: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Tool execution results (if any).",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of message.",
    )

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}


# ---------------------------------------------------------------------------
# TaskRequest (v2: task + optional manual card selection)
# ---------------------------------------------------------------------------

class TaskRequest(BaseModel):
    """User task input with optional manual card override."""

    task: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Natural language task.",
    )
    card_id: str | None = Field(
        default=None,
        description="Optional UUID of card to use. If None, auto-classify.",
    )
    local_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Device context (clipboard, env, etc.).",
    )
    # v2 addition: let user select execution mode
    preferred_execution_mode: Literal["function_calling", "json_structured", "summarization"] | None = Field(
        default=None,
        description="Optional override of card's default execution mode.",
    )

    @field_validator("card_id")
    @classmethod
    def validate_card_id(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            uuid.UUID(v)
        except ValueError as exc:
            raise ValueError(f"TaskRequest.card_id must be valid UUID or null, got: {v!r}") from exc
        return v


# ---------------------------------------------------------------------------
# ToolCall (for function calling mode)
# ---------------------------------------------------------------------------

class ToolCall(BaseModel):
    """A single tool invocation."""

    tool_name: str = Field(
        ...,
        min_length=1,
        description="Exact tool name from registry.",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments.",
    )


# ---------------------------------------------------------------------------
# AgentResponse (v2: supports all 3 execution modes)
# ---------------------------------------------------------------------------

class AgentResponse(BaseModel):
    """Structured output from Gemini (all 3 modes)."""

    # Common fields
    thought: str = Field(
        default="",
        description="Internal chain-of-thought (not shown to user).",
    )
    reply: str = Field(
        ...,
        min_length=1,
        description="Human-facing response.",
    )

    # Mode 1: Function Calling
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Actions to execute (function calling mode).",
    )

    # Mode 2: JSON Structured (for data retrieval)
    json_data: dict[str, Any] | None = Field(
        default=None,
        description="Structured JSON result (JSON structured mode).",
    )

    # Mode 3: Summarization
    summary_points: list[str] = Field(
        default_factory=list,
        description="Bulleted summary (summarization mode).",
    )

    # v2 additions
    execution_mode: Literal["function_calling", "json_structured", "summarization"] = Field(
        default="function_calling",
        description="Which execution mode was used.",
    )
    new_card: AgentCard | None = Field(
        default=None,
        description="If a new AgentCard was created, it's embedded here.",
    )

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}
