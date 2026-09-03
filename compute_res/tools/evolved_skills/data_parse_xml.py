"""Skill: data_parse_xml
Category: data-processing
Description: Parse an XML string to a nested dict.
"""

def run(**kwargs):
    import xml.etree.ElementTree as ET
    raw = kwargs.get('raw', '<root/>')
    def e2d(el):
        d = {'tag': el.tag, 'attrib': el.attrib, 'text': (el.text or '').strip()}
        kids = [e2d(c) for c in el]
        if kids: d['children'] = kids
        return d
    try:
        return {'parsed': e2d(ET.fromstring(raw))}
    except ET.ParseError as e:
        return {'error': str(e)}
