# Engineering Standards

## 1. Code Quality
- **Idiomatic:** Adhere strictly to language/framework conventions.
- **Safety:** Maintain structural integrity and type safety (e.g., in TypeScript). Never hack around type checks.
- **Modularity:** Prefer composition over inheritance. Consolidate logic into clean, traceable abstractions.

## 2. Validation
- **Mandatory:** Validation is not optional. It consists of:
    - **Automated Tests:** Running existing suites or creating new ones to verify changes.
    - **Standards Check:** Running linters/formatters (`eslint`, `ruff`, etc.).
- **Regressions:** Every change must prove no regressions were introduced.

## 3. Documentation
- **Repo-wide:** Update `GEMINI.md` for shared conventions.
- **Private:** Document local/machine-specific workflows in private memory folders.
- **Lifecycle:** Documentation is part of the code artifact. A task is incomplete if documentation is stale.
