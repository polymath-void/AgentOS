"""Skill: data_chunk_list
Category: data-processing
Description: Split a list into equal-sized chunks.
"""

def run(**kwargs):
    items = kwargs.get('items', [])
    size = int(kwargs.get('size', 10))
    chunks = [items[i:i+size] for i in range(0, len(items), size)]
    return {'chunks': chunks, 'chunk_count': len(chunks)}
