"""Skill: net_dns_lookup
Category: networking
Description: Resolve a hostname to its IP addresses.
"""

def run(**kwargs):
    import socket
    host = kwargs.get('host', '')
    try:
        results = socket.getaddrinfo(host, None)
        ips = list({r[4][0] for r in results})
        return {'host': host, 'ips': ips}
    except Exception as e:
        return {'error': str(e)}
