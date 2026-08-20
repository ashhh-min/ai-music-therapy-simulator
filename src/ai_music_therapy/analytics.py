from __future__ import annotations

import pandas as pd

from .models import TrialRecord


def composite_score(trial: TrialRecord) -> float:
    """Researcher-defined descriptive index; not a clinical score."""
    r = trial.reaction
    anxiety_component = (10 - r.anxiety_level) / 9
    engagement_component = (r.engagement_level - 1) / 9
    mood_component = (r.mood_score - 1) / 9
    regulation_component = (r.regulation_score - 1) / 9
    score = (
        0.35 * anxiety_component
        + 0.30 * engagement_component
        + 0.20 * mood_component
        + 0.15 * regulation_component
    )
    return round(score, 4)


def trials_to_frame(trials: list[TrialRecord]) -> pd.DataFrame:
    rows = []
    for trial in trials:
        rows.append(
            {
                "trial_id": trial.trial_id,
                "persona_id": trial.persona_id,
                "scene": trial.scene,
                "genre": trial.music.genre,
                "bpm": trial.music.bpm,
                "volume": trial.music.volume,
                "instrument": trial.music.instrument,
                "tonality": trial.music.tonality,
                "engine": trial.engine,
                "anxiety_level": trial.reaction.anxiety_level,
                "engagement_level": trial.reaction.engagement_level,
                "mood_score": trial.reaction.mood_score,
                "regulation_score": trial.reaction.regulation_score,
                "attention_duration_sec": trial.reaction.attention_duration_sec,
                "composite_score": composite_score(trial),
                "created_at": trial.created_at,
            }
        )
    return pd.DataFrame(rows)


def composite_heatmap(trials: list[TrialRecord]) -> pd.DataFrame:
    """Persona x scenario matrix of mean composite scores, from stored trials.

    Cells with no stored trials are NaN (never imputed) so the chart honestly
    shows coverage gaps. Descriptive only - not a clinical measure.
    """
    if not trials:
        return pd.DataFrame()
    frame = trials_to_frame(trials)
    return frame.pivot_table(
        index="persona_id", columns="scene", values="composite_score", aggfunc="mean"
    )


def music_signature(trial: TrialRecord) -> str:
    """Compact signature of the full music configuration (for same-music grouping)."""
    m = trial.music
    return (
        f"{m.genre}/{m.bpm}bpm/{m.volume}/{m.instrument}/{m.tonality}/"
        f"{m.duration_sec}s/lyrics:{m.lyrics_language}"
    )


def same_music_comparisons(trials: list[TrialRecord]) -> dict[str, pd.DataFrame]:
    """Group trials by identical music configuration; keep groups comparing 2+ personas.

    Each returned frame keeps sample counts (n_trials) and engine labels per
    persona so a comparison can never be read as a single-engine clinical claim.
    Returns {music_signature: comparison_frame}, only for signatures shared by
    two or more distinct personas.
    """
    groups: dict[str, list[TrialRecord]] = {}
    for trial in trials:
        groups.setdefault(music_signature(trial), []).append(trial)

    comparisons: dict[str, pd.DataFrame] = {}
    for signature, group in sorted(groups.items()):
        personas = {t.persona_id for t in group}
        if len(personas) < 2:
            continue
        rows = []
        for persona_id in sorted(personas):
            subset = [t for t in group if t.persona_id == persona_id]
            scores = [composite_score(t) for t in subset]
            rows.append(
                {
                    "persona_id": persona_id,
                    "n_trials": len(subset),
                    "engines": "+".join(sorted({t.engine for t in subset})),
                    "mean_composite": round(sum(scores) / len(scores), 4),
                    "mean_anxiety": round(
                        sum(t.reaction.anxiety_level for t in subset) / len(subset), 2
                    ),
                    "mean_engagement": round(
                        sum(t.reaction.engagement_level for t in subset) / len(subset), 2
                    ),
                    "mean_regulation": round(
                        sum(t.reaction.regulation_score for t in subset) / len(subset), 2
                    ),
                }
            )
        comparisons[signature] = pd.DataFrame(rows)
    return comparisons


DIMENSIONS = ("calm", "engagement", "mood", "regulation", "attention", "stability")


def _attention_ratio(trial: TrialRecord) -> float:
    """Attended fraction of the configured trial duration."""
    duration = trial.music.duration_sec
    if duration <= 0:
        return 0.0
    return min(1.0, trial.reaction.attention_duration_sec / duration)


def _stability(trial: TrialRecord) -> float:
    """Inverse of the anxiety change magnitude across the temporal sequence.

    1.0 = anxiety identical at start and end; 0.0 = maximum swing (9 points).
    A descriptive software signal about the simulated trajectory shape.
    """
    stages = {s.stage: s for s in trial.reaction.time_series}
    change = abs(stages["end"].anxiety_level - stages["start"].anxiety_level)
    return 1.0 - change / 9.0


def dimension_scores(trial: TrialRecord) -> dict[str, float]:
    """Six researcher-defined descriptive dimensions, each normalized to [0, 1].

    Not clinical measures; see docs/chart_interpretation.md.
    """
    r = trial.reaction
    return {
        "calm": (10 - r.anxiety_level) / 9,
        "engagement": (r.engagement_level - 1) / 9,
        "mood": (r.mood_score - 1) / 9,
        "regulation": (r.regulation_score - 1) / 9,
        "attention": _attention_ratio(trial),
        "stability": _stability(trial),
    }


def dimension_profile(trials: list[TrialRecord]) -> pd.DataFrame:
    """Mean six-dimension profile across trials, with counts and engine labels."""
    rows = [
        {**dimension_scores(t), "engine": t.engine, "persona_id": t.persona_id}
        for t in trials
    ]
    frame = pd.DataFrame(rows)
    profile = {
        dimension: round(frame[dimension].mean(), 4) for dimension in DIMENSIONS
    }
    profile["n_trials"] = len(trials)
    profile["engines"] = "+".join(sorted(frame["engine"].unique()))
    return pd.DataFrame([profile])


def temporal_stage_frame(trials: list[TrialRecord]) -> pd.DataFrame:
    """Flatten stored start/middle/end sequences into one row per stage."""
    rows = []
    for trial in trials:
        for index, stage in enumerate(trial.reaction.time_series):
            rows.append(
                {
                    "trial_id": trial.trial_id,
                    "persona_id": trial.persona_id,
                    "scene": trial.scene,
                    "engine": trial.engine,
                    "stage": stage.stage,
                    "stage_index": index,
                    "anxiety_level": stage.anxiety_level,
                    "engagement_level": stage.engagement_level,
                    "observation": stage.observation,
                }
            )
    return pd.DataFrame(rows)


def descriptive_rankings(trials: list[TrialRecord]) -> pd.DataFrame:
    """Rank personas by mean composite score. Descriptive only; counts always shown."""
    rows = []
    for persona_id in sorted({t.persona_id for t in trials}):
        subset = [t for t in trials if t.persona_id == persona_id]
        scores = [composite_score(t) for t in subset]
        rows.append(
            {
                "persona_id": persona_id,
                "mean_composite": round(sum(scores) / len(scores), 4),
                "n_trials": len(subset),
                "engines": "+".join(sorted({t.engine for t in subset})),
            }
        )
    frame = pd.DataFrame(rows)
    return frame.sort_values("mean_composite", ascending=False).reset_index(drop=True)
