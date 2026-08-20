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
- Active unit: S07 accepted and committed (2026-08-12); between-session infra/safety work committed 2026-08-12; SQLite-to-PostgreSQL switch committed 2026-08-19 (D015). Next unit is S15 (Dashboard II: Radar, Time Series, and Summaries). S14 accepted 2026-08-20 (D023): AI client on Responses API, store=False, strict validation boundary, live-verified with Volcano Ark - includes the GLM Responses-API/base-URL fix from D014) - activate on resume. S08 accepted 2026-08-20 (D017); S07 accepted 2026-08-12; between-session infra 2026-08-12 and PostgreSQL switch 2026-08-19 (D015). — activate on resume.
- Last checkpoint: run `git rev-parse --short HEAD` on resume (S07 + infra committed 2026-08-12); prior accepted = c87c076 (S06).
- Last passing commands (2026-08-20, S14): `.venv/bin/python -m pytest` (23 passed), `.venv/bin/ruff check src tests scripts` (clean), `scripts/smoke_test.py` (PASS), test_analytics 5 passed, full suite 209 passed, ruff clean, smoke PASS, AppTest dashboard verified; see `evidence/S14/check_outputs.txt`. Dev DB now holds 8 synthetic demo trials (6 added at S14 for comparison data). S12 evidence: `evidence/S12/check_outputs.txt`. S11 evidence: `evidence/S11/check_outputs.txt`. S10 evidence: `evidence/S10/check_outputs.txt`. Prior S09 evidence: `evidence/S09/check_outputs.txt`. S08 evidence: `evidence/S08/check_outputs.txt`.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: NOT yet functional with GLM — deferred to S10 (Responses API vs GLM /chat/completions; also set OPENAI_BASE_URL to the API root). See D014.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file + the S08 prompt, re-run smoke + pytest, then activate S15 (Dashboard II: Radar, Time Series, and Summaries) (S08 per D015; S09 per D018; S10 per D019 - AI mode now works with the current Ark `.env.local`; if the provider changes, re-probe /responses support - against PostgreSQL per D015, superseding the prompt's SQLite wording).
