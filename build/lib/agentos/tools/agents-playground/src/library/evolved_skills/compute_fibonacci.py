# Dynamic EvolvOS Synthesized Skill: compute_fibonacci
def compute_fibonacci(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Built-in Verification Assertions
if __name__ == '__main__':
    assert compute_fibonacci(10) == 55
