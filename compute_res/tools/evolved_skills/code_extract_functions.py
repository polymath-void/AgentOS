"""Skill: code_extract_functions
Category: code-analysis
Description: Extract all function definitions from Python source.
"""

def run(**kwargs):
    import ast
    code = kwargs.get('code', '')
    try:
        tree = ast.parse(code)
        funcs = []
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.append({'name': n.name, 'args': [a.arg for a in n.args.args], 'lineno': n.lineno, 'doc': ast.get_docstring(n) or ''})
        return {'functions': funcs, 'count': len(funcs)}
    except SyntaxError as e:
        return {'error': str(e)}
