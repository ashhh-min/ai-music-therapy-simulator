# Technical Architecture

## System layers

1. **Streamlit presentation layer**: home, personas, trial form, dashboard, methods/limits.
2. **Domain models**: Pydantic schemas for persona, music, reaction, time stages, and trial provenance.
3. **Simulation engines**:
   - deterministic engine for reproducible no-key operation;
   - optional OpenAI Responses API engine with structured outputs and `store=False`.
4. **Validation boundary**: all AI outputs must validate as `ReactionOutput` before persistence.
5. **Persistence**: PostgreSQL (local: `docker compose` container) stores complete JSON payloads and provenance.
6. **Analytics**: pandas and Plotly generate descriptive synthetic-output views.

## Data flow

`Persona + Music + Scenario -> Engine -> Pydantic Validation -> TrialRecord -> PostgreSQL -> Analytics -> Research Interpretation`

## Failure behavior

- Missing API key: deterministic mode remains available.
- Invalid AI output: reject; do not save partial data.
- Database error: show an error and preserve the input state.
- Empty dataset: useful UI empty state.
- Distress-like synthetic score: display safety flag and stop-condition language.

## Provenance fields

Every trial records: trial ID, persona ID, scenario, full music parameters, full reaction object, engine, model name, prompt version, deterministic seed when applicable, UTC timestamp, and fixed disclaimer.
