# Authoritative Plan

## Baseline preserved

The source proposal defines a closed loop:

1. Create five distinct fictional autism-spectrum personas.
2. Configure music parameters and one of five support scenarios.
3. Generate a simulated response with six quantitative/qualitative dimensions.
4. Compare results in heatmaps, time series, radar charts, and rankings.
5. Run a 5-persona × 5-scenario × 3-variant matrix for 75 synthetic trials.
6. Produce a research report, demo video, GitHub repository, and application narrative.

## Approved refinement

The project remains **AI Music Therapy**, but the implementation is explicitly an educational **neurodiversity simulation lab**, not a clinical simulator. “Real response” language is replaced by “synthetic response hypothesis.” The five named personas remain recognizable, while a single functioning-level label is replaced by multidimensional support profiles.

## Research question (frozen at S01 — 2026-08-03)

> How do explicitly synthetic, multidimensional autistic-persona profiles and configured music parameters produce differing **synthetic response hypotheses** under (a) a deterministic reference engine and (b) an optional OpenAI structured-output engine, and what does the variation across a fixed 5-persona × 5-scenario × 3-variant (75-cell) matrix reveal about software behavior, prompt/model sensitivity, and the boundaries of model-generated content — without supporting any clinical, diagnostic, or therapeutic claim?

This question studies **model and software behavior under controlled synthetic inputs**. It is not research on autistic people and cannot be answered with clinical efficacy claims. The frozen loop it preserves is: **persona → music parameters → synthetic response hypothesis → descriptive analysis**.

## Core deliverables

*Frozen at S01 (2026-08-03) as the in-scope deliverable set.*

- Five validated fictional persona records.
- Music parameter and scenario ontology.
- Deterministic reference simulator.
- Optional OpenAI structured-output simulator.
- SQLite trial provenance and audit trail.
- Streamlit multipage interface.
- Heatmap, comparison, radar/time-series, and descriptive summary views.
- Reproducible 75-run synthetic experiment.
- Research report with evidence boundaries and limitations.
- Five-to-seven-minute demo and public portfolio package.

## Schedule

- 18 core sessions × 60 minutes.
- Separate 3-hour environment and Vibe Coding module.
- 2 contingency hours for software integration and recovery.
- Total guided time: 23 hours.

## Non-negotiable exclusions

*Frozen at S01 (2026-08-03) as the out-of-scope set.*

- No real child records or clinical data.
- No diagnosis, treatment plan, or individual recommendation.
- No claim that model outputs predict real behavior.
- No causal or clinical efficacy claims from synthetic trials.
- No hidden API keys or committed secrets.
- No fabricated citations, test results, screenshots, deployments, or findings.

## Success criteria (frozen at S01 — 2026-08-03)

These are the measurable conditions under which the project is considered complete. Each must hold without making a clinical, diagnostic, or therapeutic claim.

- **Personas:** exactly five fictional personas validate against the schema; every one carries `synthetic = true`; no single functioning-level label is used.
- **Ontology:** music parameters and support scenarios are bounded by validated enums and ranges; five support scenarios are defined.
- **Deterministic engine:** identical inputs yield identical output and a stable seed, and it runs with no API key (the default mode).
- **Optional OpenAI engine:** uses the Responses API with Pydantic structured outputs, `store=False`, an environment-selected model, and a validation gate that rejects any output failing `ReactionOutput`.
- **Provenance:** every persisted trial records trial id, persona id, scenario, full music and reaction objects, engine, model name, prompt version, seed when applicable, UTC timestamp, and the fixed synthetic disclaimer.
- **Interface:** the Streamlit multipage app runs in deterministic mode by default, handles empty and non-empty datasets, and disables AI mode gracefully when no key is present.
- **Experiment:** the batch runner produces exactly 5 × 5 × 3 = 75 unique design cells and is reproducible.
- **Analytics:** heatmap, comparison, radar, time-series, and descriptive summary views render from synthetic data only.
- **Report:** the research report distinguishes observed software behavior from model-generated content and makes no causal or clinical-efficacy claim.
- **Release gate:** `pytest`, `ruff check src tests scripts`, and `python scripts/smoke_test.py` pass; the secret and private-data scan is clean; a 5–7 minute deterministic demo runs end to end.
