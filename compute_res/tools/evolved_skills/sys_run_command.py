"""Skill: sys_run_command
Category: system
Description: Run a shell command and return stdout, stderr, returncode.
"""

def run(**kwargs):
    import subprocess
    cmd = kwargs.get('cmd', '')
    timeout = int(kwargs.get('timeout', 30))
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return {'stdout': r.stdout, 'stderr': r.stderr, 'returncode': r.returncode}
