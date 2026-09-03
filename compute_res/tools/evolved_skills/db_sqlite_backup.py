"""Skill: db_sqlite_backup
Category: database
Description: Backup a SQLite database to another file.
"""

def run(**kwargs):
    import sqlite3
    src = kwargs.get('src', '')
    dst = kwargs.get('dst', src + '.bak')
    with sqlite3.connect(src) as conn:
        bak = sqlite3.connect(dst)
        conn.backup(bak)
        bak.close()
    return {'status': 'backed_up', 'src': src, 'dst': dst}
