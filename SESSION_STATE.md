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
- Active unit: S22 (UI polish: ElevenLabs-style minimal monochrome theme) IMPLEMENTED 2026-09-17, pending student acceptance; stop-and-report delivered WITH the requested Streamlit Community Cloud deployment guide. Prompt: prompts/Session_22_UI_Polish_ElevenLabs_Style.md. Cosmetic-only boundary: dual achromatic palettes in .streamlit/config.toml (default light; browser Light/Dark/System setting selects; Streamlit 1.60 has no server-side system base - crash-verified - and no st.theme()) + mode-agnostic CSS from ui/theme_css.py injected once from app.py; NO page module touched; disclaimer and settings menu stay visible; suite unchanged 312. The student's acceptance step: look at http://localhost:8501 in both light and dark. S20 ACCEPTED 2026-09-17 (a1d1f09, flip ead8c02); Max-loadability check remains available via evidence/S20/. S21 optional and DEFERRED until explicitly kicked off. Cloud go-live happens in the student's session and needs the pending git push first.
- Last checkpoint: the S22 theme commit follows ead8c02 (S20 acceptance + S21 prep, which follows a1d1f09); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-09-17, S22 theme): `.venv/bin/python -m pytest` (312 passed via junit: tests=312 failures=0 errors=0 skipped=0 with PostgreSQL up, no key; console count line swallowed - pre-existing quirk, junit authoritative), `.venv/bin/python -m ruff check src tests scripts` (clean), `scripts/smoke_test.py` with no key (PASS), `git diff --check` clean, AppTest over app.py (CSS injected, disclaimer visible), streamlit server :8501 HTTP 200 with a clean log.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: functional via Aliyun Bailian qwen3.8-max (Responses API, .env.local; D019/D026); provider history GLM, Volcano Ark, Bailian recorded in docs/limitations.md. Deterministic no-key mode remains the default.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file, re-run smoke + pytest (312 baseline). S22 is implemented pending acceptance (browser visual check light+dark); S21 stays deferred until the student explicitly kicks it off; cloud go-live remains the student's session and needs the pending push to origin first.
