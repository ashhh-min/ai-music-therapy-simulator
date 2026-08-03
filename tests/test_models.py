import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_music_therapy.models import Persona, SupportProfile

PERSONAS_PATH = Path("data/public/synthetic_personas.json")


def _load_personas() -> list[Persona]:
    payload = json.loads(PERSONAS_PATH.read_text(encoding="utf-8"))
    return [Persona.model_validate(item) for item in payload]


def _load_payload() -> list[dict]:
    return json.loads(PERSONAS_PATH.read_text(encoding="utf-8"))


def test_public_personas_validate_and_are_synthetic():
    personas = _load_personas()
    assert len(personas) == 5
    assert all(p.synthetic is True for p in personas)
    assert all(not hasattr(p, "functioning_level") for p in personas)


def test_each_persona_represents_all_five_dimensions():
    # communication, sensory, routine, trigger, support
    for p in _load_personas():
        assert p.support_profile.communication  # communication
        assert p.support_profile.sensory  # sensory (qualitative)
        assert p.sensory_profile.auditory_sensitivity >= 1  # sensory (quantitative)
        assert p.support_profile.routine  # routine
        assert p.communication_modes  # communication modes
        assert p.known_triggers  # trigger
        assert p.preferred_supports  # support


def test_support_profile_requires_routine_dimension():
    with pytest.raises(ValidationError):
        SupportProfile(communication="x", sensory="y", social="z")  # missing routine


def test_functioning_level_field_is_rejected():
    payload = _load_payload()
    payload[0]["functioning_level"] = "high"
    with pytest.raises(ValidationError):
        Persona.model_validate(payload[0])


def test_extra_field_is_rejected():
    payload = _load_payload()
    payload[0]["unexpected_extra"] = "value"
    with pytest.raises(ValidationError):
        Persona.model_validate(payload[0])


def test_empty_dimension_list_is_rejected():
    payload = _load_payload()
    payload[0]["known_triggers"] = []
    with pytest.raises(ValidationError):
        Persona.model_validate(payload[0])


def test_persona_id_must_start_with_prefix():
    payload = _load_payload()
    payload[0]["persona_id"] = "LILY"  # missing P- prefix
    with pytest.raises(ValidationError):
        Persona.model_validate(payload[0])
