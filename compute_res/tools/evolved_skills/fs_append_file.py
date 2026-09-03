"""Skill: fs_append_file
Category: filesystem
Description: Append text to a file.
"""

def run(**kwargs):
    path = kwargs.get('path', '')
    content = kwargs.get('content', '')
    with open(path, 'a') as f:
        f.write(content + '\n')
    return {'status': 'appended', 'path': path}
