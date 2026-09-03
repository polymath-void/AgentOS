"""Skill: sys_list_processes
Category: system
Description: List running processes with PID and name.
"""

def run(**kwargs):
    import subprocess
    out = subprocess.check_output(['ps', 'aux'], text=True)
    lines = out.strip().splitlines()
    return {'header': lines[0], 'processes': [{'raw': l} for l in lines[1:50]], 'total': len(lines)-1}
