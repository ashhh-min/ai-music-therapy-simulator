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
- SQLite version: 3.53.2 (Python `sqlite3` library version) — superseded 2026-08-19: persistence is now PostgreSQL 16.15 (docker container `postgres:16-alpine`), driver psycopg 3.3.4
- Docker toolchain (2026-08-19): Colima 0.10.3 VM (`colima start --vm-type qemu --cpu 2 --memory 4 --dns 1.1.1.1 --dns 8.8.8.8`; the default VZ runtime failed to boot on this Mac), Docker CLI 29.7.2, Docker Compose 5.5.0, qemu (brew) for the QEMU VM type
- Notes on the local Docker setup:
  - The Mac disk was completely full (62 MB free) before install; ~7.5 GB of regenerable caches (colima partial download, conda packages, pnpm/Homebrew/updater caches) were cleared to proceed. Keep several GB free for VM image and container storage.
  - The VM has no working DNS of its own; the docker daemon inside the VM is configured (in `/etc/docker/daemon.json` within the VM) to pull images through the host proxy at `http://192.168.5.2:15236`. This config lives in the VM disk: it survives `colima stop/start` but is lost on `colima delete` and must be re-applied before the next image pull.
  - Postgres runs via `docker compose up -d` (service `db`, port 5432, dev-only credentials `postgres:postgres`, database `mt_simulator`, named volume `mt_pgdata`).
- Baseline Git checkpoint: 1aaf431
- Notes/blockers:
  - No blocker. A project `.venv` was created and the package was installed editable (`pip install -e .[dev]`) successfully using Python 3.13.14.
  - pandas 3.0.5 and plotly 6.9.0 are also installed (analytics/dashboard dependencies).
  - The optional AI mode default model is `gpt-5.6-terra` (overridable via `OPENAI_API_KEY`/`OPENAI_MODEL`); it was not exercised during the audit because deterministic mode is the default and requires no key.
