"""Skill: data_diff_dicts
Category: data-processing
Description: Compute the difference between two dictionaries.
"""

def run(**kwargs):
    a = kwargs.get('a', {})
    b = kwargs.get('b', {})
    return {'added': {k: b[k] for k in b if k not in a}, 'removed': {k: a[k] for k in a if k not in b}, 'changed': {k: {'old': a[k], 'new': b[k]} for k in a if k in b and a[k] != b[k]}}
