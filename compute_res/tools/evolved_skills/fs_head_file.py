"""Skill: fs_head_file
Category: filesystem
Description: Return the first N lines of a file.
"""

def run(**kwargs):
    path = kwargs.get('path', '')
    n = int(kwargs.get('n', 10))
    with open(path, 'r', errors='replace') as f:
        lines = f.readlines()
    return {'lines': lines[:n], 'total': len(lines)}
