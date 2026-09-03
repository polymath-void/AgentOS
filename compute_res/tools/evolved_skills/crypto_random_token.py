"""Skill: crypto_random_token
Category: cryptography
Description: Generate a cryptographically secure random token.
"""

def run(**kwargs):
    import secrets
    n = int(kwargs.get('bytes', 32))
    fmt = kwargs.get('format', 'hex')
    if fmt == 'urlsafe': return {'token': secrets.token_urlsafe(n)}
    return {'token': secrets.token_bytes(n).hex(), 'bytes': n}
