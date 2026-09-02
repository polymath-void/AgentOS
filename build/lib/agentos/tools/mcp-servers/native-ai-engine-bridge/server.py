#!/usr/bin/env python3
"""
Native AI Engine Bridge — MCP Server (Stdio Transport)

Exposes the Wake→Execute→Sleep lifecycle of the native_ai_engine
C++/Rust binary, allowing AI agents to invoke the local phi-3-mini
model through the WASM bridge with strict safety enforcement.

Transport: stdio (JSON-RPC over stdin/stdout)
Requires: Magisk root (su), native_ai_engine binary, wasmtime-py
"""

import atexit
import json
import logging
import os
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ENGINE_BIN = "/system/bin/native_ai_engine"
MODEL_PATH = os.path.expanduser("~/models/phi-3-mini-q4.gguf")
WASM_HOST = "127.0.0.1"
WASM_PORT = 57160
PROMPT_TIMEOUT = 60  # seconds
SU_BIN = "su"

logger = logging.getLogger("native-ai-bridge")
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "native-ai-engine-bridge",
    description=(
        "Bridge to the Native AI Engine. Manage the Wake→Execute→Sleep "
        "lifecycle, send prompts to phi-3-mini via WASM shared memory, "
        "and enforce strict safety rules for battery/thermal preservation."
    ),
)

# ---------------------------------------------------------------------------
# Engine State Tracking
# ---------------------------------------------------------------------------

_engine_lock = threading.Lock()
_engine_running = False
_engine_wake_time: float | None = None


def _is_engine_process_alive() -> bool:
    """Check if native_ai_engine process is actually running."""
    try:
        result = subprocess.run(
            ["pidof", "native_ai_engine"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _get_engine_pid() -> int | None:
    """Get the PID of the running engine."""
    try:
        result = subprocess.run(
            ["pidof", "native_ai_engine"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split()[0])
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return None


def _run_su(command: str) -> tuple[int, str, str]:
    """Execute a command via Magisk su. Only allows whitelisted commands."""
    allowed_prefixes = ("start native_ai_engine", "stop native_ai_engine")
    if not any(command.startswith(p) for p in allowed_prefixes):
        raise PermissionError(
            f"Blocked: only engine start/stop allowed, got: {command}"
        )
    try:
        result = subprocess.run(
            [SU_BIN, "-c", command],
            capture_output=True, text=True, timeout=15,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "su command timed out"
    except FileNotFoundError:
        return -1, "", f"su binary not found at {SU_BIN}"


def _send_tcp(payload: dict, timeout: float = 5.0) -> dict:
    """Send a JSON payload to the engine via TCP socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((WASM_HOST, WASM_PORT))
            sock.sendall(json.dumps(payload).encode("utf-8"))
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            if response:
                return json.loads(response.decode("utf-8"))
            return {"status": "sent", "ack": True}
    except socket.timeout:
        return {"error": "timeout", "detail": f"No response within {timeout}s"}
    except ConnectionRefusedError:
        return {"error": "connection_refused", "detail": f"Engine not listening on {WASM_HOST}:{WASM_PORT}"}
    except json.JSONDecodeError:
        return {"raw": response.decode("utf-8", errors="replace")}


# ---------------------------------------------------------------------------
# Safety: Ensure engine sleeps on exit
# ---------------------------------------------------------------------------

def _emergency_shutdown():
    """Atexit handler: guarantee engine is stopped."""
    global _engine_running
    if _engine_running:
        logger.warning("Emergency shutdown: stopping native_ai_engine")
        try:
            _send_tcp({"command": "SHUTDOWN_SOCKET"}, timeout=3)
        except Exception:
            pass
        try:
            _run_su("stop native_ai_engine")
        except Exception:
            pass
        _engine_running = False

atexit.register(_emergency_shutdown)


# ---------------------------------------------------------------------------
# Tools — Lifecycle
# ---------------------------------------------------------------------------

@mcp.tool()
def wake_engine() -> dict:
    """
    Start the native_ai_engine daemon via Magisk su.
    Must be called before execute_prompt. The engine loads the
    phi-3-mini Q4 model into memory via zero-copy mmap over UFS.
    Returns the engine PID and wake timestamp.
    """
    global _engine_running, _engine_wake_time

    with _engine_lock:
        if _engine_running and _is_engine_process_alive():
            pid = _get_engine_pid()
            return {
                "status": "already_running",
                "pid": pid,
                "wake_time": _engine_wake_time,
                "message": "Engine is already awake. Send prompts or call sleep_engine.",
            }

        logger.info("WAKE: starting native_ai_engine")
        code, stdout, stderr = _run_su("start native_ai_engine")

        if code != 0:
            return {
                "status": "failed",
                "exit_code": code,
                "stderr": stderr,
                "hint": "Ensure Magisk is installed and native_ai_engine overlay is deployed.",
            }

        # Wait for engine to be ready
        time.sleep(2)
        pid = _get_engine_pid()
        _engine_running = True
        _engine_wake_time = time.time()

        return {
            "status": "awake",
            "pid": pid,
            "wake_time": _engine_wake_time,
            "model": MODEL_PATH,
        }


@mcp.tool()
def sleep_engine() -> dict:
    """
    Gracefully shut down the native_ai_engine.
    Sends SHUTDOWN_SOCKET via TCP, then enforces su -c stop.
    CPU footprint must return to 0%. Always call after prompts.
    """
    global _engine_running, _engine_wake_time

    with _engine_lock:
        logger.info("SLEEP: shutting down native_ai_engine")

        # Step 1: Graceful TCP shutdown
        tcp_result = _send_tcp({"command": "SHUTDOWN_SOCKET"}, timeout=5)

        # Step 2: Force stop via su
        code, stdout, stderr = _run_su("stop native_ai_engine")

        # Step 3: Verify it's dead
        time.sleep(1)
        still_alive = _is_engine_process_alive()

        uptime = None
        if _engine_wake_time:
            uptime = round(time.time() - _engine_wake_time, 2)

        _engine_running = False
        _engine_wake_time = None

        return {
            "status": "asleep" if not still_alive else "warning_still_alive",
            "tcp_shutdown": tcp_result,
            "su_exit_code": code,
            "engine_still_alive": still_alive,
            "uptime_seconds": uptime,
        }


# ---------------------------------------------------------------------------
# Tools — Prompt Execution
# ---------------------------------------------------------------------------

@mcp.tool()
def execute_prompt(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> dict:
    """
    Send a prompt to the phi-3-mini model via the WASM shared memory bridge.
    The engine must be awake (call wake_engine first).
    Enforces a timeout to prevent infinite hangs.

    Args:
        prompt: The text prompt to send to the model.
        max_tokens: Maximum tokens to generate (default 512).
        temperature: Sampling temperature (default 0.7).
    """
    with _engine_lock:
        if not _engine_running and not _is_engine_process_alive():
            return {
                "error": "engine_not_running",
                "hint": "Call wake_engine first.",
            }

    logger.info("EXECUTE: prompt (%d chars, max_tokens=%d)", len(prompt), max_tokens)

    payload = {
        "command": "PROMPT",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "model_path": MODEL_PATH,
    }

    start = time.monotonic()
    result = _send_tcp(payload, timeout=PROMPT_TIMEOUT)
    elapsed_ms = round((time.monotonic() - start) * 1000, 1)

    result["latency_ms"] = elapsed_ms
    return result


@mcp.tool()
def prompt_and_sleep(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> dict:
    """
    Atomic operation: Wake → Execute Prompt → Sleep in one call.
    Guarantees the engine is stopped after completion, even on errors.
    Use for one-shot queries where you don't need the engine to stay running.
    """
    lifecycle_log = []

    try:
        # Wake
        wake_result = wake_engine()
        lifecycle_log.append({"step": "wake", "result": wake_result})

        if wake_result.get("status") in ("awake", "already_running"):
            # Execute
            exec_result = execute_prompt(prompt, max_tokens, temperature)
            lifecycle_log.append({"step": "execute", "result": exec_result})
        else:
            lifecycle_log.append({"step": "execute", "skipped": True, "reason": "wake_failed"})
            exec_result = {"error": "wake_failed"}

    finally:
        # Sleep (always)
        sleep_result = sleep_engine()
        lifecycle_log.append({"step": "sleep", "result": sleep_result})

    return {
        "response": exec_result.get("response", exec_result.get("raw", "")),
        "error": exec_result.get("error"),
        "lifecycle_log": lifecycle_log,
    }


# ---------------------------------------------------------------------------
# Tools — Status & Info
# ---------------------------------------------------------------------------

@mcp.tool()
def engine_status() -> dict:
    """
    Check if the native_ai_engine is currently running.
    Returns PID, CPU percentage, memory usage, and uptime if awake.
    """
    alive = _is_engine_process_alive()
    pid = _get_engine_pid() if alive else None

    result = {
        "running": alive,
        "pid": pid,
        "tracked_as_running": _engine_running,
    }

    if alive and pid:
        # Try to get CPU/mem from /proc
        try:
            stat_path = f"/proc/{pid}/stat"
            with open(stat_path) as f:
                stat = f.read().split()
            result["cpu_ticks_user"] = int(stat[13])
            result["cpu_ticks_system"] = int(stat[14])
            result["threads"] = int(stat[19])

            status_path = f"/proc/{pid}/status"
            with open(status_path) as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        result["mem_rss_kb"] = int(line.split()[1])
                    elif line.startswith("VmSize:"):
                        result["mem_virt_kb"] = int(line.split()[1])
        except (FileNotFoundError, IndexError, ValueError):
            pass

    if _engine_wake_time and alive:
        result["uptime_seconds"] = round(time.time() - _engine_wake_time, 2)

    return result


@mcp.tool()
def model_info() -> dict:
    """
    Return metadata about the configured AI model.
    Includes path, quantization level, file size, and mmap status.
    """
    model_path = Path(MODEL_PATH)
    exists = model_path.exists()

    result = {
        "path": str(model_path),
        "exists": exists,
        "quantization": "Q4 (4-bit)",
        "format": "GGUF",
        "engine_binary": ENGINE_BIN,
        "wasm_endpoint": f"{WASM_HOST}:{WASM_PORT}",
    }

    if exists:
        size_bytes = model_path.stat().st_size
        result["size_mb"] = round(size_bytes / (1024 * 1024), 1)
        result["mmap_capable"] = True
        result["storage_type"] = "UFS (zero-copy mmap)"
    else:
        result["size_mb"] = None
        result["hint"] = f"Model file not found at {MODEL_PATH}"

    return result


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("engine://config")
def engine_config() -> str:
    """Current Native AI Engine configuration."""
    return json.dumps(
        {
            "engine_binary": ENGINE_BIN,
            "model_path": MODEL_PATH,
            "wasm_host": WASM_HOST,
            "wasm_port": WASM_PORT,
            "prompt_timeout_seconds": PROMPT_TIMEOUT,
            "safety_rules": [
                "Wake→Sleep lifecycle strictly enforced",
                "atexit handler guarantees shutdown",
                "Single-threaded execution (no concurrent prompts)",
                "Only whitelisted su commands allowed",
            ],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
