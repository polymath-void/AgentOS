"""Skill: fs_count_lines
Category: filesystem
Description: Count lines, words, and characters in a file.
"""

def run(**kwargs):
    path = kwargs.get('path', '')
    with open(path, 'r', errors='replace') as f:
        text = f.read()
    return {'lines': len(text.splitlines()), 'words': len(text.split()), 'chars': len(text)}
