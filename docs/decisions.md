# Decision Log

## D001 - Prepared starter route
The repository is already initialized. INIT remains as a reproducible contract but must not be rerun against this folder.

## D002 - Deterministic-first architecture
The no-key deterministic engine is the default so testing, teaching, and demos remain reproducible.

## D003 - Synthetic hypothesis language
All model outputs are described as synthetic hypotheses, not real reactions or clinical predictions.

## D004 - Multidimensional support profiles
The implementation replaces a single functioning-level field with communication, sensory, routine, social, trigger, and support dimensions.

## D005 - Structured-output API boundary
Optional OpenAI calls use the Responses API, Pydantic structured outputs, environment-selected model, and `store=False`.

## D006 - Audit environment and gitignore hygiene (2026-08-03)
The one-time audit confirmed the prepared starter. Runtime environment is a Python 3.11+ `.venv`; the machine's system `python3` (3.9.6) is below `requires-python` and is not used. `*.egg-info/` was added to `.gitignore` so editable-install build artifacts are never committed. Two non-blocking observations were recorded: `config/app_config.toml` is reference-only (runtime uses env vars), and the AI-mode default model `gpt-5.6-terra` is a placeholder to confirm before enabling AI mode.

## D007 - Scope and claims boundary frozen at S01 (2026-08-03)
S01 froze the project boundary in version-controlled documentation so later units implement against a fixed target. The research question, user-visible disclaimer, in-scope deliverables, exclusions, and success criteria are recorded in `docs/AuthoritativePlan.md` and `docs/ResearchEthics.md` and surfaced in `README.md`. The freeze is prose-level only: enforcing the claims boundary and synthetic labelling as code/tests is deferred to a later unit (e.g., S06 contracts/tests or S13 provenance). Deterministic no-key operation is unchanged.

## D008 - Evidence base established at S02 (2026-08-03)
S02 created the traceable evidence base: 8 real sources (NIMH, Cochrane music therapy, Cochrane sound-based interventions, Belmont Report/OHRP, UNESCO AI ethics, ASAN, OpenAI docs, Streamlit docs) logged in `docs/evidence_table.csv`; 8 background claims (C1–C8) mapped to sources in `docs/claim_ledger.md`; and a truthful non-systematic search log added to `docs/LiteratureReviewProtocol.md`. No citation or result was invented: unverified exact figures (sample sizes, effect sizes, certainty ratings, deep-link URLs) are recorded as "verify before public release." The review is student-curated and non-systematic and cannot support clinical claims.

## D009 - Persona schema finalized at S03 (2026-08-03)
S03 finalized the multidimensional persona schema in `src/ai_music_therapy/models.py`: a new `SupportProfile` (communication, sensory, routine, social) replaced the loose `support_profile: dict[str,str]`; `model_config = ConfigDict(extra="forbid")` was added to `Persona`, `SupportProfile`, and `SensoryProfile`; and behavioural lists and key text fields require `min_length=1`. Together these enforce multidimensional support and make a single functioning-level label unconstructible (covered by tests). `docs/persona_design.md` documents the schema, the five-dimension mapping, neurodiversity safeguards, and stereotype/representation limitations. The existing five fictional profiles already satisfy the hardened schema (no data change), and the deterministic simulator (which reads only `persona_id` and `sensory_profile`) is unaffected.
