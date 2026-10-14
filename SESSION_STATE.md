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
- Active unit: S22 (UI polish: ElevenLabs-style minimal monochrome theme) IMPLEMENTED 2026-09-17 + visual defect fix 2026-10-14 (root cause: the S22 blanket font rule clobbered Streamlit's Material-Symbols ligature icon spans, painting raw ligature text over expander labels - the student's red boxes; plus a dark-mode white-on-white primary button label fixed via light-dark()); site-wide verified in real Chrome via CDP: 8 pages x light+dark, painted-overlap scan 0 hits, screenshots /tmp/demo2/; pending student acceptance (browser visual check light+dark). S21 added to the TASKS.md checklist as OPTIONAL+DEFERRED (student implements in a future session; do NOT kick off). Cloud go-live (Neon seed + Streamlit Community Cloud) requested by the student and in progress: DATABASE_URL now present in .env.local; the git push to origin still needs the student's credential approval.
- Last checkpoint: the S22 theme commit follows ead8c02 (S20 acceptance + S21 prep, which follows a1d1f09); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-10-14, S22 visual fix): `.venv/bin/python -m pytest` (312 passed via junit: tests=312 failures=0 errors=0 skipped=0, PostgreSQL up, no key), `.venv/bin/python -m ruff check src tests scripts` (clean) + `ruff format --check` on the touched file (clean), `scripts/smoke_test.py` no key (PASS), `git diff --check` clean, AppTest over app.py (no exception; light-dark CSS present; disclaimer visible), server :8501 log 0 errors, CDP sweep 8 pages x 2 modes with 0 overlap hits.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: functional via Aliyun Bailian qwen3.8-max (Responses API, .env.local; D019/D026); provider history GLM, Volcano Ark, Bailian recorded in docs/limitations.md. Deterministic no-key mode remains the default.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file, re-run smoke + pytest (312 baseline). S22 is implemented pending acceptance (browser visual check light+dark); S21 stays deferred until the student explicitly kicks it off; cloud go-live remains the student's session and needs the pending push to origin first.
