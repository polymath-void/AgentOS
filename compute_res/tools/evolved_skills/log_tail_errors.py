"""Skill: log_tail_errors
Category: logging
Description: Return last N ERROR lines from a log file.
"""

def run(**kwargs):
    path = kwargs.get('path', '')
    n = int(kwargs.get('n', 20))
    errors = []
    with open(path, 'r', errors='replace') as f:
        for i, line in enumerate(f, 1):
            if 'ERROR' in line or 'CRITICAL' in line: errors.append({'lineno': i, 'line': line.rstrip()})
    return {'errors': errors[-n:], 'total_errors': len(errors)}
