"""Skill: git_log
Category: version-control
Description: Return last N git commits.
"""

def run(**kwargs):
    import subprocess
    repo = kwargs.get('repo', '.')
    n = int(kwargs.get('n', 10))
    fmt = '%H|%an|%ai|%s'
    r = subprocess.run(['git','log',f'-{n}',f'--pretty=format:{fmt}'], capture_output=True, text=True, cwd=repo)
    commits = []
    for line in r.stdout.strip().splitlines():
        parts = line.split('|', 3)
        if len(parts)==4: commits.append({'hash':parts[0],'author':parts[1],'date':parts[2],'msg':parts[3]})
    return {'commits': commits}
