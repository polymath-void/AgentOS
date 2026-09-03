"""Skill: serial_to_json
Category: serialization
Description: Serialize a Python object to JSON string.
"""

def run(**kwargs):
    import json
    data = kwargs.get('data', {})
    return {'json': json.dumps(data, default=str, ensure_ascii=False)}
