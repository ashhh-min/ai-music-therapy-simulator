from __future__ import annotations

import json
from pathlib import Path

from .config import settings
from .models import Persona
from .repository import Repository


def main() -> None:
    source = Path("data/public/synthetic_personas.json")
    payload = json.loads(source.read_text(encoding="utf-8"))
    repo = Repository(settings.database_url)
    repo.initialize()
    for item in payload:
        repo.upsert_persona(Persona.model_validate(item))
    host = settings.database_url.rsplit("@", 1)[-1]
    print(f"Seeded {len(payload)} synthetic personas into PostgreSQL ({host})")


if __name__ == "__main__":
    main()
