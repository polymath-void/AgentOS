"""Skill: bench_run_timed
Category: benchmarking
Description: Execute Python code and measure wall-clock time.
"""

def run(**kwargs):
    import time
    code = kwargs.get('code', 'pass')
    ns = {}
    start = time.perf_counter()
    exec(code, ns)
    elapsed = time.perf_counter() - start
    return {'elapsed_ms': round(elapsed*1000, 4), 'elapsed_s': elapsed}
