"""Skill: algo_bloom_filter
Category: algorithms
Description: Simple bloom filter for set membership.
"""

def run(**kwargs):
    import hashlib
    size = int(kwargs.get('size', 1024))
    items = kwargs.get('items', [])
    query = kwargs.get('query', '')
    bits = [0]*size
    def hashes(item, n=3):
        return [int(hashlib.md5(f'{item}{i}'.encode()).hexdigest(),16)%size for i in range(n)]
    for item in items:
        for idx in hashes(str(item)): bits[idx]=1
    if query:
        return {'query': query, 'probably_present': all(bits[i] for i in hashes(str(query))), 'items': len(items)}
    return {'bits_set': sum(bits), 'size': size}
