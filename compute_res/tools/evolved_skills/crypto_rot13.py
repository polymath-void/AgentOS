"""Skill: crypto_rot13
Category: cryptography
Description: Apply ROT13 encoding to a string.
"""

def run(**kwargs):
    import codecs
    text = kwargs.get('text', '')
    return {'input': text, 'rot13': codecs.encode(text, 'rot_13')}
