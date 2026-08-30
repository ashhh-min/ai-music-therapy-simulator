# Deployment Guide: Streamlit Community Cloud + Neon PostgreSQL

Status: **draft prepared 2026-08-19; hardening prerequisite completed locally
2026-08-30 (S18, D027)** for the unit S18 (Deployment, demo, portfolio, and release
audit). The target stack was chosen by the student between sessions: the app runs on
**Streamlit Community Cloud**, the database is **Neon PostgreSQL**. The deployment
hardening prerequisite (Part 0, first item) is done and tested locally; none of the
console steps (Parts 1-5) have been executed yet - they require the student's
accounts. When the cloud deployment is executed, update this file with actual
screenshots/outputs under `evidence/S18/` and mark each step done.

Why this stack (recorded for transparency):

- Streamlit is a long-running WebSocket server, so it cannot run on serverless
  platforms such as Vercel Functions.
- Streamlit Community Cloud is free and purpose-built for Streamlit apps.
- Neon is a free-tier serverless PostgreSQL that fits the project's existing
  psycopg 3 / `DATABASE_URL` persistence layer (D015) with no code change.

## 0. Prerequisites checklist

- [x] **Deployment hardening (Engineering Notes, TASKS.md): DONE locally
      2026-08-30 (D027).** The repository's fresh per-operation connections
      were replaced with a pooled connection manager (connection factory ->
      pooled engine -> transaction wrapper -> retry/timeout handling ->
      multi-user simulated deployment test) in `src/ai_music_therapy/db.py` +
      `tests/test_connection_pool.py`. `psycopg[binary,pool]` is in
      `pyproject.toml` and `requirements.txt`. Verified: 8 simulated users x
      4 ops through one max_size=4 pool, all 32 operations succeeded
      (evidence/S18/).
- [ ] GitHub repository pushed and up to date (`git push origin main`).
- [ ] Local gates green: `pytest`, `ruff check src tests scripts`,
      `python scripts/smoke_test.py`.
- [ ] A GitHub account (used to sign in to Streamlit Community Cloud).
- [ ] A Neon account (free tier) - https://neon.com .
- [ ] Real secrets only in gitignored `.env.local` (never committed) - see
      `docs/DataGovernance.md`.

## 1. Create the Neon database

1. Sign up / sign in at https://neon.com (free tier is enough for this project).
2. Create a project, e.g. `ai-music-therapy`.
3. In the Neon dashboard, create a database named `mt_simulator` (matches the local
   default so no code branches are needed).
4. Copy the **connection string**. It looks like:
   `postgresql://<user>:<password>@ep-xxxx-xxxx.region.aws.neon.tech/mt_simulator?sslmode=require`
5. Keep `?sslmode=require` - Neon requires TLS and psycopg 3 honours this parameter.

Note for the record: Neon auto-suspends idle compute on the free tier and restarts it
on the next connection (a few seconds of cold-start latency on the first request).
That is acceptable for a demo/portfolio app; mention it in the demo if asked.

## 2. Point the app at Neon (no code change needed)

`src/ai_music_therapy/config.py` reads `DATABASE_URL` with the local docker-compose
default. On Streamlit Cloud we override it with the Neon URL (step 4 below). The same
mechanism already works locally: putting the Neon URL in `.env.local` and running the
app verifies the hosted DB before deployment.

Optional local pre-check (recommended before S18):

```bash
# .env.local (gitignored): temporarily point at Neon
DATABASE_URL=postgresql://...neon.tech/mt_simulator?sslmode=require

colima start && docker compose up -d   # not needed when using Neon, but harmless
.venv/bin/python -m ai_music_therapy.seed_demo   # seeds personas into Neon
.venv/bin/pytest                                 # repository tests run against TEST_DATABASE_URL (local) - keep them local-only
streamlit run app.py
```

If seeding succeeds against Neon, the app is ready for the cloud.

## 3. Make the repository installable by Streamlit Cloud

Streamlit Community Cloud installs dependencies from `requirements.txt` and then runs
`app.py` from the repo root. Two project-specific details must be handled:

1. **The package uses a `src/` layout.** `app.py` imports
   `ai_music_therapy`, which is only importable after the package itself is
   installed. Add the editable self-install line to `requirements.txt`:

   ```
   -e .
   ```

   (Keep the pinned runtime deps below it. `pip install -e .` reads
   `pyproject.toml`, which already lists all dependencies - the explicit entries in
   `requirements.txt` remain useful as documentation and for Streamlit's dependency
   parser.)

2. **Dev dependencies are not needed in the cloud.** `requirements.txt` already
   excludes pytest/ruff; keep it that way.

S18 action item (done 2026-08-30, D027): `-e .` is at the top of
`requirements.txt` and the psycopg pin carries the `pool` extra
(`psycopg[binary,pool]>=3.2`) so the pooled `db.py` imports resolve in the
cloud build. The app boots locally with this file (verified via fresh
checkout, evidence/S18/check_outputs.txt).

## 4. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and click **Sign in with GitHub** (or email).
2. Authorize the Streamlit OAuth app for your GitHub account.
3. Click **New app** (or "Deploy an app") and fill in:
   - Repository: your GitHub repo (`ai-music-therapy-simulator`, or your fork name).
   - Branch: `main`.
   - Main file path: `app.py`.
   - App URL slug: something like `ai-music-therapy-simulator` (must be unique).
4. Open **Advanced settings** before deploying and add the environment variables
   (these replace `.env.local`, which does not exist on the server):

   | Variable | Value | Required |
   |---|---|---|
   | `DATABASE_URL` | the Neon connection string from step 1 | Yes |
   | `AI_MUSIC_APP_MODE` | `deterministic` (default) or `ai` | Yes |
   | `AI_MUSIC_PROMPT_VERSION` | e.g. `2026-08-01.v1` | Recommended |
   | `OPENAI_MODEL` | e.g. `glm-5.2` (only if AI mode) | AI mode only |
   | `OPENAI_BASE_URL` | provider API root (only if AI mode) | AI mode only |
   | `OPENAI_API_KEY` | real key (only if AI mode) | AI mode only |

   Note: if advanced-settings env vars are unavailable for the account, the
   fallback is Streamlit `secrets` (app menu → Settings → Secrets), a TOML file:

   ```toml
   DATABASE_URL = "postgresql://...neon.tech/mt_simulator?sslmode=require"
   AI_MUSIC_APP_MODE = "deterministic"
   ```

   Decision (S18, D027): use **env vars via Advanced settings** - `config.py`
   reads `os.getenv` and Streamlit Cloud exposes advanced-settings entries as
   environment variables, so no `st.secrets` code path is added. The TOML
   secrets fallback above stays documented but unused.
5. Click **Deploy**. First build takes a few minutes (pip install of streamlit,
   pandas, plotly, psycopg).
6. After the app starts, open the Personas page. If it lists the seeded personas,
   the Neon connection works. If empty, seed once from a local machine pointed at
   Neon (step 2) or run the seed via a one-off Streamlit Cloud "reboot with a seed
   flag" - simplest is local seeding; choose one and record it.

## 5. Post-deployment checks (S18 acceptance evidence)

- [ ] App URL loads without exceptions on all pages (Lab + Research).
- [ ] Global disclaimer visible in the sidebar on every page.
- [ ] Personas page lists the 5 synthetic personas from Neon.
- [ ] A deterministic trial runs end-to-end and is saved (Dashboard shows it).
- [ ] Trial provenance shows engine/model/prompt-version/seed/timestamp.
- [ ] App settings show the intended env vars; no secrets in the repo or logs.
- [ ] Save screenshots + the public URL under `evidence/S18/`.
- [ ] Update `STATUS.md`, `docs/decisions.md` (deployment decision), and this file's
      status line from "draft" to "deployed" with the actual URL.

## 6. Operational notes and limits (be honest in the portfolio)

- **Community Cloud resource limits**: apps share free infrastructure; heavy batch
  runs (the 75-cell matrix) are better executed locally and only results viewed in
  the cloud app.
- **Idle sleeping**: the app sleeps when unused and takes ~30-60 s to wake. This is
  a platform behavior, not a bug.
- **Private data**: this project has none by design (all personas synthetic,
  `CHECK (synthetic = 1)` at the database level) - see `docs/DataGovernance.md`.
- **Reproducibility**: deploys track the `main` branch; every redeploy is a fresh
  container. The database (Neon) is the only persistent state.
- **Backups**: Neon free tier keeps limited history; take a `pg_dump` before any
  schema change (`docker compose exec db pg_dump ...` pattern from
  `docs/DeploymentRunbook.md` works against Neon too, from any machine with `psql`
  or a container).

## 7. Rollback

- App: revert the commit on `main` (or pin the app to an older commit in app
  settings) - Streamlit Cloud redeploys automatically.
- Database: restore from Neon's point-in-time restore, or re-seed personas (they
  are synthetic and reproducible via `python -m ai_music_therapy.seed_demo`).
