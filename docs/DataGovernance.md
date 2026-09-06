# Data Governance

## Data classes

### Public synthetic
- Fictional persona fixtures.
- Deterministic demonstration trials.
- Documentation and prompt templates.

### Local generated
- PostgreSQL database (local docker volume; never committed).
- Batch synthetic outputs.
- Screenshots and test evidence.

### Transient uploaded audio (S19 track entrance)
- Audio uploaded through the track entrance exists in memory during extraction only.
- It is never written to disk, temp files, logs, or the database, and is discarded after the parameter profile is extracted.

### Prohibited
- Real child names, ages linked to identity, diagnoses, educational records, health records, therapy notes, voice recordings, photos, private messages, or identifiable transcripts.
- Copyrighted music uploaded without the right to use it (the uploader affirms rights at upload).

## Storage rules

- Public synthetic fixtures may be committed.
- `data/local/`, `.env`, and Streamlit secrets are ignored.
- OpenAI calls set `store=False` in the starter client.
- Never paste private data into a model prompt.

## Ad-hoc upload handling and no-retention rule (S19)

- Uploaded audio: in-memory only. The pipeline keeps at most the extracted feature profile plus the source file's name and sha256 fingerprint; the raw bytes are discarded even before the review stage.
- The database is written only at explicit approval: approved tracks (`tracks` table, write-once, `CHECK (synthetic = 1)`) and approved personas (existing path, never overwriting an existing ID).
- Rejection persists nothing: no entry, no trial, no uploaded content.
- Review-stage confirmation trials are shown in memory and never saved; they check simulator behavior, not any real-world effect.
- Approved uploads are an explicitly-labelled exploratory cohort: they never enter the frozen 75-cell matrix, the preregistration, or immutable bundle findings, and any analysis of them is reported as exploratory.

## Retention

Keep only the minimum synthetic outputs needed for the project. Delete failed or duplicate local runs after acceptance evidence is captured.

## Release gate

Before public release, scan the repository for secrets, personal data, local absolute paths, unlabelled synthetic outputs, and unsupported clinical claims.
