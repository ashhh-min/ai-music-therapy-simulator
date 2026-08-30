# Limitations

This project is an educational, evidence-first **simulator**. Its outputs are synthetic by construction, and the analysis (`docs/analysis_notebook.md`) is descriptive only. The limitations below bound every number and chart the project produces. None of them is a clinical, diagnostic, or therapeutic statement.

## 1. Persona validity

- The five personas are **fictional, researcher-designed profiles** (`data/public/synthetic_personas.json`), built to be multidimensional and non-stereotyped, but they are not derived from real children, clinical records, or population data, and they are **not representative** of the autistic population (see claim C3 in `docs/claim_ledger.md`).
- Persona parameters (sensory profile, support profile, preferences) are design assumptions. Every downstream pattern in the deterministic engine is an artifact of those assumptions plus the rule arithmetic in `docs/deterministic_model.md`.
- With only five personas, any persona-level contrast rests on n=1 or n=2 personas per group (the H2 sensory-seeking probe, for example, has exactly one high-seeking persona).

## 2. Model dependence

- **Deterministic engine:** results are exactly reproducible (same seed, same output), but reproducibility is not validity. The output is rule arithmetic with seeded jitter; a "finding" is a property of the rules, not of music or people.
- **AI engine:** outputs depend on the configured provider and model. The project has used three providers during development (GLM, Volcano Ark, and currently Aliyun Bailian `qwen3.8-max` via the OpenAI Responses API); results are **not comparable across providers** and are not reproducible run-to-run (same cell, three runs: composite 0.7056 / 0.8167 / 0.7833, attention 150s / 150s / 10s - see the notebook's engine comparison).
- On the 5 matched cells, AI composites differed from deterministic composites by -0.1278 to +0.1834 and were higher in 4 of 5 cases. The engines are not interchangeable; engine labels and model names therefore travel with every trial.
- The AI comparison subset is 5 cells (one per persona) plus 2 repeat probes - far too small for any distributional statement.

## 3. Prompt sensitivity

- AI outputs are sensitive to the system prompt, the requested JSON shape, and the scenario rubric wording; the prompt version is recorded per trial (`prompt_version`) precisely because results can change when it changes.
- The strict validation boundary (schema, ranges, complete stage sequence) plus the sanitizer tolerates only neutral shape drift; it rejects invalid content but cannot make model output consistent. Content-level drift (score levels, attention spans) remains visible in the notebook's engine comparison.
- Deterministic outputs are likewise sensitive to the rule constants and weights (e.g. the 0.35/0.30/0.20/0.15 composite weights are researcher choices, not derived from evidence).

## 4. No human participants

- No real children, clinicians, or sessions are involved anywhere in the pipeline. Nothing in the project validates simulated responses against real behavior, and no clinical, diagnostic, or treatment claim is made or implied (see the Belmont-inspired posture in `docs/ResearchEthics.md`).
- The `composite_score` and all per-dimension scores are researcher-defined software signals, not validated instruments; "anxiety" or "engagement" here are named simulation variables, not measurements of those constructs.
- The analysis plan deliberately excludes inferential statistics (no p-values, confidence intervals, or effect sizes interpreted as effects), because there is no sampling process to make inference meaningful.

## 5. Design and coverage limits

- The frozen matrix is 75 cells (5 personas x 5 scenarios x 3 variants) with **no high-volume music cells** (50 low, 25 medium), so the simulator's distress-flag condition (anxiety >= 8) and volume-high caution rule were never exercised by the batch run (0 flags across 75 cells).
- Per-stage records (`TimeStage`) carry anxiety, engagement, and an observation only - per-stage mood/regulation are not stored, so H4 is probed via stage anxiety/engagement alone.
- Deterministic scenario differentiation is weak (scenario mean composites span 0.5581-0.5807); most variation comes from persona and variant.
- AI-mode persona drafting and trials are optional and gated behind human review and API configuration; the default (and CI) path is deterministic.

## 6. Reporting and infrastructure limits

- Evidence and run bundles are local-only (`data/local/`, `evidence/` are gitignored); published artifacts reference them by path and checksum rather than embedding them.
- Provenance is complete (engine, model, prompt version, seed, timestamp, synthetic label), but the AI provider history above means historical AI outputs cannot be regenerated identically by switching `.env.local` back - the provider would also need to be available.
- The dashboard `use_container_width` deprecation (fixed in S18 via `width="stretch"`) and the un-pooled per-operation database connections (fixed in S18 via the pooled connection manager in `src/ai_music_therapy/db.py`, D027) bounded the pre-release stack; both are resolved and verified, and the remaining deployment follow-ups are listed in `docs/DeploymentRunbook.md` Part E.
