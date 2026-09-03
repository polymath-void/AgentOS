"""Skill: math_binary_convert
Category: mathematics
Description: Convert a number between bases.
"""

def run(**kwargs):
    n = kwargs.get('n', '42')
    base = int(kwargs.get('from_base', 10))
    d = int(str(n), base)
    return {'decimal': d, 'binary': bin(d), 'octal': oct(d), 'hex': hex(d)}
