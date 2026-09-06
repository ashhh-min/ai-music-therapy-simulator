# AI Music Therapy - Neurodiversity Simulation Lab

An evidence-first educational research prototype based on the original **AI Music Therapy** proposal. The system lets a student define synthetic autistic-persona profiles, specify music parameters and support scenarios, run reproducible hypothesis simulations, and analyze the resulting synthetic outputs.

> **User-visible disclaimer (frozen at S01).** This is an educational software prototype. All personas and outputs are fictional and explicitly synthetic. The system generates structured *synthetic response hypotheses* from configured persona profiles and music parameters. Outputs do not predict any real autistic child's response, do not diagnose autism or any other condition, do not recommend or constitute treatment, and do not establish therapeutic effectiveness. Treat every result as a demonstration of software behavior and prompt/model sensitivity, not as clinical evidence.

**Frozen research question (S01):** how do synthetic, multidimensional autistic-persona profiles and configured music parameters produce differing synthetic response hypotheses under a deterministic reference engine and an optional OpenAI structured-output engine, and what does the variation across a fixed 5-persona × 5-scenario × 3-variant (75-cell) matrix reveal about software behavior and prompt/model sensitivity — without any clinical claim? The full frozen scope, deliverables, exclusions, and success criteria are in `docs/AuthoritativePlan.md`.

## Prepared starter route

This repository is already initialized. **Do not run `prompts/INIT_Project_Initialization.md` against this folder.**

1. Create a baseline Git commit.
2. Run the one-time instructions in `prompts/WORKSPACE_AUDIT.md`.
3. Complete exactly one session prompt at a time, beginning with `prompts/Session_01_Project_Scope_and_Claims_Boundary.md`.
4. Preserve `TASKS.md`; never replace it with a new template.
5. Store unit evidence under `evidence/<UnitID>/`.

## Quick start

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
# Start the local PostgreSQL container (requires Docker/Colima):
colima start
docker compose up -d
python -m ai_music_therapy.seed_demo
pytest
streamlit run app.py
```

The app works in **deterministic demo mode** without an API key.

For optional AI mode:

```bash
cp .env.example .env.local
# Add OPENAI_API_KEY (plus OPENAI_MODEL / OPENAI_BASE_URL for a
# Responses-API-compatible provider) locally. Never commit .env files.
```

The code default is `gpt-5.6-terra` (via `OPENAI_MODEL`); any OpenAI
Responses-API-compatible provider works by setting `OPENAI_BASE_URL`. The
project has been exercised live with three providers (GLM, Volcano Ark, and
Aliyun Bailian `qwen3.8-max`); AI output is not reproducible run-to-run and is
always labeled with its model name. Live calls are bounded by an explicit
120-second timeout with no SDK transport retries: a reasoning-model trial
legitimately takes ~1-2 minutes (measured ~95 s against `qwen3.8-max`), and a
stalled provider surfaces as a clear error instead of an endless spinner. The
deterministic engine is instant local computation.

## Results and reports

- Research report: `docs/ResearchReport.md` (descriptive, synthetic-only).
- Analysis record: `docs/analysis_notebook.md` (full 75-cell table, engine comparison).
- Limitations: `docs/limitations.md`.
- Batch experiments: `python scripts/run_batch.py` runs the frozen 75-cell
  matrix and exports immutable, synthetic-labeled run bundles under
  `data/local/batch_runs/` (`--ai-subset N` adds an optional AI comparison).

## Ad-hoc entrances (experimental, S19)

Two extra pages share one staged workflow: **propose -> review (editable) ->
confirmation trial (in-memory only) -> explicit approval -> write-once library
entry**. Nothing is persisted before approval; rejection saves nothing.

- **Propose a Track**: upload a wav / flac / ogg / mp3 file (max 120 MB;
  compressed formats recommended for long tracks). Local
  deterministic DSP (librosa) estimates tempo, volume bucket, duration,
  spectral centroid, and a gated major/minor heuristic; the reviewer edits the
  parameters, optionally runs an unsaved confirmation trial, and only approval
  commits a TrackBase entry: reviewed parameter profile + source-file sha256 +
  extraction provenance. Raw audio is never stored anywhere. Approved tracks
  become selectable as a music source on the trial page.
- **Propose a Persona**: three input modes - JSON upload validated against the
  frozen Persona schema, an optional key-gated AI-assisted draft (reusing the
  S11 pipeline), and a manual form - all passing the same gates: stereotype and
  synthetic-wording hard flags block approval, near-duplicates require explicit
  confirmation, existing persona IDs are never overwritten.

Approved uploads form an explicitly-labelled exploratory cohort; they never
enter the frozen 75-cell matrix or its bundle findings. Both entrances work
with no API key (the AI draft is correctly gated).

## Deployment

- Runbook (local, demo, Streamlit Community Cloud + Neon PostgreSQL):
  `docs/DeploymentRunbook.md`.
- Provider-specific manual guide: `docs/DeploymentGuide_StreamlitCloud_Neon.md`.
- Database access is pooled (bounded connection pool, transaction wrapper,
  retry + timeout) so a multi-user cloud deployment shares a small set of
  connections instead of opening one per operation.

## Demo and portfolio

- 5-7 minute demo that needs no API key: `docs/DemoScript.md`.
- How to present this project (what to show, what to claim, what to avoid):
  `docs/PortfolioGuide.md`.

## Research boundary

- All personas are fictional and explicitly synthetic.
- No real child records, transcripts, diagnoses, names, or therapy notes belong in this repository.
- The app uses multidimensional support profiles, not a single “high/medium/low functioning” label.
- Trial outputs must retain provenance: engine, model, prompt version, timestamp, seed, and limitations.
- Public claims must distinguish observed software behavior from model-generated content.

## Repository map

```text
.
├── app.py
├── README.md
├── TASKS.md
├── STATUS.md
├── SESSION_STATE.md
├── pyproject.toml
├── requirements.txt
├── config/
├── data/public/
├── docs/
├── evidence/
├── prompts/
├── scripts/
├── src/ai_music_therapy/
└── tests/
```

## Main commands

```bash
docker compose up -d   # once per machine session, after `colima start`
python -m ai_music_therapy.seed_demo
python scripts/smoke_test.py
python scripts/run_batch.py            # frozen 75-cell matrix (no key needed)
python scripts/run_batch.py --dry-run  # validate the matrix only
pytest
streamlit run app.py
```

## References used in the project design

- NIMH, Autism Spectrum Disorder overview.
- Cochrane, *Music therapy for autistic people* (2022 review; evidence certainty varies by outcome).
- HHS OHRP, Belmont Report principles.
- UNESCO Recommendation on the Ethics of Artificial Intelligence.
- OpenAI official documentation for the Responses API and Structured Outputs.
- Streamlit official documentation for multipage apps, deployment, and secrets.
