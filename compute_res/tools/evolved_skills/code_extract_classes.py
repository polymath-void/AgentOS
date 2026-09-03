"""Skill: code_extract_classes
Category: code-analysis
Description: Extract all class definitions from Python source.
"""

def run(**kwargs):
    import ast
    code = kwargs.get('code', '')
    try:
        tree = ast.parse(code)
        classes = []
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef):
                bases = [b.id for b in n.bases if isinstance(b, ast.Name)]
                methods = [m.name for m in ast.walk(n) if isinstance(m, ast.FunctionDef)]
                classes.append({'name': n.name, 'bases': bases, 'methods': methods})
        return {'classes': classes, 'count': len(classes)}
    except SyntaxError as e:
        return {'error': str(e)}
