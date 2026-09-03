"""Skill: config_validate_json_schema
Category: configuration
Description: Validate a JSON object against a schema dict.
"""

def run(**kwargs):
    data = kwargs.get('data', {})
    schema = kwargs.get('schema', {})
    errors = []
    for key, expected in schema.items():
        if key not in data: errors.append(f'Missing: {key}')
        elif not isinstance(data[key], eval(expected)): errors.append(f'{key}: expected {expected}')
    return {'valid': len(errors)==0, 'errors': errors}
