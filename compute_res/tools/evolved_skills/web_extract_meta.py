"""Skill: web_extract_meta
Category: web
Description: Extract title and meta tags from HTML.
"""

def run(**kwargs):
    import re
    html = kwargs.get('html', '')
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE|re.DOTALL)
    meta = {}
    for m in re.finditer(r'<meta[^>]+>', html, re.IGNORECASE):
        tag = m.group()
        nm = re.search(r'(?:name|property)=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        cm = re.search(r'content=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if nm and cm: meta[nm.group(1)] = cm.group(1)
    return {'title': title.group(1).strip() if title else None, 'meta': meta}
