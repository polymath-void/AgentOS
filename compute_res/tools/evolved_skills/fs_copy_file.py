"""Skill: fs_copy_file
Category: filesystem
Description: Copy a file from source to destination.
"""

def run(**kwargs):
    import shutil, os
    src = kwargs.get('src', '')
    dst = kwargs.get('dst', '')
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    shutil.copy2(src, dst)
    return {'status': 'copied', 'src': src, 'dst': dst}
