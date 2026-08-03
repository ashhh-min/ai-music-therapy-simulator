import json
from pathlib import Path

from ai_music_therapy.analytics import composite_score
from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord


def test_composite_score_is_bounded():
    persona = Persona.model_validate(json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))[0])
    music = MusicParameters(genre="instrumental", bpm=60, volume="low", instrument="piano", tonality="major", duration_sec=180)
    reaction, seed = simulate(persona, music, "sleep_support")
    trial = TrialRecord(trial_id="T-TEST", persona_id=persona.persona_id, scene="sleep_support", music=music, reaction=reaction, engine="deterministic", prompt_version="test", seed=seed)
    assert 0 <= composite_score(trial) <= 1
