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
- Active unit: none open. S19 ACCEPTED by the student 2026-09-06 (all four implementation-order steps plus two same-day review revisions complete; stop-and-report done; acceptance recorded). Prompt: prompts/Session_19_Adhoc_Entrances_Track_Persona_Libraries.md. Locked decisions: approved tracks store profile + source sha256 only (raw audio never persisted); review-stage confirmation trials are not persisted; persona entrance = JSON upload + AI draft (S11 pipeline reuse) + manual form. Implementation order: (1) staged workflow + TrackBase persistence; (2) audio extraction + track entrance UI; (3) persona entrance; (4) docs/control docs. Cloud go-live happens in the student's offline session (S19 is accepted). Next unit: S20 (parameter-to-Max/MSP patch generation, the reversed S19 flow) with its prompt prepared at prompts/Session_20_Parameter_to_MaxMSP_Patch_Generation.md; do NOT begin until the student explicitly says to start S20.
- Last checkpoint: the S19 implementation commit follows f177134 (find it with `git log --oneline -3`); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-09-06, S19 implementation): `.venv/bin/python -m pytest` (284 passed via junit: tests=284 failures=0 errors=0 skipped=0; includes both 2026-09-06 review revisions: mp3 support + 120 MB cap, and bounded live-AI calls (timeout 120 s, no SDK transport retries) + engine-expectation hints; the console count line is swallowed by this environment - pre-existing quirk, junit is authoritative), `.venv/bin/ruff check src tests scripts` (clean), `scripts/smoke_test.py` (PASS), `git diff --check` clean, clean checkout with no key and no .env.local (smoke PASS + 284/284).
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: functional via Aliyun Bailian qwen3.8-max (Responses API, .env.local; D019/D026); provider history GLM, Volcano Ark, Bailian recorded in docs/limitations.md. Deterministic no-key mode remains the default.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file + the S19 prompt, re-run smoke + pytest (284 baseline). S19 is ACCEPTED: do not start the cloud go-live (student's offline session) and do not begin S20 until the student explicitly says to start it.
