# Workflow Methodology

## 1. Research Phase
- **Goal:** Map the problem space.
- **Tools:** `grep`, `glob`, `read_file`.
- **Imperative:** Never assume; validate state. If the request is ambiguous, use `enter_plan_mode`.
- **Bug Fixes:** Empirically reproduce the issue with a test case *before* attempting a fix.

## 2. Strategy Phase
- **Goal:** Formulate a grounded plan.
- **Imperative:** For complex tasks, use `write_todos` (pending/in_progress/completed/blocked/cancelled).
- **Communication:** Share a concise strategy summary with the user.

## 3. Execution Phase (Plan-Act-Validate)
- **Plan:** Outline implementation + verification.
- **Act:** Surgical, atomic edits. No batch changes in one file in one turn.
- **Validate:** Mandatory automated tests and linting. A task is not finished until it is verified.
