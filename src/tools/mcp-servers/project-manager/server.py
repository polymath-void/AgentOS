#!/usr/bin/env python3
"""
Project Manager — MCP Server (Stdio Transport)

Automates project directory indexing, chat session tracking,
and workspace scaffolding. Manages project-dir.md, sub-dir.md,
and active_chats.md as structured markdown files.

Transport: stdio (JSON-RPC over stdin/stdout)
"""

import json
import logging
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECTS_ROOT = Path(os.path.expanduser("~/Projects"))
PROJECT_DIR_FILE = PROJECTS_ROOT / "project-dir.md"
SUB_DIR_FILE = PROJECTS_ROOT / "sub-dir.md"
ACTIVE_CHATS_FILE = PROJECTS_ROOT / "active_chats.md"

# Directories and patterns always excluded from tree scans
EXCLUDE_DIRS = {
    "target", "dist", "build", "node_modules", "__pycache__",
    ".cache", "venv", ".venv", ".git", ".hg", ".svn",
    ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
    "egg-info", ".gradle", ".idea", ".vscode",
}
EXCLUDE_EXTENSIONS = {
    ".apk", ".tar.gz", ".so", ".pyc", ".pyo", ".tmp",
    ".o", ".a", ".dylib", ".class", ".jar",
}

# Project scaffolding templates
SCAFFOLDS = {
    "python": {
        "dirs": ["src", "tests", "docs"],
        "files": {
            "README.md": "# {name}\n\n{description}\n",
            "src/__init__.py": "",
            "tests/__init__.py": "",
            ".gitignore": "__pycache__/\n*.pyc\n.venv/\ndist/\n*.egg-info/\n",
            "requirements.txt": "",
        },
    },
    "rust": {
        "dirs": ["src"],
        "files": {
            "README.md": "# {name}\n\n{description}\n",
            "src/main.rs": 'fn main() {{\n    println!("Hello, {name}!");\n}}\n',
            ".gitignore": "target/\n",
            "Cargo.toml": '[package]\nname = "{name_snake}"\nversion = "0.1.0"\nedition = "2021"\n',
        },
    },
    "node": {
        "dirs": ["src", "tests"],
        "files": {
            "README.md": "# {name}\n\n{description}\n",
            "src/index.js": 'console.log("Hello, {name}!");\n',
            ".gitignore": "node_modules/\ndist/\n.env\n",
            "package.json": '{{\n  "name": "{name_snake}",\n  "version": "0.1.0",\n  "main": "src/index.js"\n}}\n',
        },
    },
    "web": {
        "dirs": ["css", "js", "assets"],
        "files": {
            "README.md": "# {name}\n\n{description}\n",
            "index.html": '<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n  <title>{name}</title>\n  <link rel="stylesheet" href="css/style.css">\n</head>\n<body>\n  <h1>{name}</h1>\n  <script src="js/main.js"></script>\n</body>\n</html>\n',
            "css/style.css": "/* {name} styles */\n",
            "js/main.js": '// {name} main script\n',
            ".gitignore": "node_modules/\ndist/\n",
        },
    },
    "native-ai": {
        "dirs": ["src", "wasm", "models", "tests"],
        "files": {
            "README.md": "# {name}\n\n{description}\n\n## Native AI Module\nIntegrates with the local Native AI Engine.\n",
            "src/main.py": '"""Entry point for {name}."""\n',
            "src/bridge.py": '"""WASM bridge interface."""\n',
            ".gitignore": "__pycache__/\n*.pyc\n.venv/\ntarget/\nmodels/*.gguf\n",
        },
    },
}

logger = logging.getLogger("project-manager")
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "project-manager",
    description=(
        "Project workspace management tools. Index projects, generate "
        "directory trees, track chat sessions, and scaffold new projects "
        "with standardized templates."
    ),
)


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _is_excluded(name: str) -> bool:
    """Check if a file/dir name should be excluded from tree scans."""
    if name in EXCLUDE_DIRS:
        return True
    for ext in EXCLUDE_EXTENSIONS:
        if name.endswith(ext):
            return True
    return False


def _safe_path(path: str) -> Path:
    """Validate that a path is within PROJECTS_ROOT."""
    resolved = Path(path).resolve()
    if not str(resolved).startswith(str(PROJECTS_ROOT.resolve())):
        raise ValueError(f"Path {path} is outside ~/Projects/")
    return resolved


def _build_tree(root: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> tuple[str, int, int]:
    """Generate a filtered directory tree string."""
    if current_depth >= max_depth:
        return "", 0, 0

    lines = []
    file_count = 0
    dir_count = 0

    try:
        entries = sorted(root.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return f"{prefix}[permission denied]\n", 0, 0

    visible = [e for e in entries if not _is_excluded(e.name) and not e.name.startswith(".")]

    for i, entry in enumerate(visible):
        is_last = i == len(visible) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            dir_count += 1
            extension = "    " if is_last else "│   "
            subtree, sf, sd = _build_tree(entry, prefix + extension, max_depth, current_depth + 1)
            if subtree:
                lines.append(subtree.rstrip("\n"))
            file_count += sf
            dir_count += sd
        else:
            file_count += 1

    return "\n".join(lines) + "\n" if lines else "", file_count, dir_count


def _atomic_write(path: Path, content: str):
    """Write content atomically using temp file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Backup existing file
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
    # Write to temp then rename
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)
        raise


def _parse_project_index() -> list[dict]:
    """Parse project-dir.md markdown table into list of dicts."""
    if not PROJECT_DIR_FILE.exists():
        return []

    content = PROJECT_DIR_FILE.read_text()
    projects = []
    in_table = False

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("|") and "Name" in line and "Path" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---") or line.startswith("| ---"):
            continue
        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 2:
                entry = {"name": cells[0], "path": cells[1]}
                if len(cells) >= 3:
                    entry["description"] = cells[2]
                projects.append(entry)
        elif in_table and not line.startswith("|"):
            in_table = False

    return projects


def _parse_chats_table() -> list[dict]:
    """Parse active_chats.md markdown table."""
    if not ACTIVE_CHATS_FILE.exists():
        return []

    content = ACTIVE_CHATS_FILE.read_text()
    chats = []
    in_table = False

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("|") and "Project" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---") or line.startswith("| ---"):
            continue
        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 3:
                entry = {
                    "project": cells[0],
                    "conversation_id": cells[1],
                    "description": cells[2],
                }
                if len(cells) >= 4:
                    entry["timestamp"] = cells[3]
                chats.append(entry)
        elif in_table and not line.startswith("|"):
            in_table = False

    return chats


# ---------------------------------------------------------------------------
# Tools — Project Listing
# ---------------------------------------------------------------------------

@mcp.tool()
def list_projects() -> dict:
    """
    Parse and return all projects from project-dir.md.
    Returns a list of projects with name, path, and description.
    """
    projects = _parse_project_index()
    return {"projects": projects, "count": len(projects), "source": str(PROJECT_DIR_FILE)}


@mcp.tool()
def get_project_tree(project_name: str, max_depth: int = 3) -> dict:
    """
    Generate a filtered directory tree for a project.
    Excludes build artifacts, caches, node_modules, etc.

    Args:
        project_name: Name or relative path of the project under ~/Projects/.
        max_depth: Maximum directory depth to traverse (default 3).
    """
    max_depth = max(1, min(max_depth, 8))
    project_path = _safe_path(str(PROJECTS_ROOT / project_name))

    if not project_path.exists():
        return {"error": "not_found", "path": str(project_path)}
    if not project_path.is_dir():
        return {"error": "not_a_directory", "path": str(project_path)}

    tree, file_count, dir_count = _build_tree(project_path, max_depth=max_depth)

    return {
        "project": project_name,
        "path": str(project_path),
        "tree": f"{project_name}/\n{tree}",
        "file_count": file_count,
        "dir_count": dir_count,
        "max_depth": max_depth,
    }


# ---------------------------------------------------------------------------
# Tools — Index Management
# ---------------------------------------------------------------------------

@mcp.tool()
def update_project_index(include_hidden: bool = False) -> dict:
    """
    Rescan ~/Projects/ and regenerate project-dir.md.
    Compares against the existing index to report added/removed projects.

    Args:
        include_hidden: Include hidden directories (starting with .) if True.
    """
    existing = {p["name"]: p for p in _parse_project_index()}
    current_names = set()

    entries = []
    for item in sorted(PROJECTS_ROOT.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith(".") and not include_hidden:
            continue
        if _is_excluded(item.name):
            continue
        # Skip index files themselves
        if item.name in ("project-dir.md", "sub-dir.md", "active_chats.md"):
            continue

        current_names.add(item.name)
        desc = existing.get(item.name, {}).get("description", "")
        entries.append({"name": item.name, "path": str(item), "description": desc})

    added = current_names - set(existing.keys())
    removed = set(existing.keys()) - current_names

    # Generate markdown
    lines = [
        "# Project Directory Index",
        "",
        f"*Auto-generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "| Name | Path | Description |",
        "| :--- | :--- | :--- |",
    ]
    for entry in entries:
        lines.append(f"| {entry['name']} | {entry['path']} | {entry['description']} |")
    lines.append("")

    _atomic_write(PROJECT_DIR_FILE, "\n".join(lines))

    return {
        "total": len(entries),
        "added": sorted(added),
        "removed": sorted(removed),
        "index_file": str(PROJECT_DIR_FILE),
    }


@mcp.tool()
def update_subtree(project_name: str) -> dict:
    """
    Regenerate sub-dir.md with a detailed tree for a specific project.

    Args:
        project_name: Name of the project under ~/Projects/.
    """
    project_path = _safe_path(str(PROJECTS_ROOT / project_name))
    if not project_path.exists() or not project_path.is_dir():
        return {"error": "not_found", "path": str(project_path)}

    tree, file_count, dir_count = _build_tree(project_path, max_depth=5)

    content = (
        f"# Sub-Directory Tree: {project_name}\n\n"
        f"*Auto-generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
        f"```\n{project_name}/\n{tree}```\n\n"
        f"Files: {file_count} | Directories: {dir_count}\n"
    )

    _atomic_write(SUB_DIR_FILE, content)

    return {"tree": f"{project_name}/\n{tree}", "file_count": file_count, "dir_count": dir_count, "updated": True}


# ---------------------------------------------------------------------------
# Tools — Chat Tracking
# ---------------------------------------------------------------------------

@mcp.tool()
def log_chat(project_name: str, conversation_id: str, description: str) -> dict:
    """
    Record a conversation ID and project tag in active_chats.md.
    Appends a new row with an ISO timestamp.

    Args:
        project_name: The project this chat is about.
        conversation_id: The Antigravity conversation ID.
        description: Brief description of the task/topic.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not ACTIVE_CHATS_FILE.exists():
        content = (
            "# Active Chat Sessions\n\n"
            "| Project | Conversation ID | Description | Timestamp |\n"
            "| :--- | :--- | :--- | :--- |\n"
        )
    else:
        content = ACTIVE_CHATS_FILE.read_text()
        if not content.strip():
            content = (
                "# Active Chat Sessions\n\n"
                "| Project | Conversation ID | Description | Timestamp |\n"
                "| :--- | :--- | :--- | :--- |\n"
            )

    new_row = f"| {project_name} | {conversation_id} | {description} | {timestamp} |\n"
    content = content.rstrip("\n") + "\n" + new_row

    _atomic_write(ACTIVE_CHATS_FILE, content)

    return {
        "logged": True,
        "entry": {
            "project": project_name,
            "conversation_id": conversation_id,
            "description": description,
            "timestamp": timestamp,
        },
    }


@mcp.tool()
def get_active_chats(project_name: str = "") -> dict:
    """
    List all tracked chat sessions from active_chats.md.
    Optionally filter by project name.

    Args:
        project_name: Filter by project (empty = all chats).
    """
    chats = _parse_chats_table()

    if project_name:
        chats = [c for c in chats if c["project"].lower() == project_name.lower()]

    return {"chats": chats, "count": len(chats)}


# ---------------------------------------------------------------------------
# Tools — Project Scaffolding
# ---------------------------------------------------------------------------

@mcp.tool()
def create_project(name: str, project_type: str = "python", description: str = "") -> dict:
    """
    Scaffold a new project directory with standardized structure.
    Creates directories, boilerplate files, and updates the project index.

    Args:
        name: Project name (used as directory name).
        project_type: Template type — 'python', 'rust', 'node', 'web', or 'native-ai'.
        description: Brief project description for README and index.
    """
    if project_type not in SCAFFOLDS:
        return {
            "error": "unknown_type",
            "available_types": list(SCAFFOLDS.keys()),
        }

    project_path = PROJECTS_ROOT / name
    if project_path.exists():
        return {"error": "already_exists", "path": str(project_path)}

    scaffold = SCAFFOLDS[project_type]
    name_snake = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    fmt = {"name": name, "name_snake": name_snake, "description": description or f"A {project_type} project."}

    created_files = []

    # Create directories
    project_path.mkdir(parents=True, exist_ok=True)
    for d in scaffold["dirs"]:
        (project_path / d).mkdir(parents=True, exist_ok=True)

    # Create files
    for filepath, template in scaffold["files"].items():
        full_path = project_path / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        content = template.format(**fmt)
        full_path.write_text(content)
        created_files.append(filepath)

    # Update project index
    index_result = update_project_index()

    return {
        "created": True,
        "path": str(project_path),
        "type": project_type,
        "structure": created_files,
        "index_updated": True,
        "index_result": index_result,
    }


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("projects://index")
def projects_index() -> str:
    """Current project directory index."""
    if PROJECT_DIR_FILE.exists():
        return PROJECT_DIR_FILE.read_text()
    return "No project-dir.md found."


@mcp.resource("projects://config")
def projects_config() -> str:
    """Project Manager configuration."""
    return json.dumps(
        {
            "projects_root": str(PROJECTS_ROOT),
            "index_file": str(PROJECT_DIR_FILE),
            "subtree_file": str(SUB_DIR_FILE),
            "chats_file": str(ACTIVE_CHATS_FILE),
            "excluded_dirs": sorted(EXCLUDE_DIRS),
            "excluded_extensions": sorted(EXCLUDE_EXTENSIONS),
            "scaffold_types": list(SCAFFOLDS.keys()),
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
