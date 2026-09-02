"""
tool_registry.py — All tool definitions for SaaS-Agent v2.

Organized by domain:
  - Media (YouTube, streaming)
  - Communication (calls, SMS)
  - File Management (CRUD, search, cloud sync)
  - Email (fetch, summarize)
  - Calendar (list, add events)
  - Notes (write, read)
  - System Control (brightness, WiFi, battery, monitoring)
"""

from __future__ import annotations


def get_tool_definitions() -> list[dict]:
    """Return all tool schemas for Gemini function calling."""
    return [
        # ===================================================================
        # MEDIA CONTROL
        # ===================================================================
        {
            "name": "play_youtube",
            "description": (
                "Search YouTube and play a video/song. "
                "Uses yt-dlp to fetch stream URL, then mpv to play. "
                "Supports audio-only mode for songs. "
                "Example: 'play world cup fifa song' → searches, finds video, streams."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (song name, artist, video title).",
                    },
                    "audio_only": {
                        "type": "boolean",
                        "description": "If true, play audio only (no video). Default: false.",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        },
        # ===================================================================
        # COMMUNICATION — CALLS
        # ===================================================================
        {
            "name": "get_call_logs",
            "description": (
                "Retrieve call logs from Android device. "
                "Requires root + READ_CALL_LOG permission. "
                "Can filter by type (INCOMING, OUTGOING, MISSED). "
                "Returns recent calls with number, name, duration, type."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "call_type": {
                        "type": "string",
                        "enum": ["ALL", "INCOMING", "OUTGOING", "MISSED"],
                        "description": "Filter call logs by type.",
                        "default": "ALL",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max number of calls to return. Default: 20.",
                        "default": 20,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "place_call",
            "description": (
                "Initiate an outbound call on Android device. "
                "Requires CALL_PHONE permission + root. "
                "Opens the phone dialer with the number. "
                "Example: 'call +1-234-567-8900'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Phone number to dial (e.g. '+1234567890', '9876543210').",
                    },
                },
                "required": ["phone_number"],
            },
        },
        # ===================================================================
        # COMMUNICATION — SMS
        # ===================================================================
        {
            "name": "send_sms",
            "description": (
                "Send an SMS text message via Android device. "
                "Requires SEND_SMS permission + root. "
                "Example: send_sms(phone_number='+1234567890', message='Hello!')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Recipient phone number.",
                    },
                    "message": {
                        "type": "string",
                        "description": "SMS text message (max 160 chars per SMS).",
                    },
                },
                "required": ["phone_number", "message"],
            },
        },
        {
            "name": "read_sms",
            "description": (
                "Read SMS messages from Android device. "
                "Requires READ_SMS permission + root. "
                "Can filter by phone number or limit results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max number of SMS to return. Default: 20.",
                        "default": 20,
                    },
                    "from_number": {
                        "type": "string",
                        "description": "Optional: filter SMS from a specific number.",
                    },
                },
                "required": [],
            },
        },
        # ===================================================================
        # FILE MANAGEMENT
        # ===================================================================
        {
            "name": "list_files",
            "description": (
                "List files in a directory. "
                "Supports local paths and cloud paths (via rclone). "
                "Example: '/data/local/downloads', '~/Documents', 's3://bucket/'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (local or cloud via rclone).",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If true, list files recursively. Default: false.",
                        "default": False,
                    },
                },
                "required": ["path"],
            },
        },
        {
            "name": "read_file",
            "description": (
                "Read file contents. "
                "Safe for text files; returns first N bytes for large files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path.",
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": "Max bytes to read. Default: 8192.",
                        "default": 8192,
                    },
                },
                "required": ["path"],
            },
        },
        {
            "name": "write_file",
            "description": (
                "Write or overwrite a file. "
                "Creates parent directories if needed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write.",
                    },
                    "append": {
                        "type": "boolean",
                        "description": "If true, append instead of overwrite. Default: false.",
                        "default": False,
                    },
                },
                "required": ["path", "content"],
            },
        },
        {
            "name": "search_files",
            "description": (
                "Search for files matching a pattern. "
                "Example: find all PDFs, search for files modified today."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory to search.",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File name pattern (supports wildcards: *.pdf, *2026*).",
                    },
                },
                "required": ["path", "pattern"],
            },
        },
        {
            "name": "delete_file",
            "description": (
                "Delete a file (with confirmation). "
                "Use cautiously. Cannot delete system files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path.",
                    },
                },
                "required": ["path"],
            },
        },
        {
            "name": "copy_file",
            "description": (
                "Copy a file from source to destination. "
                "Supports local and cloud (rclone) paths."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file path.",
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination file path.",
                    },
                },
                "required": ["source", "destination"],
            },
        },
        {
            "name": "sync_cloud",
            "description": (
                "Sync files to/from cloud storage (AWS S3, Google Drive, etc.) via rclone. "
                "Example: sync_cloud(source='~/Documents/reports', destination='gdrive:Backups/reports')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source path (local or remote).",
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path (remote or local).",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, preview changes without executing. Default: false.",
                        "default": False,
                    },
                },
                "required": ["source", "destination"],
            },
        },
        # ===================================================================
        # EMAIL
        # ===================================================================
        {
            "name": "get_emails",
            "description": (
                "Fetch emails from Gmail inbox (via IMAP). "
                "Requires Gmail OAuth token or app password. "
                "Returns unread or recent emails as structured data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "unread_only": {
                        "type": "boolean",
                        "description": "If true, fetch only unread emails. Default: true.",
                        "default": True,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max number of emails to fetch. Default: 10.",
                        "default": 10,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "summarize_emails",
            "description": (
                "Fetch unread emails and generate a bulleted summary. "
                "Uses Gemini to digest email content and extract key points. "
                "Respects privacy: does NOT show full email bodies unless requested."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max number of emails to summarize. Default: 20.",
                        "default": 20,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "send_email",
            "description": (
                "Send an email via Gmail. "
                "Requires OAuth token + Gmail send permission."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject.",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body (plain text or HTML).",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        },
        # ===================================================================
        # CALENDAR
        # ===================================================================
        {
            "name": "get_calendar_events",
            "description": (
                "Fetch calendar events from Google Calendar. "
                "Requires Google Calendar API key + OAuth. "
                "Can filter by date range."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days to look ahead. Default: 7.",
                        "default": 7,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "add_calendar_event",
            "description": (
                "Add an event to Google Calendar. "
                "Requires Google Calendar API key + OAuth + CALENDAR write permission."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Event title.",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start datetime (ISO 8601: '2026-06-17T09:00:00').",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End datetime (ISO 8601). If omitted, defaults to start_time + 1 hour.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional event description.",
                    },
                },
                "required": ["title", "start_time"],
            },
        },
        # ===================================================================
        # NOTES
        # ===================================================================
        {
            "name": "write_note",
            "description": (
                "Write a timestamped note using jrnl or fallback to plain text file. "
                "Example: 'write_note(text=\"Meeting notes: discussed project roadmap\")'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Note content.",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags (e.g. ['meeting', 'project']).",
                    },
                },
                "required": ["text"],
            },
        },
        {
            "name": "read_notes",
            "description": (
                "Read recent notes. Returns timestamped entries."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent notes to return. Default: 10.",
                        "default": 10,
                    },
                },
                "required": [],
            },
        },
        # ===================================================================
        # SYSTEM CONTROL
        # ===================================================================
        {
            "name": "set_brightness",
            "description": (
                "Set screen brightness (0–100%). "
                "Automatically disables auto-brightness first. "
                "Requires root on Android."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "percent": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Brightness level as percentage.",
                    },
                },
                "required": ["percent"],
            },
        },
        {
            "name": "toggle_wifi",
            "description": (
                "Toggle WiFi on/off. "
                "Requires root on Android or sudo on Linux."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": ["on", "off", "toggle"],
                        "description": "Desired state.",
                    },
                },
                "required": ["state"],
            },
        },
        {
            "name": "clear_notifications",
            "description": (
                "Clear all notifications on Android device. "
                "Requires root or notification listener permission."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_system_info",
            "description": (
                "Get system information: battery, uptime, disk usage, memory, running processes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["battery", "uptime", "disk", "memory", "processes", "all"],
                        "description": "Type of system info to retrieve.",
                        "default": "all",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "run_shell_command",
            "description": (
                "Execute an arbitrary shell command. "
                "Use with caution. Agent will validate command safety before execution."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute.",
                    },
                    "require_root": {
                        "type": "boolean",
                        "description": "If true, command is prefixed with 'su -c'. Default: false.",
                        "default": False,
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds. Default: 30.",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
        },
        # ===================================================================
        # CARD MANAGEMENT (internal)
        # ===================================================================
        {
            "name": "create_agent_card",
            "description": (
                "Create a new AgentCard for a recurring task. "
                "User can call create_agent_card(agent_name, system_prompt, description). "
                "The card becomes available immediately for future use."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Display name for the new card.",
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Full system prompt for the card.",
                    },
                    "description": {
                        "type": "string",
                        "description": "One-liner description.",
                    },
                    "scope_tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for auto-routing (e.g. 'media', 'calls').",
                    },
                },
                "required": ["agent_name", "system_prompt"],
            },
        },
        {
            "name": "list_agent_cards",
            "description": (
                "List all available AgentCards (name, description, ID)."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]


def get_tool_names() -> list[str]:
    """Return tool name strings for whitelisting."""
    return [t["name"] for t in get_tool_definitions()]


def filter_tools_for_card(allowed: list[str]) -> list[dict]:
    """Filter tool definitions by whitelist. Empty list = all tools."""
    all_tools = get_tool_definitions()
    if not allowed:
        return all_tools
    allowed_set = set(allowed)
    return [t for t in all_tools if t["name"] in allowed_set]
