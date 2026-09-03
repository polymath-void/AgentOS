"""Skill: data_parse_json
Category: data-processing
Description: Parse a JSON string and return the object.
"""

def run(**kwargs):
    import json
    try:
        obj = json.loads(kwargs.get('raw', '{}'))
        return {'parsed': obj, 'type': type(obj).__name__}
    except json.JSONDecodeError as e:
        return {'error': str(e)}
