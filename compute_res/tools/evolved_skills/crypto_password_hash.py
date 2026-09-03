"""Skill: crypto_password_hash
Category: cryptography
Description: Hash a password using PBKDF2-HMAC-SHA256.
"""

def run(**kwargs):
    import hashlib, os, base64
    pw = kwargs.get('password', '')
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, 200000)
    return {'hash': f'pbkdf2:sha256:200000:{base64.b64encode(salt).decode()}:{base64.b64encode(dk).decode()}'}
