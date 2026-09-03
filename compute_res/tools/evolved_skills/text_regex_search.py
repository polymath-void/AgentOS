"""Skill: text_regex_search
Category: text-processing
Description: Find all regex matches in text.
"""

def run(**kwargs):
    import re
    pattern = kwargs.get('pattern', '')
    text = kwargs.get('text', '')
    try:
        matches = re.findall(pattern, text, re.MULTILINE)
        return {'matches': matches, 'count': len(matches)}
    except re.error as e:
        return {'error': str(e)}
