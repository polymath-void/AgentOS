"""
models.py — Core schema layer for SaaS-Agent
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# AgentCard
# ---------------------------------------------------------------------------

class AgentCard(BaseModel):
    """
    Persistent agent configuration.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(default="", max_length=512)
    system_prompt: str = Field(..., min_length=1)

    tools: list[str] = Field(
        default_factory=list,
        description="Allowed tool whitelist. Empty = all tools allowed."
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        uuid.UUID(v)
        return v

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# TaskRequest
# ---------------------------------------------------------------------------

class TaskRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=4096)
    card_id: str | None = None
    local_context: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# ToolCall
# ---------------------------------------------------------------------------

class ToolCall(BaseModel):
    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Workflow Steps & Plans
# ---------------------------------------------------------------------------

class WorkflowStep(BaseModel):
    """
    Individual step within an agentic workflow execution array.
    """
    step_id: int | str = Field(default=1, description="Sequential step index or identifier.")
    title: str = Field(default="", description="Brief description of the action being taken.")
    action_type: str = Field(default="shell", description="'shell' for raw terminal execution, 'tool' for structured tool call.")
    command: str | None = Field(default=None, description="Shell command string to execute (if action_type == 'shell').")
    tool_name: str | None = Field(default=None, description="Tool name (if action_type == 'tool').")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for tool call.")
    require_root: bool = Field(default=False, description="Whether root privilege (su) is required.")
    timeout: int = Field(default=30, description="Timeout in seconds.")
    capture_var: str | None = Field(default=None, description="Context variable name to store the output into (e.g., 'ip', 'pkg').")
    condition: str | None = Field(default=None, description="Optional condition expression before running (e.g., '${battery_pct} < 20').")
    on_failure: str = Field(default="heal", description="Failure strategy: 'heal' (agentic self-healing), 'continue', 'abort', 'retry'.")


class WorkflowPlan(BaseModel):
    """
    Contextual workflow blueprint compiled by the Gemini reasoning engine.
    """
    goal: str = Field(default="", description="High-level goal of the workflow.")
    summary: str = Field(default="", description="Human-facing summary overview.")
    steps: list[WorkflowStep] = Field(default_factory=list, description="Ordered array of contextual workflow steps.")
    verification: WorkflowStep | None = Field(default=None, description="Optional post-execution verification step.")


# ---------------------------------------------------------------------------
# Step and Task Execution Results
# ---------------------------------------------------------------------------

class StepResult(BaseModel):
    """
    Output log and telemetry of an executed workflow step.
    """
    step_id: int | str
    title: str = ""
    action_type: str = "shell"
    target: str = ""
    status: str = "success"  # "success" | "failed" | "skipped" | "healed"
    returncode: int | None = 0
    output: str = ""
    error: str | None = None
    duration_ms: int = 0
    healed_with: list[dict[str, Any]] = Field(default_factory=list, description="Self-healing recovery actions if triggered.")
    captured_var: str | None = None
    captured_value: Any = None


class TaskExecutionResult(BaseModel):
    """
    Complete summary of a workflow execution run.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    card_name: str = "System Agent"
    task: str
    reply: str = ""
    status: str = "completed"  # "completed" | "partial" | "failed"
    step_results: list[StepResult] = Field(default_factory=list)
    context_variables: dict[str, Any] = Field(default_factory=dict)
    new_card: dict[str, Any] | None = None
    duration_ms: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# AgentResponse
# ---------------------------------------------------------------------------

class AgentResponse(BaseModel):
    """
    Structured response mapping supporting both agentic workflows and one-shot execution plans.
    """
    reply: str = Field(..., description="Human-facing summary execution overview.")
    workflow: WorkflowPlan | None = Field(default=None, description="Full agentic workflow plan.")
    execution_plan: list[str] = Field(default_factory=list, description="Ordered list of shell commands (fallback / legacy).")
    tool_calls: list[ToolCall] = Field(default_factory=list)
    new_card: Any = Field(default=None)

