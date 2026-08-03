# Session State

Use this file when pausing or resuming work.

## Before Pausing
- Record the active unit and exact acceptance status.
- Run the unit's required checks.
- Save evidence under `evidence/<UnitID>/`.
- Update `TASKS.md`, `STATUS.md`, `docs/decisions.md`, and `docs/CoBuildLog.md` truthfully.
- Commit only passing or explicitly documented work.

## On Resume
1. Confirm the repository root.
2. Run `git status --short`.
3. Read `TASKS.md`, this file, the active prompt, and the latest log entries.
4. Record the current checkpoint with `git rev-parse --short HEAD`.
5. Re-run the last passing checks.
6. Continue from the current state; do not regenerate validated modules.

## Current Resume Record
- Active unit: S03 accepted and committed (2026-08-03); session paused. Next unit is S04 — activate on resume.
- Last known checkpoint: 5842ff5 (S02 evidence base). S03 is HEAD (latest commit); run `git rev-parse --short HEAD` on resume to confirm.
- Last passing commands: `.venv/bin/python scripts/smoke_test.py` (PASS) and `.venv/bin/python -m pytest` (10 passed); see `evidence/S03/check_outputs.txt`.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- On resume: run `git status` / `git log`, re-read `TASKS.md` + this file + the S04 prompt, re-run smoke + pytest as a baseline, then activate S04 (Music Parameter Ontology and Scenario Rubric).
