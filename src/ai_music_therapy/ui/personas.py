import streamlit as st

from ai_music_therapy.config import settings
from ai_music_therapy.persona_service import (
    DraftRejected,
    approve_and_save,
    draft_persona_with_openai,
)
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

st.divider()
with st.expander("Draft a new persona with AI (human review required)"):
    st.caption(
        "AI drafts are suggestions only. Nothing is saved until a human reviews, "
        "resolves all flags, and explicitly accepts. Approved personas can never "
        "be overwritten."
    )
    brief = st.text_input(
        "Design brief (what support/sensory/communication profile to draft)",
        value="a persona who seeks rhythm and deep pressure, communicates by AAC device",
    )
    if st.button("Generate draft (does not save)"):
        try:
            st.session_state["persona_draft"] = draft_persona_with_openai(brief)
            st.session_state.pop("summary_revision", None)
        except RuntimeError as error:
            st.error(str(error))

    draft = st.session_state.get("persona_draft")
    if draft is not None:
        st.subheader(f"Draft: {draft.persona.display_name} ({draft.persona.persona_id})")
        st.caption(f"source: {draft.source} | drafted: {draft.created_at} | NOT saved")
        st.write(draft.persona.profile_summary)
        st.json(draft.persona.model_dump())

        st.subheader("Human review")
        flags = st.session_state.get(
            "draft_flags",
            None,
        )
        if flags is None:
            from ai_music_therapy.persona_service import lint_persona

            flags = lint_persona(draft.persona, repo.list_personas())
            st.session_state["draft_flags"] = flags
        if flags:
            st.warning("Review flags (resolve before accepting):")
            for flag in flags:
                st.markdown(f"- {flag}")
        else:
            st.success("No lint flags. A human reviewer still makes the final call.")

        revision = st.text_area(
            "Revise profile_summary (required if flagged for wording)",
            value=st.session_state.get("summary_revision", draft.persona.profile_summary),
        )
        st.session_state["summary_revision"] = revision

        similar = any(f.startswith("near-duplicate") for f in flags)
        confirm_similar = st.checkbox(
            "I confirm this draft is meaningfully different from the similar approved persona",
            disabled=not similar,
        )

        col_reject, col_accept = st.columns(2)
        if col_reject.button("Reject draft"):
            st.session_state.pop("persona_draft", None)
            st.session_state.pop("draft_flags", None)
            st.session_state.pop("summary_revision", None)
            st.info("Draft rejected. Nothing was saved.")
        if col_accept.button("Accept and save", type="primary"):
            try:
                # Apply the reviewer's summary revision, then re-run the gates.
                revised = draft.persona.model_copy(update={"profile_summary": revision.strip()})
                from dataclasses import replace

                revised_draft = replace(draft, persona=revised)
                approve_and_save(
                    repo,
                    revised_draft,
                    repo.list_personas(),
                    confirm_similar=confirm_similar,
                )
                st.success(f"Saved {revised.persona.persona_id} after review.")
                st.session_state.pop("persona_draft", None)
                st.session_state.pop("draft_flags", None)
                st.session_state.pop("summary_revision", None)
                st.rerun()
            except DraftRejected as error:
                st.error(f"Not saved: {error}")
