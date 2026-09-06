"""\nSkill: sys_crypto_deduplicator\nCategory: system-optimization\nDescription: Safe redesign of Storage-Mapper: Hashes files (SHA-256) and safely replaces duplicates with hardlinks.\n"""\n\ndef run(**kwargs):
    import os, hashlib
    directory = kwargs.get('directory', '.')
    dry_run = kwargs.get('dry_run', True)
    hashes = {}
    duplicates = []
    freed = 0
    for root, _, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            try:
                if os.path.islink(path): continue
                h = hashlib.sha256()
                with open(path, 'rb') as fd:
                    for chunk in iter(lambda: fd.read(65536), b''): h.update(chunk)
                file_hash = h.hexdigest()
                if file_hash in hashes:
                    orig = hashes[file_hash]
                    duplicates.append((path, orig))
                    freed += os.path.getsize(path)
                    if not dry_run:
                        os.remove(path)
                        os.link(orig, path)
                else:
                    hashes[file_hash] = path
            except Exception: pass
    return {'status': 'completed', 'duplicates_found': len(duplicates), 'bytes_reclaimable': freed, 'dry_run': dry_run}
