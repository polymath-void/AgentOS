"""Skill: log_grep
Category: logging
Description: Search a log file for lines matching a pattern.
"""

def run(**kwargs):
    import re
    path = kwargs.get('path', '')
    pattern = kwargs.get('pattern', '')
    context = int(kwargs.get('context', 0))
    matches = []
    with open(path, 'r', errors='replace') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if re.search(pattern, line, re.IGNORECASE):
            start = max(0, i-context); end = min(len(lines), i+context+1)
            matches.append({'lineno': i+1, 'line': line.strip(), 'ctx': [l.rstrip() for l in lines[start:end]]})
    return {'matches': matches, 'count': len(matches)}
