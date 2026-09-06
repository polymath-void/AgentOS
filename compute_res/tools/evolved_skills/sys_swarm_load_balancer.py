"""\nSkill: sys_swarm_load_balancer\nCategory: system-optimization\nDescription: Safe redesign of Governor-AI: Monitors /proc/loadavg and /proc/meminfo to recommend throttling or pausing tasks.\n"""\n\ndef run(**kwargs):
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
