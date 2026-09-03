"""Skill: sys_uptime
Category: system
Description: Return system uptime and load averages.
"""

def run(**kwargs):
    try:
        with open('/proc/uptime') as f:
            secs = float(f.read().split()[0])
        uptime = f'{int(secs//3600)}h {int((secs%3600)//60)}m {int(secs%60)}s'
        with open('/proc/loadavg') as f:
            load = f.read().strip()
        return {'uptime': uptime, 'uptime_seconds': secs, 'load': load}
    except Exception as e:
        return {'error': str(e)}
