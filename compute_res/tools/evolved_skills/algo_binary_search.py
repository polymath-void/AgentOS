"""Skill: algo_binary_search
Category: algorithms
Description: Binary search on a sorted list.
"""

def run(**kwargs):
    arr = kwargs.get('arr', [])
    target = kwargs.get('target', None)
    lo, hi = 0, len(arr)-1
    while lo <= hi:
        mid = (lo+hi)//2
        if arr[mid] == target: return {'index': mid, 'found': True}
        elif arr[mid] < target: lo = mid+1
        else: hi = mid-1
    return {'index': -1, 'found': False}
