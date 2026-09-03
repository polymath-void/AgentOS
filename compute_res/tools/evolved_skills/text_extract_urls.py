"""Skill: text_extract_urls
Category: text-processing
Description: Extract all HTTP/HTTPS URLs from text.
"""

def run(**kwargs):
    import re
    urls = list(set(re.findall(r'https?://[^\s<>"\'{\\}|^`\[\]]+', kwargs.get('text', ''))))
    return {'urls': urls, 'count': len(urls)}
