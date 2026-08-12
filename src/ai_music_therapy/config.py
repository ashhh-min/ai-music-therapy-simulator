from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load shared defaults (.env) then a local override (.env.local, gitignored).
# Real credentials belong in .env.local, which is never committed.
load_dotenv()
load_dotenv(".env.local", override=True)


@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("AI_MUSIC_APP_MODE", "deterministic")
    db_path: Path = Path(os.getenv("AI_MUSIC_DB_PATH", "data/local/app.db"))
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
    prompt_version: str = os.getenv("AI_MUSIC_PROMPT_VERSION", "2026-08-01.v1")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()
