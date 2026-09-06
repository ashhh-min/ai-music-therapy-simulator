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
- Active unit: S19 implemented 2026-09-06, PENDING ACCEPTANCE (all four implementation-order steps complete; stop-and-report done). Prompt: prompts/Session_19_Adhoc_Entrances_Track_Persona_Libraries.md. Locked decisions: approved tracks store profile + source sha256 only (raw audio never persisted); review-stage confirmation trials are not persisted; persona entrance = JSON upload + AI draft (S11 pipeline reuse) + manual form. Implementation order: (1) staged workflow + TrackBase persistence; (2) audio extraction + track entrance UI; (3) persona entrance; (4) docs/control docs. Cloud go-live deferred to an offline session after S19 acceptance.
- Last checkpoint: the S19 implementation commit follows f177134 (find it with `git log --oneline -3`); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-09-06, S19 implementation): `.venv/bin/python -m pytest` (282 passed via junit: tests=282 failures=0 errors=0 skipped=0; includes the 2026-09-06 review revision: mp3 support + 120 MB cap; the console count line is swallowed by this environment - pre-existing quirk, junit is authoritative), `.venv/bin/ruff check src tests scripts` (clean), `scripts/smoke_test.py` (PASS), `git diff --check` clean, clean checkout with no key and no .env.local (smoke PASS + 282/282).
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: functional via Aliyun Bailian qwen3.8-max (Responses API, .env.local; D019/D026); provider history GLM, Volcano Ark, Bailian recorded in docs/limitations.md. Deterministic no-key mode remains the default.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file + the S19 prompt, re-run smoke + pytest (282 baseline), then WAIT for the student's acceptance verdict on S19. Do not start the cloud go-live or any new unit: go-live happens in the student's offline session after acceptance, and no further unit exists without a new written prompt.
