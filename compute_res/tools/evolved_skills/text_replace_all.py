"""Skill: text_replace_all
Category: text-processing
Description: Perform multiple string replacements from a mapping.
"""

def run(**kwargs):
    text = kwargs.get('text', '')
    for old, new in kwargs.get('replacements', {}).items():
        text = text.replace(old, new)
    return {'result': text}
