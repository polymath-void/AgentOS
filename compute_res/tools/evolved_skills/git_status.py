"""Skill: git_status
Category: version-control
Description: Return git status of a repository.
"""

def run(**kwargs):
    import subprocess
    repo = kwargs.get('repo', '.')
    r = subprocess.run(['git','status','--porcelain'], capture_output=True, text=True, cwd=repo)
    lines = r.stdout.strip().splitlines()
    return {'changes': lines, 'count': len(lines), 'clean': len(lines)==0}
