# Handoff Report: Explorer M1-2 (Hermes Path Portability)

## 1. Observation

Direct inspection of the 5 target `hermes` sub-skills in `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/` via `view_file` and `grep_search` revealed 7 exact occurrences of non-portable hardcoded developer paths (`/home/user` and `/home/bb`):

1. **`productivity/google-workspace/SKILL.md` (Line 104)**:
   - Line content: `> \`The JSON file path is: /home/user/Downloads/client_secret_....json\``
   - Non-portable path: `/home/user/Downloads/client_secret_....json`
2. **`research/llm-wiki/SKILL.md` (Line 459)**:
   - Line content: `WorkingDirectory=/home/user/wiki`
   - Non-portable path: `/home/user/wiki`
3. **`software-development/hermes-agent-skill-authoring/SKILL.md` (Line 21)**:
   - Line content: `2. **In-repo (this skill is about this case):** \`/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md\` — committed, shipped with the package. Use \`write_file\` + \`git add\`. \`skill_manage(action='create')\` does NOT target this tree.`
   - Non-portable path: `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md`
4. **`software-development/hermes-agent-skill-authoring/SKILL.md` (Line 27)**:
   - Line content: `- You're editing an existing skill under \`/home/bb/hermes-agent/skills/\` (use \`patch\` for small edits, \`write_file\` for rewrites; \`skill_manage\` still works for patch on in-repo skills, but not for \`create\`)`
   - Non-portable path: `/home/bb/hermes-agent/skills/`
5. **`software-development/node-inspect-debugger/SKILL.md` (Line 186)**:
   - Line content: `cd /home/bb/hermes-agent/ui-tui`
   - Non-portable path: `/home/bb/hermes-agent/ui-tui`
6. **`software-development/node-inspect-debugger/SKILL.md` (Line 230)**:
   - Line content: `cd /home/bb/hermes-agent/ui-tui`
   - Non-portable path: `/home/bb/hermes-agent/ui-tui`
7. **`software-development/python-debugpy/SKILL.md` (Line 152)**:
   - Line content: `source /home/bb/hermes-agent/.venv/bin/activate`
   - Non-portable path: `/home/bb/hermes-agent/.venv/bin/activate`
8. **`software-development/python-debugpy/SKILL.md` (Line 249)**:
   - Line content: `    { "localRoot": "${workspaceFolder}", "remoteRoot": "/home/bb/hermes-agent" }`
   - Non-portable path: `/home/bb/hermes-agent`

## 2. Logic Chain

1. **Step 1**: Target repository path `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes` was located and verified.
2. **Step 2**: The 5 specified target sub-skills were read line by line.
3. **Step 3**: Regex search for `/home/(user|bb|\w+)` was executed across `user-skills/hermes/` to ensure full coverage of developer absolute paths.
4. **Step 4**: Line 89 of `google-workspace/SKILL.md` contained `https://console.cloud.google.com/projectselector2/home/dashboard`, which is a Google Cloud web URL and not a local filesystem path, and was correctly excluded.
5. **Step 5**: 7 lines containing local hardcoded developer home directories (`/home/user` and `/home/bb`) were confirmed and paired with exact `$HOME` replacement strings.
6. **Step 6**: The 7 replacements preserve original markdown formatting, code block backticks, JSON properties, and systemd syntax while making all paths portable across standard Linux, Termux, and macOS user environments.

## 3. Caveats

- **Scope**: Investigation was limited strictly to path portability analysis of the 5 requested `hermes` sub-skill files.
- **Read-Only**: No modifications were made to target source files in accordance with the Explorer archetype.
- **Web URLs**: URLs containing `/home/` (such as `console.cloud.google.com/.../home/dashboard`) must not be replaced with `$HOME`.

## 4. Conclusion

All 5 target `hermes` sub-skill files were completely audited. Exactly 7 non-portable developer paths were documented with line-by-line verbatim content and exact `$HOME` replacement strings. An implementer can directly apply the proposed replacements documented in `analysis.md`.

## 5. Verification Method

To independently verify findings:

1. **File View / Line Check**:
   - `google-workspace/SKILL.md` line 104
   - `llm-wiki/SKILL.md` line 459
   - `hermes-agent-skill-authoring/SKILL.md` lines 21, 27
   - `node-inspect-debugger/SKILL.md` lines 186, 230
   - `python-debugpy/SKILL.md` lines 152, 249

2. **Regex Audit Command**:
   ```bash
   grep -En "/home/(user|bb)" \
     /data/data/com.termux/files/home/skills-workspace/user-skills/hermes/productivity/google-workspace/SKILL.md \
     /data/data/com.termux/files/home/skills-workspace/user-skills/hermes/research/llm-wiki/SKILL.md \
     /data/data/com.termux/files/home/skills-workspace/user-skills/hermes/software-development/hermes-agent-skill-authoring/SKILL.md \
     /data/data/com.termux/files/home/skills-workspace/user-skills/hermes/software-development/node-inspect-debugger/SKILL.md \
     /data/data/com.termux/files/home/skills-workspace/user-skills/hermes/software-development/python-debugpy/SKILL.md
   ```
   **Expected Result**: Exactly 7 matching lines matching the documented lines.
