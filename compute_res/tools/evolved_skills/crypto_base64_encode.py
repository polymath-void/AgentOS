"""Skill: crypto_base64_encode
Category: cryptography
Description: Base64-encode a string.
"""

def run(**kwargs):
    import base64
    text = kwargs.get('text', '')
    return {'encoded': base64.b64encode(text.encode()).decode()}
