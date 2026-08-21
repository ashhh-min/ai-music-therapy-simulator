# Research Report - Synthetic Music-Therapy Response Simulator

**Standing notice:** everything in this report describes **synthetic software output**. Personas are fictional; scores are researcher-defined software signals. Nothing here is evidence about real people, and nothing here is a clinical, diagnostic, or therapeutic claim. Full analysis record: `docs/analysis_notebook.md`.

## Abstract

This project built and exercised an evidence-first educational simulator that maps explicitly synthetic neurodiversity personas and configured music parameters to synthetic response hypotheses. The frozen 75-cell design (5 personas x 5 scenarios x 3 music variants) was run end-to-end with a seeded deterministic engine (75/75 cells, exactly reproducible, zero safety flags), and an optional AI engine (Aliyun Bailian `qwen3.8-max`, OpenAI Responses API with strict schema validation) was compared on 5 matched cells. Descriptively: simulated anxiety was higher for high-auditory-sensitivity personas under the medium-volume and atonal variants; the single high-sensory-seeking persona's simulated engagement rose under the moderate-tempo percussion variant; composite scores varied substantially by persona and variant while scenario differentiation was weak; and regulation-support cells showed declining simulated anxiety and rising simulated engagement across the start/middle/end stages. The AI engine was not reproducible run-to-run and scored higher than the deterministic engine on 4 of 5 matched cells - a prompt/model sensitivity observation. All of these are properties of the software artifacts, not findings about music therapy or autistic people.

## 1. Background

Music therapy for autistic people has been studied systematically, but the evidence is uncertain across outcomes (Cochrane review, claim C1 in `docs/claim_ledger.md`); sound-based interventions are a distinct evidence base the project does not evaluate (C2); autism is heterogeneous and support needs are multidimensional, so the project refuses single functioning-level labels (C3) and adopts identity-first, non-deficit language (C4). The project's ethics posture (Belmont-derived principles, UNESCO AI-ethics transparency) is voluntary and involves no human subjects (C5, C6). The simulator is therefore positioned as an educational artifact about software behavior and prompt/model sensitivity - not as a therapy evaluation.

## 2. Research question and software hypotheses

Frozen in `docs/preregistration.md` before any trials ran: how do synthetic multidimensional autistic-persona profiles and configured music parameters produce differing **synthetic response hypotheses** under a deterministic engine, and what does variation across a fixed 5 x 5 x 3 matrix reveal about software behavior and prompt/model sensitivity?

Four **software hypotheses** (about simulated behavior, never about people): H1 high-auditory personas show higher simulated anxiety under the higher-volume (V2) and atonal (V3) variants; H2 the high-sensory-seeking persona shows higher simulated engagement under V2 than V1; H3 composite scores differ across scenarios/variants; H4 regulation-support cells show simulated regulation tracking lower anxiety across stages.

## 3. Methods

- **Personas:** five fictional, multidimensional, non-stereotyped profiles (sensory/support profiles, preferences, triggers), all marked synthetic; drafting safeguards and review gates in `docs/persona_design.md`.
- **Design:** frozen 75-cell matrix `config/trial_matrix.csv` (5 personas x 5 scenarios x 3 variants; no high-volume cells), guarded by contract tests.
- **Engines:** (a) seeded deterministic rule engine (`docs/deterministic_model.md`), the default, no API key required; (b) optional AI engine using the OpenAI Responses API with JSON-object output, `store=False`, sanitizer + strict Pydantic validation (reject, never clamp), one retry.
- **Provenance:** every trial records engine, model name, prompt version, seed (deterministic only), UTC timestamp, and the synthetic label; every export row and JSON document carries the synthetic label and fixed limitations text.
- **Run discipline:** `scripts/run_batch.py` validated the matrix, ran all 75 cells, enforced completeness (missing/duplicate/extra cells fail), and exported a write-once, checksum-stamped bundle; a second bundle added the 5-cell AI comparison subset.
- **Analysis posture (frozen in `docs/analysis_plan.md`):** descriptive only - means, ranges, and counts; no inferential statistics; no causal language; empty cells never imputed; safety flags surfaced, not excluded.

## 4. Results

### 4A. Observed software behavior - deterministic engine

All 75 cells ran and passed validation; **0 safety flags** were raised (no high-volume cells exist in the matrix and simulated anxiety peaked at 6). Full 75-row table and summary tables are in `docs/analysis_notebook.md`; headline values:

- Deterministic reproducibility: **75/75 trials identical across two independent full-matrix runs** (seeds included).
- Persona means (composite): P-MAX 0.7852, P-EMMA 0.6048, P-RYAN 0.5793, P-ZOE 0.4692, P-LILY 0.3870.
- Variant means (composite): V1 (low-volume piano) 0.6602 > V2 (medium-volume percussion) 0.5329 > V3 (atonal nature) 0.5022.
- Scenario means are nearly flat (0.5581-0.5807): the engine differentiates by persona and variant, weakly by scenario.

**H1 - supported descriptively.** High-auditory personas (P-LILY sensitivity 9, P-ZOE 8) showed higher simulated anxiety under V2/V3 than V1 (4.0 -> 6.0/6.0 and 4.0 -> 5.0/5.0) and higher anxiety than other personas at every variant. The V1->V2 increment (+1 to +2 points) was similar across personas, so the engine differentiates through the base anxiety level set by auditory sensitivity rather than a sensitivity-scaled increment - an artifact of the rule arithmetic.

**H2 - supported as a single-persona illustration only.** The one high-seeking persona (P-MAX, seeking 9) rose from 7.6 to 10.0 simulated engagement under V2; the other personas moved slightly down. With n=1 high-seeking persona this is a case illustration, not a pattern.

**H3 - supported.** Composites span 0.2833-0.8667 (36 distinct values over 75 cells); variant ordering is consistent (V1 > V2 > V3). Scenario differentiation is weak. Output is not uniform, and where it varies is itself informative about the rule structure.

**H4 - supported descriptively, with a measurement caveat.** Across the 25 regulation-support cells, mean simulated anxiety declined (4.87 -> 4.33 -> 4.07) and engagement rose (4.13 -> 5.13 -> 5.47) from start to end. Per-stage mood/regulation are not stored by the schema, so H4 is probed via the stage anxiety/engagement trajectory.

### 4B. Model-generated content - AI engine (separate by design)

Five matched cells (one per persona, all `sleep_support__V1`) ran through `qwen3.8-max` under the same validation boundary; all passed schema validation (in-range scores, complete stage sequence, no safety flags).

- Composite deltas vs the deterministic engine: -0.1278 to +0.1834; the AI engine scored higher in 4 of 5 cells.
- Repeat probe on one cell (three runs): composite 0.7056 / 0.8167 / 0.7833 and attention 150s / 150s / 10s, versus the deterministic engine's invariable 0.5222 / 108s.

These are observations about how the same synthetic input maps to different engines - a prompt/model sensitivity result. They are **not** evidence that either engine is more realistic or accurate; there is no ground truth.

## 5. Engine stability

The deterministic engine is exactly reproducible (verified across two independent run bundles and by tests). The AI engine is not reproducible run-to-run and drifts in content level (score distributions, attention spans) even while passing strict schema validation. Engine and model labels therefore travel with every trial, and mixed-engine aggregates are avoided or explicitly labeled. Provider dependence is recorded in `docs/limitations.md` (GLM -> Ark -> Bailian during development).

## 6. Limitations

Principal limits (full treatment in `docs/limitations.md`): fictional personas that are not representative; model dependence including non-reproducible AI output and a 3-provider history; prompt sensitivity (prompt versions are recorded because results change with them); **no human participants and no validation against real behavior**; 75-cell coverage with no high-volume cells; no inferential statistics by design; the composite score is a researcher-defined weighting, not an instrument.

## 7. Conclusion

The simulator does what it was preregistered to do: it produces complete, provenance-labeled, exactly-reproducible synthetic response hypotheses across a frozen design, it separates deterministic software behavior from model-generated content, and it demonstrates - honestly and visibly - how outputs depend on persona design, rule constants, prompts, and engine choice. As an educational artifact it illustrates why provenance, preregistration, and claim discipline matter when synthetic profiles are used in software. It does not, and cannot, say anything about whether music therapy helps any real child.

## References

Internal, verifiable sources only (no invented citations): `docs/evidence_table.csv` (8 sources behind claims C1-C8), `docs/claim_ledger.md`, `docs/preregistration.md`, `docs/analysis_plan.md`, `docs/analysis_notebook.md`, `docs/deterministic_model.md`, `docs/ai_boundary.md`, `docs/provenance.md`, `docs/limitations.md`, `docs/chart_interpretation.md`.
