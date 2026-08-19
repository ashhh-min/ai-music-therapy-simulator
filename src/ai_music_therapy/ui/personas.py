import streamlit as st

from ai_music_therapy.config import settings
from ai_music_therapy.repository import Repository

st.title("Synthetic Personas")
repo = Repository(settings.database_url)
repo.initialize()
personas = repo.list_personas()

if not personas:
    st.warning("No personas found. Run `python -m ai_music_therapy.seed_demo`.")
else:
    selected = st.selectbox(
        "Choose a fictional profile", personas, format_func=lambda p: p.display_name
    )
    st.caption("Synthetic profile - not a clinical case record")
    st.write(selected.profile_summary)
    st.json(selected.model_dump())
