# Portfolio Guide

How to present this project honestly: what it demonstrates, where the
artifacts live, the S01-S18 narrative, and the claims to avoid.

## Positioning

This is an **educational, evidence-first simulator** built to practice
disciplined AI-assisted research engineering - not a clinical tool. The
portfolio story is the discipline itself:

- Bounded claims: a frozen claim ledger (`docs/claim_ledger.md`) separates
  what the literature supports (C1-C6, background only) from what the
  software can show (H1-H4, software hypotheses about the simulator).
- Synthetic by construction: every persona, trial, and export carries an
  explicit synthetic label; the database enforces `CHECK (synthetic = 1)`.
- Reproducibility where possible, honesty where not: the deterministic engine
  is 75/75 reproducible by seed; the AI engine is explicitly
  non-reproducible and labelled with provider, model, and prompt version.
- Audit trail over results: immutable write-once batch bundles, provenance on
  every trial, decisions log (D-numbered), co-build log, and per-unit
  evidence folders.

One-sentence pitch: "A bounded simulation lab that treats an AI-generated
response as data to be governed, validated, and audited - never as evidence
about real children."

## Artifact map

| Artifact | Path | Shows |
|---|---|---|
| App | `app.py` + `src/ai_music_therapy/ui/` | Persona -> music -> synthetic response -> analysis loop; global disclaimer everywhere. |
| Deterministic engine | `src/ai_music_therapy/deterministic_simulator.py`, `docs/deterministic_model.md` | Seeded, clamped rule arithmetic; exact reproducibility. |
| AI engine | `src/ai_music_therapy/ai_client.py` | Responses API + strict Pydantic validation boundary (reject, never clamp), store=False, one retry. |
| Persistence | `src/ai_music_therapy/repository.py` + `db.py` | PostgreSQL persistence behind a pooled connection manager (factory -> pool -> transaction -> retry), sized for multi-user deployment (D027). |
| Batch runner | `scripts/run_batch.py`, `config/trial_matrix.csv` | Frozen 75-cell matrix, validation that names the exact defect, immutable labelled bundles. |
| Analysis | `docs/analysis_notebook.md`, `docs/limitations.md`, `docs/ResearchReport.md` | Descriptive-only analysis separating software behavior (4A) from model-generated content (4B); zero inferential statistics. |
| Governance | `docs/decisions.md`, `docs/CoBuildLog.md`, `docs/DataGovernance.md`, `docs/ResearchEthics.md`, `TASKS.md`, `STATUS.md`, `SESSION_STATE.md` | Decision history (D001-D027), unit-by-unit co-build record, privacy posture, ethics posture. |
| Deployment | `docs/DeploymentRunbook.md`, `docs/DeploymentGuide_StreamlitCloud_Neon.md` | Hardened local stack; cloud checklist prepared, executed only when accounts are available. |
| Demo | `docs/DemoScript.md` | A 5-7 minute offline demo with fallbacks and claims discipline. |

Batch bundles live under gitignored `data/local/batch_runs/`; reference them
by run id and matrix sha256 (recorded in each `manifest.json` and in the
notebook), not by attaching them.

## S01-S18 narrative (one line per unit)

- INIT / WORKSPACE_AUDIT: starter materialized; one-time workspace audit.
- S01: project scope and the clinical claims boundary.
- S02: evidence review protocol and bibliography.
- S03: persona schema and neurodiversity safeguards (five fictional,
  multidimensional, non-stereotyped personas).
- S04: music parameter ontology and scenario rubric.
- S05: experiment design and preregistration (frozen question, H1-H4).
- S06: repository contracts, schemas, and tests.
- S07: Streamlit navigation and interface shell.
- S08: PostgreSQL persistence and synthetic fixtures (D015).
- S09: deterministic reference simulator (154 simulator tests, 75 cells).
- S10: OpenAI Responses API and structured outputs with a strict validation
  boundary.
- S11: AI persona generation gated behind schema/diversity/human review.
- S12: reaction simulation and enforced start/middle/end temporal sequence.
- S13: trial workflow, audit trail, and provenance; labelled exports.
- S14: Dashboard I - heatmap and same-music comparisons (never imputed).
- S15: Dashboard II - radar, temporal stages, rankings, uncertainty notes,
  exports.
- S16: batch runner over the frozen 75-cell matrix; immutable bundles.
- S17: analysis notebook, limitations, research report; 5-cell AI comparison
  with variance probes.
- S18: deployment hardening (pooled connections, transactions, retry,
  multi-user test), deployment/demo/portfolio docs, release audit.

## Talking points

1. "The most interesting result is what we refused to claim." The report
   contains zero p-values and zero efficacy statements by design.
2. Reproducibility split: deterministic engine reproduced 75/75 cells by seed;
   the same AI cell gave composites 0.7056 / 0.8167 / 0.7833 across three
   runs - so engine and model travel with every record.
3. Validation as a boundary: invalid AI output is rejected, never clamped or
   silently repaired; refused outputs are never persisted.
4. Deployment honesty: the pooling layer is implemented and tested (8
   simulated users through a 4-connection pool, all 32 operations green);
   the public cloud deploy is a checklist awaiting student accounts, and the
   docs say so.
5. Limitations as artifacts: `docs/limitations.md` is a first-class deliverable,
   not a footnote - six sections bounding every number the project produces.

## Claims to avoid (never say / never imply)

- Any therapeutic, diagnostic, or predictive claim about real autistic
  children or anyone else.
- That composite scores, rankings, or flags are clinical measures or
  outcomes.
- That the personas represent real people, groups, or prevalence.
- That AI-engine outputs validate the deterministic ones (they are different
  artifacts with different failure modes).
- That the project is "deployed" or "live" before Part C/D of
  `docs/DeploymentRunbook.md` is executed with saved evidence.

If asked "does it work?", the answer is: "It works as specified - a
reproducible, audited simulation pipeline. Whether music-based approaches
help real people is exactly the question this project is not equipped to
answer, and the docs say why."
