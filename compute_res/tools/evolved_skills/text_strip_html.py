"""Skill: text_strip_html
Category: text-processing
Description: Remove all HTML tags from a string.
"""

def run(**kwargs):
    import re
    html = kwargs.get('html', '')
    clean = re.sub(r'<[^>]+>', '', html)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return {'plain': clean, 'clean_len': len(clean)}
