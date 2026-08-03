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
