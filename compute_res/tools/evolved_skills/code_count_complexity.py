"""Skill: code_count_complexity
Category: code-analysis
Description: Count cyclomatic complexity in Python source.
"""

def run(**kwargs):
    import ast
    code = kwargs.get('code', '')
    BRANCH = (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler, ast.With, ast.Assert)
    try:
        tree = ast.parse(code)
        count = sum(1 for n in ast.walk(tree) if isinstance(n, BRANCH))
        return {'cyclomatic_complexity': count+1, 'branches': count}
    except SyntaxError as e:
        return {'error': str(e)}
