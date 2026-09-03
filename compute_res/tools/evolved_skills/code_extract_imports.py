"""Skill: code_extract_imports
Category: code-analysis
Description: List all import statements from Python source.
"""

def run(**kwargs):
    import ast
    code = kwargs.get('code', '')
    try:
        tree = ast.parse(code)
        imports = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names: imports.append({'module': a.name, 'alias': a.asname})
            elif isinstance(n, ast.ImportFrom):
                for a in n.names: imports.append({'from': n.module, 'name': a.name})
        return {'imports': imports, 'count': len(imports)}
    except SyntaxError as e:
        return {'error': str(e)}
