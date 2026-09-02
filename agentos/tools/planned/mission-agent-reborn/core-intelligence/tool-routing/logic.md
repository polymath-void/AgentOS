# Tool Routing & Orchestration Logic

## Selection Logic
- **Complexity Analysis:** Simple tasks (1-2 tools) are executed directly. Complex/multi-step tasks require `update_topic` and a `write_todos` list.
- **Sub-Agent Delegation:** Use sub-agents (`codebase_investigator`, `generalist`) to compress repetitive tasks or high-volume investigations. Never run multiple sub-agents that mutate the same files.
- **Efficiency:** Combine reads/searches in one turn. Use `grep` + `context` to minimize file-reading turns.

## Routing Rules
- **Security:** Never execute modifying commands without an explanation.
- **Integrity:** Never stage/commit without an explicit directive.
- **Validation:** Always follow up action with verification tools (lint, test, build).
