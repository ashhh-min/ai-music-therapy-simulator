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
Unit code: S06
Unit focus: Repository Contracts, Schemas, and Tests (code + config + tests).
Current prompt: `prompts/Session_06_Repository_Contracts_Schemas_and_Tests.md`
Status: Accepted and committed on 2026-08-12. S07 is the next unit and is NOT yet started; activate it next.
Acceptance evidence: `evidence/S06/summary.md`, `evidence/S06/check_outputs.txt`.
Pre-unit checkpoint: 3b5f14e.

## Acceptance Criteria for Current Unit
- Smoke and unit tests pass without API credentials: YES.
- Schemas reject invalid/unlabelled records (extra=forbid + synthetic enforcement + tests): YES.
- CI does not depend on a live API (`AI_MUSIC_APP_MODE=deterministic`; ai_client guarded): YES.
- ruff now clean (26 pre-existing fixed → 0); smoke + pytest pass (18 passed); `git diff --check` clean.

## Session Checklist
- [x] INIT - Prepared starter materialized by package generator
- [x] WORKSPACE_AUDIT - One-time audit (complete 2026-08-03; accepted)
- [x] S01 - Project scope and claims boundary (complete 2026-08-03; accepted)
- [x] S02 - Evidence review protocol and bibliography (complete 2026-08-03; accepted)
- [x] S03 - Persona schema and neurodiversity safeguards (complete 2026-08-03; accepted)
- [x] S04 - Music parameter ontology and scenario rubric (complete 2026-08-12; accepted)
- [x] S05 - Experiment design and preregistration (complete 2026-08-12; accepted)
- [x] S06 - Repository contracts, schemas, and tests (complete 2026-08-12; accepted)
- [ ] S07 - Streamlit navigation and interface shell
- [ ] S08 - SQLite persistence and synthetic fixtures
- [ ] S09 - Deterministic reference simulator
- [ ] S10 - OpenAI Responses API and structured outputs
- [ ] S11 - Persona generation and validation
- [ ] S12 - Reaction simulation and temporal sequence
- [ ] S13 - Trial workflow, audit trail, and provenance
- [ ] S14 - Dashboard I: heatmap and comparisons
- [ ] S15 - Dashboard II: radar, time series, and summaries
- [ ] S16 - Batch experiment runner and trial matrix
- [ ] S17 - Analysis, limitations, and research report
- [ ] S18 - Deployment, demo, portfolio, and release audit

## Known Issues
- None blocking. Non-blocking observations recorded during audit:
  - `config/app_config.toml` is reference/documentation only; the runtime reads configuration from environment variables only (`config.py`). Values are currently consistent but the TOML could drift. Flagged for a future unit; no action required for the audit.
  - The optional AI-mode default model id `gpt-5.6-terra` is a placeholder overridable via `OPENAI_MODEL`; confirm/replace with a valid model id before enabling AI mode.
  - Setup note (resolved): the system `python3` is 3.9.6, below `requires-python = ">=3.11"`. A `.venv` was created from Python 3.13.14 (conda env `vibe-ash`) and the package installed successfully. Future setups must use a Python 3.11+ interpreter.
  - Pre-existing lint (RESOLVED at S06): `ruff check src tests scripts` was 26 errors on the starter baseline; S06 fixed all of them and the gate is now green. Remaining follow-up: make `scripts/run_batch_demo.py` read `config/trial_matrix.csv` in S16 so the runner shares the matrix's single source of truth.

## Last Test Evidence
- Unit: S06 (code + config + tests: contracts, CI, baseline tests).
- Smoke test (`python scripts/smoke_test.py`): PASS — now also runs one deterministic simulate() and checks the 75-cell matrix.
- pytest: 18 passed (was 14; +4 contract/repository/ai-client tests).
- `ruff check src tests scripts`: **All checks passed!** (0; was 26 pre-existing).
- `git diff --check`: clean.
- Scan: 0 secrets; clinical-claim match is only the guard-test assertion.
- CI no-API: `.env.example` keeps `OPENAI_API_KEY=` empty; CI sets `AI_MUSIC_APP_MODE=deterministic`.
- Raw output: `evidence/S06/check_outputs.txt`.

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

## Next Unit Preparation
After S06 is accepted, activate S07 (Streamlit Navigation and Interface Shell) only. Do not begin S07 or any implementation work early.
