"""Skill: code_parse_ast
Category: code-analysis
Description: Parse Python source and return AST node type summary.
"""

def run(**kwargs):
    import ast
    code = kwargs.get('code', '')
    try:
        tree = ast.parse(code)
        nodes = {}
        for n in ast.walk(tree): t = type(n).__name__; nodes[t] = nodes.get(t,0)+1
        return {'node_types': nodes, 'syntax_valid': True}
    except SyntaxError as e:
        return {'syntax_valid': False, 'error': str(e)}
