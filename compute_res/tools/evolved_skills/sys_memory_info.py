"""Skill: sys_memory_info
Category: system
Description: Return current system memory usage.
"""

def run(**kwargs):
    info = {}
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    info[parts[0].rstrip(':')] = parts[1]
    except Exception as e:
        return {'error': str(e)}
    return {'meminfo': info}
