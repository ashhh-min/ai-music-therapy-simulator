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
Unit code: WORKSPACE_AUDIT
Unit focus: Verify the prepared starter without implementing S01.
Current prompt: `prompts/WORKSPACE_AUDIT.md`

## Acceptance Criteria for Current Unit
- Repository tree and control files are inspected.
- Actual environment versions are recorded without invention.
- Secret/private-data/configuration scans pass or blockers are documented.
- Import smoke test runs; no feature unit is implemented.

## Session Checklist
- [x] INIT - Prepared starter materialized by package generator
- [ ] WORKSPACE_AUDIT - One-time audit
- [ ] S01 - Project scope and claims boundary
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
- None recorded. Replace this line only with truthful issues found during audit or implementation.

## Last Test Evidence
- Package import: Not yet run on the student's machine.
- Unit tests: Not yet run on the student's machine.
- Streamlit UI: Not yet run on the student's machine.
- Manual demo path: Not yet run on the student's machine.

## Decisions
- Prepared-starter route; INIT must not be rerun.
- Deterministic mode is the default and requires no API key.
- AI mode is optional, uses environment configuration, and stores no API response by default.
- A single functioning-level label is excluded; support profiles are multidimensional.

## Next Unit Preparation
After the workspace audit is accepted, activate S01 only. Do not begin S02 or implementation work early.
