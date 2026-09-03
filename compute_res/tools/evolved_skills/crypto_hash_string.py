"""Skill: crypto_hash_string
Category: cryptography
Description: Hash a string using SHA-256.
"""

def run(**kwargs):
    import hashlib
    text = kwargs.get('text', '')
    algo = kwargs.get('algo', 'sha256')
    h = hashlib.new(algo, text.encode())
    return {'input': text, 'algo': algo, 'digest': h.hexdigest()}
