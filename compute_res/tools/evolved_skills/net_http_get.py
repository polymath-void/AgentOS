"""Skill: net_http_get
Category: networking
Description: Perform an HTTP GET request and return status and body.
"""

def run(**kwargs):
    import urllib.request
    url = kwargs.get('url', '')
    timeout = int(kwargs.get('timeout', 10))
    if not url: return {'error': 'url required'}
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return {'status': r.status, 'body': r.read().decode('utf-8', errors='replace')[:5000]}
    except Exception as e:
        return {'error': str(e), 'url': url}
