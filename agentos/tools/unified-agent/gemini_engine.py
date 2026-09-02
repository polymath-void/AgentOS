from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from google import genai
from google.genai import types

from models import AgentCard, AgentResponse, ToolCall, WorkflowPlan, WorkflowStep
from tool_registry import filter_tools_for_card, get_tool_definitions

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONFIG & LOAD BALANCING TARGETS
# ---------------------------------------------------------------------------

MODEL_COMPLEX = "gemini-flash-latest"      # For structural synthesis, self-healing & complex logic
MODEL_ROUTINE = "gemini-flash-latest"      # Fast workhorse model



GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MAX_CONTEXT_VALUE_LEN = 1024

# ---------------------------------------------------------------------------
# CONTEXTUAL AGENTIC WORKFLOW SCHEMA
# ---------------------------------------------------------------------------

AGENT_WORKFLOW_SCHEMA = """\
You MUST respond with ONLY a valid JSON object matching this schema layout:
{
  "reply": "<string: clear, human-facing overview of the workflow blueprint>",
  "workflow": {
    "goal": "<string: high-level goal of the workflow>",
    "summary": "<string: summary of the multi-step execution>",
    "steps": [
      {
        "step_id": 1,
        "title": "<string: brief title/purpose of step>",
        "action_type": "shell", // or "tool"
        "command": "<string: exact shell command to execute, e.g., 'pkg install -y jq' or 'dumpsys battery'>",
        "tool_name": null, // or string tool name if action_type == 'tool'
        "arguments": {}, // tool arguments if action_type == 'tool'
        "require_root": false, // true for Android system settings, su, svc, hardware
        "timeout": 30,
        "capture_var": null, // or string var name (e.g. 'ip_addr', 'pkg_list') to store stdout into context
        "condition": null, // or condition string e.g. '${battery_pct} > 15'
        "on_failure": "heal" // 'heal' (agentic self-repair), 'continue', 'abort', 'retry'
      }
    ],
    "verification": null // or optional WorkflowStep to verify goal outcome
  },
  "execution_plan": [
    "<string: exact shell command 1>",
    "<string: exact shell command 2>"
  ]
}

Rules:
1. You are an advanced Contextual Agentic Workflow Synthesis Engine for Termux/Android (rooted).
2. Analyze the user's task and available device context. Generate a structured, step-by-step contextual workflow plan.
3. Automatically chain prerequisites (e.g. 'pkg install -y ...' or 'pip install ...') into initial steps before dependent commands.
4. Support variable chaining: use capture_var (e.g. capture_var: "my_ip") in earlier steps, and reference them as ${my_ip} in subsequent commands.
5. If the user asks to create an agent card or manipulate cards, use action_type: "tool" with tool_name: "create_agent_card" or run shell commands.
6. Set require_root: true ONLY for Android system modifications (e.g., 'settings put', 'svc wifi', 'svc data'). For standard commands, reading status, uptime, battery, or files, set require_root: false.

7. Also provide the flat "execution_plan" list of shell commands for backward compatibility.
8. Output ONLY raw valid JSON. Do not wrap in markdown code blocks. No introductory or trailing text.
"""

HEAL_STEP_SCHEMA = """\
You MUST respond with ONLY a valid JSON object matching this schema layout:
{
  "diagnosis": "<string: brief explanation of why the command failed>",
  "can_recover": true,
  "recovery_steps": [
    {
      "step_id": "heal_1",
      "title": "<string: compensatory or alternative action>",
      "action_type": "shell",
      "command": "<string: fixed shell command or prerequisite install>",
      "require_root": false,
      "timeout": 30,
      "on_failure": "continue"
    }
  ]
}
"""


class GeminiEngineError(Exception):
    pass


class GeminiEngine:
    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise GeminiEngineError("Missing GEMINI_API_KEY")

        self._client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("GeminiEngine ready with multi-model contextual workflow compiler.")

    def execute(
        self,
        task: str,
        card: AgentCard,
        local_context: dict[str, Any],
    ) -> AgentResponse:
        system_prompt = self._build_system_prompt(card, local_context)
        tools = filter_tools_for_card(card.tools)
        user_message = self._build_user_message(task, local_context)

        selected_model = self._route_task_by_complexity(task)
        raw = self._call_gemini_with_fallback(selected_model, system_prompt, user_message, tools)
        return self._parse(raw)

    def heal_step(
        self,
        task: str,
        failed_step: WorkflowStep,
        error_output: str,
        accumulated_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Agentic self-healing: Analyzes a failed step and synthesizes compensatory recovery actions.
        """
        logger.info("GeminiEngine: synthesizing self-healing recovery for failed step: %s", failed_step.command or failed_step.tool_name)
        system_prompt = (
            "You are an expert Linux/Termux system debugger and agentic self-healing compiler.\n"
            "A workflow step failed during execution. Analyze the failure error output and provide\n"
            "compensatory recovery steps (e.g. missing package install, path fix, permission change, alternative binary).\n\n"
            + HEAL_STEP_SCHEMA
        )

        user_content = json.dumps({
            "overall_task": task,
            "failed_step": failed_step.model_dump(),
            "error_output": error_output[:1024],
            "context_variables": {k: str(v)[:256] for k, v in accumulated_context.items() if not k.startswith("_")},
        }, indent=2)

        try:
            raw = self._call_gemini_with_fallback(
                MODEL_COMPLEX,
                system_prompt,
                f"Diagnose and recover from this step failure:\n{user_content}",
                get_tool_definitions(),
            )
            cleaned = re.sub(r"```json|```", "", raw).strip()
            return json.loads(cleaned)
        except Exception as exc:
            logger.warning("GeminiEngine: self-healing synthesis failed: %s", exc)
            return {"diagnosis": f"Self-healing error: {exc}", "can_recover": False, "recovery_steps": []}

    # ------------------------------------------------------------------
    # PROMPT BUILDING
    # ------------------------------------------------------------------

    def _build_system_prompt(self, card: AgentCard, ctx: dict) -> str:
        safe_ctx = self._sanitize(ctx)
        current_cwd = safe_ctx.get("cwd", "/data/data/com.termux/files/home")

        context_block = ""
        if safe_ctx:
            context_block = "\n\n## CURRENT DEVICE CONTEXT:\n" + json.dumps(safe_ctx, indent=2)

        universal_rules = (
            f"\n\n## CRITICAL SHELL & WORKFLOW EXECUTION RULES:\n"
            f"1. Host Working Directory: {current_cwd}\n"
            f"2. NEVER call the client script './agent_cli.sh' recursively.\n"
            f"3. Use native Linux/Termux binaries directly ('date', 'ls', 'cat', 'pkg', 'am', 'dumpsys', 'svc').\n"
            f"4. If a step depends on previous step outputs, set 'capture_var': 'var_name' on the source step, "
            f"and reference '${{var_name}}' in subsequent steps.\n"
            f"5. All system-modifying or Android API commands requiring su MUST have require_root=true.\n"
        )

        return f"{card.system_prompt}{context_block}{universal_rules}\n\n{AGENT_WORKFLOW_SCHEMA}"

    def _build_user_message(self, task: str, ctx: dict) -> str:
        clipboard = (ctx.get("clipboard") or "")[:MAX_CONTEXT_VALUE_LEN]
        notifications = ctx.get("notifications")
        notif_str = ""
        if notifications and isinstance(notifications, list) and len(notifications) > 0:
            notif_str = f"\nActive Notifications: {json.dumps(notifications[:5])}"

        if clipboard:
            return f"Clipboard Content:\n{clipboard}{notif_str}\n\nUser Task:\n{task}"
        return f"{notif_str}\nUser Task:\n{task}".strip()

    def _sanitize(self, ctx: dict) -> dict:
        blocked = re.compile(r"(token|secret|password|auth|api_key)", re.I)
        out = {}
        for k, v in ctx.items():
            if blocked.search(k):
                out[k] = "[REDACTED]"
            else:
                s = str(v)
                out[k] = s[:MAX_CONTEXT_VALUE_LEN]
        return out

    # ------------------------------------------------------------------
    # LOAD BALANCER & ROUTING LOGIC
    # ------------------------------------------------------------------

    def _route_task_by_complexity(self, task: str) -> str:
        """Dynamically route complex workflows to Flash and high-frequency routine workflows to Flash-Lite."""
        complex_triggers = ["install", "compile", "setup", "fix", "debug", "create agent", "workflow", "script", "build", "pipeline"]
        if any(word in task.lower() for word in complex_triggers):
            logger.info("Routing complex synthesis task to %s", MODEL_COMPLEX)
            return MODEL_COMPLEX
        
        logger.info("Routing routine execution task to %s", MODEL_ROUTINE)
        return MODEL_ROUTINE

    def _call_gemini_with_fallback(self, primary_model: str, system: str, user: str, tools: list[dict]) -> str:
        """Executes call with single-shot 429 recovery and cascade to secondary model."""
        import time

        tool_names = [t["name"] for t in tools]
        full_system = f"{system}\nAVAILABLE_TOOLS:\n{json.dumps(tool_names)}"

        config = types.GenerateContentConfig(
            system_instruction=full_system,
            temperature=0.15,
            max_output_tokens=1500,
            response_mime_type="application/json",
        )

        secondary_model = MODEL_COMPLEX if primary_model == MODEL_ROUTINE else MODEL_ROUTINE
        
        for active_model in [primary_model, secondary_model]:
            try:
                logger.debug("Executing payload against: %s", active_model)
                resp = self._client.models.generate_content(
                    model=active_model,
                    contents=user,
                    config=config,
                )
                return resp.text or "{}"

            except Exception as exc:
                msg = str(exc)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    logger.warning("Model %s quota exhausted. Cascading route...", active_model)
                    continue

                if "404" in msg or "NOT_FOUND" in msg:
                    raise GeminiEngineError(f"Invalid Gemini model identifier: {active_model}") from exc

                raise GeminiEngineError(f"Gemini API failure: {msg}") from exc
        
        logger.error("Both models rate-limited. Initiating emergency cooldown...")
        time.sleep(30)
        
        try:
            resp = self._client.models.generate_content(
                model=MODEL_ROUTINE,
                contents=user,
                config=config,
            )
            return resp.text or "{}"
        except Exception as last_exc:
            raise GeminiEngineError(f"All model endpoints exhausted: {last_exc}") from last_exc

    # ------------------------------------------------------------------
    # PARSER & WORKFLOW SYNTHESIZER
    # ------------------------------------------------------------------

    def _parse(self, raw: str) -> AgentResponse:
        cleaned = re.sub(r"^```json\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)

        try:
            data = json.loads(cleaned)
        except Exception as exc:
            logger.error("JSON parse failed on raw output: %s", raw[:300])
            # Fallback wrapper
            return AgentResponse(
                reply=f"Executed task (raw output parse fallback).",
                execution_plan=[cleaned] if cleaned else [],
            )

        reply = data.get("reply", "")
        execution_plan = data.get("execution_plan", [])
        new_card = data.get("new_card")

        # Parse workflow plan if present
        workflow_data = data.get("workflow")
        workflow_plan: WorkflowPlan | None = None

        if isinstance(workflow_data, dict):
            raw_steps = workflow_data.get("steps", [])
            parsed_steps: list[WorkflowStep] = []
            for idx, s in enumerate(raw_steps, 1):
                if isinstance(s, dict):
                    parsed_steps.append(
                        WorkflowStep(
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
                        )
                    )
                elif isinstance(s, str):
                    parsed_steps.append(
                        WorkflowStep(
                            step_id=idx,
                            title=f"Execute command: {s[:40]}",
                            action_type="shell",
                            command=s,
                            on_failure="heal",
                        )
                    )

            verification_raw = workflow_data.get("verification")
            verification_step = None
            if isinstance(verification_raw, dict):
                verification_step = WorkflowStep(
                    step_id="verification",
                    title=verification_raw.get("title", "Verification"),
                    action_type=verification_raw.get("action_type", "shell"),
                    command=verification_raw.get("command"),
                    tool_name=verification_raw.get("tool_name"),
                    arguments=verification_raw.get("arguments", {}),
                    require_root=verification_raw.get("require_root", False),
                    timeout=verification_raw.get("timeout", 15),
                    on_failure="continue",
                )

            workflow_plan = WorkflowPlan(
                goal=workflow_data.get("goal", ""),
                summary=workflow_data.get("summary", reply),
                steps=parsed_steps,
                verification=verification_step,
            )

        elif execution_plan and isinstance(execution_plan, list):
            # Synthesize workflow from flat execution_plan
            synthesized_steps = [
                WorkflowStep(
                    step_id=i + 1,
                    title=f"Execute: {cmd[:40]}",
                    action_type="shell",
                    command=cmd,
                    on_failure="heal",
                )
                for i, cmd in enumerate(execution_plan)
                if isinstance(cmd, str)
            ]
            workflow_plan = WorkflowPlan(
                goal=reply,
                summary=reply,
                steps=synthesized_steps,
            )

        # Parse tool calls
        tool_calls = [
            ToolCall(
                tool_name=t["tool_name"],
                arguments=t.get("arguments", {}),
            )
            for t in data.get("tool_calls", [])
            if isinstance(t, dict) and "tool_name" in t
        ]

        return AgentResponse(
            reply=reply,
            workflow=workflow_plan,
            execution_plan=execution_plan if isinstance(execution_plan, list) else [],
            tool_calls=tool_calls,
            new_card=new_card,
        )

