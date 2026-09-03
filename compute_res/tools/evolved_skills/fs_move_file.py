"""Skill: fs_move_file
Category: filesystem
Description: Move or rename a file or directory.
"""

def run(**kwargs):
    import shutil
    src = kwargs.get('src', '')
    dst = kwargs.get('dst', '')
    shutil.move(src, dst)
    return {'status': 'moved', 'src': src, 'dst': dst}
