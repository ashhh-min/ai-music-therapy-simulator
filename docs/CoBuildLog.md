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
