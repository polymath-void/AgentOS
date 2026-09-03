"""Skill: fs_zip_directory
Category: filesystem
Description: Zip an entire directory into a .zip archive.
"""

def run(**kwargs):
    import shutil, os
    src = kwargs.get('src_dir', '')
    out = kwargs.get('out_path', src + '.zip')
    base = os.path.splitext(out)[0]
    shutil.make_archive(base, 'zip', src)
    return {'status': 'archived', 'archive': base + '.zip'}
