"""Skill: os_path_exists
Category: system
Description: Check if a path exists and classify it.
"""

def run(**kwargs):
    import os
    path = kwargs.get('path', '')
    return {'exists': os.path.exists(path), 'is_file': os.path.isfile(path), 'is_dir': os.path.isdir(path), 'abs': os.path.abspath(path)}
