"""Skill: algo_quicksort
Category: algorithms
Description: Sort a list using quicksort.
"""

def run(**kwargs):
    def qs(arr, lo, hi):
        if lo < hi:
            pivot = arr[hi]; i = lo-1
            for j in range(lo, hi):
                if arr[j] <= pivot: i+=1; arr[i],arr[j]=arr[j],arr[i]
            arr[i+1],arr[hi]=arr[hi],arr[i+1]; p=i+1
            qs(arr,lo,p-1); qs(arr,p+1,hi)
    arr = list(kwargs.get('arr', []))
    qs(arr, 0, len(arr)-1)
    return {'sorted': arr}
