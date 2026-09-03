import json
import time
from compute_res.memory.chat_db import db

def run(action=None, project="Global", context=None, **kwargs):
    """
    Teamwork Projects integration skill.
    Handles 'login' and 'share_context' actions for external agents collaborating on projects.
    All contexts and intents are routed into the high-speed FTS5 Chat DB.
    """
    # Use the database to store this context natively!
    agent_id = kwargs.get("agent_id", "UnknownTeamworkAgent")
    message = context if context else json.dumps(kwargs)
    
    row_id = db.insert(
        session_id=project, 
        agent_id=agent_id, 
        action=action or "share_context", 
        message=message
    )
        
    return {
        "status": "SUCCESS",
        "message": f"Teamwork handshake successful for project '{project}'. Context routed to ChatDB.",
        "db_row_id": row_id
    }
