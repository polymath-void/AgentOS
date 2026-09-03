"""Skill: log_count_errors
Category: logging
Description: Count ERROR/WARNING/INFO lines in a log file.
"""

def run(**kwargs):
    path = kwargs.get('path', '')
    counts = {'ERROR': 0, 'WARNING': 0, 'INFO': 0, 'DEBUG': 0, 'CRITICAL': 0}
    with open(path, 'r', errors='replace') as f:
        for line in f:
            for level in counts:
                if level in line: counts[level] += 1
    return {'counts': counts, 'path': path}
