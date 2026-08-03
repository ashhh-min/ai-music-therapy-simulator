import streamlit as st

st.title("AI Music Therapy")
st.subheader("Neurodiversity Simulation Lab")
st.warning(
    "Educational synthetic simulation only. This application does not predict a real child's "
    "response, diagnose autism, recommend treatment, or establish therapeutic effectiveness."
)

st.markdown(
    """
This lab preserves the original project loop:

**Persona definition → music input → synthetic response → analysis → strategy revision**

The refined implementation adds four controls:

1. Every persona and trial is explicitly synthetic.
2. Deterministic mode provides reproducible offline testing.
3. AI mode uses structured outputs and records model/prompt provenance.
4. All conclusions must separate software observations from clinical claims.
"""
)

st.info("Begin by seeding the demo database: `python -m ai_music_therapy.seed_demo`.")
