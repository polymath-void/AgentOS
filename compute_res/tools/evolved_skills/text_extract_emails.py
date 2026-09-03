"""Skill: text_extract_emails
Category: text-processing
Description: Extract all email addresses from text.
"""

def run(**kwargs):
    import re
    text = kwargs.get('text', '')
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(pattern, text)))
    return {'emails': emails, 'count': len(emails)}
