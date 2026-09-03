"""Skill: sys_env_vars
Category: system
Description: Return environment variables, optionally filtered by prefix.
"""

def run(**kwargs):
    import os
    prefix = kwargs.get('prefix', '')
    env = {k: v for k, v in os.environ.items() if k.startswith(prefix)}
    return {'env': env, 'count': len(env)}
