"""Skill: git_diff
Category: version-control
Description: Return git diff for the repo or a file.
"""

def run(**kwargs):
    import subprocess
    repo = kwargs.get('repo', '.')
    path = kwargs.get('path', '')
    cmd = ['git','diff'] + ([path] if path else [])
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo)
    return {'diff': r.stdout, 'lines': len(r.stdout.splitlines())}
