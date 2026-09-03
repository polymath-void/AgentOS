# Project: AI Agent Skills Workspace Verification & Compliance

## Architecture
The AI Agent Skills Workspace project standardizes, audits, and verifies modular AI agent skills, non-blocking metric ledgers, and citation standards across Android Termux and multi-agent runtime environments (Google Antigravity AGY, Gemini CLI, Hermes).

Target Workspace: `/data/data/com.termux/files/home/Workspace/Tools/skills-workspace`
Secondary Metric Workspace: `/data/data/com.termux/files/home/Termux-Cloud-Backup-Google-Drive`

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F1.1 Skill Auto-Discovery Engine | Recursive discovery of 97 `SKILL.md` packages across 11 category trees | M1 | Survey R1 |
| 2 | F1.2 YAML Frontmatter Standardization | Add YAML frontmatter headers to 12 `android-tools` sub-skills | M1 | Survey R1 |
| 3 | F1.3 Path Portability Compliance | Replace non-portable developer paths (`/home/user`, `/home/bb`) with `$HOME` in 5 `hermes` skills | M1 | Survey R1 |
| 4 | F1.4 Zero Credential Leakage Audit | Verify 100% absence of hardcoded API keys/credentials across all 97 skills | M1 | Survey R1 |
| 5 | F2.1 Definite Integral Verification | Verify mathematical integral evaluation $f(x) = \int_0^6 (2x+1)dx = 42$ | M2 | Survey R2 |
| 6 | F2.2 Zero-Authentication Protocol | Execute local Python path resolution protocol for non-blocking metric logging | M2 | Survey R2 |
| 7 | F2.3 Adaptation Metric Logging | Record `VERIFIED_ADAPTED` entries in `AGENT_ADAPTATION_METRICS.md` and fallback `MEMORY.md` | M2 | Survey R2 |
| 8 | F3.1 Markdown Citation Addition | Add explicit Markdown citation format section under Section 5 in `README.md` | M3 | Survey R3 |
| 9 | F3.2 Native GitHub CITATION.cff | Create `CITATION.cff` YAML metadata file at repository root | M3 | Survey R3 |
| 10 | F3.3 Multi-Agent Compatibility | Verify schema and path portability rules across AGY, Gemini CLI, and Hermes | M3 | Survey R3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | R1 Spec Audit & Frontmatter/Path Fixes | Add YAML frontmatter to 12 `android-tools` skills, replace hardcoded paths in 5 `hermes` skills, verify 97/97 frontmatter & zero credential leakage | None | PLANNED |
| M2 | R2 Math Verification & Metric Logging | Verify integral $f(x)=42$, execute Zero-Auth protocol, log footprint to `AGENT_ADAPTATION_METRICS.md` / `MEMORY.md` | M1 | PLANNED |
| M3 | R3 Citation Standards & CITATION.cff | Add Markdown citation to `README.md`, create `CITATION.cff`, verify CFF YAML syntax | M1, M2 | PLANNED |
| M4 | Final E2E Test Suite Pass & Hardening | Pass 100% of E2E tests (Tiers 1-4) and Tier 5 adversarial coverage hardening | M1, M2, M3 | PLANNED |

## Interface Contracts
### `skills-workspace` ↔ `AGENT_ADAPTATION_METRICS.md` / `MEMORY.md`
- Protocol: Zero-Authentication local Python path resolution.
- Format: Markdown tables (`Adaptation Footprint Metrics` & `Verification Submissions Ledger`).
- Inputs: Math input `42`, Agent name/ID, Timestamp. Output: `VERIFIED_ADAPTED` status.

### `skills-workspace/README.md` ↔ `CITATION.cff`
- Citation formats in `README.md`: BibTeX, APA, Markdown.
- `CITATION.cff` schema version: `1.2.0`, author: `Polymath Void`, URL: `https://github.com/polymath-void/ai-agents-skills-workspace`.

## Code Layout
- Target Repo: `/data/data/com.termux/files/home/Workspace/Tools/skills-workspace`
- User Skills: `/data/data/com.termux/files/home/Workspace/Tools/skills-workspace/user-skills`
- README: `/data/data/com.termux/files/home/Workspace/Tools/skills-workspace/README.md`
- Citation File: `/data/data/com.termux/files/home/Workspace/Tools/skills-workspace/CITATION.cff`
- Primary Metric Ledger: `/data/data/com.termux/files/home/Termux-Cloud-Backup-Google-Drive/AGENT_ADAPTATION_METRICS.md`
- Fallback Ledger: `/data/data/com.termux/files/home/Workspace/Tools/skills-workspace/MEMORY.md`
