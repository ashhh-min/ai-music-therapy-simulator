from __future__ import annotations

import streamlit as st

from ai_music_therapy.config import settings

st.set_page_config(
    page_title="AI Music Therapy - Simulation Lab",
    page_icon="🎵",
    layout="wide",
)

# Global disclaimer shown in the sidebar on every page.
with st.sidebar:
    st.warning(
        "Educational synthetic simulation only. Outputs do not predict any real "
        "child's response, diagnose autism, recommend treatment, or establish "
        "therapeutic effectiveness."
    )
    st.caption(f"Engine mode: {settings.mode} | prompt version {settings.prompt_version}")

pages = {
    "Lab": [
        st.Page("src/ai_music_therapy/ui/home.py", title="Home", icon="🏠"),
        st.Page("src/ai_music_therapy/ui/personas.py", title="Synthetic Personas", icon="🧩"),
        st.Page("src/ai_music_therapy/ui/trial.py", title="Run a Trial", icon="🎧"),
        st.Page("src/ai_music_therapy/ui/dashboard.py", title="Dashboard", icon="📊"),
    ],
    "Research": [
        st.Page("src/ai_music_therapy/ui/methods.py", title="Methods and Limits", icon="📚"),
    ],
}

navigation = st.navigation(pages)
navigation.run()
