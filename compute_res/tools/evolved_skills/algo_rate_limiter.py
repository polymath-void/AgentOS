"""Skill: algo_rate_limiter
Category: algorithms
Description: Token bucket rate limiter.
"""

def run(**kwargs):
    import time
    rate = float(kwargs.get('rate', 5))
    capacity = float(kwargs.get('capacity', 10))
    tokens = float(kwargs.get('tokens', capacity))
    last = float(kwargs.get('last_checked', time.time()))
    now = time.time()
    tokens = min(capacity, tokens + (now-last)*rate)
    allowed = tokens >= 1
    if allowed: tokens -= 1
    return {'allowed': allowed, 'tokens': round(tokens,4), 'now': now}
