# Analysis Plan — Synthetic Trial Matrix

- Status: **Frozen on 2026-08-12, before trials are run (S16).**
- Companion to `docs/preregistration.md`. Applies to the 75-cell deterministic matrix in `config/trial_matrix.csv`.
- Non-clinical: this plan produces **descriptive summaries of synthetic outputs**. It does not perform confirmatory inference and makes no causal or clinical claim.

## Analysis posture

Descriptive only. We summarize and compare constructed synthetic scores across the design cells to illustrate software behavior and prompt/model sensitivity. Any numeric pattern is an artifact of the synthetic personas, the music ontology, and the deterministic rules — not evidence about real people.

## Primary descriptive measure

- **`composite_score`** (researcher-defined, bounded 0–1): a weighted combination of inverted simulated anxiety (0.35), engagement (0.30), mood (0.20), and regulation (0.15), as implemented in `src/ai_music_therapy/analytics.py`. Higher means a more favorable *simulated* pattern, not a better outcome for any real child.

## Secondary measures

Per-dimension `ReactionOutput` fields: `anxiety_level`, `engagement_level`, `mood_score`, `regulation_score` (each 1–10) and `attention_duration_sec` (0–1800); plus the start/middle/end stage trajectories in `time_series`.

## Summaries and comparisons

- **By cell:** one deterministic result per cell; report all 75.
- **By persona (across scenarios/variants):** mean composite and per-dimension profiles.
- **By scenario (across personas/variants):** mean composite per scenario, against each scenario's rubric (`docs/scenario_rubric.md`).
- **By music variant (V1/V2/V3):** compare composite and per-dimension outcomes to probe H1–H3.
- **Stage trajectories:** start/middle/end anxiety and engagement per cell, to probe H4.

## Visualization (descriptive, all labelled synthetic)

- Heatmap of composite score over persona × scenario.
- Variant comparison (composite and per-dimension) across personas.
- Radar of per-dimension profiles per persona.
- Time-series of stage trajectories.
- (Implemented in the dashboard units S14/S15. Every figure/table carries a synthetic label and provenance.)

## What this plan does NOT do

- No inferential tests (no p-values, confidence intervals, or effect-size tests) interpreted as clinical effects.
- No causal claims about music "causing" outcomes.
- No conversion of composite or dimension scores into clinical, diagnostic, or therapeutic statements.
- No generalization beyond the five fictional personas.

## Exclusion and robustness handling

- Apply the preregistration exclusion/reporting rules (`docs/preregistration.md`): reject validation failures; report all 75 cells; surface distress safety flags with stop-condition language rather than excluding them.
- **Reproducibility check:** re-running a cell yields identical output and seed (deterministic); report the seed with each trial.
- **Missing/empty data:** if a cell is missing or a dataset is empty, show a clear empty state and do not fabricate values.

## Reporting

Every table and figure is labelled synthetic. Outputs include provenance (engine, prompt version, seed, timestamp, disclaimer). The final research report (S17) states observed software behavior separately from any model-generated content and records the limitations above.
