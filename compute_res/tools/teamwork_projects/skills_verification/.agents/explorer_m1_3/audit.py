import os
import glob
import re
import yaml
import json

base_dir = '/data/data/com.termux/files/home/skills-workspace/user-skills'
skill_files = sorted(glob.glob(os.path.join(base_dir, '**', 'SKILL.md'), recursive=True))

results = []

# Secret scanning regexes
secret_patterns = [
    ('OpenAI API Key', re.compile(r'sk-[a-zA-Z0-9]{20,}')),
    ('Google API Key', re.compile(r'AIzaSy[a-zA-Z0-9_-]{33}')),
    ('GitHub Token', re.compile(r'ghp_[a-zA-Z0-9]{36}')),
    ('GitLab Token', re.compile(r'glpat-[a-zA-Z0-9_-]{20}')),
    ('Slack Token', re.compile(r'xox[baprs]-[a-zA-Z0-9_-]{10,}')),
    ('Private Key Header', re.compile(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----')),
    ('JWT Token', re.compile(r'eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+')),
    ('URL Credentials', re.compile(r'https?://[a-zA-Z0-9._%+-]+:[a-zA-Z0-9._%+-]+@')),
    ('Generic Hardcoded Secret/Key/Password', re.compile(r'(?i)(api[_-]?key|secret|password|passwd|token|auth[_-]?token)\s*[:=]\s*["\']([^"\'$\s]{8,})["\']')),
]

placeholder_words = {'your', 'example', 'sample', 'placeholder', '<', '>', '$', 'xxx', 'dummy', 'test', 'change', 'my_', 'insert', 'null', 'none'}

def is_placeholder(val):
    val_lower = val.lower()
    return any(p in val_lower for p in placeholder_words)

for filepath in skill_files:
    rel_path = os.path.relpath(filepath, base_dir)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Frontmatter check
    has_fm = False
    fm_valid = False
    fm_data = {}
    fm_error = None
    
    # Check if starts with ---
    fm_match = re.match(r'^\s*---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        has_fm = True
        raw_fm = fm_match.group(1)
        try:
            parsed = yaml.safe_load(raw_fm)
            if isinstance(parsed, dict):
                fm_valid = True
                fm_data = parsed
            else:
                fm_error = "Frontmatter did not parse into a dictionary"
        except Exception as e:
            fm_error = f"YAML parse error: {str(e)}"
    else:
        # Check if there is any frontmatter block at all
        if content.strip().startswith('---'):
            has_fm = True
            fm_error = "Unclosed or malformed frontmatter delimiters"
        else:
            has_fm = False
            fm_error = "Missing frontmatter delimiters (---)"

    # Frontmatter field compliance
    has_name = 'name' in fm_data and bool(str(fm_data['name']).strip()) if fm_valid else False
    has_desc = 'description' in fm_data and bool(str(fm_data['description']).strip()) if fm_valid else False

    # Secret scanning
    findings = []
    lines = content.split('\n')
    for idx, line in enumerate(lines, 1):
        for pat_name, pat in secret_patterns:
            matches = pat.findall(line)
            if matches:
                for match in matches:
                    matched_str = match[1] if isinstance(match, tuple) else match
                    if not is_placeholder(matched_str):
                        findings.append({
                            'line': idx,
                            'type': pat_name,
                            'snippet': line.strip()[:100],
                            'match': matched_str[:50]
                        })

    # Hardcoded path scanning
    hardcoded_paths = []
    for idx, line in enumerate(lines, 1):
        if re.search(r'/home/(?:user|bb|ubuntu|admin)', line):
            hardcoded_paths.append({
                'line': idx,
                'snippet': line.strip()[:100]
            })

    results.append({
        'rel_path': rel_path,
        'abs_path': filepath,
        'has_frontmatter': has_fm,
        'frontmatter_valid': fm_valid,
        'frontmatter_error': fm_error,
        'name': fm_data.get('name', None),
        'description': fm_data.get('description', None),
        'has_name': has_name,
        'has_description': has_desc,
        'secret_findings': findings,
        'hardcoded_path_findings': hardcoded_paths
    })

print(json.dumps(results, indent=2))
