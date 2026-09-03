"""Skill: serial_from_json
Category: serialization
Description: Deserialize a JSON string to a Python object.
"""

def run(**kwargs):
    import json
    try:
        obj = json.loads(kwargs.get('raw', '{}'))
        return {'data': obj, 'type': type(obj).__name__}
    except json.JSONDecodeError as e:
        return {'error': str(e)}
