"""Persona entrance: JSON upload / AI draft / manual form, staged review (S19).

Three input modes feed one staged workflow: propose -> review (editable) ->
confirmation trial (in-memory only) -> explicit approval. All gates come from
``persona_service`` (S11): stereotype/synthetic-wording hard flags block
approval, near-duplicates need explicit confirmation, and an existing
``persona_id`` is never overwritten. Nothing is persisted before approval.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import streamlit as st
from pydantic import ValidationError

from ai_music_therapy.config import settings
from ai_music_therapy.models import Persona, TrialRecord
from ai_music_therapy.persona_service import (
    DraftRejected,
    PersonaDraft,
    approve_and_save,
    draft_persona_with_openai,
    lint_persona,
)
from ai_music_therapy.repository import Repository
from ai_music_therapy.ui.confirm_trial import (
    DEFAULT_CONFIRMATION_MUSIC,
    SCENES,
    engine_options,
    render_trial_result,
    run_in_memory_trial,
)

DRAFT_KEY = "persona_draft_payload"
CONFIRMATION_KEY = "persona_confirmation"

st.title("Propose a Persona (Experimental Entrance)")
st.caption(
    "Propose a new explicitly-synthetic persona through JSON upload, an "
    "AI-assisted draft, or a manual form. Every draft passes the same review "
    "gates; approval saves it through the existing persona path, rejection "
    "persists nothing. Personas are design constructs, not real children."
)

repo = Repository(settings.database_url)
repo.initialize()
existing = repo.list_personas()


def _set_draft(persona: Persona, source: str) -> None:
    st.session_state[DRAFT_KEY] = {
        "persona": persona.model_dump(),
        "source": source,
        "created_at": datetime.now(UTC).isoformat(),
    }
    st.session_state.pop(CONFIRMATION_KEY, None)
    st.session_state["pp_summary"] = persona.profile_summary


def _clear_draft_state() -> None:
    for key in (DRAFT_KEY, CONFIRMATION_KEY):
        st.session_state.pop(key, None)


def _persona_from_dict(data: dict) -> Persona:
    if isinstance(data, dict):
        data.pop("synthetic", None)  # locked to True by the schema anyway
    return Persona.model_validate(data)


def _comma_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


if DRAFT_KEY not in st.session_state:
    tab_json, tab_ai, tab_manual = st.tabs(
        ["Upload JSON", "AI-assisted draft", "Manual form"]
    )

    with tab_json:
        st.caption(
            "Upload a JSON object validated against the frozen Persona schema "
            "(unknown fields are rejected). Works without any API key."
        )
        uploaded = st.file_uploader("Persona JSON file", type=["json"], key="persona_uploader")
        if uploaded is not None and st.button("Validate and send to review", key="validate_json"):
            try:
                data = json.loads(uploaded.getvalue())
                persona = _persona_from_dict(data)
            except json.JSONDecodeError as error:
                st.error(f"Not valid JSON: {error}. Nothing was saved.")
            except ValidationError as error:
                st.error(f"Rejected by the Persona schema: {error}. Nothing was saved.")
            else:
                _set_draft(persona, "json-upload")

    with tab_ai:
        st.caption(
            "The AI drafts a candidate against the system-boundary prompt; the "
            "draft still passes every human review gate below. Optional and "
            "key-gated."
        )
        brief = st.text_area(
            "Design brief (age range, sensory focus, communication style...)",
            key="ai_brief",
        )
        if not settings.openai_api_key:
            st.info(
                "OPENAI_API_KEY is not configured; the AI draft is unavailable. "
                "JSON upload and the manual form work without any key."
            )
        if st.button(
            "Generate draft", key="generate_ai", disabled=not settings.openai_api_key
        ):
            try:
                draft = draft_persona_with_openai(brief.strip() or "open brief")
            except RuntimeError as error:
                st.error(f"AI draft stopped: {error}. Nothing was saved.")
            else:
                _set_draft(draft.persona, "ai")

    with tab_manual:
        st.caption("Build every field by hand; the same schema validates on submit.")
        with st.form("manual_persona_form"):
            f1, f2, f3 = st.columns(3)
            persona_id = f1.text_input("persona_id", value=f"P-{uuid4().hex[:6].upper()}")
            display_name = f2.text_input("display_name")
            age_years = f3.number_input("age_years", 4, 18, 8)
            profile_summary = st.text_area(
                "profile_summary (must state the profile is synthetic)", height=100
            )
            s1, s2, s3 = st.columns(3)
            communication_support = s1.text_input("support_profile.communication")
            sensory_support = s2.text_input("support_profile.sensory")
            routine_support = s3.text_input("support_profile.routine")
            social_support = st.text_input("support_profile.social")
            r1, r2, r3 = st.columns(3)
            auditory = r1.slider("sensory.auditory_sensitivity", 1, 10, 5)
            seeking = r2.slider("sensory.sensory_seeking", 1, 10, 5)
            change = r3.slider("sensory.change_sensitivity", 1, 10, 5)
            communication_modes = st.text_input("communication_modes (comma-separated)")
            music_preferences = st.text_input("music_preferences (comma-separated)")
            known_triggers = st.text_input("known_triggers (comma-separated)")
            preferred_supports = st.text_input("preferred_supports (comma-separated)")
            submitted = st.form_submit_button("Build draft and send to review")
        if submitted:
            try:
                persona = Persona.model_validate(
                    {
                        "persona_id": persona_id.strip(),
                        "display_name": display_name.strip(),
                        "age_years": int(age_years),
                        "profile_summary": profile_summary.strip(),
                        "support_profile": {
                            "communication": communication_support.strip(),
                            "sensory": sensory_support.strip(),
                            "routine": routine_support.strip(),
                            "social": social_support.strip(),
                        },
                        "sensory_profile": {
                            "auditory_sensitivity": auditory,
                            "sensory_seeking": seeking,
                            "change_sensitivity": change,
                        },
                        "communication_modes": _comma_list(communication_modes),
                        "music_preferences": _comma_list(music_preferences),
                        "known_triggers": _comma_list(known_triggers),
                        "preferred_supports": _comma_list(preferred_supports),
                    }
                )
            except ValidationError as error:
                st.error(f"Rejected by the Persona schema: {error}. Nothing was saved.")
            else:
                _set_draft(persona, "manual-form")

if DRAFT_KEY in st.session_state:
    payload = st.session_state[DRAFT_KEY]
    persona = Persona.model_validate(payload["persona"])
    edited_summary = (
        st.session_state["pp_summary"] if "pp_summary" in st.session_state
        else persona.profile_summary
    )
    if edited_summary != persona.profile_summary:
        persona = persona.model_copy(update={"profile_summary": edited_summary})

    st.subheader("Review draft (editable before approval)")
    st.caption(f"Source: {payload['source']} | created {payload['created_at']}")
    m1, m2, m3 = st.columns(3)
    m1.metric("persona_id", persona.persona_id)
    m2.metric("display_name", persona.display_name)
    m3.metric("age_years", persona.age_years)
    st.text_area(
        "profile_summary (editable; must state the profile is synthetic)",
        key="pp_summary",
        height=100,
    )
    with st.expander("Full draft (Persona JSON)"):
        st.json(persona.model_dump())

    flags = lint_persona(persona, existing)
    hard = [f for f in flags if f.split(":")[0] in ("stereotype", "synthetic-wording")]
    soft = [f for f in flags if f.split(":")[0] not in ("stereotype", "synthetic-wording")]
    for flag in hard:
        st.error(f"Hard flag blocks approval: {flag}")
    confirm_similar = False
    for flag in soft:
        st.warning(flag)
    if soft:
        confirm_similar = st.checkbox(
            "I confirm this draft is meaningfully different from the flagged persona(s)",
            key="confirm_similar",
        )

    st.subheader("Confirmation trial (in-memory only, never saved)")
    st.caption(
        f"Runs the pending persona against the neutral default stimulus "
        f"({DEFAULT_CONFIRMATION_MUSIC.genre}, {DEFAULT_CONFIRMATION_MUSIC.bpm} BPM, "
        f"{DEFAULT_CONFIRMATION_MUSIC.instrument}). Checks simulator behavior only; "
        "nothing is persisted."
    )
    t1, t2 = st.columns(2)
    scene = t1.selectbox("Support scenario", SCENES, key="pp_scene")
    engine = t2.radio("Engine", engine_options(), horizontal=True, key="pp_engine")
    if st.button("Run confirmation trial", key="pp_run_trial"):
        record = run_in_memory_trial(persona, DEFAULT_CONFIRMATION_MUSIC, scene, engine)
        st.session_state[CONFIRMATION_KEY] = record.model_dump()
    if CONFIRMATION_KEY in st.session_state:
        render_trial_result(TrialRecord.model_validate(st.session_state[CONFIRMATION_KEY]))

    st.subheader("Approval or rejection")
    b_approve, b_reject = st.columns(2)
    if b_approve.button(
        "Approve and save persona", type="primary", key="approve_persona",
        disabled=bool(hard),
    ):
        draft = PersonaDraft(
            persona=persona, source=payload["source"], created_at=payload["created_at"]
        )
        try:
            saved = approve_and_save(repo, draft, existing, confirm_similar=confirm_similar)
        except DraftRejected as error:
            st.error(f"Approval stopped and nothing was saved: {error}")
        else:
            _clear_draft_state()
            st.success(
                f"Approved {saved.persona_id} ({saved.display_name}) into the "
                "persona set (labelled synthetic)."
            )
    if b_reject.button("Reject draft", key="reject_persona"):
        _clear_draft_state()
        st.info("Draft rejected. Nothing was saved.")
