"""Skill: data_compute_stats
Category: data-processing
Description: Compute min, max, mean, median, stdev of a numeric list.
"""

def run(**kwargs):
    import statistics
    nums = [float(x) for x in kwargs.get('nums', [])]
    if not nums: return {'error': 'empty list'}
    r = {'count': len(nums), 'min': min(nums), 'max': max(nums), 'mean': statistics.mean(nums), 'median': statistics.median(nums)}
    if len(nums) > 1: r['stdev'] = statistics.stdev(nums)
    return r
