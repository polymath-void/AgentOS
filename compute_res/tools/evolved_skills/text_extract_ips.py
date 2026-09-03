"""Skill: text_extract_ips
Category: text-processing
Description: Extract all IPv4 addresses from text.
"""

def run(**kwargs):
    import re
    ips = list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', kwargs.get('text', ''))))
    return {'ips': ips, 'count': len(ips)}
