"""Skill: data_json_to_csv
Category: data-processing
Description: Convert a list of dicts to CSV format string.
"""

def run(**kwargs):
    import json, io, csv
    data = kwargs.get('data', [])
    if isinstance(data, str): data = json.loads(data)
    if not data: return {'csv': '', 'rows': 0}
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(data[0].keys()))
    w.writeheader(); w.writerows(data)
    return {'csv': buf.getvalue(), 'rows': len(data)}
