from compute_res.memory.chat_db import db

def run(action="search", query=None, session_id=None, **kwargs):
    """
    Queries the high-speed FTS5 Chat Database.
    
    Args:
        action: 'search' (default) or 'get_session'.
        query: The full-text search string (required if action is 'search').
        session_id: The session/project name (required if action is 'get_session').
    """
    if action == "search":
        if not query:
            return {"error": "Must provide 'query' for search action."}
        return {"results": db.search(query)}
    elif action == "get_session":
        if not session_id:
            return {"error": "Must provide 'session_id' for get_session action."}
        return {"results": db.get_session(session_id)}
    else:
        return {"error": f"Unknown action '{action}'. Use 'search' or 'get_session'."}
