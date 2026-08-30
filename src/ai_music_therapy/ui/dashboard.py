import pandas as pd
import plotly.express as px
import streamlit as st

from ai_music_therapy import analytics
from ai_music_therapy.analytics import (
    composite_heatmap,
    same_music_comparisons,
    trials_to_frame,
)
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
st.dataframe(frame, width="stretch")

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
        width="stretch",
        config={"toImageButtonOptions": {"format": "png", "filename": "composite_heatmap"}},
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
    st.dataframe(comparison, hide_index=True, width="stretch")
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
        width="stretch",
        config={"toImageButtonOptions": {"format": "png", "filename": "same_music_comparison"}},
    )
    st.caption(NON_CLINICAL_NOTICE)

st.subheader("Six-dimension descriptive profile (radar)")
st.caption(NON_CLINICAL_NOTICE)
persona_ids = sorted({t.persona_id for t in trials})
radar_persona = st.selectbox("Persona", persona_ids, key="radar_persona")
radar_trials = [t for t in trials if t.persona_id == radar_persona]
profile = analytics.dimension_profile(radar_trials)
dimensions = list(analytics.DIMENSIONS)
radar_frame = pd.DataFrame(
    {
        "dimension": dimensions + [dimensions[0]],
        "mean_score": [float(profile[d].iloc[0]) for d in dimensions]
        + [float(profile[dimensions[0]].iloc[0])],
    }
)
st.plotly_chart(
    px.line_polar(
        radar_frame,
        r="mean_score",
        theta="dimension",
        line_close=True,
        range_r=[0, 1],
    ),
    width="stretch",
    config={"toImageButtonOptions": {"format": "png", "filename": "dimension_profile"}},
)
st.caption(
    f"Means over {int(profile['n_trials'].iloc[0])} stored trial(s) "
    f"(engines: {profile['engines'].iloc[0]}). Dimensions are researcher-defined "
    "software signals, not clinical measures."
)

st.subheader("Temporal stage view (stored sequences)")
st.caption(NON_CLINICAL_NOTICE)
stage_frame = analytics.temporal_stage_frame(trials)
stage_means = (
    stage_frame.groupby("stage", as_index=False)[["anxiety_level", "engagement_level"]]
    .mean()
)
stage_means["stage"] = pd.Categorical(
    stage_means["stage"], ["start", "middle", "end"], ordered=True
)
stage_means = stage_means.sort_values("stage")
st.plotly_chart(
    px.line(
        stage_means,
        x="stage",
        y=["anxiety_level", "engagement_level"],
        markers=True,
        labels={"value": "mean level (1 to 10)", "stage": "stage"},
    ),
    width="stretch",
    config={"toImageButtonOptions": {"format": "png", "filename": "temporal_stages"}},
)
st.caption(
    f"Mean of stored start/middle/end values across {len(trials)} trial(s); "
    "describes simulated trajectories only."
)

st.subheader("Descriptive rankings by persona")
st.caption(NON_CLINICAL_NOTICE)
rankings = analytics.descriptive_rankings(trials)
st.dataframe(rankings, hide_index=True, width="stretch")
st.caption(
    "Sorted by mean composite index. Ranking position reflects stored synthetic "
    "trials only; personas differ by design, so a higher rank is not an outcome."
)

st.subheader("Uncertainty and provenance notes")
engine_counts = frame.groupby("engine").size()
st.write(
    "Stored trials by engine: "
    + ", ".join(f"{engine} ({count})" for engine, count in engine_counts.items())
)
ai_notes = [f"{t.trial_id} ({t.engine}): {t.reaction.uncertainty_note}" for t in trials]
with st.expander(f"Per-trial uncertainty notes ({len(ai_notes)})"):
    for note in ai_notes:
        st.markdown(f"- {note}")

st.subheader("Export")
st.write(
    "Each chart has a camera icon for PNG download. The buttons below export the "
    "underlying data for the radar, stage, and ranking views."
)
col_a, col_b, col_c = st.columns(3)
col_a.download_button(
    "Radar data (CSV)",
    radar_frame.to_csv(index=False).encode(),
    file_name="dimension_profile.csv",
    mime="text/csv",
)
col_b.download_button(
    "Stage means (CSV)",
    stage_means.to_csv(index=False).encode(),
    file_name="temporal_stage_means.csv",
    mime="text/csv",
)
col_c.download_button(
    "Rankings (CSV)",
    rankings.to_csv(index=False).encode(),
    file_name="descriptive_rankings.csv",
    mime="text/csv",
)
st.caption("Exports contain synthetic simulation output only.")

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
    width="stretch",
    config={"toImageButtonOptions": {"format": "png", "filename": "anxiety_engagement_scatter"}},
)
st.caption(NON_CLINICAL_NOTICE)

st.warning(
    "Charts summarize generated synthetic outputs. "
    "They are not evidence of clinical efficacy."
)
