# Data Governance

## Data classes

### Public synthetic
- Fictional persona fixtures.
- Deterministic demonstration trials.
- Documentation and prompt templates.

### Local generated
- SQLite database.
- Batch synthetic outputs.
- Screenshots and test evidence.

### Prohibited
- Real child names, ages linked to identity, diagnoses, educational records, health records, therapy notes, voice recordings, photos, private messages, or identifiable transcripts.

## Storage rules

- Public synthetic fixtures may be committed.
- `data/local/`, `.env`, and Streamlit secrets are ignored.
- OpenAI calls set `store=False` in the starter client.
- Never paste private data into a model prompt.

## Retention

Keep only the minimum synthetic outputs needed for the project. Delete failed or duplicate local runs after acceptance evidence is captured.

## Release gate

Before public release, scan the repository for secrets, personal data, local absolute paths, unlabelled synthetic outputs, and unsupported clinical claims.
