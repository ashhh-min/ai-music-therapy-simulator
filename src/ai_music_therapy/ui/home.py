import streamlit as st

st.title("AI Music Therapy")
st.subheader("Neurodiversity Simulation Lab")

st.warning(
    "Educational synthetic simulation only. Outputs do not predict any real "
    "child's response, diagnose autism, recommend treatment, or establish "
    "therapeutic effectiveness."
)

st.markdown(
    """
This is an evidence-first educational prototype. Define **fictional, explicitly
synthetic** autistic-persona profiles, configure music parameters and a support
scenario, run reproducible hypothesis simulations, and analyze the synthetic
outputs.

**The loop:** persona → music parameters → synthetic response hypothesis → descriptive analysis.

Every persona and every output is explicitly synthetic. Nothing here diagnoses,
prescribes, or predicts a real person's response.
"""
)

st.markdown("### How to use the lab")
st.markdown(
    """
1. **Synthetic Personas** — browse the five fictional profiles.
2. **Run a Trial** — choose a persona, music, and a support scenario. The
   deterministic engine is the default and needs no API key.
3. **Dashboard** — view descriptive summaries of saved synthetic trials.
4. **Methods and Limits** — read the evidence boundary and the project limitations.
"""
)

st.info(
    "If no personas appear, seed the demo database first: "
    "`python -m ai_music_therapy.seed_demo`."
)
