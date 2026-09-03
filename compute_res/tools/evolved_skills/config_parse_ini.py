"""Skill: config_parse_ini
Category: configuration
Description: Parse an INI config file.
"""

def run(**kwargs):
    import configparser
    config = configparser.ConfigParser()
    if kwargs.get('path'): config.read(kwargs['path'])
    else: config.read_string(kwargs.get('raw', ''))
    return {'config': {s: dict(config[s]) for s in config.sections()}, 'sections': config.sections()}
