import json
from pathlib import Path

from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona


def load_persona() -> Persona:
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    return Persona.model_validate(payload[0])


def test_deterministic_simulator_is_reproducible():
    persona = load_persona()
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
