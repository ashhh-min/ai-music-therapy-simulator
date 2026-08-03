# One-Time Workspace Audit

Read completely: `README.md`, `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/AuthoritativePlan.md`, `docs/Architecture.md`, `docs/TestPlan.md`, `docs/DataGovernance.md`, `docs/ResearchEthics.md`, `docs/decisions.md`, `docs/CoBuildLog.md`, and `prompts/GlobalEngineeringContract.md`.

Inspect and report the actual tree. Confirm INIT is marked complete, WORKSPACE_AUDIT is active, S01-S18 all exist, and S01 is the intended first implementation unit. Record only actual environment versions in `docs/EnvironmentRecord.md`. Check for secrets, personal/private data, unexpected generated files, invalid JSON/TOML, path/configuration conflicts, unlabelled synthetic outputs, and setup blockers. Run only:

- package import or `python scripts/smoke_test.py`;
- configuration parse;
- public fixture validation.

Update audit evidence truthfully, report changed files, and stop. Do not implement product/research features and do not begin S01.
