"""Skill: fs_list_dir
Category: filesystem
Description: List files and folders in a directory with sizes.
"""

def run(**kwargs):
    import os
    path = kwargs.get('path', '.')
    entries = []
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        entries.append({'name': name, 'is_dir': os.path.isdir(full), 'size': os.path.getsize(full) if os.path.isfile(full) else None})
    return {'path': path, 'entries': entries, 'count': len(entries)}
