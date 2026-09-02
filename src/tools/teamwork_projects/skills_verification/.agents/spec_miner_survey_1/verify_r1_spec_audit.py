#!/usr/bin/env python3
import re
import yaml
from pathlib import Path

def main():
    base_dir = Path("/data/data/com.termux/files/home/skills-workspace/user-skills")
    assert base_dir.exists(), f"Directory not found: {base_dir}"
    
    skill_files = sorted(list(base_dir.rglob("SKILL.md")))
    assert len(skill_files) == 97, f"Expected 97 SKILL.md files, found {len(skill_files)}"
    
    yaml_pass = []
    yaml_fail = []
    
    cred_leak_count = 0
    cred_patterns = [
        r"ghp_[A-Za-z0-9]{36}",
        r"sk-[A-Za-z0-9]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"AIzaSy[A-Za-z0-9_-]{35}",
        r"-----BEGIN PRIVATE KEY-----",
        r"-----BEGIN RSA PRIVATE KEY-----"
    ]
    
    hardcoded_paths = []
    
    for sf in skill_files:
        rel = str(sf.relative_to(base_dir))
        content = sf.read_text(encoding="utf-8", errors="ignore")
        
        # 1. Frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if fm_match:
            try:
                data = yaml.safe_load(fm_match.group(1))
                if isinstance(data, dict) and data.get("name") and data.get("description"):
                    yaml_pass.append(rel)
                else:
                    yaml_fail.append((rel, "Missing name or description in YAML"))
            except Exception as e:
                yaml_fail.append((rel, f"YAML parse error: {e}"))
        else:
            yaml_fail.append((rel, "Missing frontmatter delimiters ---"))

        # 2. Credential leakage
        for pat in cred_patterns:
            if re.search(pat, content):
                cred_leak_count += 1
                
        # 3. Path portability (excluding URLs)
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if "http://" in line or "https://" in line:
                continue
            if re.search(r"/home/[a-zA-Z0-9_-]+|/Users/[a-zA-Z0-9_-]+", line):
                hardcoded_paths.append((rel, idx, line.strip()))

    print("Verification Summary:")
    print(f"- Total SKILL.md files: {len(skill_files)} (EXPECTED: 97)")
    print(f"- Valid YAML frontmatter: {len(yaml_pass)} (EXPECTED: 85)")
    print(f"- Missing YAML frontmatter: {len(yaml_fail)} (EXPECTED: 12)")
    print(f"- Credential leak instances: {cred_leak_count} (EXPECTED: 0)")
    print(f"- Hardcoded file paths (excluding URLs): {len(hardcoded_paths)} (EXPECTED: 8 lines across 5 files)")
    
    # Assertions
    assert len(yaml_pass) == 85, f"Expected 85 valid frontmatter files, got {len(yaml_pass)}"
    assert len(yaml_fail) == 12, f"Expected 12 invalid frontmatter files, got {len(yaml_fail)}"
    assert cred_leak_count == 0, f"Expected 0 credential leaks, got {cred_leak_count}"
    assert len(hardcoded_paths) == 8, f"Expected 8 hardcoded path lines, got {len(hardcoded_paths)}"
    
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
