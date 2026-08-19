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
cp .env.example .env
# Add OPENAI_API_KEY locally. Never commit .env.
```

Default model configuration is `gpt-5.6-terra`, selected through `OPENAI_MODEL` and replaceable without code changes.

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
python scripts/run_batch_demo.py --output data/local/batch_demo.csv
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
