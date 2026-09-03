"""Skill: crypto_xor_cipher
Category: cryptography
Description: XOR-encrypt/decrypt a string with a single-byte key.
"""

def run(**kwargs):
    text = kwargs.get('text', '')
    key = int(kwargs.get('key', 42))
    return {'result': ''.join(chr(ord(c) ^ key) for c in text)}
