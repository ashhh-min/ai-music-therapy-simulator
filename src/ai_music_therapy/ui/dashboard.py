import plotly.express as px
import streamlit as st

from ai_music_therapy.analytics import trials_to_frame
from ai_music_therapy.config import settings
from ai_music_therapy.repository import Repository

st.title("Synthetic Trial Dashboard")
repo = Repository(settings.db_path)
repo.initialize()
trials = repo.list_trials()

if not trials:
    st.info("No saved trials yet. Run at least one synthetic trial.")
    st.stop()

frame = trials_to_frame(trials)
st.dataframe(frame, use_container_width=True)

heat = frame.pivot_table(
    index="persona_id", columns="scene", values="composite_score", aggfunc="mean"
)
st.plotly_chart(
    px.imshow(heat, text_auto=True, aspect="auto", title="Descriptive Composite Index"),
    use_container_width=True,
)

st.plotly_chart(
    px.scatter(
        frame,
        x="anxiety_level",
        y="engagement_level",
        color="persona_id",
        size="attention_duration_sec",
        hover_data=["scene", "engine", "instrument", "bpm"],
        title="Synthetic Anxiety-Engagement Pattern",
    ),
    use_container_width=True,
)

st.warning(
    "Charts summarize generated synthetic outputs. "
    "They are not evidence of clinical efficacy."
)
