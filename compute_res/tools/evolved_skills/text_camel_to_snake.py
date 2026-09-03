"""Skill: text_camel_to_snake
Category: text-processing
Description: Convert camelCase to snake_case.
"""

def run(**kwargs):
    import re
    text = kwargs.get('text', '')
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return {'input': text, 'snake_case': s.lower()}
