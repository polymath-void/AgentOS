"""Skill: db_sqlite_list_tables
Category: database
Description: List all tables and columns in a SQLite database.
"""

def run(**kwargs):
    import sqlite3
    db_path = kwargs.get('db_path', '')
    with sqlite3.connect(db_path) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        result = {t[0]: [{'col': c[1], 'type': c[2]} for c in conn.execute(f'PRAGMA table_info("{t[0]}")').fetchall()] for t in tables}
    return {'tables': result, 'count': len(result)}
