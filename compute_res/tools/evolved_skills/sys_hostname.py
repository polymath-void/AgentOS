"""Skill: sys_hostname
Category: system
Description: Return the system hostname and FQDN.
"""

def run(**kwargs):
    import socket
    return {'hostname': socket.gethostname(), 'fqdn': socket.getfqdn()}
