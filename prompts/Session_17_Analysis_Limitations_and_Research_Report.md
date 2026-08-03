# S17 - Analysis, Limitations, and Research Report

## Role
Act as the implementation partner for this bounded InnovationLab session in `ai-music-therapy-simulator`.

## Read First
- `README.md`
- `TASKS.md`
- `STATUS.md`
- `SESSION_STATE.md`
- `docs/AuthoritativePlan.md`
- `docs/Architecture.md`
- `docs/TestPlan.md`
- `docs/DataGovernance.md`
- `docs/ResearchEthics.md`
- `prompts/GlobalEngineeringContract.md`
- Latest entries in `docs/decisions.md` and `docs/CoBuildLog.md`

## Prior-State Check
- Confirm the one-time workspace audit is accepted.
- Confirm `S17` is the only active unit in `TASKS.md`.
- Record the pre-unit Git checkpoint.
- Run the currently passing baseline checks before editing.

## Session Objective
Analyze only accepted synthetic outputs, compare engine stability, write findings and limitations, and complete the research report.

## Files to Create or Modify
- `docs/ResearchReport.md`
- `docs/analysis_notebook.md`
- `docs/limitations.md`
- `evidence/S17/`

## Implementation Requirements
1. Preserve the original AI Music Therapy identity and the persona → music → synthetic response → analysis loop.
2. Keep every persona and output explicitly synthetic.
3. Preserve the clinical claims boundary, privacy rules, and provenance requirements.
4. Make only the files needed for this unit's objective.
5. Add or update tests and documentation for every behavior introduced.
6. Keep deterministic no-key operation working.

## Tests and Checks
- Run the smallest relevant unit tests first.
- Run `python scripts/smoke_test.py`.
- Run `pytest` unless the unit is documentation-only; for documentation-only work, validate all referenced files and links.
- Run `git diff --check`.
- Scan changed files for secrets, private data, unlabelled synthetic output, and unsupported clinical claims.
- Save truthful command output or manual evidence under `evidence/S17/`.

## Acceptance Criteria
- Claims stay inside the preregistered analysis plan.
- Software observations are separated from clinical evidence.
- Limitations cover persona validity, model dependence, prompt sensitivity, and no human participants.
- Student can explain the principal change and one limitation.
- `TASKS.md`, `STATUS.md`, decisions, co-build log, tests, and evidence agree.

## Do Not Do
- Do not implement future units.
- Do not overwrite the full `TASKS.md` file.
- Do not add credentials, real-person data, medical advice, or fabricated evidence.
- Do not report a deployment, experiment, or test as successful unless it was actually completed.

## TASKS.md Update
Mark `S17` complete only after every acceptance item passes. Record changed files, actual test results, evidence path, unresolved issues, and prepare the next unit without implementing it.

## Stop Condition
Stop after `S17`. Report the diff, tests, evidence, issues, and next unit; do not begin the next prompt.
