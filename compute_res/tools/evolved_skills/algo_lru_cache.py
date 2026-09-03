"""Skill: algo_lru_cache
Category: algorithms
Description: Simulate an LRU cache with get/put operations.
"""

def run(**kwargs):
    from collections import OrderedDict
    ops = kwargs.get('ops', [])
    capacity = int(kwargs.get('capacity', 3))
    cache = OrderedDict(); results = []
    for op in ops:
        if op[0]=='get':
            k = op[1]
            if k in cache: cache.move_to_end(k); results.append(cache[k])
            else: results.append(-1)
        elif op[0]=='put':
            k,v = op[1],op[2]
            if k in cache: cache.move_to_end(k)
            cache[k]=v
            if len(cache)>capacity: cache.popitem(last=False)
            results.append(None)
    return {'results': results, 'final_cache': dict(cache)}
