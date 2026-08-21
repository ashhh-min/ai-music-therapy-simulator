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
- Active unit: S16 implemented 2026-08-21 (pending mentor acceptance, D025): batch runner scripts/run_batch.py runs the frozen 75-cell matrix (config/trial_matrix.csv as single source of truth), validates matrix + completeness, exports immutable synthetic-labeled bundles under data/local/batch_runs/<stamp>-<matrix-sha>/; optional --ai-subset N adds key-gated AI comparison trials (live-verified with Ark, 1 cell). Official run: 20260821T053515Z-e5f50132 (75/75 deterministic cells). On acceptance, activate S17 (Analysis, Limitations, and Research Report).
- Last checkpoint: S16 commit follows 678fe0d (S15); run `git rev-parse --short HEAD` on resume. Note: user-side uncommitted change present during S16 - .gitignore now also ignores bailian.md (empty scratch file); not part of the S16 commit.
- Last passing commands (2026-08-21, S16): `.venv/bin/python -m pytest` (227 passed incl. 14 batch tests), `.venv/bin/ruff check src tests scripts` (clean), `scripts/smoke_test.py` (PASS), `scripts/run_batch.py --dry-run` (matrix valid), official run 75/75 cells, immutability guard verified (re-run same id exits 1), live AI-subset smoke 1 cell via Ark; see `evidence/S16/check_outputs.txt`.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: NOT yet functional with GLM — deferred to S10 (Responses API vs GLM /chat/completions; also set OPENAI_BASE_URL to the API root). See D014.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file + the S17 prompt, re-run smoke + pytest, then activate S17 (Analysis, Limitations, and Research Report): analysis reads the immutable batch bundle(s) under data/local/batch_runs/ (never rewrites them); findings belong to S17 only. S18 reminder: pooled DB connections before Neon.
