"""Skill: algo_sliding_window
Category: algorithms
Description: Max sum sliding window of size K.
"""

def run(**kwargs):
    arr = [int(x) for x in kwargs.get('arr', [])]
    k = int(kwargs.get('k', 3))
    if len(arr)<k: return {'error': f'Array shorter than k={k}'}
    ws = sum(arr[:k]); mx = ws; mx_start = 0
    for i in range(k, len(arr)):
        ws += arr[i]-arr[i-k]
        if ws > mx: mx=ws; mx_start=i-k+1
    return {'max_sum': mx, 'window': arr[mx_start:mx_start+k]}
