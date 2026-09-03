"""Skill: fs_find_files
Category: filesystem
Description: Recursively find files matching a glob pattern.
"""

def run(**kwargs):
    import glob, os
    root = kwargs.get('root', '.')
    pattern = kwargs.get('pattern', '*')
    matches = glob.glob(os.path.join(root, '**', pattern), recursive=True)
    return {'matches': matches, 'count': len(matches)}
