# Scope: Milestone M1 (R1 Spec Audit & Frontmatter/Path Fixes)

## Objectives
1. Add standard YAML frontmatter headers (`--- \n name: ... \n description: ... \n ---`) to the 12 `android-tools` sub-skills in `/data/data/com.termux/files/home/skills-workspace/user-skills/android-tools/`.
2. Convert non-portable developer home paths (`/home/user`, `/home/bb`) to `$HOME` in 5 `hermes` sub-skills:
   - `hermes/productivity/google-workspace/SKILL.md`
   - `hermes/research/llm-wiki/SKILL.md`
   - `hermes/software-development/hermes-agent-skill-authoring/SKILL.md`
   - `hermes/software-development/node-inspect-debugger/SKILL.md`
   - `hermes/software-development/python-debugpy/SKILL.md`
3. Audit all 97 skills across the workspace to guarantee zero credential leakage and 100% frontmatter compliance.

## Target Paths
- Target Workspace: `/data/data/com.termux/files/home/skills-workspace`
- Target Category 1: `user-skills/android-tools/` (12 sub-skills)
- Target Category 2: `user-skills/hermes/` (5 specific SKILL.md files)
- Audit Scope: All 97 `SKILL.md` packages in `user-skills/`

## Acceptance Criteria
- All 12 `android-tools` sub-skills have valid YAML frontmatter headers (`name`, `description`).
- All 5 specified `hermes` sub-skills use `$HOME` instead of `/home/user` or `/home/bb`.
- 100% of the 97 `SKILL.md` files in `user-skills/` pass YAML frontmatter schema validation.
- 0 hardcoded personal credentials or API keys exist in any `SKILL.md`.

## Iteration Status
- Current iteration: 0 / 32
