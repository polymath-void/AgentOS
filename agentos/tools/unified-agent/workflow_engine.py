"""
workflow_engine.py — Contextual Agentic Workflow Execution Engine

Design & Capabilities:
  - Executes multi-step WorkflowPlan blueprints compiled by GeminiEngine.
  - Contextual Variable Interpolation: Replaces ${var} in commands & tool args using context variables accumulated across steps.
  - Condition Evaluation: Evaluates pre-step conditions before execution.
  - Unified Tool Dispatch: Dispatches both raw shell commands (with su root support) and native tool calls.
  - Variable Capture: Automatically saves step outputs into named context variables (capture_var).
  - Agentic Self-Healing (auto-heal): On step failure, calls GeminiEngine.heal_step() to diagnose the error
    and dynamically compile & execute compensatory recovery actions in real time.
  - Telemetry & History: Records step timings, duration, status, and persists run history into card_store.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, TYPE_CHECKING

import card_store
from models import (
    AgentCard,
    AgentResponse,
    StepResult,
    TaskExecutionResult,
    ToolCall,
    WorkflowPlan,
    WorkflowStep,
)
import tool_executor

if TYPE_CHECKING:
    from gemini_engine import GeminiEngine

logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(self, gemini_engine: GeminiEngine) -> None:
        self._gemini = gemini_engine

    def execute_workflow(
        self,
        task: str,
        card: AgentCard,
        local_context: dict[str, Any],
    ) -> TaskExecutionResult:
        start_time = time.time()
        
        # Initialise contextual variable store with local context
        context_vars: dict[str, Any] = dict(local_context)
        context_vars["_task"] = task
        context_vars["_card_name"] = card.name

        logger.info("WorkflowEngine: compiling workflow for task: %r using card: %s", task, card.name)

        # Step 1: Synthesise workflow plan via GeminiEngine
        try:
            agent_response: AgentResponse = self._gemini.execute(task, card, local_context)
        except Exception as exc:
            logger.error("WorkflowEngine: synthesis failed — %s", exc)
            return TaskExecutionResult(
                card_name=card.name,
                task=task,
                reply=f"Engine failure during workflow synthesis: {exc}",
                status="failed",
                duration_ms=int((time.time() - start_time) * 1000),
            )

        workflow: WorkflowPlan | None = agent_response.workflow
        reply = agent_response.reply or "Workflow generated."
        new_card = agent_response.new_card

        if not workflow or not workflow.steps:
            logger.warning("WorkflowEngine: no steps in workflow plan, returning reply directly.")
            result = TaskExecutionResult(
                card_name=card.name,
                task=task,
                reply=reply,
                status="completed",
                context_variables=self._clean_context_vars(context_vars),
                new_card=new_card,
                duration_ms=int((time.time() - start_time) * 1000),
            )
            card_store.save_task_history(result.model_dump())
            return result

        logger.info("WorkflowEngine: executing %d contextual workflow steps...", len(workflow.steps))
        step_results: list[StepResult] = []
        overall_status = "completed"

        # Step 2: Sequential step execution with context propagation and self-healing
        for step in workflow.steps:
            # Condition check
            if not self._evaluate_condition(step.condition, context_vars):
                logger.info("WorkflowEngine: skipping step %s due to condition: %s", step.step_id, step.condition)
                step_results.append(
                    StepResult(
                        step_id=step.step_id,
                        title=step.title,
                        action_type=step.action_type,
                        target=step.command or step.tool_name or "",
                        status="skipped",
                    )
                )
                continue

            step_res = self._execute_single_step(task, step, context_vars)
            step_results.append(step_res)

            # Store captured variable if step succeeded
            if step_res.status in ("success", "healed") and step.capture_var:
                val = step_res.output.strip()
                context_vars[step.capture_var] = val
                step_res.captured_var = step.capture_var
                step_res.captured_value = val[:200]
                logger.info("WorkflowEngine: captured context var %s = %r", step.capture_var, val[:50])

            if step_res.status == "failed":
                if step.on_failure == "abort":
                    logger.error("WorkflowEngine: aborting workflow at step %s", step.step_id)
                    overall_status = "failed"
                    break
                else:
                    overall_status = "partial"

        # Step 3: Optional Verification Step
        if workflow.verification and overall_status != "failed":
            if self._evaluate_condition(workflow.verification.condition, context_vars):
                logger.info("WorkflowEngine: running verification step...")
                v_res = self._execute_single_step(task, workflow.verification, context_vars)
                step_results.append(v_res)

        total_duration_ms = int((time.time() - start_time) * 1000)

        execution_result = TaskExecutionResult(
            card_name=card.name,
            task=task,
            reply=reply,
            status=overall_status,
            step_results=step_results,
            context_variables=self._clean_context_vars(context_vars),
            new_card=new_card,
            duration_ms=total_duration_ms,
        )

        # Persist execution run summary into SQLite history
        card_store.save_task_history(execution_result.model_dump())
        return execution_result

    # ------------------------------------------------------------------
    # Step Execution & Self-Healing
    # ------------------------------------------------------------------

    def _execute_single_step(
        self,
        task: str,
        step: WorkflowStep,
        context_vars: dict[str, Any],
    ) -> StepResult:
        step_start = time.time()

        # Interpolate variables into step targets
        action_type = step.action_type
        require_root = step.require_root
        timeout = step.timeout

        if action_type == "shell" or step.command:
            interpolated_cmd = self._interpolate_vars(step.command or "", context_vars)
            target_str = interpolated_cmd
            logger.info("WorkflowEngine: [Step %s] Shell: %s (root=%s)", step.step_id, interpolated_cmd, require_root)
            
            tc = ToolCall(
                tool_name="run_shell_command",
                arguments={"command": interpolated_cmd, "timeout": timeout, "require_root": require_root},
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
        returncode = raw_res.get("returncode", 0 if status == "ok" else 1)

        if status == "ok":
            return StepResult(
                step_id=step.step_id,
                title=step.title,
                action_type=action_type,
                target=target_str,
                status="success",
                returncode=0,
                output=output,
                duration_ms=duration_ms,
            )

        # --------------------------------------------------------------
        # Step Failed — Trigger Agentic Self-Healing if configured
        # --------------------------------------------------------------
        logger.warning("WorkflowEngine: Step %s failed output: %s", step.step_id, output[:200])

        if step.on_failure == "heal":
            logger.info("WorkflowEngine: Initiating Agentic Self-Healing for Step %s...", step.step_id)
            healing_res = self._gemini.heal_step(task, step, output, context_vars)
            
            recovery_steps = healing_res.get("recovery_steps", [])
            healed_records = []
            
            if healing_res.get("can_recover") and recovery_steps:
                healed_success = True
                for h_idx, rec_step_dict in enumerate(recovery_steps, 1):
                    rec_cmd = self._interpolate_vars(rec_step_dict.get("command", ""), context_vars)
                    logger.info("WorkflowEngine: [Self-Heal %s] Running recovery command: %s", h_idx, rec_cmd)
                    
                    rec_tc = ToolCall(
                        tool_name="run_shell_command",
                        arguments={"command": rec_cmd, "timeout": 30, "require_root": rec_step_dict.get("require_root", False)},
                    )
                    rec_res = tool_executor.execute_tool(rec_tc)
                    healed_records.append({
                        "command": rec_cmd,
                        "status": rec_res.get("status"),
                        "output": rec_res.get("output", "")[:200],
                    })

                    if rec_res.get("status") != "ok":
                        healed_success = False
                        break

                if healed_success:
                    logger.info("WorkflowEngine: Step %s successfully self-healed!", step.step_id)
                    return StepResult(
                        step_id=step.step_id,
                        title=f"{step.title} (Healed)",
                        action_type=action_type,
                        target=target_str,
                        status="healed",
                        returncode=0,
                        output=f"{output}\n\n[SELF-HEALED]: {healed_records}",
                        duration_ms=int((time.time() - step_start) * 1000),
                        healed_with=healed_records,
                    )

        return StepResult(
            step_id=step.step_id,
            title=step.title,
            action_type=action_type,
            target=target_str,
            status="failed",
            returncode=returncode,
            output=output,
            error=output,
            duration_ms=duration_ms,
        )

    # ------------------------------------------------------------------
    # Variable Interpolation & Condition Helpers
    # ------------------------------------------------------------------

    def _interpolate_vars(self, text: str, ctx: dict[str, Any]) -> str:
        if not text:
            return ""
        
        def repl(match: re.Match) -> str:
            var_name = match.group(1) or match.group(2)
            val = ctx.get(var_name, "")
            return str(val)

        # Replaces ${var_name} or $var_name
        return re.sub(r"\$\{([a-zA-Z0-9_]+)\}|\$([a-zA-Z0-9_]+)", repl, text)

    def _interpolate_args(self, args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
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
        if not condition:
            return True
        
        interpolated = self._interpolate_vars(condition, ctx).strip()
        if not interpolated:
            return True

        # Handle simple truthy/falsy or string comparisons safely
        if interpolated.lower() in ("true", "1", "yes"):
            return True
        if interpolated.lower() in ("false", "0", "no"):
            return False

        try:
            # Safe evaluation of numerical / string equality without exec
            if "==" in interpolated:
                left, right = [x.strip().strip("'\"") for x in interpolated.split("==", 1)]
                return left == right
            if "!=" in interpolated:
                left, right = [x.strip().strip("'\"") for x in interpolated.split("!=", 1)]
                return left != right
        except Exception:
            pass

        return True

    def _clean_context_vars(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in ctx.items() if not k.startswith("_")}
