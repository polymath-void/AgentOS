"""Skill: net_port_check
Category: networking
Description: Check if a TCP port is open on a remote host.
"""

def run(**kwargs):
    import socket
    host = kwargs.get('host', 'localhost')
    port = int(kwargs.get('port', 80))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(float(kwargs.get('timeout', 3)))
    try:
        s.connect((host, port))
        s.close()
        return {'host': host, 'port': port, 'open': True}
    except Exception:
        return {'host': host, 'port': port, 'open': False}
