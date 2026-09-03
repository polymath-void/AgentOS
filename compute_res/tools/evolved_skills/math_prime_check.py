"""Skill: math_prime_check
Category: mathematics
Description: Check if a number is prime.
"""

def run(**kwargs):
    import math
    n = int(kwargs.get('n', 2))
    if n < 2: return {'is_prime': False}
    if n == 2: return {'is_prime': True}
    if n % 2 == 0: return {'is_prime': False}
    for i in range(3, int(math.sqrt(n))+1, 2):
        if n % i == 0: return {'is_prime': False, 'factor': i}
    return {'n': n, 'is_prime': True}
