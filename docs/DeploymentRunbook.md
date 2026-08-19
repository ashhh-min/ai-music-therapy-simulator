# Deployment Runbook

## Local

1. Create and activate `.venv`.
2. Install with `python -m pip install -e .[dev]`.
3. Run `python -m ai_music_therapy.seed_demo`.
4. Run `pytest`.
5. Run `streamlit run app.py`.

## Streamlit Community Cloud

- Push the reviewed repository to GitHub.
- Use `app.py` as the entry point.
- Keep `requirements.txt` at repository root.
- Set the Python version in Advanced settings.
- Add `OPENAI_API_KEY`, `OPENAI_MODEL`, and mode settings through Streamlit secrets or environment configuration; never commit them.
- Deploy first in deterministic mode and verify the public disclaimer.

## Recovery

- If AI calls fail, switch to deterministic mode.
- If the database is corrupted, back it up (`docker compose exec db pg_dump -U postgres mt_simulator`), recreate the container volume (`docker compose down -v && docker compose up -d`), reseed personas, and rerun accepted synthetic trials only when their design/provenance is available.
- If a unit breaks the demo, reset to the last accepted checkpoint and reapply only the bounded change.
