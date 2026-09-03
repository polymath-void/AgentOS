"""Skill: net_http_post
Category: networking
Description: Perform an HTTP POST with a JSON body.
"""

def run(**kwargs):
    import urllib.request, json
    url = kwargs.get('url', '')
    data = kwargs.get('data', {})
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return {'status': r.status, 'body': r.read().decode(errors='replace')[:5000]}
    except Exception as e:
        return {'error': str(e)}
