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
Unit code: S01
Unit focus: Project Scope and Claims Boundary (documentation-only freeze).
Current prompt: `prompts/Session_01_Project_Scope_and_Claims_Boundary.md`
Status: Complete on 2026-08-03. Acceptance criteria met; awaiting mentor acceptance. S02 is NOT yet started and must be activated only after acceptance.
Acceptance evidence: `evidence/S01/summary.md`, `evidence/S01/check_outputs.txt`.
Pre-unit checkpoint: 15856bb.

## Acceptance Criteria for Current Unit
- Baseline persona → music → synthetic response → analysis loop remains recognizable.
- Every public claim distinguishes synthetic software behavior from clinical evidence.
- No implementation beyond bounded documentation changes (research question, disclaimer, deliverables, exclusions, success criteria frozen).
- Changed docs validated; baseline checks (smoke + pytest) still pass.

## Session Checklist
- [x] INIT - Prepared starter materialized by package generator
- [x] WORKSPACE_AUDIT - One-time audit (complete 2026-08-03; accepted)
- [x] S01 - Project scope and claims boundary (complete 2026-08-03; awaiting acceptance)
- [ ] S02 - Evidence review protocol and bibliography
- [ ] S03 - Persona schema and neurodiversity safeguards
- [ ] S04 - Music parameter ontology and scenario rubric
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

## Last Test Evidence
- Unit: S01 (documentation-only; no code changed).
- Smoke test (`python scripts/smoke_test.py`): PASS — five validated synthetic personas.
- pytest: 4 passed (baseline preserved).
- `git diff --check`: clean.
- Documentation reference validation: all referenced files exist.
- Claims/secret scan on changed docs: no positive clinical claims, no secrets; synthetic labelling reinforced.
- Raw output: `evidence/S01/check_outputs.txt`.

## Decisions
- Prepared-starter route; INIT must not be rerun.
- Deterministic mode is the default and requires no API key.
- AI mode is optional, uses environment configuration, and stores no API response by default.
- A single functioning-level label is excluded; support profiles are multidimensional.
- Audit environment: project runs under a Python 3.11+ `.venv` (system python 3.9.6 is too old); added `*.egg-info/` to `.gitignore` to keep build artifacts out of version control (see D006).
- S01 scope freeze (see D007): research question, user-visible disclaimer, in-scope deliverables, exclusions, and success criteria are frozen in `docs/AuthoritativePlan.md`, `docs/ResearchEthics.md`, and `README.md`; later units implement against this fixed boundary.

## Next Unit Preparation
After S01 is accepted, activate S02 (Evidence Review Protocol and Bibliography) only. Do not begin S02 or any implementation work early.
