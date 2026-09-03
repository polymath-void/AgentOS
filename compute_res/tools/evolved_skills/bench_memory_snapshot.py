"""Skill: bench_memory_snapshot
Category: benchmarking
Description: Return current process memory usage in MB.
"""

def run(**kwargs):
    import os
    try:
        with open(f'/proc/{os.getpid()}/status') as f:
            for line in f:
                if line.startswith('VmRSS'):
                    kb = int(line.split()[1])
                    return {'rss_mb': round(kb/1024,2), 'rss_kb': kb}
    except Exception as e:
        return {'error': str(e)}
