"""Skill: fs_write_file
Category: filesystem
Description: Write or overwrite a file with provided content.
"""

def run(**kwargs):
    path = kwargs.get('path', '')
    content = kwargs.get('content', '')
    mode = kwargs.get('mode', 'w')
    with open(path, mode) as f:
        f.write(content)
    return {'status': 'written', 'path': path, 'bytes': len(content)}
