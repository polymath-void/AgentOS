"""Skill: text_slug_generate
Category: text-processing
Description: Convert a string to a URL-safe slug.
"""

def run(**kwargs):
    import re
    text = kwargs.get('text', '')
    slug = re.sub(r'[^\w\s-]', '', text.lower().strip())
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return {'input': text, 'slug': slug}
