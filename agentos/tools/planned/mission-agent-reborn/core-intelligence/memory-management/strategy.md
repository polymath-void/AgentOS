# Memory Management Strategy

I persist long-lived project context by editing markdown files directly, NOT through a built-in memory tool.

## Tiered Memory Routing
1. **`GEMINI.md` (Project Root):** Shared conventions, architecture, and repo-wide workflows. Committed to the repository.
2. **Sub-directory `GEMINI.md`:** Highly scoped overrides. Supersedes all other levels for its scope.
3. **Private Project Memory (`/home/.gemini/tmp/.../MEMORY.md`):** Machine-specific, private setup, or non-committable notes. Index for sibling `*.md` notes.
4. **Global Personal Memory (`~/.gemini/GEMINI.md`):** Cross-project, user-wide preferences (e.g., preferred test framework).

## Imperative
- **Do not duplicate facts:** Each piece of knowledge belongs in *exactly one* tier.
- **Do not save transient state:** Only durable, durable knowledge is stored.
- **Routing:** If a fact could plausibly belong to multiple tiers, ask the user before writing.
