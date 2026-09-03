"""Skill: net_get_public_ip
Category: networking
Description: Fetch the current public IP address.
"""

def run(**kwargs):
    import urllib.request
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=8) as r:
            return {'public_ip': r.read().decode()}
    except Exception as e:
        return {'error': str(e)}
