"""Skill: db_sqlite_query
Category: database
Description: Execute a SELECT query on SQLite and return rows.
"""

def run(**kwargs):
    import sqlite3
    db_path = kwargs.get('db_path', ':memory:')
    query = kwargs.get('query', 'SELECT 1')
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(query, kwargs.get('params', [])).fetchall()]
    return {'rows': rows, 'count': len(rows)}
