# Co-Build Log

For every session, append:

- Unit ID and date.
- Student's intended change.
- AI assistance used.
- Files changed.
- Tests/checks run and actual results.
- Student explanation of one key decision.
- Errors or rejected suggestions.
- Evidence path.
- Mentor acceptance or required revision.

## WORKSPACE_AUDIT — 2026-08-03

- Unit ID and date: WORKSPACE_AUDIT, 2026-08-03.
- Student's intended change: One-time verification of the prepared starter (no feature implementation, no S01).
- AI assistance used: Claude Code (CLI) — read control files, inspected tree, scanned for secrets/private data/config issues, set up the Python environment, and ran the permitted checks.
- Files changed: `docs/EnvironmentRecord.md` (filled with observed versions), `.gitignore` (added `*.egg-info/`), `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D006), and this log. New local evidence under `evidence/WORKSPACE_AUDIT/`.
- Tests/checks run and actual results: package import PASS (8 modules, v0.1.0); `python scripts/smoke_test.py` PASS; TOML/JSON config parse PASS; public fixture validation PASS (5 synthetic personas + 5 labelled demo-trial rows). Secret/private-data/clinical-data scans clean.
- Student explanation of one key decision: Keep all checks within the audit's allow-list (import/smoke/config/fixture) and record only actually observed versions, so the audit stays truthful and does not drift into S01 work.
- Errors or rejected suggestions: None. Non-blocking observations recorded (TOML reference-only; `gpt-5.6-terra` placeholder model; system python 3.9.6 too old -> used Python 3.13.14 venv).
- Evidence path: `evidence/WORKSPACE_AUDIT/audit_report.md`, `evidence/WORKSPACE_AUDIT/check_outputs.txt`.
- Mentor acceptance or required revision: Awaiting mentor acceptance; S01 not started.

## S01 — Project Scope and Claims Boundary — 2026-08-03

- Unit ID and date: S01, 2026-08-03 (documentation-only).
- Student's intended change: Freeze the research question, user-visible disclaimer, in-scope deliverables, exclusions, and success criteria.
- AI assistance used: Claude Code (CLI) — ran prior-state baseline checks, edited three docs, validated references, and re-ran checks.
- Files changed: `docs/AuthoritativePlan.md` (research question + freeze markers + success criteria), `docs/ResearchEthics.md` (canonical user-visible disclaimer), `README.md` (user-visible disclaimer + one-line research question). Control files updated: `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D007), and this log.
- Tests/checks run and actual results: smoke_test PASS; pytest 4 passed (baseline preserved); `git diff --check` clean; doc reference validation all OK; claims/secret scan clean (no positive clinical claims, no secrets; synthetic labelling reinforced).
- Student explanation of one key decision: Freeze scope in version-controlled docs and surface the disclaimer in the README so every later unit implements against a fixed, user-visible boundary.
- Errors or rejected suggestions: None. Limitation noted: the freeze is prose-level; enforcing the claims boundary and synthetic labelling as code/tests is deferred to a later unit (D007).
- Evidence path: `evidence/S01/summary.md`, `evidence/S01/check_outputs.txt`.
- Mentor acceptance or required revision: Awaiting mentor acceptance; S02 not started.

## S02 — Evidence Review Protocol and Bibliography — 2026-08-03

- Unit ID and date: S02, 2026-08-03 (documentation-only).
- Student's intended change: Create the evidence table, literature search log, claim ledger, and minimum authoritative bibliography.
- AI assistance used: Claude Code (CLI) — ran baseline checks, generated the CSV via Python's csv module, wrote the claim ledger, updated the protocol, and validated.
- Files changed: `docs/evidence_table.csv` (new, 8 sources), `docs/claim_ledger.md` (new, 8 claims), `docs/LiteratureReviewProtocol.md` (extraction-table pointer + search log). Control files updated: `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D008), and this log.
- Tests/checks run and actual results: CSV parses (8 sources, required columns non-empty); claim-ledger cross-reference PASS; smoke_test PASS; pytest 4 passed; `git diff --check` clean; no-invention scan PASS (0 secrets, 0 fabricated DOIs/stats, 0 positive clinical claims).
- Student explanation of one key decision: Log only real sources already named in the project references/protocol, and mark unverified figures as "verify before public release" so the no-invention rule is honored literally.
- Errors or rejected suggestions: None. Limitation noted: a non-systematic student review can miss evidence and cannot support clinical claims; exact figures must be verified before public release.
- Evidence path: `evidence/S02/summary.md`, `evidence/S02/check_outputs.txt`.
- Mentor acceptance or required revision: Awaiting mentor acceptance; S03 not started.

## S03 — Persona Schema and Neurodiversity Safeguards — 2026-08-03

- Unit ID and date: S03, 2026-08-03 (code).
- Student's intended change: Finalize the multidimensional persona schema and validate the five fictional profiles without a single functioning-level label.
- AI assistance used: Claude Code (CLI) — checked dependencies, hardened `models.py`, expanded `tests/test_models.py`, wrote `docs/persona_design.md`, ran checks.
- Files changed: `src/ai_music_therapy/models.py` (new `SupportProfile`; `extra="forbid"`; non-empty fields), `tests/test_models.py` (6 new safeguard tests), `docs/persona_design.md` (new). Control files updated: `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D009), and this log. `data/public/synthetic_personas.json` unchanged (already schema-compliant).
- Tests/checks run and actual results: smoke_test PASS; pytest 10 passed (4 baseline + 6 new); test_models.py 7/7; `git diff --check` clean; safeguard spot-check (5 personas, all synthetic, all five dimensions) PASS; secret/clinical-claim scan clean. ruff: 26 pre-existing errors, 0 introduced by S03.
- Student explanation of one key decision: Enforce multidimensionality and reject a functioning-level label at the schema level (`extra="forbid"` + required named dimensions + non-empty fields), so the safeguard is structural and testable rather than relying on convention.
- Errors or rejected suggestions: None. Limitation noted: schema enforces structure, not meaning — stereotype/representation risk remains and is documented.
- Evidence path: `evidence/S03/summary.md`, `evidence/S03/check_outputs.txt`.
- Mentor acceptance or required revision: Accepted; S04 started after resume.

## S04 — Music Parameter Ontology and Scenario Rubric — 2026-08-12

- Unit ID and date: S04, 2026-08-12 (code + data + docs).
- Student's intended change: Define the controlled music parameter vocabulary, five support scenarios, and non-clinical outcome rubric.
- AI assistance used: Claude Code (CLI) — wrote the ontology JSON, added model docstrings, wrote the rubric doc, added consistency tests, ran checks.
- Files changed: `config/music_ontology.json` (new), `docs/scenario_rubric.md` (new), `src/ai_music_therapy/models.py` (docstrings on MusicParameters/ReactionOutput/TrialRecord), `tests/test_models.py` (4 ontology-consistency tests). Control files updated: `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D010), and this log.
- Tests/checks run and actual results: smoke_test PASS; pytest 14 passed (10 baseline + 4 new); `git diff --check` clean; ontology JSON parses with 5 scenarios (each with rubric+stop+clinical_note); secret scan clean; ruff unchanged at 26 (0 introduced).
- Student explanation of one key decision: Make the vocabulary and rubric centralized data in `config/music_ontology.json` and bind it to the Pydantic schema with a consistency test, so the human-readable ontology and the enforced schema cannot drift.
- Errors or rejected suggestions: None. Limitation noted: the ontology is a narrow teaching vocabulary and the rubric reads only simulated signals.
- Evidence path: `evidence/S04/summary.md`, `evidence/S04/check_outputs.txt`.
- Mentor acceptance or required revision: Accepted; S05 started.

## S05 — Experiment Design and Preregistration — 2026-08-12

- Unit ID and date: S05, 2026-08-12 (docs + data).
- Student's intended change: Freeze the 5 × 5 × 3 synthetic trial matrix, hypotheses, variables, analysis plan, and exclusions before running trials.
- AI assistance used: Claude Code (CLI) — generated and validated the 75-cell matrix via Python's csv module; wrote the preregistration and analysis plan; ran checks.
- Files changed: `config/trial_matrix.csv` (new, 75 cells), `docs/preregistration.md` (new), `docs/analysis_plan.md` (new). Control files updated: `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D011), and this log.
- Tests/checks run and actual results: matrix validation PASS (75 cells; personas/scenes match fixtures + model; fully crossed; variants match `scripts/run_batch_demo.py`; schema-valid); smoke_test PASS; pytest 14 passed (baseline preserved); `git diff --check` clean; secret scan 0; clinical-overclaim scan 0.
- Student explanation of one key decision: Make the 3 variants in the matrix identical to those already encoded in the batch runner so the preregistered design and the future S16 run cannot disagree by construction.
- Errors or rejected suggestions: None. Limitation noted: the preregistration is data/prose and not yet enforced by code; a guard test is recommended for S06/S16.
- Evidence path: `evidence/S05/summary.md`, `evidence/S05/check_outputs.txt`.
- Mentor acceptance or required revision: Accepted; S06 started.

## S06 — Repository Contracts, Schemas, and Tests — 2026-08-12

- Unit ID and date: S06, 2026-08-12 (code + config + tests).
- Student's intended change: Strengthen package contracts, validation, CI, and baseline tests without adding UI features.
- AI assistance used: Claude Code (CLI) — fixed ruff, tightened model contracts, extended the smoke test and CI, added tests, ran checks.
- Files changed: `src/ai_music_therapy/{models,deterministic_simulator,repository,ai_client}.py`, `src/ai_music_therapy/ui/{dashboard,personas,trial}.py` (formatting-only), `scripts/{smoke_test,run_batch_demo}.py`, `.github/workflows/ci.yml`, `tests/{test_models,test_repository,test_analytics}.py`, and new `tests/test_ai_client.py`. Control files updated: `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D012), and this log.
- Tests/checks run and actual results: smoke_test PASS (extended); pytest 18 passed (was 14); `ruff check src tests scripts` → All checks passed! (0; was 26 pre-existing); `git diff --check` clean; secret scan 0; CI confirmed API-free.
- Student explanation of one key decision: Add `extra="forbid"` to all data models and a committed trial-matrix contract test so invalid/unlabelled records and any drift from the preregistered matrix are caught automatically rather than by convention.
- Errors or rejected suggestions: None. Follow-up noted: make the batch runner read `config/trial_matrix.csv` in S16 (single source of truth).
- Evidence path: `evidence/S06/summary.md`, `evidence/S06/check_outputs.txt`.
- Mentor acceptance or required revision: Accepted; S07 started.

## S07 — Streamlit Navigation and Interface Shell — 2026-08-12

- Unit ID and date: S07, 2026-08-12 (UI).
- Student's intended change: Implement the multipage Streamlit shell, global disclaimer, empty states, and navigation only.
- AI assistance used: Claude Code (CLI) — rewrote app.py/home.py/methods.py, edited trial.py, verified pages headlessly with streamlit AppTest.
- Files changed: `app.py`, `src/ai_music_therapy/ui/{home,trial,methods}.py`. `personas.py` and `dashboard.py` unchanged (already met empty-state/synthetic criteria; now carry the global sidebar disclaimer). Control files updated: `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` (D013), and this log.
- Tests/checks run and actual results: py_compile OK; ruff All checks passed!; smoke PASS; pytest 18 passed (no regression); headless AppTest — all pages load with no exception, empty states present, disclaimer visible globally + on Home/methods/trial results; git diff --check clean; secret scan 0.
- Student explanation of one key decision: Put the disclaimer in the app.py sidebar so it is global (every page) rather than re-implementing it per page, and verify the shell headlessly with AppTest so "all pages load" is checked, not assumed.
- Errors or rejected suggestions: None. Limitation noted: AppTest is headless and does not exercise real browser interaction or the live AI path; full UI verification is deferred to the S18 manual demo.
- Evidence path: `evidence/S07/summary.md`, `evidence/S07/check_outputs.txt`.
- Mentor acceptance or required revision: Accepted; S08 not started.

## Between sessions — local credentials + AI-mode probe — 2026-08-12

- Unit ID and date: between-session infrastructure/safety work, 2026-08-12 (not a session unit).
- Student's intended change: Use real credentials kept in `.env.local`; ensure it is never committed; broadly check the app before next session.
- AI assistance used: Claude Code (CLI) — gitignore/safety hardening, config + env-example changes, headless + live verification.
- Files changed: `.gitignore` (cover `.env`/`.env.*`, keep `.env.example`), `src/ai_music_therapy/config.py` (load `.env.local` with override), `.env.example` (document `OPENAI_BASE_URL`). Recorded in D014.
- Tests/checks run and actual results: `.env.local` confirmed ignored + untracked + absent from history; smoke + pytest (18) + ruff green; AppTest shell loads; end-to-end deterministic data path works (seed → trial → persist → provenance). Live AI probe returned 404 `…/v4/chat/completions/responses` (see D014): AI mode not yet functional with GLM — deferred to S10.
- Student explanation of one key decision: Keep the secret out of git by ignoring `.env.*`, and make the app read the user's chosen `.env.local` rather than asking them to rename it.
- Errors or rejected suggestions: Did not edit `.env.local` or guess the GLM base URL; did not implement the S10 AI-client fix (out of scope between sessions).
- Evidence path: `evidence/S07/check_outputs.txt` (regression); AI-probe output captured in this log.
- Mentor acceptance or required revision: Infra/safety changes committed; S08 is the next unit.

## Between sessions - SQLite to PostgreSQL switch - 2026-08-19

- Unit ID and date: between-session infrastructure unit, 2026-08-19 (not a session unit; user-directed). Recorded in D015.
- Student's intended change: Switch all persistence from SQLite to PostgreSQL ahead of a planned Vercel deployment; install Docker locally if not ready.
- AI assistance used: Claude Code (CLI) - Docker/Colima installation and troubleshooting, repository rewrite on psycopg 3, tests/CI, docs.
- Environment work actually done: installed Colima 0.10.3 + Docker CLI 29.7.2 + Compose 5.5.0 + qemu via Homebrew; cleared ~7.5 GB of regenerable caches because the Mac disk was 100% full; the default VZ VM failed to boot (empty serial console), so the VM was recreated with `--vm-type qemu`; the VM has no working DNS, so the docker daemon inside the VM was configured to pull images through the host proxy. PostgreSQL 16.15 now runs as `docker compose` service `db` (healthy).
- Files changed: `docker-compose.yml` (new), `src/ai_music_therapy/config.py` (`database_url`), `src/ai_music_therapy/repository.py` (psycopg 3 rewrite, BIGINT seed), `src/ai_music_therapy/seed_demo.py`, `src/ai_music_therapy/ui/{personas,dashboard,trial}.py`, `tests/test_repository.py` (Postgres-backed, skip-with-message when DB down), `.github/workflows/ci.yml` (postgres service), `requirements.txt` + `pyproject.toml` (psycopg[binary]), `.env.example`, `README.md`, docs (Architecture/DataGovernance/DeploymentRunbook/EnvironmentRecord/decisions/this log), `TASKS.md`/`STATUS.md`/`SESSION_STATE.md` notes.
- Tests/checks run and actual results: `pytest` 19 passed (Postgres tests ran live); `ruff check src tests scripts` clean; `scripts/smoke_test.py` PASS; seed into PostgreSQL OK (5 personas); Streamlit AppTest shell loads with disclaimers and no exception.
- Student explanation of one key decision: the repository keeps the exact same tables/constraints/provenance and only the driver changed, so the S08 acceptance criteria still apply unchanged - against PostgreSQL instead of SQLite.
- Errors or rejected suggestions: VZ runtime boot failure (switched to qemu); first `--runtime qemu` attempt used the wrong flag (it selects docker/containerd; the VM type flag is `--vm-type`); disk-full blocked everything until caches were cleared; `seed INTEGER` overflowed in Postgres (now BIGINT).
- Deployment caveat stated to the user: Streamlit cannot run on Vercel serverless; realistic path is Render/Railway/Fly/Streamlit Community Cloud + hosted PostgreSQL (Neon/Supabase/Vercel Postgres). The PostgreSQL switch supports all of these.
- Evidence path: `evidence/infra-postgres/check_outputs.txt`.
- Mentor acceptance or required revision: Pending mentor acceptance; S08 remains the next unit (executed against PostgreSQL).

## S08 - Persistence and synthetic fixtures (PostgreSQL) - 2026-08-20

- Unit ID and date: S08, 2026-08-20. Accepted same day. Checkpoint before unit: 5c9774b.
- Student's intended change: Implement repository initialization, persona seed, trial persistence, and round-trip tests (per the S08 prompt, executed against PostgreSQL per D015).
- AI assistance used: Claude Code (CLI) - baseline verification, four new tests, evidence collection, control-doc updates.
- Files changed: `tests/test_repository.py` (4 new tests: initialize idempotency, seed_demo end-to-end idempotency, DB-enforced synthetic-only guard, provenance preservation in payload_json), `evidence/S08/check_outputs.txt` (new), control docs (`TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` D017, this log). No production code changes were needed - the persistence layer from D015 already satisfied the objective.
- Tests/checks run and actual results: baseline re-run before edits (19 passed); after: `pytest` 23 passed, `ruff check src tests scripts` clean, `scripts/smoke_test.py` PASS, `git diff --check` clean, double `seed_demo` run left exactly 5 personas / 5 distinct ids in `mt_simulator`, `git check-ignore` confirms `data/local/` ignored.
- Student explanation of one key decision: the synthetic-only guarantee is enforced by a database CHECK constraint (`synthetic = 1`), so no code path - present or future - can persist a record that claims to be non-synthetic; the test proves the database rejects it.
- Errors or rejected suggestions: two test-authoring iterations (frozen settings dataclass needed `dataclasses.replace` for the seed test; the provenance test initially expected a `synthetic` key inside `payload_json`, but that is a DB column, not a `TrialRecord` field - the test now checks both correctly). Recurring control-doc edit friction: some lines contain Unicode em dashes that defeat literal string matching; edits now anchor on dash-free substrings.
- Evidence path: `evidence/S08/check_outputs.txt`.
- Mentor acceptance or required revision: Student accepted and approved resumption before the unit; unit complete pending mentor sign-off per workflow. Next unit: S09 (Deterministic Reference Simulator).

## S09 - Deterministic Reference Simulator - 2026-08-20

- Unit ID and date: S09, 2026-08-20. Accepted same day. Checkpoint before unit: 9abc525.
- Student's intended change: Implement a reproducible bounded rule engine for offline testing and demonstration (the engine existed from the starter; this unit verified and documented it).
- AI assistance used: Claude Code (CLI) - matrix-parameterized test suite, model documentation, evidence, control docs.
- Files changed: `tests/test_deterministic_simulator.py` (rewritten: 1 -> 8 test functions / 154 cases), `docs/deterministic_model.md` (new), `evidence/S09/check_outputs.txt` (new), control docs (`TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md` D018, this log). No changes to `src/ai_music_therapy/deterministic_simulator.py`.
- Tests/checks run and actual results: targeted simulator suite 154 passed; full `pytest` 176 passed; `ruff check src tests scripts` clean; `scripts/smoke_test.py` PASS; `git diff --check` clean.
- Student explanation of one key decision: test the engine against the frozen 75-cell preregistered matrix rather than ad-hoc inputs, so the acceptance guarantees (reproducibility, bounds, complete stages) are proven for exactly the cells the experiment will run.
- Errors or rejected suggestions: one test initially assumed the matrix contains high-volume cells; it does not (50 low / 25 medium), so the volume-flag test now constructs its input outside the matrix - a real design fact now recorded in the docs.
- Evidence path: `evidence/S09/check_outputs.txt`.
- Mentor acceptance or required revision: Student accepted and approved resumption before the unit; unit complete pending mentor sign-off per workflow. Next unit: S10 (OpenAI Responses API and Structured Outputs; includes GLM fixes from D014).

## S10 - OpenAI Responses API and Structured Outputs - 2026-08-20

- Unit ID and date: S10, 2026-08-20. Accepted same day. Checkpoint before unit: c230d52.
- Student's intended change: Implement the optional AI client with Pydantic structured output, environment-selected model, no-storage setting, and graceful no-key behavior.
- AI assistance used: Claude Code (CLI) - live provider probing, client redesign, mocked test suite, boundary documentation.
- Files changed: `src/ai_music_therapy/ai_client.py` (rewritten), `src/ai_music_therapy/config.py` (`openai_base_url`), `tests/test_ai_client.py` (1 -> 6 tests), `docs/ai_boundary.md` (new), `.env.example` (provider compatibility note), `evidence/S10/check_outputs.txt` (new), control docs.
- Tests/checks run and actual results: test_ai_client 6 passed (mocked transport; no live calls); full suite 182 passed; ruff clean; smoke PASS; one live end-to-end call via the real client returned a validated ReactionOutput (scores in range, 3 stages, synthetic=True).
- Student explanation of one key decision: keep the strict Pydantic boundary as the source of truth - the model is asked politely for the exact schema, but the system trusts only validation; out-of-range values are rejected rather than clamped, so no invalid AI output can ever be persisted.
- Errors or rejected suggestions: rejected `responses.parse` with `text_format=ReactionOutput` because the provider does not enforce the schema server-side (live probes returned extra fields and type drift, which the strict schema rightly rejected); an early grep accidentally echoed part of the API key into the local session transcript - flagged to the user immediately with a rotate recommendation, never written to any file or commit.
- Evidence path: `evidence/S10/check_outputs.txt`.
- Mentor acceptance or required revision: Student accepted and approved resumption before the unit; unit complete pending mentor sign-off per workflow. Next unit: S11 (Persona Generation and Validation).
