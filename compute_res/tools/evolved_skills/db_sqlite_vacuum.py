"""Skill: db_sqlite_vacuum
Category: database
Description: Run VACUUM on a SQLite database.
"""

def run(**kwargs):
    import sqlite3, os
    p = kwargs.get('db_path', '')
    size_before = os.path.getsize(p)
    with sqlite3.connect(p) as conn: conn.execute('VACUUM')
    return {'before': size_before, 'after': os.path.getsize(p), 'saved': size_before - os.path.getsize(p)}
