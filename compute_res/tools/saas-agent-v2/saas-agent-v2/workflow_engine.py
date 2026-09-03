"""
workflow_engine.py — Self-Healing Agentic Workflow Engine for SaaS-Agent v2.

Merged from unified-agent's workflow engine with multi-tenant adaptations.

Core Capabilities:
  - Multi-step workflow execution from LLM-compiled plans
  - Contextual variable interpolation: ${var} chaining across steps
  - Pre-step condition evaluation
  - Agentic Self-Healing: on failure, LLM diagnoses error and generates
    compensatory recovery commands automatically
  - Variable capture: step outputs stored as named context vars
  - Telemetry: step timings, status tracking, full execution history
  - Per-user execution history persistence

THIS IS THE KILLER FEATURE. No other AI agent platform does this.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, TYPE_CHECKING

import tool_executor
from models import ToolCall

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Workflow Data Models (embedded to avoid circular imports)
# ---------------------------------------------------------------------------

from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class WorkflowStep(BaseModel):
    """Individual step within a workflow execution plan."""
    step_id: int | str = Field(default=1)
    title: str = Field(default="")
    action_type: str = Field(default="shell", description="'shell' or 'tool'")
    command: str | None = Field(default=None)
    tool_name: str | None = Field(default=None)
    arguments: dict[str, Any] = Field(default_factory=dict)
    require_root: bool = Field(default=False)
    timeout: int = Field(default=30)
    capture_var: str | None = Field(default=None, description="Store stdout into this context variable")
    condition: str | None = Field(default=None, description="Pre-condition expression e.g. '${battery} > 20'")
    on_failure: str = Field(default="heal", description="'heal' | 'continue' | 'abort' | 'retry'")


class WorkflowPlan(BaseModel):
    """Multi-step workflow blueprint compiled by the LLM."""
    goal: str = Field(default="")
    summary: str = Field(default="")
    steps: list[WorkflowStep] = Field(default_factory=list)
    verification: WorkflowStep | None = Field(default=None)


class StepResult(BaseModel):
    """Execution result of a single workflow step."""
    step_id: int | str
    title: str = ""
    action_type: str = "shell"
    target: str = ""
    status: str = "success"  # success | failed | skipped | healed
    returncode: int | None = 0
    output: str = ""
    error: str | None = None
    duration_ms: int = 0
    healed_with: list[dict[str, Any]] = Field(default_factory=list)
    captured_var: str | None = None
    captured_value: Any = None


class WorkflowResult(BaseModel):
    """Complete execution summary of a workflow run."""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    card_name: str = "System Agent"
    task: str
    reply: str = ""
    status: str = "completed"  # completed | partial | failed
    step_results: list[StepResult] = Field(default_factory=list)
    context_variables: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Workflow Synthesis Schema (sent to LLM)
# ---------------------------------------------------------------------------

WORKFLOW_SYNTHESIS_SCHEMA = """\
You MUST respond with ONLY valid JSON (no markdown fences):
{
  "reply": "<string: human-facing summary of what this workflow will do>",
  "workflow": {
    "goal": "<string: high-level goal>",
    "summary": "<string: brief execution overview>",
    "steps": [
      {
        "step_id": 1,
        "title": "<brief description of this step>",
        "action_type": "shell",
        "command": "<exact shell command to execute>",
        "tool_name": null,
        "arguments": {},
        "require_root": false,
        "timeout": 30,
        "capture_var": null,
        "condition": null,
        "on_failure": "heal"
      }
    ],
    "verification": null
  },
  "tool_calls": []
}

Rules:
1. Analyze the task and generate a structured multi-step workflow plan.
2. Chain prerequisites automatically (e.g., 'pkg install -y ...' before using a tool).
3. Use capture_var to store outputs, reference as ${var_name} in later steps.
4. Set require_root: true ONLY for Android system settings (settings put, svc wifi, etc).
5. Set on_failure: "heal" for steps that can be auto-recovered.
6. Output ONLY raw valid JSON. No markdown fences.
"""

HEAL_STEP_SCHEMA = """\
You MUST respond with ONLY valid JSON (no markdown fences):
{
  "diagnosis": "<brief explanation of why the command failed>",
  "can_recover": true,
  "recovery_steps": [
    {
      "step_id": "heal_1",
      "title": "<compensatory action>",
      "command": "<fixed shell command or prerequisite install>",
      "require_root": false,
      "timeout": 30
    }
  ]
}
"""


# ---------------------------------------------------------------------------
# Workflow Engine
# ---------------------------------------------------------------------------

class WorkflowEngine:
    """
    Executes multi-step agentic workflows with self-healing.

    This is the core differentiator of SaaS-Agent v2:
    - Steps fail? The LLM diagnoses the error and auto-generates recovery commands
    - Variables chain across steps automatically
    - Conditions gate step execution
    """

    def __init__(self, gemini_engine) -> None:
        self._gemini = gemini_engine

    def execute_workflow(
        self,
        task: str,
        card,
        local_context: dict[str, Any],
        user_api_key: str = "",
        user_model: str = "",
    ) -> WorkflowResult:
        """Execute a full workflow: synthesize plan → execute steps → self-heal failures."""
        start_time = time.time()

        # Initialize context variable store
        context_vars: dict[str, Any] = dict(local_context)
        context_vars["_task"] = task
        context_vars["_card_name"] = card.name

        logger.info("WorkflowEngine: compiling workflow for: %r using card: %s", task, card.name)

        # Step 1: Synthesize workflow via LLM
        try:
            raw_response = self._call_llm_for_workflow(task, card, local_context, user_api_key, user_model)
            workflow, reply = self._parse_workflow_response(raw_response)
        except Exception as exc:
            logger.error("WorkflowEngine: synthesis failed — %s", exc)
            return WorkflowResult(
                card_name=card.name,
                task=task,
                reply=f"Workflow synthesis failed: {exc}",
                status="failed",
                duration_ms=int((time.time() - start_time) * 1000),
            )

        if not workflow or not workflow.steps:
            return WorkflowResult(
                card_name=card.name,
                task=task,
                reply=reply or "No workflow steps generated.",
                status="completed",
                context_variables=self._clean_context(context_vars),
                duration_ms=int((time.time() - start_time) * 1000),
            )

        logger.info("WorkflowEngine: executing %d steps…", len(workflow.steps))
        step_results: list[StepResult] = []
        overall_status = "completed"

        # Step 2: Execute steps sequentially with context propagation
        for step in workflow.steps:
            # Check pre-condition
            if not self._evaluate_condition(step.condition, context_vars):
                logger.info("WorkflowEngine: skipping step %s (condition: %s)", step.step_id, step.condition)
                step_results.append(StepResult(
                    step_id=step.step_id, title=step.title,
                    action_type=step.action_type, status="skipped",
                ))
                continue

            # Execute step
            step_res = self._execute_step(task, step, context_vars, user_api_key, user_model)
            step_results.append(step_res)

            # Capture output variable
            if step_res.status in ("success", "healed") and step.capture_var:
                val = step_res.output.strip()
                context_vars[step.capture_var] = val
                step_res.captured_var = step.capture_var
                step_res.captured_value = val[:200]

            if step_res.status == "failed":
                if step.on_failure == "abort":
                    overall_status = "failed"
                    break
                else:
                    overall_status = "partial"

        # Step 3: Optional verification
        if workflow.verification and overall_status != "failed":
            if self._evaluate_condition(workflow.verification.condition, context_vars):
                v_res = self._execute_step(task, workflow.verification, context_vars, user_api_key, user_model)
                step_results.append(v_res)

        return WorkflowResult(
            card_name=card.name,
            task=task,
            reply=reply,
            status=overall_status,
            step_results=step_results,
            context_variables=self._clean_context(context_vars),
            duration_ms=int((time.time() - start_time) * 1000),
        )

    # ------------------------------------------------------------------
    # Step Execution & Self-Healing
    # ------------------------------------------------------------------

    def _execute_step(
        self,
        task: str,
        step: WorkflowStep,
        context_vars: dict[str, Any],
        user_api_key: str = "",
        user_model: str = "",
    ) -> StepResult:
        """Execute a single step, with self-healing on failure."""
        step_start = time.time()

        if step.action_type == "shell" or step.command:
            interpolated_cmd = self._interpolate_vars(step.command or "", context_vars)
            target_str = interpolated_cmd
            logger.info("WorkflowEngine: [Step %s] Shell: %s (root=%s)", step.step_id, interpolated_cmd, step.require_root)

            tc = ToolCall(
                tool_name="run_shell_command",
                arguments={"command": interpolated_cmd, "timeout": step.timeout, "require_root": step.require_root},
            )
            raw_res = tool_executor.execute_tool(tc)
        else:
            tool_name = step.tool_name or "run_shell_command"
            interpolated_args = self._interpolate_args(step.arguments, context_vars)
            target_str = f"{tool_name}({interpolated_args})"
            logger.info("WorkflowEngine: [Step %s] Tool: %s", step.step_id, target_str)

            tc = ToolCall(tool_name=tool_name, arguments=interpolated_args)
            raw_res = tool_executor.execute_tool(tc)

        duration_ms = int((time.time() - step_start) * 1000)
        status = raw_res.get("status", "error")
        output = raw_res.get("output", "")

        if status == "ok":
            return StepResult(
                step_id=step.step_id, title=step.title,
                action_type=step.action_type, target=target_str,
                status="success", returncode=0, output=output,
                duration_ms=duration_ms,
            )

        # --- SELF-HEALING ---
        logger.warning("WorkflowEngine: Step %s failed: %s", step.step_id, output[:200])

        if step.on_failure == "heal":
            logger.info("WorkflowEngine: 🔧 Initiating self-healing for Step %s…", step.step_id)
            healed = self._attempt_healing(task, step, output, context_vars, user_api_key, user_model)
            if healed is not None:
                healed.duration_ms = int((time.time() - step_start) * 1000)
                return healed

        return StepResult(
            step_id=step.step_id, title=step.title,
            action_type=step.action_type, target=target_str,
            status="failed", returncode=1, output=output, error=output,
            duration_ms=duration_ms,
        )

    def _attempt_healing(
        self,
        task: str,
        failed_step: WorkflowStep,
        error_output: str,
        context_vars: dict[str, Any],
        user_api_key: str = "",
        user_model: str = "",
    ) -> StepResult | None:
        """Use LLM to diagnose failure and execute recovery commands."""
        try:
            healing_res = self._call_llm_for_healing(task, failed_step, error_output, context_vars, user_api_key, user_model)

            if not healing_res.get("can_recover") or not healing_res.get("recovery_steps"):
                logger.warning("WorkflowEngine: LLM says cannot recover")
                return None

            healed_records = []
            for rec_step in healing_res["recovery_steps"]:
                rec_cmd = self._interpolate_vars(rec_step.get("command", ""), context_vars)
                logger.info("WorkflowEngine: [Self-Heal] Running: %s", rec_cmd)

                rec_tc = ToolCall(
                    tool_name="run_shell_command",
                    arguments={
                        "command": rec_cmd,
                        "timeout": rec_step.get("timeout", 30),
                        "require_root": rec_step.get("require_root", False),
                    },
                )
                rec_res = tool_executor.execute_tool(rec_tc)
                healed_records.append({
                    "command": rec_cmd,
                    "status": rec_res.get("status"),
                    "output": rec_res.get("output", "")[:200],
                })

                if rec_res.get("status") != "ok":
                    logger.warning("WorkflowEngine: healing step failed, giving up")
                    return None

            logger.info("WorkflowEngine: ✅ Step %s self-healed!", failed_step.step_id)
            return StepResult(
                step_id=failed_step.step_id,
                title=f"{failed_step.title} (Self-Healed ✨)",
                action_type=failed_step.action_type,
                target=failed_step.command or failed_step.tool_name or "",
                status="healed",
                returncode=0,
                output=f"{error_output}\n\n[SELF-HEALED] Recovery: {json.dumps(healed_records)}",
                healed_with=healed_records,
            )
        except Exception as exc:
            logger.warning("WorkflowEngine: healing failed — %s", exc)
            return None

    # ------------------------------------------------------------------
    # LLM Calls (uses the existing GeminiEngine's infrastructure)
    # ------------------------------------------------------------------

    def _call_llm_for_workflow(self, task, card, local_context, api_key, model):
        """Call LLM to synthesize a workflow plan."""
        from google import genai
        from google.genai import types
        from tool_registry import get_tool_definitions

        client = genai.Client(api_key=api_key) if api_key else self._gemini._client
        model_id = model or self._gemini._model

        # Build system prompt with workflow schema
        context_block = ""
        if local_context:
            safe = {k: str(v)[:200] for k, v in local_context.items() if not k.startswith("_")}
            context_block = f"\n\n## Device Context:\n{json.dumps(safe, indent=2)}"

        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]

        system = (
            f"{card.system_prompt}"
            f"{context_block}\n\n"
            f"## Available Tools:\n{json.dumps(tool_names)}\n\n"
            f"{WORKFLOW_SYNTHESIS_SCHEMA}"
        )

        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.15,
            max_output_tokens=2048,
            response_mime_type="application/json",
        )

        resp = client.models.generate_content(
            model=model_id,
            contents=f"Task: {task}",
            config=config,
        )
        return resp.text or "{}"

    def _call_llm_for_healing(self, task, failed_step, error_output, context_vars, api_key, model):
        """Call LLM to diagnose and generate recovery steps."""
        from google import genai
        from google.genai import types
        from tool_registry import get_tool_definitions

        client = genai.Client(api_key=api_key) if api_key else self._gemini._client
        model_id = model or self._gemini._model

        system = (
            "You are an expert Linux/Termux system debugger and self-healing engine.\n"
            "A workflow step failed. Analyze the error and provide recovery commands.\n\n"
            + HEAL_STEP_SCHEMA
        )

        user_content = json.dumps({
            "task": task,
            "failed_step": {
                "command": failed_step.command,
                "tool_name": failed_step.tool_name,
                "title": failed_step.title,
            },
            "error_output": error_output[:1024],
            "context": {k: str(v)[:200] for k, v in context_vars.items() if not k.startswith("_")},
        }, indent=2)

        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.1,
            max_output_tokens=1024,
            response_mime_type="application/json",
        )

        resp = client.models.generate_content(
            model=model_id,
            contents=f"Diagnose and fix:\n{user_content}",
            config=config,
        )

        cleaned = re.sub(r"```json|```", "", (resp.text or "{}")).strip()
        return json.loads(cleaned)

    def _parse_workflow_response(self, raw: str) -> tuple[WorkflowPlan | None, str]:
        """Parse LLM JSON response into a WorkflowPlan."""
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return None, f"Workflow parse failed (raw: {raw[:200]})"

        reply = data.get("reply", "")
        workflow_data = data.get("workflow")

        if not isinstance(workflow_data, dict):
            return None, reply

        raw_steps = workflow_data.get("steps", [])
        steps = []
        for idx, s in enumerate(raw_steps, 1):
            if isinstance(s, dict):
                steps.append(WorkflowStep(
                    step_id=s.get("step_id", idx),
                    title=s.get("title", f"Step {idx}"),
                    action_type=s.get("action_type", "shell"),
                    command=s.get("command"),
                    tool_name=s.get("tool_name"),
                    arguments=s.get("arguments", {}),
                    require_root=s.get("require_root", False),
                    timeout=s.get("timeout", 30),
                    capture_var=s.get("capture_var"),
                    condition=s.get("condition"),
                    on_failure=s.get("on_failure", "heal"),
                ))
            elif isinstance(s, str):
                steps.append(WorkflowStep(
                    step_id=idx, title=f"Execute: {s[:40]}",
                    action_type="shell", command=s, on_failure="heal",
                ))

        verification = None
        v_raw = workflow_data.get("verification")
        if isinstance(v_raw, dict):
            verification = WorkflowStep(
                step_id="verify", title=v_raw.get("title", "Verification"),
                action_type=v_raw.get("action_type", "shell"),
                command=v_raw.get("command"), require_root=v_raw.get("require_root", False),
                timeout=v_raw.get("timeout", 15), on_failure="continue",
            )

        plan = WorkflowPlan(
            goal=workflow_data.get("goal", ""),
            summary=workflow_data.get("summary", reply),
            steps=steps, verification=verification,
        )
        return plan, reply

    # ------------------------------------------------------------------
    # Variable Interpolation & Condition Helpers
    # ------------------------------------------------------------------

    def _interpolate_vars(self, text: str, ctx: dict[str, Any]) -> str:
        """Replace ${var} or $var with context values."""
        if not text:
            return ""

        def repl(match: re.Match) -> str:
            var_name = match.group(1) or match.group(2)
            return str(ctx.get(var_name, ""))

        return re.sub(r"\$\{([a-zA-Z0-9_]+)\}|\$([a-zA-Z0-9_]+)", repl, text)

    def _interpolate_args(self, args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        """Recursively interpolate variables in tool arguments."""
        out = {}
        for k, v in args.items():
            if isinstance(v, str):
                out[k] = self._interpolate_vars(v, ctx)
            elif isinstance(v, dict):
                out[k] = self._interpolate_args(v, ctx)
            else:
                out[k] = v
        return out

    def _evaluate_condition(self, condition: str | None, ctx: dict[str, Any]) -> bool:
        """Safely evaluate a condition expression."""
        if not condition:
            return True

        interpolated = self._interpolate_vars(condition, ctx).strip()
        if not interpolated:
            return True

        lower = interpolated.lower()
        if lower in ("true", "1", "yes"):
            return True
        if lower in ("false", "0", "no"):
            return False

        try:
            if "==" in interpolated:
                left, right = [x.strip().strip("'\"") for x in interpolated.split("==", 1)]
                return left == right
            if "!=" in interpolated:
                left, right = [x.strip().strip("'\"") for x in interpolated.split("!=", 1)]
                return left != right
        except Exception:
            pass

        return True

    def _clean_context(self, ctx: dict[str, Any]) -> dict[str, Any]:
        """Remove internal variables from context output."""
        return {k: v for k, v in ctx.items() if not k.startswith("_")}
