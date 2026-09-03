"""Skill: fs_unzip_archive
Category: filesystem
Description: Extract a .zip archive to a target directory.
"""

def run(**kwargs):
    import zipfile, os
    zp = kwargs.get('zip_path', '')
    out = kwargs.get('out_dir', os.path.dirname(zp))
    with zipfile.ZipFile(zp, 'r') as zf:
        zf.extractall(out)
    return {'status': 'extracted', 'to': out}
