#!/usr/bin/env python3
"""
SQLite Database Tools — MCP Server (Stdio Transport)

Provides safe, structured access to local SQLite databases.
Primarily targets the Swarm Playground's episodic memory (memory.db)
but supports any project database within ~/Projects/.

Transport: stdio (JSON-RPC over stdin/stdout)
Security: Read-only by default, parameterized queries, SQL validation
"""

import csv
import io
import json
import logging
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECTS_ROOT = Path(os.path.expanduser("~/Projects"))
DEFAULT_DB = PROJECTS_ROOT / "local" / "agents-playground" / "src" / "memory.db"
MAX_ROWS = 1000
WRITE_MODE = False  # Global write mode toggle

# Dangerous SQL patterns — blocked even in write mode
BLOCKED_PATTERNS = [
    re.compile(r"\b(DROP|ALTER|TRUNCATE)\s+(TABLE|DATABASE|INDEX|VIEW)", re.IGNORECASE),
    re.compile(r"\bATTACH\s+DATABASE\b", re.IGNORECASE),
    re.compile(r"\bDETACH\s+DATABASE\b", re.IGNORECASE),
    re.compile(r"\bPRAGMA\s+(journal_mode|wal_checkpoint|integrity_check)", re.IGNORECASE),
    re.compile(r"\bCREATE\s+TRIGGER\b", re.IGNORECASE),
]

# DML patterns — blocked in read-only mode
WRITE_PATTERNS = [
    re.compile(r"\b(INSERT|UPDATE|DELETE|REPLACE)\b", re.IGNORECASE),
    re.compile(r"\bCREATE\s+(TABLE|INDEX|VIEW)\b", re.IGNORECASE),
]

logger = logging.getLogger("sqlite-tools")
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "sqlite-database-tools",
    description=(
        "Safe SQLite database access for AI agents. Query databases, "
        "inspect schemas, search episodic memory, and export results. "
        "Read-only by default with SQL injection prevention."
    ),
)


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _validate_db_path(db_path: str) -> Path:
    """Validate that db_path is within ~/Projects/."""
    resolved = Path(db_path).expanduser().resolve()
    projects_resolved = PROJECTS_ROOT.resolve()
    if not str(resolved).startswith(str(projects_resolved)):
        raise ValueError(
            f"Access denied: {db_path} is outside ~/Projects/. "
            f"Only databases under {PROJECTS_ROOT} are allowed."
        )
    if not resolved.exists():
        raise FileNotFoundError(f"Database not found: {resolved}")
    return resolved


def _validate_sql(sql: str, allow_write: bool = False):
    """Validate SQL statement for safety."""
    stripped = sql.strip().rstrip(";")

    # Always block dangerous operations
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(stripped):
            raise PermissionError(
                f"Blocked: SQL contains a dangerous operation. "
                f"Matched pattern: {pattern.pattern}"
            )

    # Block writes in read-only mode
    if not allow_write:
        for pattern in WRITE_PATTERNS:
            if pattern.search(stripped):
                raise PermissionError(
                    f"Blocked: Write operations are not allowed in read-only mode. "
                    f"Use insert_memory for approved write operations."
                )


def _connect(db_path: Path, readonly: bool = True) -> sqlite3.Connection:
    """Create a safe SQLite connection."""
    if readonly:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=5)
    else:
        conn = sqlite3.connect(str(db_path), timeout=5)

    conn.row_factory = sqlite3.Row
    # Enable WAL for concurrent read access
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        pass  # Read-only mode may block this
    return conn


# ---------------------------------------------------------------------------
# Tools — Query
# ---------------------------------------------------------------------------

@mcp.tool()
def query_db(db_path: str = "", sql: str = "", params: str = "[]") -> dict:
    """
    Execute a SELECT query on a SQLite database.
    Uses parameterized queries for SQL injection prevention.
    Limited to read-only operations and MAX_ROWS results.

    Args:
        db_path: Path to the .db file (default: episodic memory.db).
        sql: The SQL SELECT query to execute.
        params: JSON array of query parameters for ? placeholders.
    """
    db = _validate_db_path(db_path or str(DEFAULT_DB))
    _validate_sql(sql)

    try:
        param_list = json.loads(params) if params else []
    except json.JSONDecodeError:
        return {"error": "invalid_params", "detail": "params must be a JSON array"}

    # Enforce LIMIT
    sql_upper = sql.strip().upper()
    if "LIMIT" not in sql_upper:
        sql = sql.rstrip(";") + f" LIMIT {MAX_ROWS}"

    conn = _connect(db)
    try:
        cursor = conn.execute(sql, param_list)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(row) for row in cursor.fetchmany(MAX_ROWS)]
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": len(rows) >= MAX_ROWS,
            "database": str(db),
        }
    except sqlite3.Error as e:
        return {"error": "query_failed", "detail": str(e)}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Tools — Schema Inspection
# ---------------------------------------------------------------------------

@mcp.tool()
def list_tables(db_path: str = "") -> dict:
    """
    List all tables in a SQLite database with row counts.

    Args:
        db_path: Path to the .db file (default: episodic memory.db).
    """
    db = _validate_db_path(db_path or str(DEFAULT_DB))
    conn = _connect(db)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = []
        for row in cursor:
            name = row["name"]
            try:
                count_cursor = conn.execute(f'SELECT COUNT(*) as cnt FROM "{name}"')
                count = count_cursor.fetchone()["cnt"]
            except sqlite3.Error:
                count = -1
            tables.append({"name": name, "row_count": count})

        return {"tables": tables, "count": len(tables), "database": str(db)}
    except sqlite3.Error as e:
        return {"error": "list_tables_failed", "detail": str(e)}
    finally:
        conn.close()


@mcp.tool()
def describe_table(db_path: str = "", table: str = "") -> dict:
    """
    Get the schema of a table: columns, types, nullable, primary key.

    Args:
        db_path: Path to the .db file (default: episodic memory.db).
        table: Table name to describe.
    """
    if not table:
        return {"error": "table_name_required"}

    db = _validate_db_path(db_path or str(DEFAULT_DB))

    # Validate table name (no SQL injection via table name)
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
        return {"error": "invalid_table_name", "detail": "Table name contains invalid characters"}

    conn = _connect(db)
    try:
        cursor = conn.execute(f'PRAGMA table_info("{table}")')
        columns = []
        for row in cursor:
            columns.append({
                "cid": row["cid"],
                "name": row["name"],
                "type": row["type"],
                "nullable": not row["notnull"],
                "default": row["dflt_value"],
                "primary_key": bool(row["pk"]),
            })

        if not columns:
            return {"error": "table_not_found", "table": table}

        # Get CREATE statement
        create_cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        create_row = create_cursor.fetchone()
        create_sql = create_row["sql"] if create_row else None

        return {
            "table": table,
            "columns": columns,
            "column_count": len(columns),
            "create_sql": create_sql,
            "database": str(db),
        }
    except sqlite3.Error as e:
        return {"error": "describe_failed", "detail": str(e)}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Tools — Episodic Memory (Specialized)
# ---------------------------------------------------------------------------

@mcp.tool()
def search_episodic_memory(query: str, limit: int = 20) -> dict:
    """
    Search the neuro-symbolic episodic memory database.
    Searches across state, action, and observation fields using
    LIKE pattern matching with relevance scoring by recency.

    Args:
        query: Search keywords (space-separated, any match).
        limit: Maximum results to return (default 20).
    """
    db = DEFAULT_DB
    if not db.exists():
        return {"error": "memory_db_not_found", "path": str(db), "hint": "Start the Swarm Playground first."}

    limit = max(1, min(limit, 100))
    keywords = query.strip().split()
    if not keywords:
        return {"error": "empty_query"}

    # Build WHERE clause with LIKE for each keyword
    conditions = []
    params = []
    for kw in keywords:
        pattern = f"%{kw}%"
        conditions.append("(state LIKE ? OR action LIKE ? OR observation LIKE ?)")
        params.extend([pattern, pattern, pattern])

    where = " OR ".join(conditions)
    sql = f"""
        SELECT id, state, action, observation, timestamp, metadata
        FROM episodes
        WHERE {where}
        ORDER BY timestamp DESC
        LIMIT ?
    """
    params.append(limit)

    conn = _connect(db)
    try:
        cursor = conn.execute(sql, params)
        memories = []
        for row in cursor:
            memories.append({
                "id": row["id"],
                "state": row["state"],
                "action": row["action"],
                "observation": row["observation"],
                "timestamp": row["timestamp"],
                "metadata": row["metadata"],
            })

        return {
            "query": query,
            "keywords": keywords,
            "memories": memories,
            "count": len(memories),
        }
    except sqlite3.OperationalError as e:
        # Table might not exist yet
        if "no such table" in str(e):
            return {
                "error": "table_not_found",
                "detail": "episodes table not found. The memory database may be empty.",
                "database": str(db),
            }
        return {"error": "query_failed", "detail": str(e)}
    finally:
        conn.close()


@mcp.tool()
def insert_memory(state: str, action: str, observation: str) -> dict:
    """
    Write a new State-Action-Observation triplet to episodic memory.
    This is the ONLY write operation allowed and uses the default memory.db.

    Args:
        state: The state/context description.
        action: The action taken.
        observation: The observed result/outcome.
    """
    db = DEFAULT_DB
    if not db.exists():
        return {"error": "memory_db_not_found", "path": str(db)}

    timestamp = time.time()
    conn = _connect(db, readonly=False)
    try:
        cursor = conn.execute(
            "INSERT INTO episodes (state, action, observation, timestamp) VALUES (?, ?, ?, ?)",
            (state, action, observation, timestamp),
        )
        conn.commit()
        return {
            "success": True,
            "id": cursor.lastrowid,
            "timestamp": timestamp,
        }
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            # Auto-create the table
            conn2 = _connect(db, readonly=False)
            try:
                conn2.execute("""
                    CREATE TABLE IF NOT EXISTS episodes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        state TEXT,
                        action TEXT,
                        observation TEXT,
                        timestamp REAL,
                        metadata TEXT
                    )
                """)
                conn2.execute(
                    "INSERT INTO episodes (state, action, observation, timestamp) VALUES (?, ?, ?, ?)",
                    (state, action, observation, timestamp),
                )
                conn2.commit()
                return {"success": True, "id": conn2.execute("SELECT last_insert_rowid()").fetchone()[0], "timestamp": timestamp, "table_created": True}
            finally:
                conn2.close()
        return {"error": "insert_failed", "detail": str(e)}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Tools — Database Stats
# ---------------------------------------------------------------------------

@mcp.tool()
def db_stats(db_path: str = "") -> dict:
    """
    Get database statistics: file size, table count, total rows, WAL status.

    Args:
        db_path: Path to the .db file (default: episodic memory.db).
    """
    db = _validate_db_path(db_path or str(DEFAULT_DB))

    size_bytes = db.stat().st_size
    conn = _connect(db)
    try:
        # Table count
        tables_cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row["name"] for row in tables_cursor]

        # Total rows
        total_rows = 0
        for table in tables:
            try:
                count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                total_rows += count
            except sqlite3.Error:
                pass

        # Journal mode
        journal = conn.execute("PRAGMA journal_mode").fetchone()[0]

        # Page info
        page_size = conn.execute("PRAGMA page_size").fetchone()[0]
        page_count = conn.execute("PRAGMA page_count").fetchone()[0]

        return {
            "database": str(db),
            "size_mb": round(size_bytes / (1024 * 1024), 3),
            "size_bytes": size_bytes,
            "table_count": len(tables),
            "tables": tables,
            "total_rows": total_rows,
            "journal_mode": journal,
            "page_size": page_size,
            "page_count": page_count,
        }
    except sqlite3.Error as e:
        return {"error": "stats_failed", "detail": str(e)}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Tools — Export
# ---------------------------------------------------------------------------

@mcp.tool()
def export_query(
    db_path: str = "",
    sql: str = "",
    output_format: str = "json",
    output_path: str = "",
) -> dict:
    """
    Run a query and save results as JSON or CSV.
    Output path must be within ~/Projects/.

    Args:
        db_path: Path to the .db file (default: episodic memory.db).
        sql: The SQL SELECT query to execute.
        output_format: 'json' or 'csv' (default 'json').
        output_path: Where to save the output file (must be under ~/Projects/).
    """
    if not output_path:
        return {"error": "output_path_required"}
    if output_format not in ("json", "csv"):
        return {"error": "invalid_format", "allowed": ["json", "csv"]}

    db = _validate_db_path(db_path or str(DEFAULT_DB))
    out = _validate_db_path(output_path)  # Reuse path validation

    _validate_sql(sql)

    conn = _connect(db)
    try:
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(row) for row in cursor.fetchmany(MAX_ROWS)]

        out_path = Path(output_path).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "json":
            with open(out_path, "w") as f:
                json.dump({"columns": columns, "rows": rows}, f, indent=2, default=str)
        else:
            with open(out_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)

        return {
            "path": str(out_path),
            "format": output_format,
            "rows_exported": len(rows),
            "truncated": len(rows) >= MAX_ROWS,
        }
    except sqlite3.Error as e:
        return {"error": "export_failed", "detail": str(e)}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("sqlite://config")
def sqlite_config() -> str:
    """Current SQLite Tools configuration."""
    return json.dumps(
        {
            "default_database": str(DEFAULT_DB),
            "projects_root": str(PROJECTS_ROOT),
            "max_rows": MAX_ROWS,
            "write_mode": WRITE_MODE,
            "blocked_operations": [
                "DROP TABLE/DATABASE/INDEX/VIEW",
                "ALTER TABLE",
                "TRUNCATE",
                "ATTACH/DETACH DATABASE",
                "CREATE TRIGGER",
            ],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
