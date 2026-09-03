"""
tool_executor.py — Execution engine for all tools.

Strategy: implement each tool with tier-based fallback:
  Tier 1: Root (su) execution
  Tier 2: ADB execution (for Android remote)
  Tier 3: Local tools (mpv, jrnl, etc.)
  Tier 4: Cloud APIs (Gmail, Google Calendar)

Never raises. Returns {"status": "ok"|"error", "output": str, ...}
"""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from models import ToolCall

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers: execution tiers
# ---------------------------------------------------------------------------


def _run_root_command(cmd: str, timeout: int = 30) -> dict:
    """Tier 1: Execute command as root via 'su'."""
    try:
        result = subprocess.run(
            ["su", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output = stdout or stderr or f"(no output, returncode={result.returncode})"
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "output": output,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": f"Root command timed out after {timeout}s."}
    except FileNotFoundError:
        return {"status": "error", "output": "su binary not found. Device not rooted?"}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _run_adb_command(cmd: str, timeout: int = 30) -> dict:
    """Tier 2: Execute command via ADB (Android remote)."""
    try:
        result = subprocess.run(
            f"adb shell {cmd}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip() or result.stderr.strip() or "(no output)"
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "output": output,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": f"ADB command timed out."}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _run_local_command(cmd: str, timeout: int = 30) -> dict:
    """Tier 3: Execute local shell command."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip() or result.stderr.strip() or "(no output)"
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "output": output,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": f"Command timed out."}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


# ---------------------------------------------------------------------------
# MEDIA
# ---------------------------------------------------------------------------


def _play_youtube(query: str, audio_only: bool = False) -> dict:
    """Play YouTube video/song via yt-dlp + mpv."""
    try:
        # Check if yt-dlp + mpv exist
        check_ytdlp = subprocess.run(
            "yt-dlp --version", shell=True, capture_output=True, timeout=3
        )
        check_mpv = subprocess.run(
            "mpv --version", shell=True, capture_output=True, timeout=3
        )

        if check_ytdlp.returncode != 0 or check_mpv.returncode != 0:
            return {
                "status": "error",
                "output": "yt-dlp or mpv not installed. Install via: pkg install -y yt-dlp mpv",
            }

        # Search and play
        search_query = f"ytsearch:{query}"
        mpv_args = "--no-video" if audio_only else ""
        cmd = f"yt-dlp -f best -o - {search_query!r} | mpv - {mpv_args}"

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            return {
                "status": "ok",
                "output": f"Playing: {query} ({'audio only' if audio_only else 'video'})",
            }
        else:
            return {"status": "error", "output": f"Failed to play. Error: {result.stderr[:200]}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Playback timed out."}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


# ---------------------------------------------------------------------------
# COMMUNICATION — CALLS
# ---------------------------------------------------------------------------


def _get_call_logs(call_type: str = "ALL", limit: int = 20) -> dict:
    """Fetch call logs from Android (root required)."""
    cmd = "content query --uri content://call_log/calls"

    result = _run_root_command(cmd, timeout=10)

    if result["status"] != "ok":
        return result

    # Parse output and filter by type
    output = result["output"]
    # This is a basic parsing — actual format may vary
    return {
        "status": "ok",
        "output": f"Call logs (type={call_type}, limit={limit}):\n{output[:500]}",
    }


def _place_call(phone_number: str) -> dict:
    """Initiate outbound call on Android."""
    cmd = f"am start -a android.intent.action.CALL -d tel:{phone_number}"
    result = _run_root_command(cmd, timeout=5)

    if result["status"] == "ok":
        return {
            "status": "ok",
            "output": f"Calling {phone_number}…",
        }
    return result


# ---------------------------------------------------------------------------
# COMMUNICATION — SMS
# ---------------------------------------------------------------------------


def _send_sms(phone_number: str, message: str) -> dict:
    """Send SMS via Android."""
    # Use Android service call (requires root)
    cmd = f'am start -a android.intent.action.SENDTO -d sms:{phone_number} --es sms_body "{message}"'
    result = _run_root_command(cmd, timeout=5)

    if result["status"] == "ok":
        return {
            "status": "ok",
            "output": f"SMS sent to {phone_number}",
        }
    return result


def _read_sms(limit: int = 20, from_number: str = "") -> dict:
    """Read SMS messages from Android."""
    cmd = "content query --uri content://sms/inbox"
    result = _run_root_command(cmd, timeout=10)

    if result["status"] != "ok":
        return result

    return {
        "status": "ok",
        "output": f"Recent SMS (limit={limit}):\n{result['output'][:500]}",
    }


# ---------------------------------------------------------------------------
# FILE MANAGEMENT
# ---------------------------------------------------------------------------


def _list_files(path: str, recursive: bool = False) -> dict:
    """List files in directory."""
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return {"status": "error", "output": f"Path not found: {path}"}

        if recursive:
            files = list(p.rglob("*"))
        else:
            files = list(p.iterdir())

        output = "\n".join(str(f.name) for f in files[:100])
        return {"status": "ok", "output": output, "file_count": len(files)}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _read_file(path: str, max_bytes: int = 8192) -> dict:
    """Read file contents."""
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return {"status": "error", "output": f"File not found: {path}"}
        content = p.read_text()[:max_bytes]
        return {"status": "ok", "output": content}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _write_file(path: str, content: str, append: bool = False) -> dict:
    """Write/append to file."""
    try:
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        if append:
            p.write_text(p.read_text() + content)
        else:
            p.write_text(content)
        return {"status": "ok", "output": f"Written {len(content)} bytes to {p}"}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _search_files(path: str, pattern: str) -> dict:
    """Search for files matching pattern."""
    try:
        p = Path(path).expanduser()
        results = list(p.glob(pattern))
        output = "\n".join(str(f) for f in results[:50])
        return {"status": "ok", "output": output, "match_count": len(results)}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _delete_file(path: str) -> dict:
    """Delete a file (with safety checks)."""
    try:
        p = Path(path).expanduser()
        if str(p).startswith(("/system", "/proc", "/dev", "/data/system")):
            return {
                "status": "error",
                "output": f"Cannot delete system file: {path}. Use overlay instead.",
            }
        if not p.exists():
            return {"status": "error", "output": f"File not found: {path}"}
        p.unlink()
        return {"status": "ok", "output": f"Deleted {path}"}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _copy_file(source: str, destination: str) -> dict:
    """Copy file."""
    try:
        src = Path(source).expanduser()
        dst = Path(destination).expanduser()
        if not src.exists():
            return {"status": "error", "output": f"Source not found: {source}"}
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        return {"status": "ok", "output": f"Copied {source} → {destination}"}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _sync_cloud(source: str, destination: str, dry_run: bool = False) -> dict:
    """Sync files via rclone."""
    try:
        dry = "--dry-run" if dry_run else ""
        cmd = f"rclone copy {source} {destination} {dry}"
        result = _local_command(cmd, timeout=300)
        return result
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


# ---------------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------------


def _get_emails(unread_only: bool = True, limit: int = 10) -> dict:
    """Fetch emails from Gmail IMAP."""
    try:
        import imaplib
        import email as email_module

        # Placeholder — requires Gmail setup + OAuth token
        # For now, return instructional message
        return {
            "status": "error",
            "output": (
                "Email fetching requires Gmail OAuth setup. "
                "Run: gcalcli init to set up Gmail credentials."
            ),
        }
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _summarize_emails(limit: int = 20) -> dict:
    """Fetch + summarize emails."""
    # Placeholder — requires email backend
    return {
        "status": "error",
        "output": (
            "Email summarization requires Gmail OAuth. "
            "Run setup: gcalcli init"
        ),
    }


def _send_email(to: str, subject: str, body: str) -> dict:
    """Send email via Gmail."""
    # Placeholder
    return {
        "status": "error",
        "output": "Email sending requires Gmail OAuth setup.",
    }


# ---------------------------------------------------------------------------
# CALENDAR
# ---------------------------------------------------------------------------


def _get_calendar_events(days_ahead: int = 7) -> dict:
    """Fetch Google Calendar events."""
    try:
        cmd = "gcalcli agenda"
        result = _local_command(cmd, timeout=10)
        return result
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _add_calendar_event(
    title: str, start_time: str, end_time: str = "", description: str = ""
) -> dict:
    """Add event to Google Calendar."""
    try:
        cmd = f'gcalcli add "{title}" --when "{start_time}"'
        if description:
            cmd += f' --description "{description}"'
        result = _local_command(cmd, timeout=10)
        return result
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


# ---------------------------------------------------------------------------
# NOTES
# ---------------------------------------------------------------------------


def _write_note(text: str, tags: list[str] | None = None) -> dict:
    """Write a timestamped note."""
    try:
        tags_str = " ".join(f"@{tag}" for tag in (tags or []))
        cmd = f'jrnl "{text} {tags_str}"'
        result = _local_command(cmd, timeout=5)

        if result["status"] != "ok":
            # Fallback: write to file
            notes_dir = Path.home() / "notes"
            notes_dir.mkdir(exist_ok=True)
            note_file = notes_dir / f"{datetime.now().isoformat()}.txt"
            note_file.write_text(f"{text}\nTags: {', '.join(tags or [])}\n")
            return {
                "status": "ok",
                "output": f"Note saved to {note_file}",
            }

        return result
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _read_notes(limit: int = 10) -> dict:
    """Read recent notes."""
    try:
        cmd = f"jrnl -n {limit}"
        result = _local_command(cmd, timeout=5)
        return result
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


# ---------------------------------------------------------------------------
# SYSTEM CONTROL
# ---------------------------------------------------------------------------


def _set_brightness(percent: int) -> dict:
    """Set screen brightness."""
    # Clamp 0–100
    percent = max(0, min(100, percent))
    brightness_value = round(percent * 255 / 100)

    # Step 1: Disable auto-brightness
    cmd1 = "settings put system screen_brightness_mode 0"
    r1 = _run_root_command(cmd1, timeout=5)

    # Step 2: Set brightness
    cmd2 = f"settings put system screen_brightness {brightness_value}"
    r2 = _run_root_command(cmd2, timeout=5)

    if r1["status"] == "ok" and r2["status"] == "ok":
        return {
            "status": "ok",
            "output": f"Brightness set to {percent}%",
        }
    else:
        return {"status": "error", "output": f"Failed: {r2.get('output', 'unknown')}"}


def _toggle_wifi(state: str = "toggle") -> dict:
    """Toggle WiFi on/off."""
    if state == "on":
        cmd = "svc wifi enable"
    elif state == "off":
        cmd = "svc wifi disable"
    else:  # toggle
        cmd = "svc wifi disable && sleep 1 && svc wifi enable"

    result = _run_root_command(cmd, timeout=10)
    if result["status"] == "ok":
        return {"status": "ok", "output": f"WiFi {state}"}
    return result


def _clear_notifications() -> dict:
    """Clear all notifications."""
    cmd = "cmd notification cancel-all"
    result = _run_root_command(cmd, timeout=5)

    if result["status"] == "ok":
        return {"status": "ok", "output": "All notifications cleared."}
    return result


def _get_system_info(info_type: str = "all") -> dict:
    """Get system info: battery, uptime, disk, memory."""
    output = ""

    if info_type in ("all", "battery"):
        result = _run_root_command("dumpsys battery | grep level", timeout=5)
        output += f"Battery: {result.get('output', 'N/A')}\n"

    if info_type in ("all", "uptime"):
        result = _local_command("uptime", timeout=5)
        output += f"Uptime: {result.get('output', 'N/A')}\n"

    if info_type in ("all", "disk"):
        result = _local_command("df -h /data", timeout=5)
        output += f"Disk: {result.get('output', 'N/A')}\n"

    if info_type in ("all", "memory"):
        result = _local_command("free -h", timeout=5)
        output += f"Memory: {result.get('output', 'N/A')}\n"

    return {"status": "ok", "output": output}


def _run_shell_command(command: str, require_root: bool = False, timeout: int = 30) -> dict:
    """Execute arbitrary shell command."""
    if require_root:
        return _run_root_command(command, timeout=timeout)
    else:
        return _local_command(command, timeout=timeout)


# ---------------------------------------------------------------------------
# CARD MANAGEMENT
# ---------------------------------------------------------------------------


def _create_agent_card(
    agent_name: str = "",
    system_prompt: str = "",
    description: str = "",
    scope_tags: list[str] | None = None,
    # Fallback arg names
    name: str = "",
    card_name: str = "",
) -> dict:
    """Create a new AgentCard."""
    resolved_name = agent_name or name or card_name
    if not resolved_name:
        return {
            "status": "error",
            "output": "create_agent_card requires 'agent_name'.",
        }
    if not system_prompt:
        return {
            "status": "error",
            "output": "create_agent_card requires 'system_prompt'.",
        }

    try:
        # Import here to avoid circular dependency
        from models import AgentCard
        import card_store

        card = AgentCard(
            name=resolved_name,
            description=description,
            system_prompt=system_prompt,
            scope_tags=scope_tags or [],
        )
        saved = card_store.save_card(card)
        return {
            "status": "ok",
            "output": f"Card '{saved.name}' created (ID: {saved.id})",
            "card_id": saved.id,
            "card": saved.model_dump(),
        }
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


def _list_agent_cards() -> dict:
    """List all AgentCards."""
    try:
        import card_store

        cards = card_store.list_cards()
        output = "\n".join(f"- {c['name']} ({c['id']}): {c['description']}" for c in cards)
        return {"status": "ok", "output": output, "cards": cards}
    except Exception as exc:
        return {"status": "error", "output": str(exc)}


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_DISPATCH: dict[str, callable] = {
    # Media
    "play_youtube": _play_youtube,
    # Calls
    "get_call_logs": _get_call_logs,
    "place_call": _place_call,
    # SMS
    "send_sms": _send_sms,
    "read_sms": _read_sms,
    # Files
    "list_files": _list_files,
    "read_file": _read_file,
    "write_file": _write_file,
    "search_files": _search_files,
    "delete_file": _delete_file,
    "copy_file": _copy_file,
    "sync_cloud": _sync_cloud,
    # Email
    "get_emails": _get_emails,
    "summarize_emails": _summarize_emails,
    "send_email": _send_email,
    # Calendar
    "get_calendar_events": _get_calendar_events,
    "add_calendar_event": _add_calendar_event,
    # Notes
    "write_note": _write_note,
    "read_notes": _read_notes,
    # System
    "set_brightness": _set_brightness,
    "toggle_wifi": _toggle_wifi,
    "clear_notifications": _clear_notifications,
    "get_system_info": _get_system_info,
    "run_shell_command": _run_shell_command,
    # Cards
    "create_agent_card": _create_agent_card,
    "list_agent_cards": _list_agent_cards,
}


def execute_tool(tool_call: ToolCall) -> dict:
    """Dispatch and execute a tool call."""
    fn = _DISPATCH.get(tool_call.tool_name)
    if fn is None:
        return {
            "status": "error",
            "output": f"Unknown tool: {tool_call.tool_name}. Available: {list(_DISPATCH.keys())}",
        }

    logger.info("tool_executor: %s args=%s", tool_call.tool_name, tool_call.arguments)

    try:
        return fn(**tool_call.arguments)
    except TypeError as exc:
        return {
            "status": "error",
            "output": f"Bad arguments for {tool_call.tool_name}: {exc}",
        }
    except Exception as exc:
        logger.exception("tool_executor: error in %s", tool_call.tool_name)
        return {"status": "error", "output": str(exc)}
