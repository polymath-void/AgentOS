"""Skill: crypto_hash_file
Category: cryptography
Description: Compute SHA-256 checksum of a file.
"""

def run(**kwargs):
    import hashlib
    path = kwargs.get('path', '')
    algo = kwargs.get('algo', 'sha256')
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return {'path': path, 'algo': algo, 'checksum': h.hexdigest()}
