import os
import re
import yaml
from pathlib import Path

base_dir = Path("/data/data/com.termux/files/home/skills-workspace/user-skills")
skill_files = sorted(list(base_dir.rglob("SKILL.md")))

categories = {}

for sf in skill_files:
    rel = sf.relative_to(base_dir)
    content = sf.read_text(encoding="utf-8", errors="ignore")
    
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    fm_data = {}
    if fm_match:
        try:
            fm_data = yaml.safe_load(fm_match.group(1)) or {}
        except Exception:
            pass
            
    name = fm_data.get("name")
    desc = fm_data.get("description")
    
    if not name:
        h1 = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        name = h1.group(1).strip() if h1 else rel.parent.name
        
    top_cat = rel.parts[0]
    if top_cat not in categories:
        categories[top_cat] = []
    
    abs_paths = re.findall(r"/home/[a-zA-Z0-9_-]+|/Users/[a-zA-Z0-9_-]+", content)
    termux_home_paths = re.findall(r"/data/data/com\.termux/files/home/[^\s\"']+", content)
    
    categories[top_cat].append({
        "rel_path": str(rel),
        "name": name,
        "desc": desc,
        "has_fm": bool(fm_match),
        "has_math": ("2x+1" in content or "42" in content),
        "abs_paths": abs_paths,
        "termux_home_paths": termux_home_paths,
        "content_length": len(content)
    })

print(f"Total skills discovered: {len(skill_files)}")
for cat, skills in sorted(categories.items()):
    print(f"\nCategory: {cat} ({len(skills)} skills)")
    for s in skills:
        fm_status = "YAML_OK" if s["has_fm"] else "NO_YAML"
        math_status = "MATH_OK" if s["has_math"] else "NO_MATH"
        paths_flag = f"ABS_PATHS: {s['abs_paths']}" if s['abs_paths'] else ""
        print(f"  - {s['rel_path']} [{fm_status}] [{math_status}] {paths_flag}")
