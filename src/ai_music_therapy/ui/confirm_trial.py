"""Shared helpers for review-stage confirmation trials (S19).

A confirmation trial runs in memory only and is NEVER handed to a
Repository: it exists so a reviewer can check simulator behavior before
approving a proposed track or persona. Nothing here writes to the database.
"""

from __future__ import annotations

from uuid import uuid4

import streamlit as st

from ai_music_therapy.ai_client import ai_trial
from ai_music_therapy.config import settings
from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord

#: Neutral default stimulus for persona confirmation trials.
DEFAULT_CONFIRMATION_MUSIC = MusicParameters(
    genre="instrumental", bpm=68, volume="low", instrument="piano",
    tonality="major", duration_sec=180, lyrics_language="none",
)

SCENES = [
    "sleep_support",
    "anxiety_support",
    "focus_support",
    "engagement_support",
    "regulation_support",
]


#: Expectation-setting hint shown wherever the openai engine can be selected.
#: A live reasoning-model call takes roughly 1-2 minutes (measured ~95 s for a
#: full trial against qwen3.8-max); Streamlit renders nothing until it returns,
#: and each attempt is bounded by ai_client.OPENAI_TIMEOUT_SEC.
ENGINE_HINT = (
    "The openai engine makes a live reasoning-model call: expect roughly 1-2 "
    "minutes of waiting, with results and charts appearing only once the call "
    "completes. Each attempt is bounded by a 120-second timeout, so a stalled "
    "provider surfaces as an error message instead of an endless spinner. The "
    "deterministic engine is instant local computation."
)


def engine_options() -> list[str]:
    """Engines available for a confirmation trial (openai needs a key)."""
    return ["deterministic"] + (["openai"] if settings.openai_api_key else [])


def render_engine_hint() -> None:
    """Show ENGINE_HINT only when the openai engine is actually selectable."""
    if settings.openai_api_key:
        st.caption(ENGINE_HINT)


def run_in_memory_trial(
    persona: Persona,
    music: MusicParameters,
    scene: str,
    engine: str = "deterministic",
) -> TrialRecord:
    """Run one trial and return the record WITHOUT saving it anywhere."""
    if engine == "deterministic":
        reaction, seed = simulate(persona, music, scene)
        model_name = None
    else:
        reaction, model_name = ai_trial(persona, music, scene)
        seed = None
    return TrialRecord(
        trial_id=f"T-PREVIEW-{uuid4().hex[:8].upper()}",
        persona_id=persona.persona_id,
        scene=scene,
        music=music,
        reaction=reaction,
        engine=engine,
        model_name=model_name,
        prompt_version=settings.prompt_version,
        seed=seed,
    )


def render_trial_result(record: TrialRecord) -> None:
    """Render an unsaved confirmation trial with its non-persistence notice."""
    reaction = record.reaction
    if reaction.safety_flags:
        st.warning("Stop-condition / safety flags: " + " | ".join(reaction.safety_flags))
    st.info(f"Uncertainty: {reaction.uncertainty_note}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Anxiety", reaction.anxiety_level)
    m2.metric("Engagement", reaction.engagement_level)
    m3.metric("Mood", reaction.mood_score)
    m4.metric("Regulation", reaction.regulation_score)

    st.dataframe(
        {
            "Stage": [s.stage for s in reaction.time_series],
            "Anxiety": [s.anxiety_level for s in reaction.time_series],
            "Engagement": [s.engagement_level for s in reaction.time_series],
            "Observation": [s.observation for s in reaction.time_series],
        },
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Synthetic confirmation trial shown for review only. It was NOT saved: "
        "it checks simulator behavior with the proposed input, not any real "
        "effect of music or any property of a real person."
    )
    with st.expander("Confirmation trial record (unsaved preview JSON)"):
        st.json(record.model_dump())
