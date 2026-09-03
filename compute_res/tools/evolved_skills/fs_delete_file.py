"""Skill: fs_delete_file
Category: filesystem
Description: Safely delete a file or empty directory.
"""

def run(**kwargs):
    import os
    path = kwargs.get('path', '')
    if not os.path.exists(path):
        return {'error': f'Not found: {path}'}
    if os.path.isfile(path):
        os.remove(path)
        return {'status': 'deleted', 'type': 'file'}
    os.rmdir(path)
    return {'status': 'deleted', 'type': 'dir'}
