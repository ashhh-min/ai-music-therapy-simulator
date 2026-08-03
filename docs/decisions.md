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
