"""Skill: code_find_todos
Category: code-analysis
Description: Find all TODO/FIXME/HACK comments in source code.
"""

def run(**kwargs):
    import re
    code = kwargs.get('code', '')
    pattern = r'#.*(TODO|FIXME|HACK|XXX|BUG|NOTE).*'
    matches = []
    for i, line in enumerate(code.splitlines(), 1):
        m = re.search(pattern, line, re.IGNORECASE)
        if m: matches.append({'line': i, 'text': line.strip(), 'type': m.group(1).upper()})
    return {'todos': matches, 'count': len(matches)}
