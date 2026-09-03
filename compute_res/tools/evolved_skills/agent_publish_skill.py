"""Skill: agent_publish_skill
Category: agent-os
Description: Publish a skill to the ComputeRes SkillsHub.
"""

def run(**kwargs):
    from compute_res.memory.skillshub_db import skills_db
    sid = skills_db.publish_skill(name=kwargs.get('name',''), description=kwargs.get('description',''), author=kwargs.get('author','agent'), version=kwargs.get('version','1.0.0'), code_path=kwargs.get('code_path',''), categories=kwargs.get('categories',[]), tags=kwargs.get('tags',[]))
    return {'status': 'published', 'skill_id': sid}
