import os, sys
sys.path.insert(0, '/data/data/com.termux/files/home/Projects/ComputeRes')
from compute_res.memory.skillshub_db import SkillsHubDB

SKILLS_DIR = '/data/data/com.termux/files/home/Projects/ComputeRes/compute_res/tools/evolved_skills'
os.makedirs(SKILLS_DIR, exist_ok=True)
db = SkillsHubDB()

SKILLS = [
    (
        "sys_smart_cache_cleaner",
        "system-optimization",
        ["cache", "cleanup", "storage"],
        "Safe redesign of DeepCleanse: Scans directories for files older than X days and safely deletes them.",
        """def run(**kwargs):
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
"""
    ),
    (
        "sys_crypto_deduplicator",
        "system-optimization",
        ["storage", "deduplication", "hardlink"],
        "Safe redesign of Storage-Mapper: Hashes files (SHA-256) and safely replaces duplicates with hardlinks.",
        """def run(**kwargs):
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
"""
    ),
    (
        "sys_swarm_load_balancer",
        "system-optimization",
        ["load", "monitor", "cpu"],
        "Safe redesign of Governor-AI: Monitors /proc/loadavg and /proc/meminfo to recommend throttling or pausing tasks.",
        """def run(**kwargs):
    import os
    try:
        with open('/proc/loadavg') as f:
            load = [float(x) for x in f.read().split()[:3]]
        mem_total = mem_avail = 1
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemTotal:'): mem_total = int(line.split()[1])
                elif line.startswith('MemAvailable:'): mem_avail = int(line.split()[1])
        mem_usage_pct = 100 - (mem_avail / mem_total * 100)
        action = "NORMAL"
        if load[0] > (os.cpu_count() or 1) * 1.5 or mem_usage_pct > 90: action = "THROTTLE"
        elif load[0] > (os.cpu_count() or 1) or mem_usage_pct > 80: action = "PAUSE_BACKGROUND"
        return {'load_1m': load[0], 'mem_usage_pct': round(mem_usage_pct, 2), 'recommendation': action}
    except Exception as e:
        return {'error': str(e)}
"""
    ),
    (
        "dev_state_inspector",
        "developer-tools",
        ["debug", "memory", "introspection"],
        "Safe redesign of Hex-Mem-Mapper: Safely introspects the agent's own running state and memory footprint.",
        """def run(**kwargs):
    import sys, threading, os
    try:
        with open(f'/proc/{os.getpid()}/status') as f:
            mem = next((line.split()[1] for line in f if line.startswith('VmRSS')), '0')
        threads = [t.name for t in threading.enumerate()]
        modules = len(sys.modules)
        return {'pid': os.getpid(), 'rss_kb': int(mem), 'active_threads': threads, 'loaded_modules': modules}
    except Exception as e:
        return {'error': str(e)}
"""
    ),
    (
        "dev_wasm_pipeline",
        "developer-tools",
        ["wasm", "compile", "build"],
        "Safe redesign of WASM-Bridge: Generates compilation commands for safely building C/Rust to WASM.",
        """def run(**kwargs):
    import os
    source_file = kwargs.get('source_file', '')
    output_wasm = kwargs.get('output_wasm', 'out.wasm')
    if not source_file or not os.path.exists(source_file): return {'error': 'source_file not found'}
    cmd = ['emcc', source_file, '-O3', '-s', 'WASM=1', '-o', output_wasm]
    return {'command_to_run': ' '.join(cmd), 'status': 'ready_to_build', 'note': 'Execute this command to safely compile to WASM.'}
"""
    ),
    (
        "media_perceptual_dedup",
        "media-management",
        ["image", "hash", "dedup"],
        "Safe redesign of HoloDedup: Computes dhash for images to find visually similar files and optionally hardlinks them.",
        """def run(**kwargs):
    import os
    try:
        from PIL import Image
    except ImportError:
        return {'error': 'Pillow library required: pip install Pillow'}
    directory = kwargs.get('directory', '.')
    dry_run = kwargs.get('dry_run', True)
    
    def dhash(image, hash_size=8):
        image = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(image.getdata())
        diff = [pixels[row*hash_size + col] > pixels[row*hash_size + col + 1] for row in range(hash_size) for col in range(hash_size)]
        return sum([2 ** i for (i, v) in enumerate(diff) if v])
        
    hashes = {}; duplicates = []
    for root, _, files in os.walk(directory):
        for f in files:
            if not f.lower().endswith(('.png', '.jpg', '.jpeg')): continue
            path = os.path.join(root, f)
            try:
                with Image.open(path) as img: h = dhash(img)
                if h in hashes:
                    orig = hashes[h]
                    duplicates.append((path, orig))
                    if not dry_run:
                        os.remove(path); os.link(orig, path)
                else: hashes[h] = path
            except Exception: pass
    return {'status': 'completed', 'duplicates_found': len(duplicates), 'dry_run': dry_run}
"""
    ),
    (
        "media_metadata_anonymizer",
        "media-management",
        ["metadata", "exif", "privacy"],
        "Safe redesign of ChronoScrubber: Strips EXIF metadata from images in a folder without intercepting system writes.",
        """def run(**kwargs):
    import os
    try:
        from PIL import Image
    except ImportError:
        return {'error': 'Pillow library required: pip install Pillow'}
    directory = kwargs.get('directory', '.')
    processed = 0
    for root, _, files in os.walk(directory):
        for f in files:
            if not f.lower().endswith(('.png', '.jpg', '.jpeg')): continue
            path = os.path.join(root, f)
            try:
                with Image.open(path) as img:
                    data = list(img.getdata())
                    clean = Image.new(img.mode, img.size)
                    clean.putdata(data)
                    clean.save(path)
                processed += 1
            except Exception: pass
    return {'status': 'completed', 'images_anonymized': processed}
"""
    ),
    (
        "sec_secure_erase",
        "security",
        ["delete", "wipe", "privacy"],
        "Safe redesign of Oblivion Shredder: Overwrites a file multiple times with random data before standard deletion.",
        """def run(**kwargs):
    import os
    path = kwargs.get('path', '')
    if not os.path.exists(path) or not os.path.isfile(path): return {'error': 'File not found'}
    size = os.path.getsize(path)
    try:
        with open(path, 'r+b') as f:
            for _ in range(3):
                f.seek(0); f.write(os.urandom(size)); f.flush(); os.fsync(f.fileno())
            f.seek(0); f.write(b'\\x00' * size); f.flush(); os.fsync(f.fileno())
        os.remove(path)
        return {'status': 'securely_erased', 'path': path, 'bytes_wiped': size}
    except Exception as e:
        return {'error': str(e)}
"""
    ),
    (
        "sec_file_integrity_monitor",
        "security",
        ["fim", "integrity", "hash"],
        "Safe redesign of Aegis Vanguard: Computes baseline hashes of critical files to detect unauthorized changes.",
        """def run(**kwargs):
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
"""
    )
]

count = 0
for skill_name, category, tags, desc, code in SKILLS:
    code_path = os.path.join(SKILLS_DIR, f'{skill_name}.py')
    with open(code_path, 'w') as f:
        f.write(f'"""\\nSkill: {skill_name}\\nCategory: {category}\\nDescription: {desc}\\n"""\\n\\n')
        f.write(code)
    
    db.publish_skill(
        name=skill_name,
        description=desc,
        author="ComputeRes-Core-Library",
        version="1.0.0",
        code_path=code_path,
        categories=[category],
        tags=tags
    )
    count += 1
    print(f"Registered safe skill: {skill_name}")

print(f"Successfully implemented {count} safe tools in SkillsHub.")
