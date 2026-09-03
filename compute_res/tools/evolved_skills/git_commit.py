"""Skill: git_commit
Category: version-control
Description: Stage all changes and git commit.
"""

def run(**kwargs):
    import subprocess
    repo = kwargs.get('repo', '.')
    msg = kwargs.get('message', 'Auto-commit by ComputeRes OS')
    subprocess.run(['git','add','-A'], cwd=repo)
    r = subprocess.run(['git','commit','-m',msg], capture_output=True, text=True, cwd=repo)
    return {'stdout': r.stdout, 'returncode': r.returncode}
