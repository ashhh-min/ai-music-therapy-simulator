import json
from pathlib import Path

from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord
from ai_music_therapy.repository import Repository


def _build_trial(persona: Persona) -> TrialRecord:
    music = MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180,
    )
    reaction, seed = simulate(persona, music, "sleep_support")
    return TrialRecord(
        trial_id="T-RT", persona_id=persona.persona_id, scene="sleep_support",
        music=music, reaction=reaction, engine="deterministic",
        prompt_version="test", seed=seed,
    )


def test_repository_round_trip(tmp_path):
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    persona = Persona.model_validate(payload[0])
    repo = Repository(tmp_path / "test.db")
    repo.initialize()
    repo.upsert_persona(persona)
    assert repo.get_persona(persona.persona_id) == persona


def test_trial_round_trip(tmp_path):
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    persona = Persona.model_validate(payload[0])
    repo = Repository(tmp_path / "trials.db")
    repo.initialize()
    repo.upsert_persona(persona)
    trial = _build_trial(persona)
    repo.save_trial(trial)
    trials = repo.list_trials()
    assert len(trials) == 1
    assert trials[0] == trial
