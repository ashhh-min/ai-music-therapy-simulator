# Project Status

- Package state: Prepared starter, installed editable in a Python 3.13.14 `.venv`
- Active control step: S17 implemented 2026-08-21 (pending mentor acceptance); next unit S18
- Next implementation unit: S18 (Deployment, Demo, Portfolio, and Release Audit) - not yet started; pooled-connection hardening is the prerequisite before Neon (see docs/DeploymentGuide_StreamlitCloud_Neon.md)
- Last accepted checkpoint: see `git log` (S07 + infra committed 2026-08-12; PostgreSQL switch committed 2026-08-19); prior accepted = c87c076 (S06)
- Persistence: PostgreSQL 16 via `docker compose up -d` (Colima/QEMU local VM); repository on psycopg 3; re-seed with `python -m ai_music_therapy.seed_demo`
- Deployment target (chosen 2026-08-19, D016): Streamlit Community Cloud + Neon PostgreSQL; draft manual at docs/DeploymentGuide_StreamlitCloud_Neon.md (not yet executed - S18 will deploy)
- Current blockers: None. AI mode functional (D019): Responses API + store=False on the Volcano Ark endpoint; strict validation boundary; deterministic default unchanged.
- Live API dependency: Optional only (CI explicitly deterministic; AI mode verified live 2026-08-20 with the Ark provider)
- Offline demo path: Available through deterministic mode (smoke + pytest pass; 227 tests; research report + analysis notebook + limitations complete from immutable batch bundles, all descriptive and synthetic-labeled (D026); batch runner executes the frozen 75-cell matrix with no key (D025);
- Credentials: real key lives in gitignored `.env.local`; `.env`/`.env.*` ignored (except `.env.example`); config.py loads `.env.local`
- UI shell: multipage navigation + global disclaimer + empty states (AppTest-verified); see `app.py` and `src/ai_music_therapy/ui/`
- Contracts: extra=forbid on all data models; matrix + ontology guarded by tests; ruff gate green
- Preregistration: 75-cell 5×5×3 matrix in `config/trial_matrix.csv`; rules in `docs/preregistration.md`; plan in `docs/analysis_plan.md`
- Music ontology: `config/music_ontology.json` + `docs/scenario_rubric.md`
- Persona schema: finalized — multidimensional support, no functioning-level label (see `docs/persona_design.md`)
- Evidence base: `docs/evidence_table.csv` (8 sources), `docs/claim_ledger.md` (8 claims)
- Frozen scope: research question, disclaimer, deliverables, exclusions, success criteria (see `docs/AuthoritativePlan.md`, `docs/ResearchEthics.md`, `README.md`)
