"""Skill: fs_read_file
Category: filesystem
Description: Read a file and return its full content string.
"""

def run(**kwargs):
    path = kwargs.get('path', '')
    if not path:
        return {'error': 'path is required'}
    with open(path, 'r', errors='replace') as f:
        return {'content': f.read(), 'path': path}
