"""Skill: agent_get_kernel_status
Category: agent-os
Description: Check if the ComputeRes Kernel is reachable.
"""

def run(**kwargs):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('127.0.0.1', 5557)); s.close()
        return {'kernel': 'online'}
    except Exception as e:
        return {'kernel': 'offline', 'error': str(e)}
