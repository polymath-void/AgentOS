# Analysis Report: Hermes Skill Path Portability Audit

**Milestone**: M1 (R1 Spec Audit & Frontmatter/Path Fixes)  
**Agent**: Explorer 2 (`explorer_m1_2`)  
**Target Repository**: `/data/data/com.termux/files/home/skills-workspace`  
**Date**: 2026-08-06  

---

## Executive Summary

An audit of the 5 target `hermes` sub-skills in `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/` was conducted to identify non-portable hardcoded developer paths (such as `/home/user` or `/home/bb`). 

Across the 5 target files, **7 non-portable path occurrences** were identified. All identified non-portable paths can be replaced with `$HOME` to ensure path portability across different user environments and OS distributions.

---

## Audit Findings by Target File

### File 1: `user-skills/hermes/productivity/google-workspace/SKILL.md`
- **Absolute Path**: `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/productivity/google-workspace/SKILL.md`
- **Total Lines**: 336
- **Occurrences Found**: 1

| Line # | Current Verbatim Content | Non-Portable Target | Proposed Portable Replacement (`$HOME`) |
|--------|-------------------------|---------------------|------------------------------------------|
| **104** | `> \`The JSON file path is: /home/user/Downloads/client_secret_....json\`` | `/home/user` | `> \`The JSON file path is: $HOME/Downloads/client_secret_....json\`` |

---

### File 2: `user-skills/hermes/research/llm-wiki/SKILL.md`
- **Absolute Path**: `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/research/llm-wiki/SKILL.md`
- **Total Lines**: 508
- **Occurrences Found**: 1

| Line # | Current Verbatim Content | Non-Portable Target | Proposed Portable Replacement (`$HOME`) |
|--------|-------------------------|---------------------|------------------------------------------|
| **459** | `WorkingDirectory=/home/user/wiki` | `/home/user` | `WorkingDirectory=$HOME/wiki` |

---

### File 3: `user-skills/hermes/software-development/hermes-agent-skill-authoring/SKILL.md`
- **Absolute Path**: `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/software-development/hermes-agent-skill-authoring/SKILL.md`
- **Total Lines**: 208
- **Occurrences Found**: 2

| Line # | Current Verbatim Content | Non-Portable Target | Proposed Portable Replacement (`$HOME`) |
|--------|-------------------------|---------------------|------------------------------------------|
| **21** | `2. **In-repo (this skill is about this case):** \`/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md\` — committed, shipped with the package. Use \`write_file\` + \`git add\`. \`skill_manage(action='create')\` does NOT target this tree.` | `/home/bb` | `2. **In-repo (this skill is about this case):** \`$HOME/hermes-agent/skills/<category>/<name>/SKILL.md\` — committed, shipped with the package. Use \`write_file\` + \`git add\`. \`skill_manage(action='create')\` does NOT target this tree.` |
| **27** | `- You're editing an existing skill under \`/home/bb/hermes-agent/skills/\` (use \`patch\` for small edits, \`write_file\` for rewrites; \`skill_manage\` still works for patch on in-repo skills, but not for \`create\`)` | `/home/bb` | `- You're editing an existing skill under \`$HOME/hermes-agent/skills/\` (use \`patch\` for small edits, \`write_file\` for rewrites; \`skill_manage\` still works for patch on in-repo skills, but not for \`create\`)` |

---

### File 4: `user-skills/hermes/software-development/node-inspect-debugger/SKILL.md`
- **Absolute Path**: `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/software-development/node-inspect-debugger/SKILL.md`
- **Total Lines**: 320
- **Occurrences Found**: 2

| Line # | Current Verbatim Content | Non-Portable Target | Proposed Portable Replacement (`$HOME`) |
|--------|-------------------------|---------------------|------------------------------------------|
| **186** | `cd /home/bb/hermes-agent/ui-tui` | `/home/bb` | `cd $HOME/hermes-agent/ui-tui` |
| **230** | `cd /home/bb/hermes-agent/ui-tui` | `/home/bb` | `cd $HOME/hermes-agent/ui-tui` |

---

### File 5: `user-skills/hermes/software-development/python-debugpy/SKILL.md`
- **Absolute Path**: `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/software-development/python-debugpy/SKILL.md`
- **Total Lines**: 374
- **Occurrences Found**: 2

| Line # | Current Verbatim Content | Non-Portable Target | Proposed Portable Replacement (`$HOME`) |
|--------|-------------------------|---------------------|------------------------------------------|
| **152** | `source /home/bb/hermes-agent/.venv/bin/activate` | `/home/bb` | `source $HOME/hermes-agent/.venv/bin/activate` |
| **249** | `    { "localRoot": "${workspaceFolder}", "remoteRoot": "/home/bb/hermes-agent" }` | `/home/bb` | `    { "localRoot": "${workspaceFolder}", "remoteRoot": "$HOME/hermes-agent" }` |

---

## Summary Matrix

| # | Skill Relative Path | Non-Portable Path Count | Developer Homes Found |
|---|---------------------|-------------------------|------------------------|
| 1 | `productivity/google-workspace/SKILL.md` | 1 | `/home/user` |
| 2 | `research/llm-wiki/SKILL.md` | 1 | `/home/user` |
| 3 | `software-development/hermes-agent-skill-authoring/SKILL.md` | 2 | `/home/bb` |
| 4 | `software-development/node-inspect-debugger/SKILL.md` | 2 | `/home/bb` |
| 5 | `software-development/python-debugpy/SKILL.md` | 2 | `/home/bb` |
| **Total** | **5 Target Files** | **7 Occurrences** | `/home/user` (2), `/home/bb` (5) |

---

## Proposed Remediation Plan (For Implementer)

To implement the path portability fixes without altering surrounding syntax or formatting:
- Replace `/home/user/` and `/home/bb/` with `$HOME/` in each of the 7 specified line locations.
- Maintain surrounding quotes, backticks, inline code blocks, and systemd syntax intact.
