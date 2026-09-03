"""Skill: math_primes_sieve
Category: mathematics
Description: Generate all primes up to N using the Sieve of Eratosthenes.
"""

def run(**kwargs):
    limit = int(kwargs.get('limit', 100))
    sieve = [True]*(limit+1); sieve[0]=sieve[1]=False
    for i in range(2, int(limit**0.5)+1):
        if sieve[i]:
            for j in range(i*i, limit+1, i): sieve[j]=False
    primes = [i for i,p in enumerate(sieve) if p]
    return {'primes': primes, 'count': len(primes)}
