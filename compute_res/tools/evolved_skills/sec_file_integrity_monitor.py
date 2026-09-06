"""\nSkill: sec_file_integrity_monitor\nCategory: security\nDescription: Safe redesign of Aegis Vanguard: Computes baseline hashes of critical files to detect unauthorized changes.\n"""\n\ndef run(**kwargs):
    import os, hashlib, json
    directory = kwargs.get('directory', '.')
    baseline_path = kwargs.get('baseline_path', 'baseline.json')
    update = kwargs.get('update_baseline', False)
    
    current = {}
    for root, _, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            if path == os.path.abspath(baseline_path): continue
            try:
                h = hashlib.sha256()
                with open(path, 'rb') as fd:
                    for chunk in iter(lambda: fd.read(65536), b''): h.update(chunk)
                current[path] = h.hexdigest()
            except Exception: pass
            
    if update or not os.path.exists(baseline_path):
        with open(baseline_path, 'w') as f: json.dump(current, f)
        return {'status': 'baseline_updated', 'files_tracked': len(current)}
        
    with open(baseline_path, 'r') as f: baseline = json.load(f)
    changes = {'modified': [], 'added': [], 'deleted': []}
    for path, h in current.items():
        if path not in baseline: changes['added'].append(path)
        elif baseline[path] != h: changes['modified'].append(path)
    for path in baseline:
        if path not in current: changes['deleted'].append(path)
        
    return {'status': 'checked', 'changes_detected': any(changes.values()), 'details': changes}
