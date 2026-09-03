"""Skill: crypto_hmac_sign
Category: cryptography
Description: Sign a message with HMAC-SHA256.
"""

def run(**kwargs):
    import hmac, hashlib
    key = kwargs.get('key', '').encode()
    msg = kwargs.get('message', '').encode()
    sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return {'signature': sig, 'algo': 'hmac-sha256'}
