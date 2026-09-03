"""Skill: fs_file_stat
Category: filesystem
Description: Return detailed stat metadata for a file.
"""

def run(**kwargs):
    import os, datetime
    path = kwargs.get('path', '')
    s = os.stat(path)
    return {'path': path, 'size_bytes': s.st_size, 'modified': datetime.datetime.fromtimestamp(s.st_mtime).isoformat(), 'is_file': os.path.isfile(path), 'is_dir': os.path.isdir(path)}
