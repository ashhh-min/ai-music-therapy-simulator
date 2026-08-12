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
- Active unit: S05 (complete 2026-08-12; awaiting acceptance). Next unit is S06 — do not start until accepted.
- Last checkpoint: a31c450 (S04 music ontology). Pre-S05 checkpoint: a31c450.
- Last passing commands: `.venv/bin/python scripts/smoke_test.py` (PASS) and `.venv/bin/python -m pytest` (14 passed); see `evidence/S05/check_outputs.txt`.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- Outstanding acceptance item: Mentor acceptance of S05, then activate S06 (Repository Contracts, Schemas, and Tests).
