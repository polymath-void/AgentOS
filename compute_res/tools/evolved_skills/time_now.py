"""Skill: time_now
Category: datetime
Description: Return current UTC and local timestamp in multiple formats.
"""

def run(**kwargs):
    import datetime, time
    now = datetime.datetime.utcnow()
    return {'utc_iso': now.isoformat()+'Z', 'unix': int(time.time()), 'unix_ms': int(time.time()*1000), 'date': now.strftime('%Y-%m-%d'), 'time': now.strftime('%H:%M:%S')}
