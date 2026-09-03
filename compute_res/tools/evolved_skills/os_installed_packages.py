"""Skill: os_installed_packages
Category: system
Description: List all installed Python packages.
"""

def run(**kwargs):
    import subprocess, json
    r = subprocess.run(['pip','list','--format=json'], capture_output=True, text=True)
    if r.returncode == 0:
        pkgs = json.loads(r.stdout)
        return {'packages': pkgs, 'count': len(pkgs)}
    return {'raw': r.stdout + r.stderr}
