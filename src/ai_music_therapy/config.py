from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load shared defaults (.env) then a local override (.env.local, gitignored).
# Real credentials belong in .env.local, which is never committed.
load_dotenv()
load_dotenv(".env.local", override=True)


@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("AI_MUSIC_APP_MODE", "deterministic")
    # PostgreSQL connection string. Local default points at the docker compose
    # service; hosted deployments override via DATABASE_URL in .env.local.
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator"
    )
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
    prompt_version: str = os.getenv("AI_MUSIC_PROMPT_VERSION", "2026-08-01.v1")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    # Optional OpenAI-compatible endpoint (e.g. Volcano Ark, GLM). The OpenAI SDK
    # also reads OPENAI_BASE_URL from the environment; this makes the setting
    # explicit and test-injectable.
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL")


settings = Settings()
