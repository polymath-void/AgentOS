"""Skill: time_parse
Category: datetime
Description: Parse a datetime string in various formats.
"""

def run(**kwargs):
    from datetime import datetime
    raw = kwargs.get('raw', '')
    for fmt in ['%Y-%m-%dT%H:%M:%SZ','%Y-%m-%dT%H:%M:%S','%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d/%m/%Y']:
        try:
            dt = datetime.strptime(raw, fmt)
            return {'parsed': dt.isoformat(), 'format': fmt, 'unix': int(dt.timestamp())}
        except ValueError: continue
    return {'error': f'Cannot parse: {raw}'}
