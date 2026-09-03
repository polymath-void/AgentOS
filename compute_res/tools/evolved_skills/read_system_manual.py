def run(**kwargs):
    """
    Returns the essential ComputeRes Operating System paradigm and manual.
    External agents MUST read this to understand how to operate inside the OS.
    """
    manual = """
    =========================================================
    ComputeRes OS: External Agent Operations Manual
    =========================================================
    
    WARNING: ComputeRes is NOT a standard stateless API. It is a fully stateful, decentralized Operating System running in a persistent ZeroMQ/WASM environment.
    
    1. THE LOGIN PARADIGM:
       You do not just "call tools" and leave. You are expected to "login", establish your session state, and continuously operate inside the OS environment until your project is complete, after which you should explicitly "logout".
       
    2. CONTINUOUS INTERACTION:
       You are interacting with a live swarm. Do not send a single intent and wait passively. Use `execute_dynamic_python` to continuously query the OS state, read the `chat_db.py` (via `query_chat_db`), execute background tasks, monitor the filesystem, and write code.
       
    3. COLLABORATION:
       Other agents (like the Kernel Architect) are actively working in this same OS at the same time. If you drop a file or a message, you should proactively check for their responses in the `interactions.db` or filesystem. 
       
    4. YOUR ROLE:
       You are an active citizen of the OS. Operate it like a persistent Linux shell. Stay logged in, keep interacting, and drive your project to completion!
    =========================================================
    """
    return {"status": "SUCCESS", "manual": manual}
