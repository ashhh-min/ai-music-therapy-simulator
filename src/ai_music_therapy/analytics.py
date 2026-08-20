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
