## DISPATCH — E2E Testing Sub-Orchestrator

Your Role: E2E Testing Sub-Orchestrator
Working directory: /data/data/com.termux/files/home/teamwork_projects/skills_verification/.agents/sub_orch_e2e_testing
Project directory: /data/data/com.termux/files/home/teamwork_projects/skills_verification
Original Request path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/ORIGINAL_REQUEST.md
PROJECT.md path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/PROJECT.md
TEST_INFRA.md path: /data/data/com.termux/files/home/teamwork_projects/skills_verification/TEST_INFRA.md

Task & Objective:
Build the complete, opaque-box E2E test suite covering Tiers 1-4 for features F1.1–F3.3 (at least 115 test cases across 4 tiers):
- Tier 1: Feature Coverage (>=5 tests per feature = 50 tests)
- Tier 2: Boundary & Corner Cases (>=5 tests per feature = 50 tests)
- Tier 3: Cross-Feature Pairwise Interaction (>=10 tests)
- Tier 4: Real-World Application Scenarios (>=5 tests)

Workflow:
1. Create `SCOPE.md` in your working directory defining test creation milestones.
2. Dispatch `teamwork_preview_test_writer` or `teamwork_preview_worker` to write the test runner script (`/data/data/com.termux/files/home/teamwork_projects/skills_verification/tests/run_e2e_tests.py`) and test modules.
3. Dispatch `teamwork_preview_reviewer` to review test quality and coverage.
4. When all test cases are created and verified runnable, publish `TEST_READY.md` at project root (`/data/data/com.termux/files/home/teamwork_projects/skills_verification/TEST_READY.md`).
5. Update progress.md continuously and report back to parent when complete.
