"""Skill: text_levenshtein
Category: text-processing
Description: Compute Levenshtein distance between two strings.
"""

def run(**kwargs):
    a = kwargs.get('a', '')
    b = kwargs.get('b', '')
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m+1):
        prev = dp[0]; dp[0] = i
        for j in range(1, n+1):
            temp = dp[j]
            dp[j] = prev if a[i-1]==b[j-1] else 1+min(prev, dp[j], dp[j-1])
            prev = temp
    return {'distance': dp[n], 'similarity': round(1 - dp[n]/max(m, n, 1), 4)}
