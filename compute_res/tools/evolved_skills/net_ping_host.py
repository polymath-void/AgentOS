"""Skill: net_ping_host
Category: networking
Description: Ping a host and return latency.
"""

def run(**kwargs):
    import subprocess
    host = kwargs.get('host', '8.8.8.8')
    r = subprocess.run(['ping', '-c', '1', '-W', '3', host], capture_output=True, text=True)
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            if 'time=' in line:
                ms = line.split('time=')[1].split()[0]
                return {'host': host, 'reachable': True, 'latency_ms': float(ms)}
        return {'host': host, 'reachable': True}
    return {'host': host, 'reachable': False}
