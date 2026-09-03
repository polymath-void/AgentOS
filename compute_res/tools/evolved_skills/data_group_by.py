"""Skill: data_group_by
Category: data-processing
Description: Group a list of dicts by a specified key.
"""

def run(**kwargs):
    from collections import defaultdict
    items = kwargs.get('items', [])
    key = kwargs.get('key', '')
    groups = defaultdict(list)
    for item in items: groups[str(item.get(key, 'null'))].append(item)
    return {'groups': dict(groups), 'group_count': len(groups)}
