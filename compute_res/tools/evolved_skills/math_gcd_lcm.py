"""Skill: math_gcd_lcm
Category: mathematics
Description: Compute GCD and LCM of two integers.
"""

def run(**kwargs):
    import math
    a, b = int(kwargs.get('a',12)), int(kwargs.get('b',8))
    gcd = math.gcd(a, b)
    return {'a': a, 'b': b, 'gcd': gcd, 'lcm': abs(a*b)//gcd if gcd else 0}
