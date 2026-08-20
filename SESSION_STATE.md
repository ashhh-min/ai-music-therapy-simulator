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
- Active unit: S15 implemented 2026-08-20 (pending mentor acceptance, D024): six-dimension radar profiles, temporal stage means, descriptive rankings with counts/engines, uncertainty notes, PNG + CSV figure export; chart guide at docs/chart_interpretation.md. On acceptance, activate S16 (Batch Experiment Runner and Trial Matrix).
- Last checkpoint: S15 commit follows 91fa7f2 (pre-unit, post-S14 acceptance); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-08-20, S15): `.venv/bin/python -m pytest` (213 passed), `.venv/bin/ruff check src tests scripts` (clean), `scripts/smoke_test.py` (PASS), AppTest dashboard: 8 subheaders incl. radar/temporal/rankings/uncertainty/export, 2 selectboxes, page warning, no exceptions; see `evidence/S15/check_outputs.txt`. Dev DB holds 8 synthetic demo trials (unchanged this unit).
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: NOT yet functional with GLM — deferred to S10 (Responses API vs GLM /chat/completions; also set OPENAI_BASE_URL to the API root). See D014.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file + the S16 prompt, re-run smoke + pytest, then activate S16 (Batch Experiment Runner and Trial Matrix): make `scripts/run_batch_demo.py` read `config/trial_matrix.csv` as the single source of truth (guarded since S06). Deployment-hardening reminder for S18: pooled DB connections before Neon (TASKS.md Engineering Notes).
