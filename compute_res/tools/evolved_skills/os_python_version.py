"""Skill: os_python_version
Category: system
Description: Return current Python version and details.
"""

def run(**kwargs):
    import sys, platform
    return {'version': sys.version, 'version_info': list(sys.version_info), 'executable': sys.executable, 'implementation': platform.python_implementation()}
