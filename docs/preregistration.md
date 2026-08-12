# Preregistration — Synthetic Trial Design

- Status: **Frozen (preregistered) on 2026-08-12, before any trials are run.**
- Scope: the deterministic, 5 × 5 × 3 synthetic trial matrix (75 cells). The optional OpenAI engine is an exploratory path outside this preregistered design.
- Non-clinical: this is a software/methods study of model behavior under controlled synthetic inputs. It is not research on autistic people and cannot support clinical, diagnostic, or therapeutic claims.

## Research question (frozen at S01)

See `docs/AuthoritativePlan.md`. In short: how do synthetic multidimensional autistic-persona profiles and configured music parameters produce differing **synthetic response hypotheses** under a deterministic engine, and what does variation across a fixed 5 × 5 × 3 matrix reveal about software behavior and prompt/model sensitivity — without any clinical claim?

## Design

- Fully-crossed within-simulator design: **5 personas × 5 scenarios × 3 music variants = 75 design cells**, one deterministic trial per cell.
- Personas: the five fictional profiles in `data/public/synthetic_personas.json` (P-LILY, P-MAX, P-EMMA, P-RYAN, P-ZOE), all synthetic.
- Scenarios: `sleep_support`, `anxiety_support`, `focus_support`, `engagement_support`, `regulation_support` (see `docs/scenario_rubric.md`).
- Music variants (V1–V3): the three `MusicParameters` configurations listed below; identical to those in `scripts/run_batch_demo.py` and declared in `config/trial_matrix.csv`.
- Reproducibility: the deterministic engine derives a stable seed from persona + scene + music, so each cell's output is reproducible. The same matrix is run unchanged in S16.

| Variant | genre | bpm | volume | instrument | tonality | duration_sec | lyrics |
|---|---|---|---|---|---|---|---|
| V1 | instrumental | 54 | low | piano | major | 180 | none |
| V2 | instrumental | 82 | medium | percussion | major | 180 | none |
| V3 | nature | 64 | low | mixed | atonal | 180 | none |

The frozen cell list is `config/trial_matrix.csv` (exactly 75 rows).

## Software hypotheses (non-clinical)

These are hypotheses about **simulated/software behavior**, not predictions about real people.

- **H1 (sensory × volume/tonality):** Simulated anxiety is expected to be higher for personas with high auditory sensitivity under the higher-volume (V2) and atonal (V3) variants than under the low-volume piano variant (V1).
- **H2 (sensory-seeking × tempo/instrument):** Simulated engagement is expected to be higher for sensory-seeking personas under the moderate-tempo percussion variant (V2) than under the slow piano variant (V1).
- **H3 (scenario differentiation):** The descriptive composite score is expected to differ across scenarios and variants, demonstrating software/prompt sensitivity rather than a uniform output.
- **H4 (regulation/recovery):** In `regulation_support`, simulated regulation is expected to track lower anxiety and higher mood across the start/middle/end stages.

These are exploratory descriptive expectations about constructed scores; they are not confirmatory and cannot establish effectiveness.

## Variables

- **Independent (manipulated):** persona (5), scenario (5), music variant (3). These define the 75 cells.
- **Dependent (outcome):** the `ReactionOutput` dimensions — `anxiety_level`, `engagement_level`, `mood_score`, `regulation_score`, `attention_duration_sec` — and the researcher-defined `composite_score` (see `docs/analysis_plan.md`).
- **Controlled (held constant):** engine = deterministic; `duration_sec` = 180 for all variants; `lyrics_language` = none; `prompt_version` fixed; no API key (deterministic mode).
- **Provenance (recorded per trial):** trial id, persona id, scenario, full music parameters, full reaction object, engine, model name (n/a in deterministic), prompt version, seed, UTC timestamp, and the fixed synthetic disclaimer.

## Exclusion and reporting rules (frozen before S16)

1. **Validation gate.** Any reaction that fails `ReactionOutput` validation is rejected and not counted; the cell is flagged for re-run, not silently dropped.
2. **No directional exclusion.** No trial is excluded for an "undesirable" direction. All 75 cells are reported.
3. **Distress flags are reported, not hidden.** Trials whose simulated `anxiety_level >= 8` (or `volume == high`) carry a safety flag; they are reported with stop-condition language and are not framed as "favorable."
4. **AI-mode outputs (if ever used) are non-preregistered** and must be labelled exploratory; a structured-output validation failure is rejected.

## Non-clinical statement

All cells, outputs, and summaries are synthetic. The design tests software behavior and prompt sensitivity. It does not diagnose, predict a real child's response, recommend treatment, or establish therapeutic effectiveness.

## Limitations

- Five fictional personas cannot represent the autistic population; patterns are design artifacts.
- The deterministic engine is a constructed rule-based reference, not a validated model of response.
- The matrix varies a narrow set of musical factors; many real variables are absent.
- The optional AI engine path is out of scope for this preregistration.
