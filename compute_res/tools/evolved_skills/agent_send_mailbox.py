"""Skill: agent_send_mailbox
Category: agent-os
Description: Send a message to the ComputeRes OS mailbox.
"""

def run(**kwargs):
    from compute_res.memory.chat_db import db
    rid = db.insert(session_id=kwargs.get('session_id','default'), agent_id=kwargs.get('agent_id','unknown'), action='mailbox_push', message=kwargs.get('message',''))
    return {'status': 'sent', 'row_id': rid}
