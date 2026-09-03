"""Skill: agent_query_skills
Category: agent-os
Description: Query the SkillsHub for available skills.
"""

def run(**kwargs):
    from compute_res.memory.skillshub_db import skills_db
    q = kwargs.get('query','')
    niche = kwargs.get('niche','')
    if niche: r = skills_db.get_skills_by_niche(niche)
    elif q: r = skills_db.search_skills_fts(q)
    else: r = skills_db.get_all_skills()
    return {'results': r, 'count': len(r)}
