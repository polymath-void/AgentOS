"""Skill: sys_kill_process
Category: system
Description: Kill a process by PID.
"""

def run(**kwargs):
    import os, signal
    pid = int(kwargs.get('pid', 0))
    sig = int(kwargs.get('signal', signal.SIGTERM))
    os.kill(pid, sig)
    return {'status': 'sent', 'pid': pid, 'signal': sig}
