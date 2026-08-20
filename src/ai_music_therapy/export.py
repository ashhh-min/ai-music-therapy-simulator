"""Export accepted trial runs for evidence capture.

Every export format carries the synthetic label and the fixed limitations
text, so an exported file can never be mistaken for clinical data.
"""

from __future__ import annotations

import csv
import io
import json

from .models import TrialRecord

LIMITATIONS_TEXT = (
    "Synthetic educational simulation output. Personas are fictional; scores "
    "are constructed software signals, not validated clinical measures; this "
    "is not a clinical prediction or treatment recommendation."
)


def trials_to_csv(trials: list[TrialRecord]) -> str:
    """Flat CSV: one row per trial, synthetic + limitations on every row."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "trial_id", "persona_id", "scene", "engine", "model_name",
            "prompt_version", "seed", "created_at",
            "anxiety_level", "engagement_level", "mood_score", "regulation_score",
            "attention_duration_sec", "safety_flags",
            "synthetic", "limitations",
        ]
    )
    for trial in trials:
        reaction = trial.reaction
        writer.writerow(
            [
                trial.trial_id,
                trial.persona_id,
                trial.scene,
                trial.engine,
                trial.model_name or "",
                trial.prompt_version,
                trial.seed if trial.seed is not None else "",
                trial.created_at,
                reaction.anxiety_level,
                reaction.engagement_level,
                reaction.mood_score,
                reaction.regulation_score,
                reaction.attention_duration_sec,
                "; ".join(reaction.safety_flags),
                "true",
                LIMITATIONS_TEXT,
            ]
        )
    return buffer.getvalue()


def trials_to_json(trials: list[TrialRecord]) -> str:
    """Full-fidelity JSON export: complete records plus document-level labels."""
    document = {
        "synthetic": True,
        "limitations": LIMITATIONS_TEXT,
        "count": len(trials),
        "trials": [json.loads(trial.model_dump_json()) for trial in trials],
    }
    return json.dumps(document, indent=2, ensure_ascii=False)
