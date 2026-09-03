"""Skill: math_fibonacci
Category: mathematics
Description: Generate the first N Fibonacci numbers.
"""

def run(**kwargs):
    n = int(kwargs.get('n', 10))
    seq = [0, 1]
    while len(seq) < n: seq.append(seq[-1]+seq[-2])
    return {'fibonacci': seq[:n]}
