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
Unit code: S20
Unit focus: Parameter-to-Max/MSP Patch Generation (the reversed S19 flow).
Current prompt: `prompts/Session_20_Parameter_to_MaxMSP_Patch_Generation.md`
Status: IMPLEMENTED 2026-09-17, pending student acceptance (kicked off by the student's explicit "append new session with these, and kick it off" on 2026-09-06). All implementation-order steps landed on top of checkpoint 93ec99c: spike-verified hand-rolled .maxpat generation (no py2max, anchored on a real Max 9 export), ONE deterministic PatchSpec (seed = sha256 of canonical parameters) driving three synchronized artifacts - downloadable .maxpat, wiring DOT diagram rendered client-side via st.graphviz_chart, local preview WAV (numpy + soundfile, capped 30 s, approximation NOT Max audio) - plus the "Generate a Max Patch" page (manual widgets or approved TrackBase track as parameter source), 25 pure + 3 DB-gated AppTest tests. Gates: full suite 312 passed / 0 failures / 0 errors / 0 skipped via junit (284 baseline + 28 new, PostgreSQL up, DB-gated tests executed), ruff clean, smoke PASS, git diff --check clean, release scans clean (no secrets, no clinical claims, synthetic + Cycling '74 trademark labels present, zero audio/patch binaries committed, frozen artifacts untouched), clean checkout deterministic with no API key and no .env.local (312/312 + smoke PASS). The page persists NOTHING (session state + user-initiated downloads only). Honest boundary: Max-loadability is a MANUAL student step - sample artifacts generated at evidence/S20/synthetic_patch_1ab48c73.maxpat + synthetic_preview_1ab48c73.wav; automated tests cover structural validity and determinism only.
Acceptance evidence: `evidence/S20/check_outputs.txt` (captured 2026-09-17); decision D029 (recorded in `docs/decisions.md`).
Pre-unit checkpoint: 93ec99c.

## Acceptance Criteria for Current Unit
- Same parameters -> byte-identical PatchSpec, .maxpat, DOT, and preview WAV (seed = sha256 of the canonical parameters JSON).
- The .maxpat is valid JSON with the reference Max header shape, unique box ids, every patchline resolving to an existing id, and a closed object whitelist; synthetic + trademark comments embedded.
- All three deliverables present on the page in the student's priority order: downloadable preview WAV, wiring-logic diagram, downloadable .maxpat.
- The page persists nothing: no DB writes (tracks/trials/personas unchanged); artifacts only in session state and user-initiated downloads.
- Manual parameters and an approved TrackBase track both work as parameter sources; frozen matrix, preregistration, and bundles untouched.
- Full suite + ruff + smoke green; clean checkout still deterministic with no key.
- Max-loadability reported honestly as a manual student verification step (sample artifacts in evidence/S20/).
- `TASKS.md`, `STATUS.md`, decisions (D029), co-build log, tests, and evidence agree.

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
- [x] S19 - Ad-hoc entrances: staged review and approved track/persona libraries (implemented and ACCEPTED 2026-09-06 with two same-day review revisions: mp3 + 120 MB cap; bounded AI-client timeout + engine hints; 50 new tests, suite 284 green, evidence/S19/check_outputs.txt; prompt at prompts/Session_19_Adhoc_Entrances_Track_Persona_Libraries.md)
- [ ] S20 - Parameter-to-Max/MSP patch generation (IMPLEMENTED 2026-09-17, pending student acceptance incl. the manual desktop-Max load check; 28 new tests, suite 312 green, evidence/S20/check_outputs.txt; prompt at prompts/Session_20_Parameter_to_MaxMSP_Patch_Generation.md)

## Known Issues
- None blocking. Non-blocking observations recorded during audit:
  - Persistence is PostgreSQL as of 2026-08-19 (between-session infra unit; D015): local DB via `docker compose up -d` (Colima/QEMU VM; daemon proxy configured inside the VM - see EnvironmentRecord notes). If the Colima VM is deleted (`colima delete`), re-apply the docker daemon proxy before pulling images.
  - `config/app_config.toml` is reference/documentation only; the runtime reads configuration from environment variables only (`config.py`). Values are currently consistent but the TOML could drift. Flagged for a future unit; no action required for the audit.
  - The optional AI-mode default model id `gpt-5.6-terra` is a placeholder overridable via `OPENAI_MODEL`; confirm/replace with a valid model id before enabling AI mode.
  - Setup note (resolved): the system `python3` is 3.9.6, below `requires-python = ">=3.11"`. A `.venv` was created from Python 3.13.14 (conda env `vibe-ash`) and the package installed successfully. Future setups must use a Python 3.11+ interpreter.
  - Pre-existing lint (RESOLVED at S06): `ruff check src tests scripts` was 26 errors on the starter baseline; S06 fixed all of them and the gate is now green. Remaining follow-up: make `scripts/run_batch_demo.py` read `config/trial_matrix.csv` in S16 so the runner shares the matrix's single source of truth.
  - AI mode not yet functional with GLM (verified 2026-08-12): the user's `.env.local` sets `OPENAI_MODEL=glm-5.2` + `OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions` + a real key. A live probe returned 404 `path: /v4/chat/completions/responses`. Two causes for S10 to resolve: (a) `src/ai_music_therapy/ai_client.py` uses the OpenAI **Responses API** (`client.responses.parse`), which GLM's compatibility layer does not support (it exposes `/chat/completions`); (b) `OPENAI_BASE_URL` should be the API root (`https://open.bigmodel.cn/api/paas/v4`) without the `/chat/completions` suffix. Deterministic mode (default) is unaffected.

## Last Test Evidence
- Unit: S20 (Parameter-to-Max/MSP Patch Generation).
- pytest: 312 passed / 0 failed / 0 errors / 0 skipped (junit XML; 284 baseline + 25 patch-generation + 3 patch-page AppTest; DB-gated tests ran against mt_simulator_test with zero skips). Console count line swallowed (pre-existing environment quirk); junit authoritative. ruff check src tests scripts: All checks passed! Smoke test: PASS. `git diff --check`: clean.
- Determinism verified: byte-identical spec/.maxpat/preview WAV on rebuild; the student sample artifacts regenerated cross-session with identical seed 1ab48c73 (27 boxes, 31 wires, 17,231-char maxpat, 30.00 s preview @ 22,050 Hz, peak 0.160).
- Persistence boundary verified by AppTest: generate + render leaves tracks/trials empty; the approved-track source records provenance (track:TRK-PATCHUI) without writing anything new.
- Max-loadability: NOT machine-verifiable in this environment (no Max runtime exists here); manual student step, sample patch + WAV at evidence/S20/.
- Release scans: no secrets, no clinical claims, synthetic + Cycling '74 trademark labels present (page, patch comments, README), zero audio/patch binaries committed, frozen artifacts untouched.
- Clean checkout: fresh tree copy, fresh Python 3.13 venv, `pip install -e ".[dev]"`, no OPENAI_API_KEY, no .env.local -> smoke PASS + 312/312.
- Raw output: `evidence/S20/check_outputs.txt`.

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
S20 is IMPLEMENTED and pending student acceptance (kicked off 2026-09-06 by the student's explicit instruction; implementation completed 2026-09-17). The student's manual acceptance step: open evidence/S20/synthetic_patch_1ab48c73.maxpat (or a freshly generated patch from the page) in desktop Max, enable audio, flip the toggle, and confirm the patch plays the mapped material and auto-stops after the mapped bars. The student runs the cloud go-live steps (DeploymentRunbook Parts C/D, Streamlit Community Cloud + Neon) in an offline session. No further unit begins until the student accepts S20 and requests the next one.
## Engineering Notes
- [x] S18 deployment hardening (DONE locally 2026-08-30, D027; `src/ai_music_therapy/db.py` + `tests/test_connection_pool.py`, incl. multi-user simulated deployment test): replace fresh per-operation DB connections with a pooled connection manager before any concurrent multi-user Neon/PostgreSQL deployment. Order of work: (a) connection factory; (b) pooled engine / connection manager (e.g. psycopg_pool); (c) transaction wrapper; (d) retry + timeout handling; (e) deployment test with multiple simulated users. Local single-user demo use is acceptable as-is (D017 limitation).
- [ ] Future control-doc edits: avoid literal matching on prose lines containing Unicode punctuation (em dashes etc.); use stable dash-free anchors, headings, IDs, regex, or structured markers instead.
