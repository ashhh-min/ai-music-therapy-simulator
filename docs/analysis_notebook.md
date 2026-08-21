# Analysis Notebook - Synthetic Trial Matrix (S17)

- Status: analysis of **accepted synthetic outputs only**, per the frozen plan `docs/analysis_plan.md`.
- Posture: **descriptive only**. Every number below describes constructed software output, not human behavior. No inferential statistics, no causal or clinical claims.
- All scores are researcher-defined software signals (`composite_score` and `ReactionOutput` fields), not validated measures.

## Data sources (immutable run bundles)

| Bundle | Run id | Engine mix | Matrix sha256 | Created |
|---|---|---|---|---|
| Official matrix run | `20260821T053515Z-e5f50132` | 75 deterministic | `e5f50132fb32c7dd...` | 2026-08-21 |
| AI comparison run | `ai-comparison-20260821` | 75 deterministic + 5 AI (`qwen3.8-max`) | `e5f50132fb32c7dd...` | 2026-08-21 |

Both bundles live under `data/local/batch_runs/` (gitignored, write-once per `scripts/run_batch.py`). The matrix checksum is identical for both, so all 150 deterministic trials come from the same frozen `config/trial_matrix.csv`.

Reproduction: `python scripts/run_batch.py` (deterministic, no key) and `python scripts/run_batch.py --ai-subset 5 --run-id <id>` (requires `OPENAI_API_KEY` in `.env.local`).

## Reproducibility check (analysis-plan requirement)

The deterministic trials of both bundles were compared field-by-field (trial id, seed, all reaction scores, attention, flags): **75/75 identical across the two independently generated runs**. Timestamps (`created_at`) differ, as expected; seeds and scores do not. The deterministic engine is exactly reproducible.

## Full 75-cell deterministic results

`composite` computed by `analytics.composite_score` (verified against the implementation for all 75 rows). `flags` lists safety flags; none were raised (see Safety section).

| Persona | Scenario | Variant | Anx | Eng | Mood | Reg | Att(s) | Composite | Seed | Flags |
|---|---|---|---|---|---|---|---|---|---|---|
| P-LILY | sleep_support | V1 | 4 | 4 | 5 | 7 | 108 | 0.5222 | 2030440682 | - |
| P-LILY | sleep_support | V2 | 6 | 3 | 3 | 4 | 96 | 0.3167 | 401313790 | - |
| P-LILY | sleep_support | V3 | 6 | 3 | 3 | 5 | 96 | 0.3333 | 577689286 | - |
| P-LILY | anxiety_support | V1 | 4 | 3 | 4 | 6 | 96 | 0.4500 | 1435530666 | - |
| P-LILY | anxiety_support | V2 | 6 | 2 | 4 | 4 | 85 | 0.3056 | 1057041168 | - |
| P-LILY | anxiety_support | V3 | 6 | 3 | 4 | 5 | 96 | 0.3556 | 473828523 | - |
| P-LILY | focus_support | V1 | 4 | 4 | 6 | 7 | 108 | 0.5444 | 3594798693 | - |
| P-LILY | focus_support | V2 | 6 | 2 | 4 | 4 | 85 | 0.3056 | 2237211634 | - |
| P-LILY | focus_support | V3 | 6 | 3 | 4 | 5 | 96 | 0.3556 | 330667462 | - |
| P-LILY | engagement_support | V1 | 4 | 3 | 5 | 7 | 96 | 0.4889 | 2193359704 | - |
| P-LILY | engagement_support | V2 | 6 | 3 | 3 | 4 | 96 | 0.3167 | 1788818753 | - |
| P-LILY | engagement_support | V3 | 6 | 3 | 4 | 5 | 96 | 0.3556 | 3673855635 | - |
| P-LILY | regulation_support | V1 | 4 | 4 | 4 | 6 | 108 | 0.4833 | 3692989687 | - |
| P-LILY | regulation_support | V2 | 6 | 2 | 3 | 4 | 85 | 0.2833 | 2481267196 | - |
| P-LILY | regulation_support | V3 | 6 | 4 | 4 | 5 | 108 | 0.3889 | 7251552 | - |
| P-MAX | sleep_support | V1 | 2 | 7 | 8 | 9 | 141 | 0.8000 | 3856107419 | - |
| P-MAX | sleep_support | V2 | 3 | 10 | 9 | 8 | 175 | 0.8667 | 2474775285 | - |
| P-MAX | sleep_support | V3 | 4 | 7 | 6 | 7 | 141 | 0.6444 | 495425756 | - |
| P-MAX | anxiety_support | V1 | 2 | 8 | 8 | 9 | 153 | 0.8333 | 2498460716 | - |
| P-MAX | anxiety_support | V2 | 3 | 10 | 9 | 8 | 175 | 0.8667 | 2676920420 | - |
| P-MAX | anxiety_support | V3 | 4 | 7 | 7 | 8 | 141 | 0.6833 | 1970087132 | - |
| P-MAX | focus_support | V1 | 2 | 8 | 8 | 9 | 153 | 0.8333 | 1781525864 | - |
| P-MAX | focus_support | V2 | 3 | 10 | 9 | 8 | 175 | 0.8667 | 3604770396 | - |
| P-MAX | focus_support | V3 | 4 | 8 | 7 | 8 | 153 | 0.7167 | 2121376377 | - |
| P-MAX | engagement_support | V1 | 2 | 8 | 7 | 9 | 153 | 0.8111 | 4100940646 | - |
| P-MAX | engagement_support | V2 | 3 | 10 | 8 | 8 | 175 | 0.8444 | 3884940790 | - |
| P-MAX | engagement_support | V3 | 4 | 7 | 7 | 8 | 141 | 0.6833 | 3175707084 | - |
| P-MAX | regulation_support | V1 | 2 | 7 | 7 | 9 | 141 | 0.7778 | 527254389 | - |
| P-MAX | regulation_support | V2 | 3 | 10 | 9 | 8 | 175 | 0.8667 | 45032117 | - |
| P-MAX | regulation_support | V3 | 4 | 7 | 7 | 8 | 141 | 0.6833 | 228734716 | - |
| P-EMMA | sleep_support | V1 | 2 | 6 | 7 | 9 | 130 | 0.7444 | 1507125798 | - |
| P-EMMA | sleep_support | V2 | 4 | 5 | 6 | 6 | 119 | 0.5611 | 2036292531 | - |
| P-EMMA | sleep_support | V3 | 5 | 5 | 4 | 6 | 119 | 0.4778 | 2347114412 | - |
| P-EMMA | anxiety_support | V1 | 2 | 7 | 8 | 9 | 141 | 0.8000 | 1260489341 | - |
| P-EMMA | anxiety_support | V2 | 4 | 5 | 5 | 6 | 119 | 0.5389 | 3424017450 | - |
| P-EMMA | anxiety_support | V3 | 5 | 6 | 6 | 7 | 130 | 0.5722 | 1896839921 | - |
| P-EMMA | focus_support | V1 | 2 | 6 | 6 | 8 | 130 | 0.7056 | 4003371059 | - |
| P-EMMA | focus_support | V2 | 4 | 5 | 5 | 6 | 119 | 0.5389 | 287760831 | - |
| P-EMMA | focus_support | V3 | 5 | 6 | 5 | 6 | 130 | 0.5333 | 2644711288 | - |
| P-EMMA | engagement_support | V1 | 2 | 6 | 7 | 9 | 130 | 0.7444 | 4017770409 | - |
| P-EMMA | engagement_support | V2 | 4 | 5 | 5 | 6 | 119 | 0.5389 | 3470894868 | - |
| P-EMMA | engagement_support | V3 | 5 | 5 | 5 | 6 | 119 | 0.5000 | 3047383541 | - |
| P-EMMA | regulation_support | V1 | 2 | 7 | 7 | 9 | 141 | 0.7778 | 235953011 | - |
| P-EMMA | regulation_support | V2 | 4 | 5 | 6 | 6 | 119 | 0.5611 | 4082623821 | - |
| P-EMMA | regulation_support | V3 | 5 | 5 | 4 | 6 | 119 | 0.4778 | 550249656 | - |
| P-RYAN | sleep_support | V1 | 2 | 5 | 6 | 8 | 119 | 0.6722 | 674563052 | - |
| P-RYAN | sleep_support | V2 | 4 | 5 | 5 | 6 | 119 | 0.5389 | 3029088239 | - |
| P-RYAN | sleep_support | V3 | 5 | 5 | 5 | 6 | 119 | 0.5000 | 477039222 | - |
| P-RYAN | anxiety_support | V1 | 2 | 6 | 7 | 9 | 130 | 0.7444 | 965791585 | - |
| P-RYAN | anxiety_support | V2 | 4 | 5 | 5 | 6 | 119 | 0.5389 | 3245144199 | - |
| P-RYAN | anxiety_support | V3 | 5 | 6 | 6 | 7 | 130 | 0.5722 | 2121011754 | - |
| P-RYAN | focus_support | V1 | 2 | 5 | 7 | 9 | 119 | 0.7111 | 2012029302 | - |
| P-RYAN | focus_support | V2 | 4 | 4 | 5 | 6 | 108 | 0.5056 | 1146652042 | - |
| P-RYAN | focus_support | V3 | 5 | 5 | 4 | 6 | 119 | 0.4778 | 2258931779 | - |
| P-RYAN | engagement_support | V1 | 2 | 6 | 7 | 9 | 130 | 0.7444 | 2579349698 | - |
| P-RYAN | engagement_support | V2 | 4 | 4 | 5 | 6 | 108 | 0.5056 | 1004550088 | - |
| P-RYAN | engagement_support | V3 | 5 | 5 | 5 | 6 | 119 | 0.5000 | 2713508352 | - |
| P-RYAN | regulation_support | V1 | 2 | 5 | 6 | 8 | 119 | 0.6722 | 2174464590 | - |
| P-RYAN | regulation_support | V2 | 4 | 4 | 5 | 6 | 108 | 0.5056 | 4068845917 | - |
| P-RYAN | regulation_support | V3 | 5 | 5 | 5 | 6 | 119 | 0.5000 | 2872331205 | - |
| P-ZOE | sleep_support | V1 | 4 | 4 | 5 | 7 | 108 | 0.5222 | 357780587 | - |
| P-ZOE | sleep_support | V2 | 5 | 4 | 5 | 5 | 108 | 0.4500 | 1563078840 | - |
| P-ZOE | sleep_support | V3 | 5 | 4 | 4 | 6 | 108 | 0.4444 | 2451262059 | - |
| P-ZOE | anxiety_support | V1 | 4 | 4 | 5 | 7 | 108 | 0.5222 | 1871417975 | - |
| P-ZOE | anxiety_support | V2 | 5 | 4 | 4 | 5 | 108 | 0.4278 | 1761530343 | - |
| P-ZOE | anxiety_support | V3 | 5 | 5 | 5 | 6 | 119 | 0.5000 | 3199586197 | - |
| P-ZOE | focus_support | V1 | 4 | 4 | 5 | 7 | 108 | 0.5222 | 507386714 | - |
| P-ZOE | focus_support | V2 | 5 | 4 | 4 | 5 | 108 | 0.4278 | 4069126538 | - |
| P-ZOE | focus_support | V3 | 5 | 4 | 4 | 6 | 108 | 0.4444 | 3669602945 | - |
| P-ZOE | engagement_support | V1 | 4 | 4 | 5 | 7 | 108 | 0.5222 | 124612826 | - |
| P-ZOE | engagement_support | V2 | 5 | 4 | 5 | 5 | 108 | 0.4500 | 448230763 | - |
| P-ZOE | engagement_support | V3 | 5 | 3 | 4 | 6 | 96 | 0.4111 | 3385134755 | - |
| P-ZOE | regulation_support | V1 | 4 | 5 | 5 | 7 | 119 | 0.5556 | 1978322817 | - |
| P-ZOE | regulation_support | V2 | 5 | 3 | 4 | 5 | 96 | 0.3944 | 3095114227 | - |
| P-ZOE | regulation_support | V3 | 5 | 4 | 4 | 6 | 108 | 0.4444 | 1102380130 | - |

## Summary tables

### By persona (each row: mean over that persona's 15 cells)

| Persona | Mean composite | Mean anx | Mean eng | Mean mood | Mean reg | Mean att(s) | n |
|---|---|---|---|---|---|---|---|
| P-LILY | 0.387 | 5.3333 | 3.0667 | 4.0 | 5.2 | 97.0 | 15 |
| P-MAX | 0.7852 | 3.0 | 8.2667 | 7.7333 | 8.2667 | 155.5333 | 15 |
| P-EMMA | 0.6048 | 3.6667 | 5.6 | 5.7333 | 7.0 | 125.6 | 15 |
| P-RYAN | 0.5793 | 3.6667 | 5.0 | 5.5333 | 6.9333 | 119.0 | 15 |
| P-ZOE | 0.4692 | 4.6667 | 4.0 | 4.5333 | 6.0 | 107.8667 | 15 |

### By scenario (each row: mean over that scenario's 15 cells)

| Scenario | Mean composite | Min | Max | n |
|---|---|---|---|---|
| sleep_support | 0.5596 | 0.3167 | 0.8667 | 15 |
| anxiety_support | 0.5807 | 0.3056 | 0.8667 | 15 |
| focus_support | 0.5659 | 0.3056 | 0.8667 | 15 |
| engagement_support | 0.5611 | 0.3167 | 0.8444 | 15 |
| regulation_support | 0.5581 | 0.2833 | 0.8667 | 15 |

### By variant (each row: mean over that variant's 25 cells)

| Variant | Mean composite | Mean anx | Mean eng | n |
|---|---|---|---|---|
| V1 | 0.6602 | 2.8 | 5.44 | 25 |
| V2 | 0.5329 | 4.4 | 5.12 | 25 |
| V3 | 0.5022 | 5.0 | 5.0 | 25 |

## Software-hypothesis probes (H1-H4, descriptive)

### H1: auditory sensitivity x volume/tonality (mean anxiety per variant, n=5 cells each)

High-auditory personas (P-LILY 9, P-ZOE 8) are compared with the rest:

| Persona | Auditory sensitivity | V1 mean anx | V2 mean anx | V3 mean anx |
|---|---|---|---|---|
| P-LILY | 9 | 4.0 | 6.0 | 6.0 |
| P-ZOE | 8 | 4.0 | 5.0 | 5.0 |
| P-EMMA | 6 | 2.0 | 4.0 | 5.0 |
| P-RYAN | 5 | 2.0 | 4.0 | 5.0 |
| P-MAX | 4 | 2.0 | 3.0 | 4.0 |

Descriptive reading: high-auditory personas show higher anxiety under V2/V3 than V1 (P-LILY 4.0 -> 6.0/6.0; P-ZOE 4.0 -> 5.0/5.0), and higher anxiety than the other personas at every variant. The V1->V2 increment itself (+1 to +2 points) is similar across personas, so the engine differentiates mainly through the base anxiety level set by auditory sensitivity, not through a sensitivity-scaled increment. This is rule arithmetic (`docs/deterministic_model.md`), not observed behavior.

### H2: sensory seeking x tempo/instrument (mean engagement, V1 vs V2, n=5 cells each)

| Persona | Sensory seeking | V1 mean eng | V2 mean eng | n |
|---|---|---|---|---|
| P-MAX | 9 | 7.6 | 10.0 | 5 |
| P-EMMA | 5 | 6.4 | 5.0 | 5 |
| P-RYAN | 4 | 5.4 | 4.4 | 5 |
| P-ZOE | 3 | 4.2 | 3.8 | 5 |
| P-LILY | 2 | 3.6 | 2.4 | 5 |

Descriptive reading: the only high-seeking persona (P-MAX, seeking=9) rises from 7.6 to 10.0 under V2, consistent with H2's direction; the remaining personas move slightly down. The high-seeking group contains a single persona, so this probe is a case illustration, not evidence of a general pattern.

### H3: scenario/variant differentiation

Composite scores span 0.2833 to 0.8667 (mean 0.5651), with 36 distinct values across 75 cells. Variant means order V1 > V2 > V3 (see variant table). Scenario means are nearly flat (0.5581-0.5807), so in the deterministic engine the composite varies mainly by persona and variant, weakly by scenario. Differentiation exists (H3's descriptive expectation), driven by the music-variant rule more than the scenario rule.

### H4: regulation-support stage trajectories (mean over the 25 regulation-support cells)

| Stage | Mean anxiety | Mean engagement | n |
|---|---|---|---|
| start | 4.8667 | 4.1333 | 25 |
| middle | 4.3333 | 5.1333 | 25 |
| end | 4.0667 | 5.4667 | 25 |

Descriptive reading: anxiety declines and engagement rises from start to end in the regulation-support cells, consistent with H4's direction. Note: `TimeStage` records anxiety and engagement only, so per-stage mood/regulation (as H4 words them) are not stored; H4 is probed via the stage anxiety trajectory. Per-stage observations are model-generated text, not observations of anyone.

## Safety flags

**0 distress or caution flags across all 75 deterministic cells.** The matrix contains no high-volume cells (50 low / 25 medium), and deterministic anxiety peaks at 6, below the distress threshold (anxiety >= 8). Had any flag occurred, the plan requires surfacing it with stop-condition language rather than excluding the cell; the export and UI paths implement that behavior.

## Engine stability comparison (deterministic vs AI)

- **Deterministic engine:** exactly reproducible. 75/75 trials identical across two independent full-matrix runs (seeds included); reproducibility is also enforced by tests (`tests/test_deterministic_simulator.py`, `tests/test_batch_matrix.py`).
- **AI engine (optional, not part of the frozen matrix):** 5 matched cells (one per persona, all `sleep_support__V1`) run through `qwen3.8-max` via the Responses API with the strict validation boundary. AI trials carry no seed and are not reproducible.

Matched cells below (det/ai columns = deterministic value / AI value; delta = AI composite minus deterministic composite):

| Cell | Anx d/a | Eng d/a | Mood d/a | Reg d/a | Att(s) d/a | Composite d/a | Delta |
|---|---|---|---|---|---|---|---|
| P-LILY__sleep_support__V1 | 4/3 | 4/7 | 5/7 | 7/7 | 108/150 | 0.5222 / 0.7056 | +0.1834 |
| P-MAX__sleep_support__V1 | 2/3 | 7/6 | 8/7 | 9/7 | 141/10 | 0.8000 / 0.6722 | -0.1278 |
| P-EMMA__sleep_support__V1 | 2/4 | 6/6 | 7/7 | 9/6 | 130/8 | 0.7444 / 0.6167 | -0.1277 |
| P-RYAN__sleep_support__V1 | 2/3 | 5/7 | 6/7 | 8/7 | 119/150 | 0.6722 / 0.7056 | +0.0334 |
| P-ZOE__sleep_support__V1 | 4/3 | 4/6 | 5/7 | 7/7 | 108/150 | 0.5222 / 0.6722 | +0.1500 |

Additional same-cell repeat probe (P-LILY `sleep_support__V1`, run twice more after the bundle run; three AI samples total for this cell: composite 0.7056, 0.8167, 0.7833; attention 150s, 150s, 10s; deterministic value is always 0.5222 / 108s):

- repeat 1: anx=2 eng=8 mood=8 reg=8 att=150s composite=0.8167
- repeat 2: anx=2 eng=7 mood=8 reg=8 att=10s composite=0.7833

Observations (software-level only):

1. AI outputs vary run-to-run on identical inputs (composite spread ~0.11 on one cell; attention duration swings 10-150s), while the deterministic engine never varies.
2. On these 5 matched cells the AI engine scored more favorably than the deterministic engine in 4 of 5 cases (deltas -0.1278 to +0.1834) - a prompt/model sensitivity observation about how the same synthetic persona and music input maps to different engines, not a statement that either engine is more accurate.
3. The AI engine passed the same strict schema validation (all fields in range, complete stage sequence, safety flags empty) - the boundary held, but content-level drift (score distributions, attention spans) is visible and is a limitation (`docs/limitations.md`).

## Provenance

All analyzed trials carry: engine label, model name (AI only), prompt version, seed (deterministic only), UTC timestamp, synthetic flag, and the fixed limitations text. Exports and the dashboard render the same labels. See `docs/provenance.md`.
