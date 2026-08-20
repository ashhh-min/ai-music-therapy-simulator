from __future__ import annotations

from uuid import uuid4

import streamlit as st

from ai_music_therapy.ai_client import ai_trial
from ai_music_therapy.config import settings
from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, TrialRecord
from ai_music_therapy.repository import Repository

st.title("Run a Synthetic Trial")
st.caption("The result is a model-generated hypothesis, not a real-world prediction.")

repo = Repository(settings.database_url)
repo.initialize()
personas = repo.list_personas()
if not personas:
    st.error("Seed the demo database first: `python -m ai_music_therapy.seed_demo`.")
    st.stop()

persona = st.selectbox("Synthetic persona", personas, format_func=lambda p: p.display_name)
scene = st.selectbox(
    "Support scenario",
    [
        "sleep_support",
        "anxiety_support",
        "focus_support",
        "engagement_support",
        "regulation_support",
    ],
)

c1, c2, c3 = st.columns(3)
with c1:
    genre = st.selectbox("Genre", ["classical", "popular", "nature", "instrumental", "vocal"])
    bpm = st.slider("Tempo (BPM)", 40, 120, 68)
    volume = st.selectbox("Volume category", ["low", "medium", "high"])
with c2:
    instrument = st.selectbox(
        "Primary instrument", ["piano", "guitar", "percussion", "synth", "voice", "mixed"]
    )
    tonality = st.selectbox("Tonality", ["major", "minor", "atonal"])
    duration_sec = st.selectbox("Duration", [60, 180, 300])
with c3:
    lyrics_language = st.selectbox("Lyrics", ["none", "english", "chinese"])
    engine = st.radio("Engine", ["deterministic", "openai"], horizontal=True)

music = MusicParameters(
    genre=genre,
    bpm=bpm,
    volume=volume,
    instrument=instrument,
    tonality=tonality,
    duration_sec=duration_sec,
    lyrics_language=lyrics_language,
)

if st.button("Run synthetic trial", type="primary"):
    try:
        if engine == "deterministic":
            reaction, seed = simulate(persona, music, scene)
            model_name = None
        else:
            reaction, model_name = ai_trial(persona, music, scene)
            seed = None

        trial = TrialRecord(
            trial_id=f"T-{uuid4().hex[:12].upper()}",
            persona_id=persona.persona_id,
            scene=scene,
            music=music,
            reaction=reaction,
            engine=engine,
            model_name=model_name,
            prompt_version=settings.prompt_version,
            seed=seed,
        )
        repo.save_trial(trial)
        st.success(f"Saved {trial.trial_id}")

        if reaction.safety_flags:
            st.warning("Stop-condition / safety flags: " + " | ".join(reaction.safety_flags))
        st.info(f"Uncertainty: {reaction.uncertainty_note}")

        st.subheader("Scores")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Anxiety", reaction.anxiety_level)
        m2.metric("Engagement", reaction.engagement_level)
        m3.metric("Mood", reaction.mood_score)
        m4.metric("Regulation", reaction.regulation_score)

        st.subheader("Temporal sequence (start - middle - end)")
        st.dataframe(
            {
                "Stage": [s.stage for s in reaction.time_series],
                "Anxiety": [s.anxiety_level for s in reaction.time_series],
                "Engagement": [s.engagement_level for s in reaction.time_series],
                "Observation": [s.observation for s in reaction.time_series],
            },
            hide_index=True,
        )

        st.caption(
            "Synthetic result only: not a clinical prediction or treatment "
            "recommendation."
        )
        with st.expander("Full trial record (provenance JSON)"):
            st.json(trial.model_dump())
    except Exception as exc:
        st.error(f"Trial not run and nothing was saved: {exc}")
