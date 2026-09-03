"""Skill: sys_open_ports
Category: system
Description: List open listening TCP ports from /proc/net/tcp.
"""

def run(**kwargs):
    ports = []
    try:
        with open('/proc/net/tcp') as f:
            next(f)
            for line in f:
                parts = line.split()
                if parts[3] == '0A':
                    ports.append(int(parts[1].split(':')[1], 16))
    except Exception as e:
        return {'error': str(e)}
    return {'listening_ports': sorted(set(ports)), 'count': len(ports)}
