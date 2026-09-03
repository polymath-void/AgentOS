"""Skill: math_matrix_multiply
Category: mathematics
Description: Multiply two 2D matrices.
"""

def run(**kwargs):
    A = kwargs.get('A', [[1,0],[0,1]])
    B = kwargs.get('B', [[1,0],[0,1]])
    ra, ca = len(A), len(A[0])
    rb, cb = len(B), len(B[0])
    if ca != rb: return {'error': f'Dims mismatch {ca}!={rb}'}
    C = [[sum(A[i][k]*B[k][j] for k in range(ca)) for j in range(cb)] for i in range(ra)]
    return {'result': C, 'shape': [ra, cb]}
