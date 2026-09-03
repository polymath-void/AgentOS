"""Skill: crypto_base64_decode
Category: cryptography
Description: Base64-decode a string.
"""

def run(**kwargs):
    import base64
    try:
        return {'decoded': base64.b64decode(kwargs.get('encoded', '')).decode('utf-8', errors='replace')}
    except Exception as e:
        return {'error': str(e)}
