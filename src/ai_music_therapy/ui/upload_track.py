"""Track entrance: upload -> extract -> review -> confirm -> approve (S19).

Staged workflow over ``track_service``: the review state lives in
``st.session_state`` only, the database is written only at explicit approval,
rejection persists nothing, and the raw audio file never leaves memory.
Approved entries join TrackBase as write-once, explicitly synthetic records -
an exploratory cohort kept separate from the frozen 75-cell matrix.
"""

from __future__ import annotations

import streamlit as st
from pydantic import ValidationError

from ai_music_therapy.audio_analysis import (
    AudioExtractionError,
    estimated_music_defaults,
    extract_audio_profile,
    merge_music,
)
from ai_music_therapy.config import settings
from ai_music_therapy.models import AudioExtraction, MusicParameters, TrackEntry, TrialRecord
from ai_music_therapy.repository import Repository
from ai_music_therapy.track_service import (
    TRIAL_CONFIRMED,
    UNDER_REVIEW,
    TrackProposal,
    file_sha256,
    finalize_track,
    reject,
)
from ai_music_therapy.ui.confirm_trial import (
    SCENES,
    engine_options,
    render_trial_result,
    run_in_memory_trial,
)

PROPOSAL_KEY = "track_proposal"
CONFIRMATION_KEY = "track_confirmation"
#: 120 MB covers a full 10-minute CD-quality WAV (the 600 s duration cap,
#: ~106 MB) and stays under Streamlit's server.maxUploadSize default (200 MB),
#: so no server config change is needed locally or on Community Cloud.
MAX_UPLOAD_BYTES = 120 * 1024 * 1024

GENRES = ["classical", "popular", "nature", "instrumental", "vocal"]
INSTRUMENTS = ["piano", "guitar", "percussion", "synth", "voice", "mixed"]
TONALITIES = ["major", "minor", "atonal"]
VOLUMES = ["low", "medium", "high"]
LYRICS = ["none", "english", "chinese"]
DURATIONS = [60, 180, 300]

st.title("Analyze and Propose a Track (Experimental Entrance)")
st.caption(
    "Upload a sound/music file for local, deterministic feature extraction. "
    "Everything here is an estimate presented for review; approval adds the "
    "parameter profile to TrackBase as an explicitly synthetic exploratory "
    "entry. Not a clinical assessment of the music."
)

repo = Repository(settings.database_url)
repo.initialize()
personas = repo.list_personas()


def _clear_review_state() -> None:
    for key in (PROPOSAL_KEY, CONFIRMATION_KEY):
        st.session_state.pop(key, None)


def _seed_review_widgets(profile: AudioExtraction, source_sha256: str) -> None:
    """Initialize the editable review widgets from the DSP estimates."""
    defaults = estimated_music_defaults(profile)
    st.session_state["tk_genre"] = "instrumental"
    st.session_state["tk_bpm"] = defaults["bpm"] if "bpm" in defaults else 68
    st.session_state["tk_volume"] = defaults["volume"]
    st.session_state["tk_instrument"] = "mixed"
    st.session_state["tk_tonality"] = defaults["tonality"] if "tonality" in defaults else "major"
    st.session_state["tk_duration"] = min(
        DURATIONS, key=lambda d: abs(d - profile.duration_sec)
    )
    st.session_state["tk_lyrics"] = "none"
    st.session_state["tk_track_id"] = f"TRK-{source_sha256[:8].upper()}"
    st.session_state["tk_display_name"] = ""
    st.session_state["tk_notes"] = ""


if PROPOSAL_KEY not in st.session_state:
    st.subheader("1 - Upload")
    st.info(
        "Rights note: by uploading you declare that you have the right to use "
        "this file for analysis here. The site stores NO audio: the file is "
        "read in memory, a parameter profile is extracted, and the raw bytes "
        "are discarded. Only the profile plus a source-file fingerprint can "
        "ever be kept, and only after your explicit approval."
    )
    uploaded = st.file_uploader(
        "Audio file (wav / flac / ogg / mp3, max 120 MB)",
        type=["wav", "flac", "ogg", "mp3"],
        key="track_uploader",
    )
    st.caption(
        "Tip: long or studio-quality recordings fit best as mp3/flac/ogg - a "
        "10-minute CD-quality WAV is ~106 MB, the same track as MP3 is ~10-24 MB. "
        "Lossy compression barely affects these coarse feature estimates."
    )
    if uploaded is not None and st.button(
        "Extract parameters (local, no API)", type="primary", key="extract"
    ):
        data = uploaded.getvalue()
        if len(data) > MAX_UPLOAD_BYTES:
            st.error(
                f"File is {len(data) / (1024 * 1024):.1f} MB; the cap is "
                f"{MAX_UPLOAD_BYTES // (1024 * 1024)} MB. Nothing was kept."
            )
        else:
            try:
                profile = extract_audio_profile(data)
            except AudioExtractionError as error:
                st.error(f"Extraction stopped: {error} Nothing was saved.")
            else:
                source_sha = file_sha256(data)
                st.session_state[PROPOSAL_KEY] = {
                    "extraction": profile.model_dump(),
                    "source_file_name": uploaded.name,
                    "source_file_sha256": source_sha,
                    "state": UNDER_REVIEW,
                }
                st.session_state.pop(CONFIRMATION_KEY, None)
                _seed_review_widgets(profile, source_sha)
                # Raw bytes go out of scope here: only the profile survives.
                del data

if PROPOSAL_KEY in st.session_state:
    proposal_state = st.session_state[PROPOSAL_KEY]
    extraction = AudioExtraction.model_validate(proposal_state["extraction"])

    st.subheader("2 - Review extracted parameters (all estimates, all editable)")
    st.caption(
        f"Source: {proposal_state['source_file_name']} | fingerprint sha256 "
        f"{proposal_state['source_file_sha256'][:16]}... | workflow state: "
        f"{proposal_state['state']} | raw audio discarded after extraction."
    )
    e1, e2, e3, e4, e5 = st.columns(5)
    e1.metric("Duration (s)", f"{extraction.duration_sec:.1f}")
    e2.metric(
        "Tempo estimate",
        f"{extraction.tempo_bpm:.0f} BPM" if extraction.tempo_bpm else "no reliable estimate",
    )
    e3.metric("RMS energy", f"{extraction.rms_db:.1f} dBFS -> {extraction.volume_bucket}")
    e4.metric("Spectral centroid", f"{extraction.spectral_centroid_hz:.0f} Hz")
    e5.metric("Mode estimate", extraction.mode_estimate or "not tonal enough to call")
    with st.expander("Extraction provenance (signal evidence)"):
        st.json(extraction.model_dump())
    if extraction.tempo_bpm is None or not (40.0 <= extraction.tempo_bpm <= 120.0):
        st.info(
            "The tempo estimate is missing or outside the ontology range "
            "(40-120 BPM); estimates are never clamped, so set the tempo "
            "explicitly below."
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("Genre", GENRES, key="tk_genre")
        st.number_input("Tempo (BPM)", 40, 120, key="tk_bpm")
        st.selectbox("Volume category", VOLUMES, key="tk_volume")
    with c2:
        st.selectbox("Primary instrument", INSTRUMENTS, key="tk_instrument")
        st.selectbox("Tonality", TONALITIES, key="tk_tonality")
        st.selectbox("Duration class (s)", DURATIONS, key="tk_duration")
    with c3:
        st.selectbox("Lyrics", LYRICS, key="tk_lyrics")

    def _current_music() -> MusicParameters | None:
        """Validate the widgets against the ontology without persisting."""
        try:
            music, _overridden = merge_music(
                {
                    "genre": st.session_state["tk_genre"],
                    "bpm": int(st.session_state["tk_bpm"]),
                    "volume": st.session_state["tk_volume"],
                    "instrument": st.session_state["tk_instrument"],
                    "tonality": st.session_state["tk_tonality"],
                    "duration_sec": int(st.session_state["tk_duration"]),
                    "lyrics_language": st.session_state["tk_lyrics"],
                },
                extraction,
            )
        except ValidationError as error:
            st.error(f"Current parameters are outside the ontology: {error}")
            return None
        return music

    st.subheader("3 - Confirmation trial (in-memory only, never saved)")
    st.caption(
        "Check simulator behavior with the pending profile. This confirms the "
        "simulator runs sensibly on these parameters - it is NOT evidence of "
        "any therapeutic effect, and the run is never persisted."
    )
    if not personas:
        st.info(
            "No synthetic personas in the database yet, so no confirmation "
            "trial can run. You can still approve the parameters, or seed "
            "personas first (`python -m ai_music_therapy.seed_demo`)."
        )
    else:
        t1, t2, t3 = st.columns(3)
        trial_persona = t1.selectbox(
            "Synthetic persona", personas, format_func=lambda p: p.display_name,
            key="trial_persona",
        )
        trial_scene = t2.selectbox("Support scenario", SCENES, key="trial_scene")
        trial_engine = t3.radio("Engine", engine_options(), horizontal=True, key="trial_engine")
        if st.button("Run confirmation trial", key="run_confirmation"):
            music = _current_music()
            if music is not None:
                record = run_in_memory_trial(trial_persona, music, trial_scene, trial_engine)
                st.session_state[CONFIRMATION_KEY] = record.model_dump()
                proposal_state["state"] = TRIAL_CONFIRMED
    if CONFIRMATION_KEY in st.session_state:
        render_trial_result(TrialRecord.model_validate(st.session_state[CONFIRMATION_KEY]))

    st.subheader("4 - Approval (writes to TrackBase) or rejection")
    a1, a2, a3 = st.columns(3)
    a1.text_input("Track ID", key="tk_track_id")
    a2.text_input("Display name", key="tk_display_name")
    a3.text_input("Reviewer notes (optional)", key="tk_notes")

    b_approve, b_reject = st.columns(2)
    if b_approve.button("Approve and add to TrackBase", type="primary", key="approve_track"):
        try:
            music, overridden = merge_music(
                {
                    "genre": st.session_state["tk_genre"],
                    "bpm": int(st.session_state["tk_bpm"]),
                    "volume": st.session_state["tk_volume"],
                    "instrument": st.session_state["tk_instrument"],
                    "tonality": st.session_state["tk_tonality"],
                    "duration_sec": int(st.session_state["tk_duration"]),
                    "lyrics_language": st.session_state["tk_lyrics"],
                },
                extraction,
            )
            proposal = TrackProposal(
                extraction=extraction,
                source_file_name=proposal_state["source_file_name"],
                source_file_sha256=proposal_state["source_file_sha256"],
                state=proposal_state["state"],
            )
            entry = finalize_track(
                proposal,
                st.session_state["tk_track_id"].strip(),
                st.session_state["tk_display_name"].strip(),
                music,
                overridden,
                notes=st.session_state["tk_notes"].strip(),
            )
            repo.save_track(entry)
            _clear_review_state()
            st.success(
                f"Approved {entry.track_id} into TrackBase (write-once, labelled "
                "synthetic). The raw audio file was never stored."
            )
        except (ValueError, ValidationError) as error:
            st.error(f"Approval stopped and nothing was saved: {error}")
    if b_reject.button("Reject proposal", key="reject_track"):
        proposal = TrackProposal(
            extraction=extraction,
            source_file_name=proposal_state["source_file_name"],
            source_file_sha256=proposal_state["source_file_sha256"],
            state=proposal_state["state"],
        )
        reject(proposal)
        _clear_review_state()
        st.info("Proposal rejected. Nothing was saved; the audio was never kept.")

st.divider()
st.subheader("TrackBase (approved tracks, exploratory cohort)")
st.caption(
    "Write-once, explicitly synthetic entries approved through the staged "
    "review above. They are an exploratory cohort: they never enter the "
    "frozen 75-cell preregistered matrix or its bundle findings. Raw audio "
    "is not stored for any entry."
)
tracks = repo.list_tracks()
if not tracks:
    st.info("No approved tracks yet.")
else:
    st.dataframe(
        {
            "track_id": [t.track_id for t in tracks],
            "display_name": [t.display_name for t in tracks],
            "approved_at": [t.approved_at for t in tracks],
            "bpm": [t.music.bpm for t in tracks],
            "volume": [t.music.volume for t in tracks],
            "tonality": [t.music.tonality for t in tracks],
            "genre": [t.music.genre for t in tracks],
            "overridden_fields": [", ".join(t.overridden_fields) for t in tracks],
            "source_sha256": [t.source_file_sha256[:12] + "..." for t in tracks],
        },
        hide_index=True,
        width="stretch",
    )
    chosen_id = st.selectbox(
        "Inspect provenance", [t.track_id for t in tracks], key="inspect_track"
    )
    chosen: TrackEntry = repo.get_track(chosen_id)
    st.json(chosen.model_dump())
