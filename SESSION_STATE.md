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
- Active unit: S18 implemented 2026-08-30 (pending mentor acceptance, D027): deployment hardening (connection factory, psycopg_pool manager, transaction wrapper, retry/timeout, 8-user simulated deployment test) in src/ai_music_therapy/db.py + tests/test_connection_pool.py; repository refactored onto the pooled manager; dashboard migrated to width="stretch"; requirements.txt cloud-ready (-e ., psycopg[binary,pool]); docs/DeploymentRunbook.md, docs/DemoScript.md, docs/PortfolioGuide.md written; DeploymentGuide hardening prerequisite marked done; release scans pass; clean checkout verified deterministic. Public cloud deployment NOT executed (needs student accounts). S18 is the final unit: after acceptance the project is complete.
- Last checkpoint: S18 commit follows dbfe3df (S17); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-08-30, S18): `.venv/bin/python -m pytest` (234 passed), `.venv/bin/ruff check src tests scripts` (clean), `scripts/smoke_test.py` (PASS), `git diff --check` clean; release scans (secrets/private-data/claims/synthetic labels) clean; clean checkout (fresh tree + fresh venv + `pip install -e ".[dev]"` + smoke + pytest, no key) verified; see `evidence/S18/check_outputs.txt`.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: functional via Aliyun Bailian qwen3.8-max (Responses API, .env.local; D019/D026); provider history GLM, Volcano Ark, Bailian recorded in docs/limitations.md. Deterministic no-key mode remains the default.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file. If S18 is not yet accepted, re-run smoke + pytest and respond to mentor feedback only. If S18 is accepted, the S01-S18 plan is complete; the only remaining work is executing the cloud deployment checklist (docs/DeploymentRunbook.md Parts C/D) with the student's accounts - do not start any new implementation without a new written prompt.
