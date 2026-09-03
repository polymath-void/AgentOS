"""Skill: net_download_file
Category: networking
Description: Download a file from a URL and save locally.
"""

def run(**kwargs):
    import urllib.request, os
    url = kwargs.get('url', '')
    dest = kwargs.get('dest', os.path.basename(url.split('?')[0]))
    urllib.request.urlretrieve(url, dest)
    return {'status': 'downloaded', 'dest': dest, 'size': os.path.getsize(dest)}
