"""Skill: fs_disk_usage
Category: filesystem
Description: Return disk usage stats for a given path.
"""

def run(**kwargs):
    import shutil
    path = kwargs.get('path', '/')
    total, used, free = shutil.disk_usage(path)
    return {'total_gb': round(total/1e9,2), 'used_gb': round(used/1e9,2), 'free_gb': round(free/1e9,2), 'used_pct': round(used/total*100,1)}
