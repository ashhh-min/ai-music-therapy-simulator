"""Max/MSP patch generator page (S20): parameters -> patch + wiring + preview.

The reversed S19 flow: reviewed ``MusicParameters`` (manual widgets or an
approved TrackBase track) drive ONE deterministic PatchSpec, from which three
synchronized artifacts are derived on demand: a downloadable ``.maxpat`` file
for desktop Max/MSP, the wiring-logic diagram, and a downloadable local WAV
preview (an approximation of the patch's intended material, NOT Max audio).
Nothing is persisted anywhere; downloads are user-initiated.
"""

from __future__ import annotations

from datetime import UTC, datetime

import streamlit as st

from ai_music_therapy.config import settings
from ai_music_therapy.models import MusicParameters
from ai_music_therapy.patch_generation import (
    GENERATOR,
    PREVIEW_MAX_SEC,
    TRADEMARK_LINE,
    PatchSpec,
    build_patch_spec,
    spec_to_maxpat,
    spec_to_preview_wav,
    spec_to_wiring_dot,
)
from ai_music_therapy.repository import Repository

SPEC_KEY = "patch_spec_payload"

st.title("Generate a Max Patch (Experimental Entrance)")
st.caption(
    "The reversed track-entrance flow: music parameters in, a Max/MSP patch out. "
    "The site generates a loadable .maxpat file plus its wiring logic, and renders "
    "a short local preview of the intended material. Everything is an explicitly "
    "synthetic educational demonstration of a parameter mapping - not music "
    "theory, not a therapeutic device, no clinical claim."
)
st.caption(TRADEMARK_LINE)

repo = Repository(settings.database_url)
repo.initialize()
tracks = repo.list_tracks()

MAPPING_DOC = {
    "bpm": "metro step interval (60000/bpm ms; genre 'nature' doubles it "
           "for a half-speed pad)",
    "tonality": "scale table: major/minor semitone sets; atonal = "
                "seed-rotated chromatic walk",
    "genre": "8-step pattern: classical arpeggio, popular root/fifth "
             "alternation, nature sustained low pad, instrumental/vocal "
             "straight scale",
    "instrument": "oscillator voice + envelope: piano cycle~ fast decay, "
                  "guitar tri~ pluck, percussion osc~ two octaves down "
                  "(short tone), synth saw~, voice detuned cycle~ pair, "
                  "mixed cycle~+tri~",
    "volume": "constant output gain: low 0.18 / medium 0.35 / high 0.60 "
              "(researcher-defined, like S19's RMS thresholds)",
    "duration_sec": "number of 8-step bars before auto-stop (preview is "
                    "capped at 30 s)",
    "lyrics_language": "annotation comment box in the patch only - never "
                       "synthesized singing, never real lyrics",
}

if tracks:
    music_source = st.radio(
        "Parameter source",
        ["Manual parameters", "Approved track (TrackBase)"],
        horizontal=True,
        key="gp_music_source",
    )
else:
    music_source = "Manual parameters"

if music_source == "Approved track (TrackBase)":
    track = st.selectbox(
        "Approved track",
        tracks,
        format_func=lambda t: f"{t.display_name} ({t.track_id})",
        key="gp_track",
    )
    music = track.music
    source = f"track:{track.track_id}"
    st.caption(
        f"Using the reviewed parameters of {track.track_id} (approved "
        f"{track.approved_at}); raw audio was never stored for this entry."
    )
else:
    source = "manual"
    c1, c2, c3 = st.columns(3)
    with c1:
        genre = st.selectbox(
            "Genre", ["classical", "popular", "nature", "instrumental", "vocal"], key="gp_genre"
        )
        bpm = st.slider("Tempo (BPM)", 40, 120, 68, key="gp_bpm")
        volume = st.selectbox("Volume category", ["low", "medium", "high"], key="gp_volume")
    with c2:
        instrument = st.selectbox(
            "Primary instrument",
            ["piano", "guitar", "percussion", "synth", "voice", "mixed"],
            key="gp_instrument",
        )
        tonality = st.selectbox("Tonality", ["major", "minor", "atonal"], key="gp_tonality")
        duration_sec = st.selectbox("Duration", [60, 180, 300], key="gp_duration")
    with c3:
        lyrics_language = st.selectbox(
            "Lyrics", ["none", "english", "chinese"], key="gp_lyrics"
        )
    music = MusicParameters(
        genre=genre,
        bpm=bpm,
        volume=volume,
        instrument=instrument,
        tonality=tonality,
        duration_sec=duration_sec,
        lyrics_language=lyrics_language,
    )

with st.expander("Parameter-to-patch mapping (researcher-defined demonstration)"):
    for parameter, meaning in MAPPING_DOC.items():
        st.markdown(f"- **{parameter}** -> {meaning}")
    st.caption(
        "One deterministic PatchSpec drives all three artifacts, so the patch, "
        "the diagram, and the preview can never disagree about structure. Same "
        "parameters -> byte-identical outputs (seed = sha256 of the parameters)."
    )

if st.button("Generate patch + wiring + preview", type="primary", key="gp_generate"):
    st.session_state[SPEC_KEY] = build_patch_spec(music, source).model_dump()

if SPEC_KEY in st.session_state:
    spec = PatchSpec.model_validate(st.session_state[SPEC_KEY])
    maxpat_text = spec_to_maxpat(spec)
    wiring_dot = spec_to_wiring_dot(spec)
    preview_wav = spec_to_preview_wav(spec)
    seed8 = spec.seed[:8]

    st.divider()
    st.subheader("Generated artifacts")
    st.caption(
        f"spec {spec.spec_version} | generator {GENERATOR} | source {spec.source} | "
        f"seed {seed8} | {len(spec.boxes)} boxes, {len(spec.lines)} wires | "
        f"rendered {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC | "
        "nothing here is persisted."
    )

    d1, d2 = st.columns(2)
    d1.download_button(
        "Download .maxpat (opens in desktop Max/MSP)",
        data=maxpat_text.encode("utf-8"),
        file_name=f"synthetic_patch_{seed8}.maxpat",
        mime="application/json",
        key="gp_download_maxpat",
    )
    d2.download_button(
        "Download preview WAV (plays in any audio software)",
        data=preview_wav,
        file_name=f"synthetic_preview_{seed8}.wav",
        mime="audio/wav",
        key="gp_download_wav",
    )

    st.markdown("**Wiring logic** (the same graph the .maxpat contains)")
    st.graphviz_chart(wiring_dot)

    st.markdown("**Sample music preview** (rendered locally, approximation of the patch)")
    st.audio(preview_wav, format="audio/wav")
    st.caption(
        f"Up to {PREVIEW_MAX_SEC:.0f} s of the generated material, rendered by the "
        "site's local Python engine - NOT Max/MSP audio. Open the .maxpat in "
        "Max for the definitive rendering (requires a Max license or trial)."
    )

    with st.expander("Patch file JSON (.maxpat contents)"):
        st.json(spec_to_maxpat(spec))
    with st.expander("PatchSpec JSON (provenance and musical plan)"):
        st.json(spec.model_dump())
