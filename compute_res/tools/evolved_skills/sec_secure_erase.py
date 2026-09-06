"""\nSkill: sec_secure_erase\nCategory: security\nDescription: Safe redesign of Oblivion Shredder: Overwrites a file multiple times with random data before standard deletion.\n"""\n\ndef run(**kwargs):
    import os
    path = kwargs.get('path', '')
    if not os.path.exists(path) or not os.path.isfile(path): return {'error': 'File not found'}
    size = os.path.getsize(path)
    try:
        with open(path, 'r+b') as f:
            for _ in range(3):
                f.seek(0); f.write(os.urandom(size)); f.flush(); os.fsync(f.fileno())
            f.seek(0); f.write(b'\x00' * size); f.flush(); os.fsync(f.fileno())
        os.remove(path)
        return {'status': 'securely_erased', 'path': path, 'bytes_wiped': size}
    except Exception as e:
        return {'error': str(e)}
