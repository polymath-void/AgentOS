"""Skill: text_truncate
Category: text-processing
Description: Truncate text to N characters with ellipsis.
"""

def run(**kwargs):
    text = kwargs.get('text', '')
    n = int(kwargs.get('max_chars', 200))
    return {'result': text[:n] + ('...' if len(text) > n else ''), 'original_len': len(text)}
