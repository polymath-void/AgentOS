"""Skill: db_sqlite_execute
Category: database
Description: Execute INSERT/UPDATE/DELETE on SQLite.
"""

def run(**kwargs):
    import sqlite3
    db_path = kwargs.get('db_path', '')
    sql = kwargs.get('sql', '')
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(sql, kwargs.get('params', []))
        conn.commit()
    return {'rowcount': cur.rowcount, 'lastrowid': cur.lastrowid}
