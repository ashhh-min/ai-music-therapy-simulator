# Deployment Runbook

Status: local deployment hardened and verified 2026-08-30 (S18, D027).
Public cloud deployment is **prepared but not executed** - it requires the
student's Streamlit Community Cloud and Neon accounts
(`docs/DeploymentGuide_StreamlitCloud_Neon.md`). Nothing below claims a live
deployment happened.

## A. Local deployment

1. Create and activate `.venv` (Python >= 3.11).
2. Install with `python -m pip install -e .[dev]`.
3. Start PostgreSQL: `colima start && docker compose up -d`
   (container `mt-postgres`, port 5432, databases `mt_simulator` and
   `mt_simulator_test`, credentials postgres/postgres - local demo only).
4. Seed personas: `python -m ai_music_therapy.seed_demo`.
5. Run the gates: `pytest`, `python scripts/smoke_test.py`,
   `ruff check src tests scripts`.
6. Run the app: `streamlit run app.py`.

Deterministic mode is the default: with no `OPENAI_API_KEY` configured the
app and every batch run stay fully offline and reproducible.

### Connection management (S18 hardening)

All repository operations run through `src/ai_music_therapy/db.py` instead of
the per-operation connections used through S17. Layers, in the prescribed
order:

| Layer | Object | Behavior |
|---|---|---|
| Connection factory | `ConnectionFactory` | Builds configured psycopg connections (`dict_row`, `connect_timeout=5`) and counts them for verification. |
| Pooled engine | `PooledConnectionManager` | Lazy, thread-safe `psycopg_pool.ConnectionPool`: `min_size=1`, `max_size=8`, checkout timeout 10 s, `max_lifetime=1800 s` recycling. |
| Transaction wrapper | `manager.transaction()` | Pooled connection inside explicit BEGIN/COMMIT/ROLLBACK; connection returns to the pool afterwards. |
| Retry + timeout | `manager.run(operation)` | Up to 3 attempts with exponential backoff (0.2 s base) on transient `OperationalError`; integrity errors propagate immediately. |

One process-wide pool per database URL (`get_manager`) means Streamlit page
reruns and concurrent sessions share the bounded pool instead of opening a new
one per rerun; cached pools close at interpreter exit. This is what makes the
app safe for multi-user deployment on a small Neon database.

## B. Pre-deployment verification (executed locally, S18)

Actually run and recorded under `evidence/S18/`:

- [x] Full test suite: 234 passed (7 new `tests/test_connection_pool.py`
      tests on top of the 227 baseline).
- [x] Pool reuse: 20 sequential operations opened <= 2 connections.
- [x] Transaction semantics: commit visible, mid-transaction raise rolls back.
- [x] Retry semantics: transient `OperationalError` retried until success
      (attempt 3); non-retryable errors propagate immediately.
- [x] Multi-user simulated deployment: 8 concurrent users x 4 mixed read/write
      operations through one manager with `max_size=4`; all 32 operations
      succeeded, `pool_size <= 4`, connections opened <= 4.
- [x] `ruff check src tests scripts` clean; `python scripts/smoke_test.py`
      PASS; `git diff --check` clean.
- [x] Deterministic no-key path: headless AppTest run of the trial page saves
      a trial without any API key; batch runner `--dry-run` validates the
      frozen 75-cell matrix.
- [x] Clean checkout: fresh clone + fresh venv + `pip install -e .[dev]`
      passes smoke + pytest with DB tests skipping cleanly (see
      `evidence/S18/check_outputs.txt`).
- [x] Release scans: no secrets, no private data, no unlabelled synthetic
      output, no clinical efficacy claims in the release tree (Part E).

## C. Cloud deployment checklist (to execute; requires student accounts)

Step-by-step console instructions live in
`docs/DeploymentGuide_StreamlitCloud_Neon.md`. Summary, all still open:

- [ ] Push `main` to GitHub.
- [ ] Create the Neon project/database and copy the connection string
      (`?sslmode=require`).
- [ ] Deploy on Streamlit Community Cloud: repo + branch `main` + main file
      `app.py`; set `DATABASE_URL` and `AI_MUSIC_APP_MODE=deterministic` in
      Advanced settings (env vars; `config.py` reads them directly - no
      `st.secrets` code path was added, see D027).
- [ ] Seed personas once against Neon
      (`python -m ai_music_therapy.seed_demo` with the Neon `DATABASE_URL` in
      `.env.local`).
- [ ] Run the post-deployment checks (Part D) and save screenshots to
      `evidence/S18/`.

`requirements.txt` is already prepared for this: it installs the package
(`-e .`, needed for the `src/` layout) and pins `psycopg[binary,pool]` so the
pooled `db.py` imports resolve on the cloud build.

## D. Post-deployment verification (execute after Part C)

- [ ] Public URL loads without exceptions on every page (Lab + Research).
- [ ] Global sidebar disclaimer visible on every page.
- [ ] Personas page lists the 5 synthetic personas from Neon.
- [ ] A deterministic trial saves end-to-end and appears on the Dashboard.
- [ ] Trial provenance shows engine/model/prompt version/seed/timestamp and
      the synthetic label.
- [ ] Neon connection count stays bounded: pool `max_size=8` per app instance,
      visible via `PooledConnectionManager.stats()` (pool_size,
      connections in use/idle).
- [ ] No secrets in repo, Streamlit logs, or Neon connection strings committed
      anywhere.

## E. Release audit (S18)

Scans over the release tree (tracked files only; `data/local/` and
`evidence/` are gitignored by design):

- Secrets: pattern scan for API keys/tokens/passwords - only the local
  docker-compose demo credentials (postgres/postgres, intentionally public
  and local-only) match; no real key ever committed.
- Private data: none by construction - all personas synthetic, DB
  `CHECK (synthetic = 1)`, no real child data, transcripts, or clinical
  notes anywhere (see `docs/DataGovernance.md`).
- Claims: every analysis doc carries the standing non-clinical notice;
  results are labelled software observations (deterministic) vs
  model-generated content (AI), never effects or outcomes.
- Synthetic labelling: trial bundles, dashboard captions, README, demo, and
  portfolio materials all mark outputs synthetic.

Known non-blocking follow-ups (recorded, not done in S18):

- Cloud deployment itself (Part C/D) awaits student accounts.
- Historical AI outputs used earlier providers (GLM, Volcano Ark) and cannot
  be regenerated identically; current provider is Aliyun Bailian.
- The frozen matrix has no high-volume cells, so the distress-flag path is
  covered by unit tests but not by a batch run.

## Recovery

- If AI calls fail, switch to deterministic mode (`AI_MUSIC_APP_MODE` or
  simply unset `OPENAI_API_KEY`) - it is the default and fully featured.
- If the database is corrupted, back it up first
  (`docker compose exec mt-postgres pg_dump -U postgres mt_simulator`
  locally, or `pg_dump <neon-connection-string>` for Neon), recreate the
  local volume (`docker compose down -v && docker compose up -d`) or restore
  Neon's point-in-time backup, reseed personas, and rerun accepted synthetic
  trials only when their design/provenance is available.
- If a unit breaks the demo, reset to the last accepted checkpoint and reapply
  only the bounded change.
