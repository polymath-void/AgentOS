"""Skill: exec_python_safe
Category: runtime
Description: Execute Python code and capture stdout.
"""

def run(**kwargs):
    import io, sys, traceback
    code = kwargs.get('code', 'print("hello")')
    buf = io.StringIO(); old = sys.stdout; sys.stdout = buf; err = None
    try: exec(code, {})
    except Exception: err = traceback.format_exc()
    finally: sys.stdout = old
    return {'stdout': buf.getvalue(), 'error': err, 'success': err is None}
