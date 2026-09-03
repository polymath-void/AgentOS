"""Skill: math_percentile
Category: mathematics
Description: Calculate the Nth percentile of a numeric list.
"""

def run(**kwargs):
    import math
    data = sorted([float(x) for x in kwargs.get('data', [])])
    p = float(kwargs.get('p', 50))
    if not data: return {'error': 'empty'}
    k = (p/100)*(len(data)-1)
    f, c = math.floor(k), math.ceil(k)
    return {'percentile': p, 'value': data[f]+(data[c]-data[f])*(k-f)}
