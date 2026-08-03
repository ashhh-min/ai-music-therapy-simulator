# Environment Record

Record only values observed on the student's machine.

- Date: 2026-08-03
- Operating system: macOS 15.2 (Darwin 24.2.0)
- Python version: 3.13.14 (project `.venv` created from conda env `vibe-ash`). Note: the system `python3` is 3.9.6, which is below the `requires-python = ">=3.11"` constraint and must not be used.
- pip version: 26.1.2
- Git version: 2.39.5 (Apple Git-154)
- Editor/coding agent: Claude Code (CLI)
- Streamlit version: 1.60.0
- OpenAI Python SDK version: 2.52.0
- Pydantic version: 2.13.4
- SQLite version: 3.53.2 (Python `sqlite3` library version)
- Baseline Git checkpoint: 1aaf431
- Notes/blockers:
  - No blocker. A project `.venv` was created and the package was installed editable (`pip install -e .[dev]`) successfully using Python 3.13.14.
  - pandas 3.0.5 and plotly 6.9.0 are also installed (analytics/dashboard dependencies).
  - The optional AI mode default model is `gpt-5.6-terra` (overridable via `OPENAI_API_KEY`/`OPENAI_MODEL`); it was not exercised during the audit because deterministic mode is the default and requires no key.
