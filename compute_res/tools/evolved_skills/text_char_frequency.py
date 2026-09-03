"""Skill: text_char_frequency
Category: text-processing
Description: Count character frequencies in a string.
"""

def run(**kwargs):
    from collections import Counter
    text = kwargs.get('text', '')
    if kwargs.get('ignore_spaces', True): text = text.replace(' ', '')
    return {'frequency': dict(Counter(text).most_common()), 'total': len(text)}
