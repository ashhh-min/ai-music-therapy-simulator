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
Unit code: S04
Unit focus: Music Parameter Ontology and Scenario Rubric (code + data + docs).
Current prompt: `prompts/Session_04_Music_Parameter_Ontology_and_Scenario_Rubric.md`
Status: Accepted and committed on 2026-08-12. S05 is the next unit and is NOT yet started; activate it next.
Acceptance evidence: `evidence/S04/summary.md`, `evidence/S04/check_outputs.txt`.
Pre-unit checkpoint: 2fdf3e3.

## Acceptance Criteria for Current Unit
- Allowed BPM, volume, instrument, tonality, duration, lyrics, and scenario values are explicit (`config/music_ontology.json`, matched to the model by test): YES.
- Each scenario has a software outcome rubric and stop condition (`docs/scenario_rubric.md`): YES.
- No rubric is described as a validated clinical measure (each has a non-clinical note; guard test): YES.
- smoke + pytest pass (14 passed); `git diff --check` clean; ruff unchanged (0 new).

## Session Checklist
- [x] INIT - Prepared starter materialized by package generator
- [x] WORKSPACE_AUDIT - One-time audit (complete 2026-08-03; accepted)
- [x] S01 - Project scope and claims boundary (complete 2026-08-03; accepted)
- [x] S02 - Evidence review protocol and bibliography (complete 2026-08-03; accepted)
- [x] S03 - Persona schema and neurodiversity safeguards (complete 2026-08-03; accepted)
- [x] S04 - Music parameter ontology and scenario rubric (complete 2026-08-12; accepted)
- [ ] S05 - Experiment design and preregistration
- [ ] S06 - Repository contracts, schemas, and tests
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
  - Pre-existing lint (observed at S03): `ruff check src tests scripts` reports 26 errors on the committed starter baseline; S03 introduced 0 of them. The release gate requires ruff to pass, so these should be cleared in a dedicated cleanup/release unit (e.g., S06 or S18).

## Last Test Evidence
- Unit: S04 (code + data + docs: music ontology + rubric).
- Smoke test (`python scripts/smoke_test.py`): PASS — five validated synthetic personas.
- pytest: 14 passed (10 baseline + 4 new ontology-consistency tests).
- `git diff --check`: clean.
- Ontology JSON parses; 5 scenarios; each has rubric + stop_conditions + clinical_note.
- Scan: 0 secrets; clinical-claim matches are only the disclaimer and the guard test (negations).
- ruff: 26 pre-existing errors (unchanged by S04; 0 introduced).
- Raw output: `evidence/S04/check_outputs.txt`.

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

## Next Unit Preparation
After S04 is accepted, activate S05 (Experiment Design and Preregistration) only. Do not begin S05 or any implementation work early.
