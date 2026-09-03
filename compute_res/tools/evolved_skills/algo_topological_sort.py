"""Skill: algo_topological_sort
Category: algorithms
Description: Topological sort of a directed acyclic graph.
"""

def run(**kwargs):
    from collections import deque
    graph = kwargs.get('graph', {})
    in_deg = {n: 0 for n in graph}
    for n in graph:
        for nb in graph[n]:
            if nb not in in_deg: in_deg[nb]=0
            in_deg[nb]+=1
    q = deque([n for n,d in in_deg.items() if d==0])
    order = []
    while q:
        n = q.popleft(); order.append(n)
        for nb in graph.get(n,[]):
            in_deg[nb]-=1
            if in_deg[nb]==0: q.append(nb)
    return {'order': order, 'has_cycle': len(order)!=len(in_deg)}
