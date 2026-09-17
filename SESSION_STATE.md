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
- Active unit: none open. S20 (parameter-to-Max/MSP patch generation) ACCEPTED by the student 2026-09-17 (implemented the same day on top of 93ec99c, implementation commit a1d1f09; no revisions requested; stop-and-report delivered). Prompt: prompts/Session_20_Parameter_to_MaxMSP_Patch_Generation.md. Max-loadability remains a manual student desktop check (sample artifacts at evidence/S20/synthetic_patch_1ab48c73.maxpat + synthetic_preview_1ab48c73.wav). Optional next unit: S21 (customize the wiring logic as will), prepared 2026-09-17 at the student's request at prompts/Session_21_Customizable_Wiring_Logic.md and DEFERRED - the student will implement it "in the future sometime"; do NOT begin until explicitly told. Cloud go-live happens in the student's offline session.
- Last checkpoint: the S20 acceptance + S21-prep commit follows a1d1f09 (S20 implementation, which follows 93ec99c); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-09-17, S20 implementation): `.venv/bin/python -m pytest` (312 passed via junit: tests=312 failures=0 errors=0 skipped=0 with PostgreSQL up; console count line swallowed - pre-existing quirk, junit authoritative), `.venv/bin/python -m ruff check src tests scripts` (clean), `scripts/smoke_test.py` with no key (PASS), `git diff --check` clean, clean checkout with no key and no .env.local (smoke PASS + 312/312).
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: functional via Aliyun Bailian qwen3.8-max (Responses API, .env.local; D019/D026); provider history GLM, Volcano Ark, Bailian recorded in docs/limitations.md. Deterministic no-key mode remains the default.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file, re-run smoke + pytest (312 baseline). S20 is ACCEPTED; S21 is optional and deferred: do not begin it until the student explicitly says to start S21; cloud go-live remains the student's offline session.
