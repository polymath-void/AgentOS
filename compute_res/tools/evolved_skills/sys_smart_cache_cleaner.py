"""\nSkill: sys_smart_cache_cleaner\nCategory: system-optimization\nDescription: Safe redesign of DeepCleanse: Scans directories for files older than X days and safely deletes them.\n"""\n\ndef run(**kwargs):
    import os, time
    dirs = kwargs.get('directories', ['/tmp'])
    days = float(kwargs.get('days', 7))
    now = time.time()
    deleted, bytes_freed = 0, 0
    for d in dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for f in files:
                path = os.path.join(root, f)
                try:
                    stat = os.stat(path)
                    if (now - stat.st_mtime) > (days * 86400):
                        bytes_freed += stat.st_size
                        os.remove(path)
                        deleted += 1
                except Exception: pass
    return {'status': 'completed', 'files_deleted': deleted, 'bytes_freed': bytes_freed}
