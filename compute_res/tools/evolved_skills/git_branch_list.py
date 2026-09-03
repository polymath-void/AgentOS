"""Skill: git_branch_list
Category: version-control
Description: List all local git branches.
"""

def run(**kwargs):
    import subprocess
    repo = kwargs.get('repo', '.')
    r = subprocess.run(['git','branch','-v'], capture_output=True, text=True, cwd=repo)
    branches = []
    for line in r.stdout.splitlines():
        current = line.startswith('*')
        parts = line.lstrip('* ').split()
        if parts: branches.append({'name': parts[0], 'current': current})
    return {'branches': branches}
