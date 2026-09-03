"""Skill: time_elapsed
Category: datetime
Description: Compute elapsed time between two ISO timestamps.
"""

def run(**kwargs):
    from datetime import datetime
    s = datetime.fromisoformat(kwargs.get('start','').replace('Z',''))
    e = datetime.fromisoformat(kwargs.get('end','').replace('Z',''))
    diff = e - s
    return {'seconds': diff.total_seconds(), 'minutes': round(diff.total_seconds()/60,2), 'human': str(diff)}
