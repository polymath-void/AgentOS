"""Skill: data_merge_dicts
Category: data-processing
Description: Deep-merge two dictionaries.
"""

def run(**kwargs):
    def dm(a, b):
        r = dict(a)
        for k, v in b.items():
            r[k] = dm(r[k], v) if k in r and isinstance(r[k], dict) and isinstance(v, dict) else v
        return r
    return {'merged': dm(kwargs.get('a', {}), kwargs.get('b', {}))}
