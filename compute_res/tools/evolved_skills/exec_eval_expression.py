"""Skill: exec_eval_expression
Category: runtime
Description: Safely evaluate a Python math expression.
"""

def run(**kwargs):
    import math
    expr = kwargs.get('expr', '1+1')
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
    allowed.update({'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum, 'len': len, 'int': int, 'float': float})
    try:
        result = eval(expr, {'__builtins__': allowed})
        return {'expr': expr, 'result': result, 'type': type(result).__name__}
    except Exception as e:
        return {'error': str(e)}
