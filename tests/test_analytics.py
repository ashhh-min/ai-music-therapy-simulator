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


def test_dimension_profile_has_six_bounded_dimensions():
    from ai_music_therapy.analytics import DIMENSIONS, dimension_profile, dimension_scores

    trial = _trial("P-A", _music(), "sleep_support", trial_id="T-1")
    scores = dimension_scores(trial)
    assert tuple(scores) == DIMENSIONS
    assert len(DIMENSIONS) == 6
    assert all(0 <= value <= 1 for value in scores.values())

    profile = dimension_profile([trial, trial])
    assert int(profile["n_trials"].iloc[0]) == 2
    assert profile["engines"].iloc[0] == "deterministic"
    for dimension in DIMENSIONS:
        assert 0 <= float(profile[dimension].iloc[0]) <= 1


def test_temporal_stage_frame_has_ordered_stages_per_trial():
    from ai_music_therapy.analytics import temporal_stage_frame

    trials = [
        _trial("P-A", _music(), "sleep_support", trial_id="T-1"),
        _trial("P-B", _music(), "focus_support", engine="openai", trial_id="T-2"),
    ]
    frame = temporal_stage_frame(trials)
    assert len(frame) == 6  # three stages per trial
    for trial_id in ("T-1", "T-2"):
        subset = frame[frame.trial_id == trial_id]
        assert list(subset["stage"]) == ["start", "middle", "end"]
        assert list(subset["stage_index"]) == [0, 1, 2]
        assert set(subset["observation"])
    assert set(frame["engine"]) == {"deterministic", "openai"}


def test_descriptive_rankings_sorted_with_counts_and_engines():
    from ai_music_therapy.analytics import composite_score, descriptive_rankings

    trial_a1 = _trial("P-A", _music(), "sleep_support", trial_id="T-1")
    trial_a2 = _trial("P-A", _music(bpm=90), "sleep_support", engine="openai", trial_id="T-2")
    trial_b = _trial("P-B", _music(), "sleep_support", trial_id="T-3")
    mean_a = (composite_score(trial_a1) + composite_score(trial_a2)) / 2
    rankings = descriptive_rankings([trial_a1, trial_a2, trial_b])
    assert list(rankings["persona_id"]) == sorted(
        ["P-A", "P-B"], key=lambda p: -(mean_a if p == "P-A" else composite_score(trial_b))
    )
    by_persona = rankings.set_index("persona_id")
    assert by_persona.loc["P-A", "n_trials"] == 2
    assert by_persona.loc["P-A", "engines"] == "deterministic+openai"
    assert by_persona.loc["P-B", "n_trials"] == 1
    means = list(rankings["mean_composite"])
    assert means == sorted(means, reverse=True)


def test_dashboard_titles_do_not_imply_effectiveness():
    source = Path("src/ai_music_therapy/ui/dashboard.py").read_text(encoding="utf-8")
    lowered = source.lower()
    for phrase in ("effective", "treatment outcome", "efficacy of", "improves"):
        assert phrase not in lowered, f"title/caption language implies effectiveness: {phrase}"
