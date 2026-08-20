import json
from pathlib import Path

from ai_music_therapy.analytics import composite_score
from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord


def test_composite_score_is_bounded():
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    persona = Persona.model_validate(payload[0])
    music = MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180,
    )
    reaction, seed = simulate(persona, music, "sleep_support")
    trial = TrialRecord(
        trial_id="T-TEST",
        persona_id=persona.persona_id,
        scene="sleep_support",
        music=music,
        reaction=reaction,
        engine="deterministic",
        prompt_version="test",
        seed=seed,
    )
    assert 0 <= composite_score(trial) <= 1


def _trial(persona_id: str, music: MusicParameters, scene: str,
           engine: str = "deterministic", trial_id: str = "T-X") -> TrialRecord:
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    persona = Persona.model_validate(payload[0])
    reaction, seed = simulate(persona, music, scene)
    return TrialRecord(
        trial_id=trial_id, persona_id=persona_id, scene=scene, music=music,
        reaction=reaction, engine=engine, prompt_version="test",
        seed=seed if engine == "deterministic" else None,
    )


def _music(bpm: int = 60) -> MusicParameters:
    return MusicParameters(
        genre="instrumental", bpm=bpm, volume="low", instrument="piano",
        tonality="major", duration_sec=180,
    )


def test_composite_heatmap_computed_from_stored_trials():
    from ai_music_therapy.analytics import composite_heatmap

    trials = [
        _trial("P-A", _music(), "sleep_support", trial_id="T-1"),
        _trial("P-B", _music(), "focus_support", trial_id="T-2"),
    ]
    heat = composite_heatmap(trials)
    assert list(heat.index) == ["P-A", "P-B"]
    assert set(heat.columns) == {"sleep_support", "focus_support"}
    # Diagonal populated; off-diagonal NaN (never imputed)
    import math

    assert not math.isnan(heat.loc["P-A", "sleep_support"])
    assert math.isnan(heat.loc["P-A", "focus_support"])
    # Values equal the mean of the stored composite scores
    from ai_music_therapy.analytics import composite_score

    assert heat.loc["P-A", "sleep_support"] == composite_score(trials[0])


def test_composite_heatmap_empty_state():
    from ai_music_therapy.analytics import composite_heatmap

    assert composite_heatmap([]).empty


def test_same_music_comparison_keeps_counts_and_engines():
    from ai_music_therapy.analytics import same_music_comparisons

    shared = _music()
    trials = [
        _trial("P-A", shared, "sleep_support", trial_id="T-1"),
        _trial("P-A", shared, "sleep_support", engine="openai", trial_id="T-2"),
        _trial("P-B", shared, "sleep_support", trial_id="T-3"),
        _trial("P-C", _music(bpm=90), "sleep_support", trial_id="T-4"),  # different music
    ]
    comparisons = same_music_comparisons(trials)
    assert list(comparisons) == [  # only the shared signature qualifies
        "instrumental/60bpm/low/piano/major/180s/lyrics:none"
    ]
    comparison = comparisons[list(comparisons)[0]]
    assert list(comparison.persona_id) == ["P-A", "P-B"]
    by_persona = comparison.set_index("persona_id")
    assert by_persona.loc["P-A", "n_trials"] == 2
    assert by_persona.loc["P-A", "engines"] == "deterministic+openai"
    assert by_persona.loc["P-B", "n_trials"] == 1
    assert by_persona.loc["P-B", "engines"] == "deterministic"
    assert 0 <= by_persona.loc["P-A", "mean_composite"] <= 1


def test_same_music_comparison_empty_when_no_shared_music():
    from ai_music_therapy.analytics import same_music_comparisons

    trials = [
        _trial("P-A", _music(), "sleep_support", trial_id="T-1"),
        _trial("P-B", _music(bpm=90), "sleep_support", trial_id="T-2"),
    ]
    assert same_music_comparisons(trials) == {}
