import json
from pathlib import Path

from ai_music_therapy.models import Persona
from ai_music_therapy.repository import Repository


def test_repository_round_trip(tmp_path):
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    persona = Persona.model_validate(payload[0])
    repo = Repository(tmp_path / "test.db")
    repo.initialize()
    repo.upsert_persona(persona)
    assert repo.get_persona(persona.persona_id) == persona
