"""Skill: data_parse_csv
Category: data-processing
Description: Parse a CSV string into list of row dicts.
"""

def run(**kwargs):
    import csv, io
    raw = kwargs.get('raw', '')
    delimiter = kwargs.get('delimiter', ',')
    reader = csv.DictReader(io.StringIO(raw), delimiter=delimiter)
    rows = list(reader)
    return {'rows': rows, 'count': len(rows), 'fields': reader.fieldnames}
