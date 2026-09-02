"""
dependency_manager.py — Auto-install system dependencies.

On startup, checks if required tools exist. If missing, attempts installation via:
  1. pkg (Termux package manager)
  2. pip (Python packages)
  3. apt-get (Linux fallback)

Never fails hard — logs warnings for missing tools, agent degrades gracefully.
"""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Detect environment
# ---------------------------------------------------------------------------

IS_TERMUX = os.path.exists("/data/data/com.termux") or "TERMUX_VERSION" in os.environ
IS_LINUX = os.name == "posix" and not IS_TERMUX


# ---------------------------------------------------------------------------
# Tool registry: (cmd, install_cmd_termux, install_cmd_linux, pip_package, description)
# ---------------------------------------------------------------------------

TOOLS: dict[str, tuple[str, str, str, str, str]] = {
    # Media
    "mpv": (
        "mpv --version",
        "pkg install -y mpv",
        "apt-get install -y mpv",
        "",
        "video/audio player (YouTube streaming)",
    ),
    "yt-dlp": (
        "yt-dlp --version",
        "pkg install -y yt-dlp",
        "apt-get install -y yt-dlp",
        "yt-dlp",
        "YouTube downloader + metadata",
    ),
    # Calendar
    "gcalcli": (
        "gcalcli --version",
        "pip install gcalcli",
        "pip install gcalcli",
        "gcalcli",
        "Google Calendar CLI",
    ),
    # Notes
    "jrnl": (
        "jrnl --version",
        "pip install jrnl",
        "pip install jrnl",
        "jrnl",
        "Journal/note-taking CLI",
    ),
    # System
    "curl": (
        "curl --version",
        "pkg install -y curl",
        "apt-get install -y curl",
        "",
        "HTTP client",
    ),
    "jq": (
        "jq --version",
        "pkg install -y jq",
        "apt-get install -y jq",
        "",
        "JSON processor",
    ),
    # File/network
    "rclone": (
        "rclone version",
        "pkg install -y rclone",
        "apt-get install -y rclone",
        "rclone",
        "Cloud file sync (AWS S3, Google Drive, etc.)",
    ),
    "sqlite3": (
        "sqlite3 --version",
        "pkg install -y sqlite",
        "apt-get install -y sqlite3",
        "",
        "SQLite CLI",
    ),
}

# Python packages (imported, not CLI)
PYTHON_PACKAGES: dict[str, tuple[str, str, str]] = {
    "google": (
        "google-genai>=1.0.0",
        "Google Generative AI SDK",
    ),
    "imaplib": (
        "# stdlib",
        "IMAP email access (stdlib)",
    ),
    "twilio": (
        "twilio",
        "Twilio voice/SMS API (optional for calling)",
    ),
}


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def _check_command_exists(cmd: str) -> bool:
    """Return True if command is available."""
    try:
        subprocess.run(
            f"{cmd}",
            shell=True,
            capture_output=True,
            timeout=3,
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def _check_python_import(module: str) -> bool:
    """Return True if Python module can be imported."""
    try:
        __import__(module)
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------

def _install_tool(name: str, cmd_check: str, cmd_install: str) -> bool:
    """Attempt to install a single tool. Return True if successful."""
    try:
        logger.info(f"dependency_manager: installing {name}…")
        subprocess.run(
            cmd_install,
            shell=True,
            capture_output=True,
            timeout=60,
            check=True,
        )
        if _check_command_exists(cmd_check):
            logger.info(f"dependency_manager: {name} installed successfully.")
            return True
        else:
            logger.warning(f"dependency_manager: {name} installed but not found in PATH.")
            return False
    except subprocess.CalledProcessError as e:
        logger.warning(f"dependency_manager: failed to install {name}: {e.stderr.decode()[:200]}")
        return False
    except Exception as e:
        logger.warning(f"dependency_manager: error installing {name}: {e}")
        return False


def _install_pip_package(package: str) -> bool:
    """Attempt pip install of a package."""
    try:
        logger.info(f"dependency_manager: installing {package} via pip…")
        subprocess.run(
            f"pip install --break-system-packages {package}",
            shell=True,
            capture_output=True,
            timeout=120,
            check=True,
        )
        logger.info(f"dependency_manager: {package} installed.")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"dependency_manager: pip install {package} failed: {e.stderr.decode()[:200]}")
        return False
    except Exception as e:
        logger.warning(f"dependency_manager: error pip installing {package}: {e}")
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_and_install_dependencies() -> dict[str, bool]:
    """
    Check all tools. Install missing ones automatically (best-effort).
    Return {tool_name: is_available} for logging/debugging.

    Never raises. Logs warnings for unavailable tools.
    """
    logger.info(
        f"dependency_manager: checking tools (Termux={IS_TERMUX}, Linux={IS_LINUX})…"
    )

    results: dict[str, bool] = {}

    # Check and install CLI tools
    for tool_name, (cmd_check, cmd_termux, cmd_linux, pip_pkg, description) in TOOLS.items():
        if _check_command_exists(cmd_check):
            logger.debug(f"  OK  {tool_name}")
            results[tool_name] = True
            continue

        logger.warning(f"  MISSING  {tool_name} — {description}")

        # Determine install command
        install_cmd = cmd_termux if IS_TERMUX else cmd_linux
        if not install_cmd:
            logger.warning(f"    No install command for {tool_name}. Skipping.")
            results[tool_name] = False
            continue

        # Attempt installation
        if _install_tool(tool_name, cmd_check, install_cmd):
            results[tool_name] = True
        else:
            # Fallback: try pip if available
            if pip_pkg and _install_pip_package(pip_pkg):
                results[tool_name] = True
            else:
                results[tool_name] = False
                logger.warning(f"    Failed to auto-install {tool_name}. Agent will skip operations requiring it.")

    # Check Python imports
    for module_name, (pip_pkg, description) in PYTHON_PACKAGES.items():
        if _check_python_import(module_name):
            logger.debug(f"  OK  {module_name} (Python)")
            results[module_name] = True
        else:
            logger.warning(f"  MISSING  {module_name} — {description}")
            if pip_pkg and pip_pkg != "# stdlib":
                if _install_pip_package(pip_pkg):
                    results[module_name] = True
                else:
                    results[module_name] = False
            else:
                results[module_name] = False

    # Summary
    available = sum(1 for v in results.values() if v)
    total = len(results)
    logger.info(f"dependency_manager: {available}/{total} tools available.")

    return results


def get_tool_status() -> dict[str, bool]:
    """Quick check without installing. Used for health check endpoints."""
    results: dict[str, bool] = {}
    for tool_name, (cmd_check, _, _, _, _) in TOOLS.items():
        results[tool_name] = _check_command_exists(cmd_check)
    for module_name, _, _ in PYTHON_PACKAGES.values():
        results[module_name] = _check_python_import(module_name)
    return results
