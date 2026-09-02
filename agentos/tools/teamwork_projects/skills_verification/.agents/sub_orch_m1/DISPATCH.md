## DISPATCH — Sub-Orchestrator M1 (R1 Spec Audit & Frontmatter/Path Fixes)

Your Role: Sub-Orchestrator M1
Working directory: /data/data/com.termux/files/home/teamwork_projects/skills_verification/.agents/sub_orch_m1
Project directory: /data/data/com.termux/files/home/teamwork_projects/skills_verification
Target Repository: /data/data/com.termux/files/home/skills-workspace
Original Request path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/ORIGINAL_REQUEST.md
PROJECT.md path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/PROJECT.md

Task & Scope:
Execute Milestone M1: Skill Frontmatter & Path Portability Fixes
1. Add standard YAML frontmatter headers (`--- \n name: ... \n description: ... \n ---`) to the 12 `android-tools` sub-skills in `/data/data/com.termux/files/home/skills-workspace/user-skills/android-tools/`.
2. Convert non-portable developer home paths (`/home/user`, `/home/bb`) to `$HOME` in the 5 `hermes` sub-skills (`hermes/productivity/google-workspace/SKILL.md`, `hermes/research/llm-wiki/SKILL.md`, `hermes/software-development/hermes-agent-skill-authoring/SKILL.md`, `hermes/software-development/node-inspect-debugger/SKILL.md`, `hermes/software-development/python-debugpy/SKILL.md`).
3. Verify zero credential leakage and 100% frontmatter compliance across all 97 skills.

Workflow:
1. Create `SCOPE.md` in your working directory.
2. Run iteration loop:
   a. Dispatch 3 `teamwork_preview_explorer` (or read `spec_miner_survey_1` report) to plan precise fixes.
   b. Dispatch `teamwork_preview_worker` to execute changes and run unit tests.
      MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine.
   c. Dispatch 2 `teamwork_preview_reviewer` independently.
   d. Dispatch 2 `teamwork_preview_challenger` to test correctness.
   e. Dispatch 1 `teamwork_preview_auditor` to perform forensic integrity verification.
   f. Gate check in `GATE_STATUS.md`.
3. Update `progress.md` continuously and send completion report back to parent.
