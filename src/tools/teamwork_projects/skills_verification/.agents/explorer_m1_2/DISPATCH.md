## 2026-08-06T23:04:40Z
You are Explorer 2 for Milestone M1 (hermes path portability).

Working directory: /data/data/com.termux/files/home/teamwork_projects/skills_verification/.agents/explorer_m1_2
Target repository: /data/data/com.termux/files/home/skills-workspace
Original Request path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/ORIGINAL_REQUEST.md
PROJECT.md path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/PROJECT.md
SCOPE.md path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/.agents/sub_orch_m1/SCOPE.md

Your task:
1. Read ORIGINAL_REQUEST.md, PROJECT.md, and SCOPE.md.
2. Explore the 5 target `hermes` sub-skills in `/data/data/com.termux/files/home/skills-workspace/user-skills/hermes/`:
   - `productivity/google-workspace/SKILL.md`
   - `research/llm-wiki/SKILL.md`
   - `software-development/hermes-agent-skill-authoring/SKILL.md`
   - `software-development/node-inspect-debugger/SKILL.md`
   - `software-development/python-debugpy/SKILL.md`
3. Inspect each file for hardcoded developer paths such as `/home/user`, `/home/bb`, or other user-specific absolute home paths.
4. Record exact line numbers and occurrences of non-portable paths and formulate replacement strings using `$HOME`.
5. Create your analysis in your working directory (`/data/data/com.termux/files/home/teamwork_projects/skills_verification/.agents/explorer_m1_2/analysis.md`) and write a completed `handoff.md`.
6. Send a message to parent with your findings summary. Do NOT implement any changes — you are read-only.
