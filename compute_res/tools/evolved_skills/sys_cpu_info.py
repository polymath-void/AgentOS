"""Skill: sys_cpu_info
Category: system
Description: Return CPU model, core count, and architecture.
"""

def run(**kwargs):
    import platform, os
    info = {'machine': platform.machine(), 'processor': platform.processor(), 'cores': os.cpu_count()}
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if 'model name' in line:
                    info['model'] = line.split(':')[1].strip()
                    break
    except Exception: pass
    return info
