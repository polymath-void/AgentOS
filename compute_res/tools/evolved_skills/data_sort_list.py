"""Skill: data_sort_list
Category: data-processing
Description: Sort a list of items or dicts by a key.
"""

def run(**kwargs):
    items = kwargs.get('items', [])
    key = kwargs.get('key', None)
    reverse = kwargs.get('reverse', False)
    if key and items and isinstance(items[0], dict):
        result = sorted(items, key=lambda x: x.get(key, ''), reverse=reverse)
    else:
        result = sorted(items, reverse=reverse)
    return {'sorted': result, 'count': len(result)}
