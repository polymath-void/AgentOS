"""Skill: config_write_json
Category: configuration
Description: Write a dictionary to a JSON config file.
"""

def run(**kwargs):
    import json
    data = kwargs.get('data', {})
    path = kwargs.get('path', 'config.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=int(kwargs.get('indent', 2)), ensure_ascii=False)
    return {'status': 'written', 'path': path}
