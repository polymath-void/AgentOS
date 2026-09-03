"""Skill: data_deduplicate_list
Category: data-processing
Description: Remove duplicates from a list preserving order.
"""

def run(**kwargs):
    items = kwargs.get('items', [])
    seen = set(); result = []
    for x in items:
        k = str(x)
        if k not in seen: seen.add(k); result.append(x)
    return {'result': result, 'original': len(items), 'deduped': len(result)}
