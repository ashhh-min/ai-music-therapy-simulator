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
- Active unit: S17 implemented 2026-08-21 (pending mentor acceptance, D026): documentation-only unit - docs/analysis_notebook.md (full 75-cell deterministic table + H1-H4 descriptive probes + engine stability: 75/75 reproducible deterministic vs non-reproducible AI incl. 3-sample same-cell probe), docs/limitations.md, docs/ResearchReport.md (4A software behavior separated from 4B model-generated content). Analysis sources: immutable bundles data/local/batch_runs/20260821T053515Z-e5f50132 (75 det) and ai-comparison-20260821 (75 det + 5 AI qwen3.8-max). On acceptance, activate S18 (Deployment, Demo, Portfolio, and Release Audit) with pooled-connection hardening first.
- Last checkpoint: S17 commit follows 203f287 (S16 + bailian gitignore); run `git rev-parse --short HEAD` on resume.
- Last passing commands (2026-08-21, S17): `.venv/bin/python -m pytest` (227 passed), `.venv/bin/ruff check src tests scripts` (clean), `scripts/smoke_test.py` (PASS), `git diff --check` clean; docs-only validation: 20 referenced paths exist, links intact, claims-language scan clean; live AI calls this session: 5-cell comparison bundle + 2 same-cell repeat probes via qwen3.8-max (Aliyun Bailian); see `evidence/S17/check_outputs.txt`.
- Interpreter: `.venv/bin/python` (Python 3.13.14). System `python3` (3.9.6) is below the required 3.11 and must not be used.
- To run the UI: start the database first (`colima start` then `docker compose up -d`), then `streamlit run app.py` (deterministic by default; seed with `python -m ai_music_therapy.seed_demo`). If PostgreSQL is down, repository tests skip with a message and DB-backed pages error on use - deterministic simulation still works.
- Credentials: real key in gitignored `.env.local`; never commit `.env.*` (except `.env.example`).
- AI mode: NOT yet functional with GLM — deferred to S10 (Responses API vs GLM /chat/completions; also set OPENAI_BASE_URL to the API root). See D014.
- On resume: `git status` / `git log`, re-read `TASKS.md` + this file + the S18 prompt, re-run smoke + pytest, then activate S18 (Deployment, Demo, Portfolio, and Release Audit): pooled DB connections first (psycopg_pool; repository -> pooled engine -> transaction wrapper -> retry+timeout -> multi-user simulated test), then Streamlit Community Cloud + Neon per docs/DeploymentGuide_StreamlitCloud_Neon.md and D016/D023.
