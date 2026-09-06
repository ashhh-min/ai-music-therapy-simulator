# TASKS.md - AI Music Therapy

## Project Goal
Build an evidence-first educational simulator that explores how explicitly synthetic neurodiversity profiles may produce different model-generated responses to music parameters, while preventing clinical overclaims and preserving reproducibility.

## Global Rules
- The system is educational and research-oriented, not diagnostic or therapeutic.
- Never represent AI output as a real child's predicted response.
- Never store real child data, private health information, identifiable transcripts, or clinical notes.
- Every persona and trial must be marked synthetic.
- Preserve prompt/model/seed/version provenance.
- Do not invent citations, experiments, screenshots, test results, or deployment status.
- Do not hard-code secrets or commit `.env` or `.streamlit/secrets.toml`.
- Implement exactly one bounded unit at a time.
- Save evidence under `evidence/<UnitID>/` and stop before the next unit.

## Current Unit
Unit code: S19
Unit focus: Ad-hoc Entrances - Staged Review and Approved Track/Persona Libraries.
Current prompt: `prompts/Session_19_Adhoc_Entrances_Track_Persona_Libraries.md`
Status: Implemented 2026-09-06, PENDING ACCEPTANCE. All four implementation-order steps landed on top of checkpoint f177134: staged state machine + write-once TrackBase persistence, local librosa extraction + track entrance UI end-to-end, persona entrance (JSON upload / key-gated AI draft / manual form) through the S11 gates, docs + control docs. Gates: full suite 281 passed via junit (234 baseline + 47 new; 0 failures/errors/skips), ruff clean, smoke PASS, git diff --check clean, clean checkout deterministic with no API key and no .env.local (281/281 + smoke PASS), release scans clean (no secrets, no clinical claims, synthetic labels present, zero audio files committed). Locked student decisions implemented as agreed: approved tracks store profile + sha256 only (raw audio never persisted); review-stage trials not persisted; three persona input modes; write-once approval, existing IDs never overwritten. Cloud go-live remains deferred to the student's offline session after S19 acceptance.
Acceptance evidence: `evidence/S19/check_outputs.txt` (captured 2026-09-06); decision D028 (recorded in `docs/decisions.md`).
Pre-unit checkpoint: f177134.

## Acceptance Criteria for Current Unit
- Upload, extract, review (edit), confirmation trial, approval persists a TrackBase entry with full provenance; rejection persists nothing.
- Raw audio is verifiably never persisted (memory only; database stores the reviewed parameter profile + source sha256).
- All three persona input modes (JSON upload, AI draft, manual form) reach the same gates; approval saves, rejection does not, existing persona IDs never overwritten.
- Deterministic no-key path works for both entrances (AI draft correctly key-gated).
- Frozen 75-cell matrix, preregistration, and immutable bundles untouched.
- Full suite + ruff + smoke green; clean checkout still runs deterministic.
- `TASKS.md`, `STATUS.md`, decisions (D028), co-build log, tests, and evidence agree.

## Session Checklist
- [x] INIT - Prepared starter materialized by package generator
- [x] WORKSPACE_AUDIT - One-time audit (complete 2026-08-03; accepted)
- [x] S01 - Project scope and claims boundary (complete 2026-08-03; accepted)
- [x] S02 - Evidence review protocol and bibliography (complete 2026-08-03; accepted)
- [x] S03 - Persona schema and neurodiversity safeguards (complete 2026-08-03; accepted)
- [x] S04 - Music parameter ontology and scenario rubric (complete 2026-08-12; accepted)
- [x] S05 - Experiment design and preregistration (complete 2026-08-12; accepted)
- [x] S06 - Repository contracts, schemas, and tests (complete 2026-08-12; accepted)
- [x] S07 - Streamlit navigation and interface shell (complete 2026-08-12; accepted)
- [x] S08 - persistence and synthetic fixtures (complete 2026-08-20; accepted - executed against PostgreSQL per D015; repository init/persona seed/trial persistence verified by 7 repository tests incl. DB-enforced synthetic-only guard; evidence/S08/check_outputs.txt)
- [x] S09 - Deterministic reference simulator (complete 2026-08-20; accepted - 154 simulator tests over the full 75-cell matrix prove reproducibility, bounds, complete time stages, and flag conditions; docs/deterministic_model.md states the fictional non-clinical nature; evidence/S09/check_outputs.txt)
- [x] S10 - OpenAI Responses API and structured outputs (complete 2026-08-20; accepted - Responses API with store=False, json-object format + strict Pydantic validation boundary with sanitizer and one retry; no-key default preserved; 6 mocked tests, no live calls in tests; one live call verified manually; evidence/S10/check_outputs.txt)
- [x] S11 - Persona generation and validation (complete 2026-08-20; accepted - AI drafting with schema/diversity/human-review gates, hard lint flags block saves, near-duplicate needs confirmation, existing IDs never overwritten; 12 tests, live draft verified unsaved; evidence/S11/check_outputs.txt)
- [x] S12 - Reaction simulation and temporal sequence (complete 2026-08-20; accepted - schema-enforced start/middle/end sequence, ai_trial provenance helper, uncertainty/safety/sequence visible in trial UI, refused AI output never persisted; 6 workflow tests + AppTest end-to-end; evidence/S12/check_outputs.txt)
- [x] S13 - Trial workflow, audit trail, and provenance (complete 2026-08-20; accepted - filterable audit trail + provenance inspection in UI, labeled CSV/JSON export (synthetic + limitations on every row), duplicate IDs rejected without overwrite, incomplete records impossible; 7 tests; evidence/S13/check_outputs.txt)
- [x] S14 - Dashboard I: heatmap and comparisons (complete 2026-08-20; accepted - stored-trial heatmap (never imputed), same-music/different-persona comparisons with n_trials + engine labels, empty states + per-chart non-clinical captions; 5 analytics tests + AppTest; evidence/S14/check_outputs.txt)
- [x] S15 - Dashboard II: radar, time series, and summaries (complete 2026-08-20; accepted - six-dimension radar profile (calm/engagement/mood/regulation/attention/stability), temporal stage means, descriptive rankings with n_trials + engines, per-trial uncertainty notes, PNG camera icon + CSV data export; chart guide in docs/chart_interpretation.md; 4 new analytics tests + title-language guard; AppTest verified; evidence/S15/check_outputs.txt)
- [x] S16 - Batch experiment runner and trial matrix (complete 2026-08-21; accepted - `scripts/run_batch.py` runs the frozen 75-cell matrix from `config/trial_matrix.csv` (single source of truth), validates matrix+completeness (missing/duplicate/extra cells fail), exports an immutable synthetic-labeled run bundle (trials.csv/json + manifest with matrix sha256 and findings: null) under data/local/batch_runs/; optional `--ai-subset N` (key-gated, live-verified 1 cell via Ark); 14 new tests; official run: 75/75 cells; evidence/S16/check_outputs.txt)
- [x] S17 - Analysis, limitations, and research report (complete 2026-08-21; accepted 2026-08-30 - docs/analysis_notebook.md (full 75-cell table, persona/scenario/variant summaries, H1-H4 probes, 0 safety flags, engine stability incl. 5 matched AI cells + 3-sample same-cell variance probe), docs/limitations.md (persona validity, model dependence incl. 3-provider history, prompt sensitivity, no human participants + coverage limits), docs/ResearchReport.md (separates 4A software behavior from 4B model content); new AI comparison bundle ai-comparison-20260821 (75 det + 5 AI via qwen3.8-max); evidence/S17/check_outputs.txt)
- [x] S18 - Deployment, demo, portfolio, and release audit (complete 2026-08-30; accepted 2026-08-30 - DB hardening per Engineering Notes: `src/ai_music_therapy/db.py` (ConnectionFactory, PooledConnectionManager with psycopg_pool min1/max8/checkout 10s/lifetime 1800s, transaction wrapper, run() with 3-attempt exponential-backoff retry on OperationalError, process-wide get_manager registry + atexit close), repository refactored onto manager.run, 7 new pool tests incl. 8-user simulated deployment (32/32 ops through max_size=4); dashboard migrated off deprecated use_container_width to width="stretch"; requirements.txt prepared for Streamlit Cloud (-e ., psycopg[binary,pool]); docs/DeploymentRunbook.md + DemoScript.md + PortfolioGuide.md written; DeploymentGuide hardening prerequisite marked done; release scans pass (secrets/private data/claims/synthetic labels); clean checkout verified deterministic; cloud deployment itself NOT executed (needs student accounts); evidence/S18/check_outputs.txt)
- [ ] S19 - Ad-hoc entrances: staged review and approved track/persona libraries (implemented 2026-09-06, pending acceptance; 47 new tests, suite 281 green, evidence/S19/check_outputs.txt; prompt at prompts/Session_19_Adhoc_Entrances_Track_Persona_Libraries.md)

## Known Issues
- None blocking. Non-blocking observations recorded during audit:
  - Persistence is PostgreSQL as of 2026-08-19 (between-session infra unit; D015): local DB via `docker compose up -d` (Colima/QEMU VM; daemon proxy configured inside the VM - see EnvironmentRecord notes). If the Colima VM is deleted (`colima delete`), re-apply the docker daemon proxy before pulling images.
  - `config/app_config.toml` is reference/documentation only; the runtime reads configuration from environment variables only (`config.py`). Values are currently consistent but the TOML could drift. Flagged for a future unit; no action required for the audit.
  - The optional AI-mode default model id `gpt-5.6-terra` is a placeholder overridable via `OPENAI_MODEL`; confirm/replace with a valid model id before enabling AI mode.
  - Setup note (resolved): the system `python3` is 3.9.6, below `requires-python = ">=3.11"`. A `.venv` was created from Python 3.13.14 (conda env `vibe-ash`) and the package installed successfully. Future setups must use a Python 3.11+ interpreter.
  - Pre-existing lint (RESOLVED at S06): `ruff check src tests scripts` was 26 errors on the starter baseline; S06 fixed all of them and the gate is now green. Remaining follow-up: make `scripts/run_batch_demo.py` read `config/trial_matrix.csv` in S16 so the runner shares the matrix's single source of truth.
  - AI mode not yet functional with GLM (verified 2026-08-12): the user's `.env.local` sets `OPENAI_MODEL=glm-5.2` + `OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions` + a real key. A live probe returned 404 `path: /v4/chat/completions/responses`. Two causes for S10 to resolve: (a) `src/ai_music_therapy/ai_client.py` uses the OpenAI **Responses API** (`client.responses.parse`), which GLM's compatibility layer does not support (it exposes `/chat/completions`); (b) `OPENAI_BASE_URL` should be the API root (`https://open.bigmodel.cn/api/paas/v4`) without the `/chat/completions` suffix. Deterministic mode (default) is unaffected.

## Last Test Evidence
- Unit: S19 (Ad-hoc Entrances: Staged Review and Approved Track/Persona Libraries).
- pytest: 281 passed / 0 failed / 0 errors / 0 skipped (junit XML; 234 baseline + 15 track-library + 19 audio-analysis + 13 entrance-UI AppTest). Note: this environment swallows pytest's final console count line (pre-existing, unrelated to S19), so junit is the authoritative count. ruff check src tests scripts: All checks passed! Smoke test: PASS. `git diff --check`: clean.
- Persistence boundary verified by tests: raw audio never persisted (proposal carries extraction + sha256 only); review confirmation trials never saved (list_trials empty after in-memory trial); duplicate track_id refused as write-once violation; `tracks` table CHECK (synthetic = 1) guard; invalid state-machine jumps refused; existing persona IDs never overwritten.
- Deterministic no-key path: full suite + smoke ran with no OPENAI_API_KEY; clean checkout (fresh tree copy, fresh Python 3.13 venv, `pip install -e ".[dev]"`, no key, no .env.local) passed smoke + 281/281.
- Release scans: secrets (none beyond intentional local docker test-DB defaults), clinical claims (none in new sources), synthetic labels (present on both entrances and in confirm_trial output), audio files committed (none; fixtures are generated in-memory signals), frozen artifacts (trial_matrix.csv, preregistration, bundles, ontology: untouched).
- Raw output: `evidence/S19/check_outputs.txt`.

## Decisions
- Prepared-starter route; INIT must not be rerun.
- Deterministic mode is the default and requires no API key.
- AI mode is optional, uses environment configuration, and stores no API response by default.
- A single functioning-level label is excluded; support profiles are multidimensional.
- Audit environment: project runs under a Python 3.11+ `.venv` (system python 3.9.6 is too old); added `*.egg-info/` to `.gitignore` to keep build artifacts out of version control (see D006).
- S01 scope freeze (see D007): research question, user-visible disclaimer, in-scope deliverables, exclusions, and success criteria are frozen in `docs/AuthoritativePlan.md`, `docs/ResearchEthics.md`, and `README.md`; later units implement against this fixed boundary.
- S02 evidence base (see D008): 8 real sources logged in `docs/evidence_table.csv`; 8 background claims mapped in `docs/claim_ledger.md`; non-systematic search log added to `docs/LiteratureReviewProtocol.md`; unverified figures marked "verify before public release".
- S03 persona schema (see D009): `SupportProfile` (communication/sensory/routine/social) replaces the loose dict; `extra="forbid"` + non-empty fields enforce multidimensional support and reject a functioning-level label; `docs/persona_design.md` documents safeguards and representation limits.
- S04 music ontology (see D010): `config/music_ontology.json` declares the controlled vocabulary + 5 non-clinical scenario rubrics/stop-conditions; a test keeps the JSON in sync with the Pydantic schema; `docs/scenario_rubric.md` is the human-readable spec.
- S05 preregistration (see D011): 75-cell 5×5×3 matrix frozen in `config/trial_matrix.csv`; non-clinical hypotheses, variables, and exclusion rules in `docs/preregistration.md`; descriptive analysis plan in `docs/analysis_plan.md`. A future unit (S06/S16) should add a guard test so the batch runner cannot drift from the matrix.
- S06 contracts/CI/tests (see D012): fixed all 26 ruff errors; added `extra="forbid"` to TimeStage/ReactionOutput/TrialRecord; extended smoke_test to cover the deterministic loop + matrix; CI forces `AI_MUSIC_APP_MODE=deterministic`; added 4 tests (matrix contract, extra-field rejection, trial round-trip, ai-client no-key). The matrix is now guarded as a contract; S16 should make the batch runner read it.
- S07 UI shell (see D013): multipage navigation with a global sidebar disclaimer on every page; Home landing with the frozen disclaimer; disclaimer on the trial results surface + safety_flags; empty states on all pages (AppTest-verified). No new analytics/AI; pre-existing trial/dashboard logic preserved for S13/S14.

## Next Unit Preparation
S19 is implemented and pending acceptance (2026-09-06; extension beyond the S01-S18 plan, requested and scoped by the student). After S19 acceptance, the student runs the cloud go-live steps (DeploymentRunbook Parts C/D, Streamlit Community Cloud + Neon) in an offline session. No further unit is prepared; do not begin anything without a new written prompt.
## Engineering Notes
- [x] S18 deployment hardening (DONE locally 2026-08-30, D027; `src/ai_music_therapy/db.py` + `tests/test_connection_pool.py`, incl. multi-user simulated deployment test): replace fresh per-operation DB connections with a pooled connection manager before any concurrent multi-user Neon/PostgreSQL deployment. Order of work: (a) connection factory; (b) pooled engine / connection manager (e.g. psycopg_pool); (c) transaction wrapper; (d) retry + timeout handling; (e) deployment test with multiple simulated users. Local single-user demo use is acceptable as-is (D017 limitation).
- [ ] Future control-doc edits: avoid literal matching on prose lines containing Unicode punctuation (em dashes etc.); use stable dash-free anchors, headings, IDs, regex, or structured markers instead.
