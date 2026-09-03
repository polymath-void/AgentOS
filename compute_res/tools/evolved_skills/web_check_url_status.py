"""Skill: web_check_url_status
Category: web
Description: Check HTTP status codes for a list of URLs.
"""

def run(**kwargs):
    import urllib.request
    results = []
    for url in kwargs.get('urls', [])[:20]:
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as r:
                results.append({'url': url, 'status': r.status, 'ok': r.status < 400})
        except Exception as e:
            results.append({'url': url, 'ok': False, 'error': str(e)})
    return {'results': results}
