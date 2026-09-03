import sqlite3
import os
import json
from typing import List, Dict, Any, Optional


class SkillsHubDB:
    """
    SkillsHub DB — the ComputeRes OS distributed skill registry.
    Stores agent-published skills with niche categorization, tagging,
    and FTS5 full-text search for fast discovery.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, "skillshub.db")
        else:
            self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript('''
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS skills (
                    skill_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    author     TEXT,
                    version    TEXT DEFAULT '1.0.0',
                    code_path  TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL UNIQUE,
                    description TEXT
                );

                CREATE TABLE IF NOT EXISTS skill_categories (
                    skill_id    INTEGER,
                    category_id INTEGER,
                    PRIMARY KEY (skill_id, category_id),
                    FOREIGN KEY (skill_id)    REFERENCES skills(skill_id)    ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS tags (
                    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name   TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS skill_tags (
                    skill_id INTEGER,
                    tag_id   INTEGER,
                    PRIMARY KEY (skill_id, tag_id),
                    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id)   REFERENCES tags(tag_id)     ON DELETE CASCADE
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
                    name,
                    description,
                    content=\'skills\',
                    content_rowid=\'skill_id\'
                );
            ''')

            # FTS triggers (safe idempotent check)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name='skills_ai'")
            if not cursor.fetchone():
                cursor.executescript('''
                    CREATE TRIGGER skills_ai AFTER INSERT ON skills BEGIN
                        INSERT INTO skills_fts(rowid, name, description)
                        VALUES (new.skill_id, new.name, new.description);
                    END;

                    CREATE TRIGGER skills_ad AFTER DELETE ON skills BEGIN
                        INSERT INTO skills_fts(skills_fts, rowid, name, description)
                        VALUES (\'delete\', old.skill_id, old.name, old.description);
                    END;

                    CREATE TRIGGER skills_au AFTER UPDATE ON skills BEGIN
                        INSERT INTO skills_fts(skills_fts, rowid, name, description)
                        VALUES (\'delete\', old.skill_id, old.name, old.description);
                        INSERT INTO skills_fts(rowid, name, description)
                        VALUES (new.skill_id, new.name, new.description);
                    END;
                ''')
            conn.commit()

    # ------------------------------------------------------------------ #
    #  PUBLISHING                                                          #
    # ------------------------------------------------------------------ #

    def publish_skill(
        self,
        name: str,
        description: str,
        author: str,
        version: str,
        code_path: str,
        categories: List[str] = None,
        tags: List[str] = None,
    ) -> int:
        """Publish or update a skill in the SkillsHub. Returns the skill_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO skills (name, description, author, version, code_path)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    description = excluded.description,
                    author      = excluded.author,
                    version     = excluded.version,
                    code_path   = excluded.code_path,
                    updated_at  = CURRENT_TIMESTAMP
            ''', (name, description, author, version, code_path))

            cursor.execute("SELECT skill_id FROM skills WHERE name = ?", (name,))
            skill_id = cursor.fetchone()[0]

            if categories:
                for cat in categories:
                    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
                    cursor.execute("SELECT category_id FROM categories WHERE name = ?", (cat,))
                    cat_id = cursor.fetchone()[0]
                    cursor.execute(
                        "INSERT OR IGNORE INTO skill_categories (skill_id, category_id) VALUES (?, ?)",
                        (skill_id, cat_id)
                    )

            if tags:
                for tag in tags:
                    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                    cursor.execute("SELECT tag_id FROM tags WHERE name = ?", (tag,))
                    tag_id = cursor.fetchone()[0]
                    cursor.execute(
                        "INSERT OR IGNORE INTO skill_tags (skill_id, tag_id) VALUES (?, ?)",
                        (skill_id, tag_id)
                    )

            conn.commit()
            return skill_id

    # ------------------------------------------------------------------ #
    #  DISCOVERY                                                           #
    # ------------------------------------------------------------------ #

    def search_skills_fts(self, query: str) -> List[Dict[str, Any]]:
        """Full-text search across skill names and descriptions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT skills.*
                    FROM skills_fts
                    JOIN skills ON skills_fts.rowid = skills.skill_id
                    WHERE skills_fts MATCH ?
                    ORDER BY rank
                    LIMIT 20;
                ''', (query,))
            except sqlite3.OperationalError:
                # Fallback for malformed FTS queries
                cursor.execute('''
                    SELECT * FROM skills
                    WHERE name LIKE ? OR description LIKE ?
                    LIMIT 20;
                ''', (f"%{query}%", f"%{query}%"))
            return [dict(row) for row in cursor.fetchall()]

    def get_skills_by_niche(self, category_name: str) -> List[Dict[str, Any]]:
        """Return all skills belonging to a specific niche/category."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.*
                FROM skills s
                JOIN skill_categories sc ON s.skill_id = sc.skill_id
                JOIN categories c ON sc.category_id = c.category_id
                WHERE LOWER(c.name) = LOWER(?)
            ''', (category_name,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Return all published skills with their categories and tags."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills ORDER BY updated_at DESC")
            skills = [dict(row) for row in cursor.fetchall()]
            for skill in skills:
                sid = skill["skill_id"]
                cursor.execute('''
                    SELECT c.name FROM categories c
                    JOIN skill_categories sc ON c.category_id = sc.category_id
                    WHERE sc.skill_id = ?
                ''', (sid,))
                skill["categories"] = [r["name"] for r in cursor.fetchall()]
                cursor.execute('''
                    SELECT t.name FROM tags t
                    JOIN skill_tags st ON t.tag_id = st.tag_id
                    WHERE st.skill_id = ?
                ''', (sid,))
                skill["tags"] = [r["name"] for r in cursor.fetchall()]
            return skills

    def get_skill_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single skill record by name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_niches(self) -> List[str]:
        """Return all registered niche categories."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            return [r["name"] for r in cursor.fetchall()]


# Global singleton
skills_db = SkillsHubDB()
