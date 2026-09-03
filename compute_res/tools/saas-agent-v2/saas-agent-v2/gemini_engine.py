"""
gemini_engine.py — Gemini engine with dynamic API key and model support.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from google import genai
from google.genai import types

from intent_router import classify_with_recommendation
from models import AgentCard, AgentResponse, ToolCall
from tool_registry import filter_tools_for_card

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

AGENT_RESPONSE_SCHEMA = """\
Respond ONLY with valid JSON (no fences):
{
  "thought": "<internal reasoning>",
  "reply": "<human-facing message>",
  "tool_calls": [{"tool_name": "...", "arguments": {...}}],
  "json_data": null,
  "summary_points": [],
  "execution_mode": "function_calling|json_structured|summarization",
  "new_card": null
}
"""


class GeminiEngineError(Exception):
    """LLM engine error."""


class GeminiEngine:
    """Stateless LLM engine with dynamic model and key support."""

    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set in environment. Use header to provide key.")
        self._api_key = GEMINI_API_KEY
        self._model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = genai.Client(api_key=self._api_key) if self._api_key else None
        logger.info(f"GeminiEngine: initialized with {self._model}")

    def execute(
        self,
        task: str,
        card: AgentCard,
        local_context: dict[str, Any],
        available_cards: list[AgentCard] | None = None,
    ) -> AgentResponse:
        """Execute task using card's preferred mode."""
        if not self._api_key:
            raise GeminiEngineError("No API key provided.")

        mode = card.execution_mode
        system_prompt = self._build_system_prompt(card, local_context, mode)
        tools = filter_tools_for_card(card.tools)
        user_message = self._build_user_message(task, local_context)

        logger.debug(f"execute: card={card.name} mode={mode} model={self._model}")

        raw = self._call_gemini(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=tools,
            mode=mode,
        )
        return self._parse_response(raw, mode)

    def _build_system_prompt(
        self, card: AgentCard, context: dict, mode: str
    ) -> str:
        """Build system prompt with mode-specific instructions."""
        context_block = ""
        if context:
            lines = "\n".join(f"  {k}: {str(v)[:100]}" for k, v in context.items())
            context_block = f"\n\n## Device Context\n{lines}"

        mode_instruction = {
            "function_calling": (
                "\n\n## Execution Mode: Function Calling\n"
                "You MUST invoke tools to execute tasks. "
                "Use tool_calls array with exact tool_name and arguments."
            ),
            "json_structured": (
                "\n\n## Execution Mode: JSON Structured\n"
                "Return structured JSON data in json_data field."
            ),
            "summarization": (
                "\n\n## Execution Mode: Summarization\n"
                "Generate 5-10 bullet point summary in summary_points array."
            ),
        }

        return (
            f"{card.system_prompt}"
            f"{context_block}"
            f"{mode_instruction.get(mode, '')}"
            f"\n\n## Response Format\n{AGENT_RESPONSE_SCHEMA}"
        )

    def _build_user_message(self, task: str, context: dict) -> str:
        clipboard = context.get("clipboard", "").strip()
        if clipboard:
            return f"Clipboard:\n{clipboard[:500]}\n\nTask: {task}"
        return f"Task: {task}"

    def _call_gemini(
        self, system_prompt: str, user_message: str, tools: list[dict], mode: str
    ) -> str:
        """Call Gemini with dynamic model and key."""
        if not self._client:
            self._client = genai.Client(api_key=self._api_key)

        tool_hint = f"\n## Tools\n{json.dumps([t['name'] for t in tools], indent=2)}\n"

        config = types.GenerateContentConfig(
            system_instruction=system_prompt + tool_hint,
            temperature=0.2,
            top_p=0.95,
            max_output_tokens=2048 if mode == "function_calling" else 4096,
            response_mime_type="application/json",
        )

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user_message,
                config=config,
            )
            return response.text
        except Exception as exc:
            raise GeminiEngineError(f"Gemini API failed: {exc}") from exc

    def _parse_response(self, raw: str, mode: str) -> AgentResponse:
        """Parse JSON response."""
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise GeminiEngineError(f"Non-JSON response: {raw[:300]!r}") from exc

        tool_calls = [
            ToolCall(tool_name=tc.get("tool_name", ""), arguments=tc.get("arguments", {}))
            for tc in data.get("tool_calls", [])
            if isinstance(tc, dict) and tc.get("tool_name")
        ]

        try:
            return AgentResponse(
                thought=data.get("thought", ""),
                reply=data.get("reply", ""),
                tool_calls=tool_calls,
                json_data=data.get("json_data"),
                summary_points=data.get("summary_points", []),
                execution_mode=mode,
                new_card=None,
            )
        except Exception as exc:
            raise GeminiEngineError(f"Response validation failed: {exc}") from exc
