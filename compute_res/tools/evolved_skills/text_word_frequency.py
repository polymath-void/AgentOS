"""Skill: text_word_frequency
Category: text-processing
Description: Count word frequencies in text.
"""

def run(**kwargs):
    import re
    from collections import Counter
    text = kwargs.get('text', '').lower()
    n = int(kwargs.get('n', 20))
    words = re.findall(r'\b[a-z]+\b', text)
    return {'top': Counter(words).most_common(n), 'total_words': len(words)}
