"""Skill: agent_read_mailbox
Category: agent-os
Description: Read all messages from a session mailbox.
"""

def run(**kwargs):
    from compute_res.memory.chat_db import db
    msgs = db.get_session(kwargs.get('session_id','default'))
    return {'messages': msgs, 'count': len(msgs)}
