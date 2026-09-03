"""Skill: web_extract_links
Category: web
Description: Extract all href links from HTML.
"""

def run(**kwargs):
    import re
    html = kwargs.get('html', '')
    hrefs = list(set(re.findall(r'href=["\']([^"\'>]+)["\']', html, re.IGNORECASE)))
    return {'links': hrefs, 'count': len(hrefs)}
