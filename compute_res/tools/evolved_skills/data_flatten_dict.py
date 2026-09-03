"""Skill: data_flatten_dict
Category: data-processing
Description: Flatten a nested dictionary into dot-notation keys.
"""

def run(**kwargs):
    data = kwargs.get('data', {})
    sep = kwargs.get('sep', '.')
    def _flat(d, parent=''):
        items = {}
        for k, v in d.items():
            key = f'{parent}{sep}{k}' if parent else k
            if isinstance(v, dict): items.update(_flat(v, key))
            else: items[key] = v
        return items
    return {'flattened': _flat(data)}
