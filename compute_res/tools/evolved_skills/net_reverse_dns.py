"""Skill: net_reverse_dns
Category: networking
Description: Reverse DNS lookup on an IP address.
"""

def run(**kwargs):
    import socket
    ip = kwargs.get('ip', '')
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return {'ip': ip, 'hostname': hostname}
    except Exception as e:
        return {'error': str(e)}
