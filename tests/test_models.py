import json
from pathlib import Path
from typing import get_args

import pytest
from pydantic import ValidationError

from ai_music_therapy.models import MusicParameters, Persona, SupportProfile, TrialRecord

PERSONAS_PATH = Path("data/public/synthetic_personas.json")
ONTOLOGY_PATH = Path("config/music_ontology.json")


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


# --- Music ontology (S04) -----------------------------------------------------


def _ontology() -> dict:
    return json.loads(ONTOLOGY_PATH.read_text(encoding="utf-8"))


def _literal_values(model: type, field: str) -> set:
    return set(get_args(model.model_fields[field].annotation))


def _valid_music(**overrides) -> MusicParameters:
    base = {
        "genre": "instrumental",
        "bpm": 60,
        "volume": "low",
        "instrument": "piano",
        "tonality": "major",
        "duration_sec": 180,
    }
    base.update(overrides)
    return MusicParameters(**base)


def test_ontology_literal_values_match_model():
    music = _ontology()["music_parameters"]
    for field in ["genre", "volume", "instrument", "tonality", "lyrics_language"]:
        assert set(music[field]["allowed"]) == _literal_values(MusicParameters, field), field


def test_ontology_ranges_match_enforced_bounds():
    music = _ontology()["music_parameters"]
    bpm_min, bpm_max = music["bpm"]["min"], music["bpm"]["max"]
    dur_min, dur_max = music["duration_sec"]["min"], music["duration_sec"]["max"]
    # declared boundaries are accepted by the model
    _valid_music(bpm=bpm_min)
    _valid_music(bpm=bpm_max)
    _valid_music(duration_sec=dur_min)
    _valid_music(duration_sec=dur_max)
    # values just outside the declared range are rejected
    for value in (bpm_min - 1, bpm_max + 1):
        with pytest.raises(ValidationError):
            _valid_music(bpm=value)
    for value in (dur_min - 1, dur_max + 1):
        with pytest.raises(ValidationError):
            _valid_music(duration_sec=value)


def test_ontology_scenarios_match_model_and_have_rubric():
    scenarios = _ontology()["scenarios"]
    assert {s["id"] for s in scenarios} == _literal_values(TrialRecord, "scene")
    assert len(scenarios) == 5
    for s in scenarios:
        assert s.get("rubric"), f"missing rubric for {s['id']}"
        assert s.get("stop_conditions"), f"missing stop_conditions for {s['id']}"
        note = s.get("clinical_note", "")
        assert note and "not" in note.lower(), f"missing non-clinical note for {s['id']}"
        # No rubric may be described as a validated clinical measure.
        for field in ("rubric", "clinical_note"):
            assert "is a validated clinical measure" not in s.get(field, "").lower()


def test_outcome_dimensions_are_declared_non_clinical():
    block = _ontology()["outcome_dimensions"]
    assert "clinical_note" in block
    for dim in block["dimensions"].values():
        lo, hi = dim["range"]
        assert lo < hi
