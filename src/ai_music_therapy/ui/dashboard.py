import plotly.express as px
import streamlit as st

from ai_music_therapy.analytics import composite_heatmap, same_music_comparisons, trials_to_frame
from ai_music_therapy.config import settings
from ai_music_therapy.repository import Repository

NON_CLINICAL_NOTICE = "Descriptive view of synthetic outputs - not evidence of clinical efficacy."

st.title("Synthetic Trial Dashboard")
repo = Repository(settings.database_url)
repo.initialize()
trials = repo.list_trials()

if not trials:
    st.info("No saved trials yet. Run at least one synthetic trial.")
    st.stop()

frame = trials_to_frame(trials)
st.dataframe(frame, use_container_width=True)

st.subheader("Persona x scenario heatmap (mean composite index)")
heat = composite_heatmap(trials)
if heat.empty:
    st.info("Not enough stored trials to build the heatmap.")
else:
    st.plotly_chart(
        px.imshow(
            heat,
            text_auto=True,
            aspect="auto",
            title="Descriptive Composite Index (mean per persona x scenario)",
        ),
        use_container_width=True,
    )
    st.caption(NON_CLINICAL_NOTICE)
    st.caption(
        "Empty cells mean no stored trials for that combination - values are "
        "never imputed."
    )

st.subheader("Same music, different personas")
comparisons = same_music_comparisons(trials)
if not comparisons:
    st.info(
        "No music configuration has been run with two or more personas yet. "
        "Run the same music settings for different personas to compare."
    )
else:
    selected_signature = st.selectbox(
        "Music configuration (shared by 2+ personas)", list(comparisons)
    )
    comparison = comparisons[selected_signature]
    st.dataframe(comparison, hide_index=True, use_container_width=True)
    st.caption(
        "Each row keeps its sample count (n_trials) and engine labels so the "
        "comparison stays attributable."
    )
    st.plotly_chart(
        px.bar(
            comparison,
            x="persona_id",
            y="mean_composite",
            color="persona_id",
            text="n_trials",
            hover_data=["engines"],
            title=f"Mean composite under identical music: {selected_signature}",
        ),
        use_container_width=True,
    )
    st.caption(NON_CLINICAL_NOTICE)

st.subheader("Synthetic anxiety-engagement pattern")
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
st.caption(NON_CLINICAL_NOTICE)

st.warning(
    "Charts summarize generated synthetic outputs. "
    "They are not evidence of clinical efficacy."
)
