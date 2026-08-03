import json
from pathlib import Path

from ai_music_therapy.models import Persona


def test_public_personas_validate_and_are_synthetic():
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    personas = [Persona.model_validate(item) for item in payload]
    assert len(personas) == 5
    assert all(p.synthetic is True for p in personas)
    assert all(not hasattr(p, "functioning_level") for p in personas)
