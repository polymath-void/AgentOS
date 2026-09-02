"""
tool_executor.py — Executes tool calls dispatched from GeminiEngine.

Each function mirrors a tool definition in tool_registry.py.
All executors return a dict with at least {"status": "ok"|"error", "output": str}.
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

import httpx

import card_store
from models import AgentCard, ToolCall

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Individual tool implementations
# ---------------------------------------------------------------------------


def _run_shell_command(
    command: str,
    timeout: int = 30,
    require_root: bool = False,
) -> dict:
    """
    Execute a shell command. If require_root=True, attempts root via `su -c`.
    If root execution fails, is denied, or returns non-zero, falls back to non-root shell execution.
    """
    if require_root:
        argv = ["su", "-c", command]
        try:
            result = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0:
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                return {
                    "status": "ok",
                    "returncode": 0,
                    "output": stdout or stderr or "(no output, returncode=0)",
                    "stderr": stderr if (stderr and stdout) else "",
                    "executed_with_root": True,
                }
            logger.warning("Root command su returned code %d, attempting non-root fallback...", result.returncode)
        except Exception as exc:
            logger.warning("Root execution failed (%s), attempting non-root fallback...", exc)

    # Standard non-root shell execution (default or fallback)
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": f"Command timed out after {timeout}s."}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    output = stdout or stderr or f"(no output, returncode={result.returncode})"
    status = "ok" if result.returncode == 0 else "error"

    return {
        "status": status,
        "returncode": result.returncode,
        "output": output,
        "stderr": stderr if (stderr and stdout) else "",
        "executed_with_root": False,
    }



def _read_file(path: str, max_bytes: int = 8192) -> dict:
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return {"status": "error", "output": f"File not found: {path}"}
        content = p.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
        truncated = len(p.read_bytes()) > max_bytes
        return {
            "status": "ok",
            "output": content,
            "truncated": truncated,
            "path": str(p),
        }
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _write_file(path: str, content: str, append: bool = False) -> dict:
    try:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        if append:
            with open(p, "a", encoding="utf-8") as f:
                f.write(content)
        else:
            p.write_text(content, encoding="utf-8")
        return {"status": "ok", "output": f"Written to {p} ({'appended' if append else 'overwritten'})."}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}



def _get_clipboard() -> dict:
    """Try Termux API first, then xclip/xsel for desktop Linux."""
    for cmd in ["termux-clipboard-get", "xclip -o", "xsel --output"]:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return {"status": "ok", "output": result.stdout.strip()}
    return {"status": "error", "output": "No clipboard tool available (termux-clipboard-get / xclip / xsel)."}


def _set_clipboard(content: str) -> dict:
    for cmd in [
        f"echo {content!r} | termux-clipboard-set",
        f"echo {content!r} | xclip -selection clipboard",
        f"echo {content!r} | xsel --clipboard --input",
    ]:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return {"status": "ok", "output": "Clipboard updated."}
    return {"status": "error", "output": "No clipboard write tool available."}


def _list_agent_cards() -> dict:
    cards = card_store.list_cards()
    return {"status": "ok", "output": cards}


def _create_agent_card(
    name: str,
    system_prompt: str,
    description: str = "",
    tools: list[str] | None = None,
) -> dict:
    try:
        card = AgentCard(
            name=name,
            description=description,
            system_prompt=system_prompt,
            tools=tools or [],
        )
        saved = card_store.save_card(card)
        return {
            "status": "ok",
            "output": f"AgentCard '{saved.name}' created with id={saved.id}.",
            "card_id": saved.id,
            "card": saved.model_dump(),
        }
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _delete_agent_card(card_id: str) -> dict:
    try:
        deleted = card_store.delete_card(card_id)
        if deleted:
            return {"status": "ok", "output": f"Card {card_id} deleted."}
        return {"status": "error", "output": f"Card {card_id} not found."}
    except card_store.CardStoreError as exc:
        return {"status": "error", "output": str(exc)}


def _http_get(url: str, headers: dict | None = None, timeout: int = 15) -> dict:
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url, headers=headers or {})
            return {
                "status": "ok",
                "http_status": resp.status_code,
                "output": resp.text[:4096],
            }
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_DISPATCH: dict = {
    "run_shell_command": _run_shell_command,
    "read_file": _read_file,
    "write_file": _write_file,
    "get_clipboard": _get_clipboard,
    "set_clipboard": _set_clipboard,
    "list_agent_cards": _list_agent_cards,
    "create_agent_card": _create_agent_card,
    "delete_agent_card": _delete_agent_card,
    "http_get": _http_get,
}


def execute_tool(tool_call: ToolCall) -> dict:
    """
    Dispatch a ToolCall to its executor.

    Returns a result dict with at least {"status": "ok"|"error", "output": ...}.
    Never raises — errors are captured and returned as {"status": "error", ...}.
    """
    fn = _DISPATCH.get(tool_call.tool_name)
    if fn is None:
        return {
            "status": "error",
            "output": f"Unknown tool: {tool_call.tool_name!r}. "
                      f"Available: {list(_DISPATCH.keys())}",
        }
    logger.info("tool_executor: calling %s args=%s", tool_call.tool_name, tool_call.arguments)
    try:
        return fn(**tool_call.arguments)
    except TypeError as exc:
        return {
            "status": "error",
            "output": f"Bad arguments for {tool_call.tool_name}: {exc}",
        }
    except Exception as exc:
        logger.exception("tool_executor: unhandled error in %s", tool_call.tool_name)
        return {"status": "error", "output": str(exc)}
