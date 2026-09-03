"""Skill: code_format_json
Category: code-analysis
Description: Pretty-print a JSON string.
"""

def run(**kwargs):
    import json
    raw = kwargs.get('raw', '{}')
    indent = int(kwargs.get('indent', 2))
    try:
        return {'formatted': json.dumps(json.loads(raw), indent=indent, ensure_ascii=False)}
    except json.JSONDecodeError as e:
        return {'error': str(e)}
