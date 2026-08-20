import csv
import json
from pathlib import Path

import pytest

from ai_music_therapy.deterministic_simulator import simulate, stable_seed
from ai_music_therapy.models import MusicParameters, Persona


def load_persona(persona_id: str) -> Persona:
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    for item in payload:
        if item["persona_id"] == persona_id:
            return Persona.model_validate(item)
    raise KeyError(persona_id)


def load_matrix() -> list[dict]:
    with open("config/trial_matrix.csv", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def music_from_cell(cell: dict) -> MusicParameters:
    return MusicParameters(
        genre=cell["genre"],
        bpm=int(cell["bpm"]),
        volume=cell["volume"],
        instrument=cell["instrument"],
        tonality=cell["tonality"],
        duration_sec=int(cell["duration_sec"]),
        lyrics_language=cell["lyrics_language"],
    )


def test_deterministic_simulator_is_reproducible():
    persona = load_persona("P-LILY")
    music = MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180
    )
    first, seed1 = simulate(persona, music, "sleep_support")
    second, seed2 = simulate(persona, music, "sleep_support")
    assert seed1 == seed2
    assert first == second
    assert first.synthetic is True
    assert len(first.time_series) == 3


@pytest.mark.parametrize("cell", load_matrix(), ids=lambda c: c["cell_id"])
def test_every_matrix_cell_is_bounded_and_complete(cell):
    """All scores stay in range and time stages are complete for all 75 cells."""
    persona = load_persona(cell["persona_id"])
    music = music_from_cell(cell)
    reaction, seed = simulate(persona, music, cell["scene"])

    assert seed == stable_seed(persona.persona_id, cell["scene"], music)
    for score in (
        reaction.anxiety_level,
        reaction.engagement_level,
        reaction.mood_score,
        reaction.regulation_score,
    ):
        assert 1 <= score <= 10
    assert 15 <= reaction.attention_duration_sec <= music.duration_sec

    stages = [s.stage for s in reaction.time_series]
    assert stages == ["start", "middle", "end"]
    for stage in reaction.time_series:
        assert 1 <= stage.anxiety_level <= 10
        assert 1 <= stage.engagement_level <= 10
        assert stage.observation  # non-empty
    assert reaction.synthetic is True
    assert reaction.uncertainty_note


@pytest.mark.parametrize("cell", load_matrix(), ids=lambda c: c["cell_id"])
def test_every_matrix_cell_is_reproducible(cell):
    persona = load_persona(cell["persona_id"])
    music = music_from_cell(cell)
    first, seed1 = simulate(persona, music, cell["scene"])
    second, seed2 = simulate(persona, music, cell["scene"])
    assert seed1 == seed2
    assert first == second


def test_seed_changes_with_each_input_dimension():
    persona = load_persona("P-LILY")
    base = MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180
    )
    other_persona = load_persona("P-MAX")
    louder = base.model_copy(update={"volume": "high"})
    seeds = {
        "base": stable_seed(persona.persona_id, "sleep_support", base),
        "persona": stable_seed(other_persona.persona_id, "sleep_support", base),
        "scene": stable_seed(persona.persona_id, "focus_support", base),
        "music": stable_seed(persona.persona_id, "sleep_support", louder),
    }
    assert len(set(seeds.values())) == len(seeds)


def test_safety_flags_match_rule_conditions():
    """Distress flag iff anxiety >= 8; volume flag iff volume == high."""
    for cell in load_matrix():
        persona = load_persona(cell["persona_id"])
        reaction, _ = simulate(persona, music_from_cell(cell), cell["scene"])
        distress = any("distress" in f for f in reaction.safety_flags)
        assert distress == (reaction.anxiety_level >= 8), cell["cell_id"]
        volume = any("high-volume" in f for f in reaction.safety_flags)
        assert volume == (cell["volume"] == "high"), cell["cell_id"]


def test_volume_flag_fires_on_high_volume_input():
    """The preregistered matrix contains no high-volume cells, so construct one."""
    persona = load_persona("P-LILY")
    loud = MusicParameters(
        genre="instrumental", bpm=60, volume="high", instrument="piano",
        tonality="major", duration_sec=180
    )
    reaction, _ = simulate(persona, loud, "sleep_support")
    assert any("high-volume" in f for f in reaction.safety_flags)
