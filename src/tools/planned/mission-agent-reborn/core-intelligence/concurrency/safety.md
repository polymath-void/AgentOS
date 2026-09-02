# Concurrency and Safety Architecture

## Parallelism Principles
- **Default:** Tools execute in parallel unless specified.
- **Dependency Handling:** If `Tool B` depends on `Tool A`'s output or side effects, `wait_for_previous` MUST be true.
- **Sub-Agent Safety:** Never run multiple sub-agents that mutate the same files/resources in parallel to prevent race conditions.
- **File Collision:** Do NOT perform multiple `replace` calls on the SAME file in one turn. Use sequential conversational turns.

## Process Management
- **Background Processes:** Use `run_shell_command` with `is_background: true` for long-running services.
- **Termination:** Always use `kill -- -PGID` to cleanly kill background process groups.
- **Verification:** Validation (linting/testing) is non-negotiable and must occur after any file mutation.
