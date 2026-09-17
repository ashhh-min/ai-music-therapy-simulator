"""S20 patch-generation tests: pure functions, no DB, no network.

The `.maxpat` format has no official specification, so these tests assert the
structural invariants that matter for a loadable patch (valid JSON, reference
header keys, unique box ids, patchlines referencing existing ids, a closed
object vocabulary) plus the deterministic parameter mapping and preview
properties. Whether Max actually opens the file is a MANUAL student
acceptance step, recorded honestly in the unit report.
"""

import io
import json
from hashlib import sha256

import pytest
import soundfile

from ai_music_therapy.models import MusicParameters
from ai_music_therapy.patch_generation import (
    OBJECT_WHITELIST,
    PREVIEW_MAX_SEC,
    PREVIEW_SAMPLE_RATE,
    ROOT_MIDI,
    SCALES,
    SPEC_VERSION,
    STEPS_PER_BAR,
    VOICES,
    VOLUME_AMPLITUDE,
    build_patch_spec,
    spec_to_maxpat,
    spec_to_preview_wav,
    spec_to_wiring_dot,
)


def _music(**overrides) -> MusicParameters:
    values = dict(
        genre="instrumental", bpm=68, volume="low", instrument="piano",
        tonality="major", duration_sec=180, lyrics_language="none",
    )
    values.update(overrides)
    return MusicParameters(**values)


def _newobj_texts(spec) -> list[str]:
    return [b.text for b in spec.boxes if b.maxclass == "newobj"]


# ------------------------------------------------------------- determinism

def test_spec_is_deterministic_for_identical_parameters():
    a = build_patch_spec(_music())
    b = build_patch_spec(_music())
    assert a.model_dump_json() == b.model_dump_json()
    assert spec_to_maxpat(a) == spec_to_maxpat(b)
    assert spec_to_preview_wav(a) == spec_to_preview_wav(b)


def test_seed_is_sha256_of_canonical_parameters():
    music = _music()
    spec = build_patch_spec(music)
    assert spec.seed == sha256(music.model_dump_json().encode("utf-8")).hexdigest()


def test_different_parameters_produce_different_specs():
    a = build_patch_spec(_music(bpm=68))
    b = build_patch_spec(_music(bpm=120))
    assert a.seed != b.seed
    assert spec_to_maxpat(a) != spec_to_maxpat(b)


def test_track_source_is_recorded():
    spec = build_patch_spec(_music(), source="track:TRK-DEADBEEF")
    assert spec.source == "track:TRK-DEADBEEF"
    assert spec.spec_version == SPEC_VERSION


# ---------------------------------------------------------------- mapping

def test_bpm_maps_to_metro_interval():
    spec = build_patch_spec(_music(bpm=120))
    assert f"metro {spec.beat_ms}" in _newobj_texts(spec)
    assert spec.beat_ms == 500
    assert build_patch_spec(_music(bpm=60)).beat_ms == 1000


def test_nature_genre_doubles_step_time():
    fast = build_patch_spec(_music(genre="instrumental", bpm=120))
    slow = build_patch_spec(_music(genre="nature", bpm=120))
    assert slow.beat_ms == 2 * fast.beat_ms


def test_volume_maps_to_documented_amplitude():
    for bucket, amplitude in VOLUME_AMPLITUDE.items():
        spec = build_patch_spec(_music(volume=bucket))
        assert spec.amplitude == amplitude


def test_major_step_notes_stay_inside_the_scale():
    spec = build_patch_spec(_music(tonality="major"))
    allowed = {(ROOT_MIDI + semitone) % 12 for semitone in SCALES["major"]}
    assert len(spec.step_notes) == STEPS_PER_BAR
    assert all((note - 12 * ((note - ROOT_MIDI) // 12)) % 12 in allowed
               or (note - ROOT_MIDI) % 12 in SCALES["major"]
               for note in spec.step_notes)


def test_minor_pattern_differs_from_major():
    major = build_patch_spec(_music(tonality="major"))
    minor = build_patch_spec(_music(tonality="minor"))
    assert major.step_notes != minor.step_notes


def test_atonal_walk_is_seed_rotated_but_deterministic():
    a = build_patch_spec(_music(tonality="atonal"))
    b = build_patch_spec(_music(tonality="atonal"))
    assert a.step_notes == b.step_notes
    rotation = int(a.seed[:8], 16) % 12
    expected = [ROOT_MIDI + (degree + rotation) % 12 for degree in range(STEPS_PER_BAR)]
    assert a.step_notes == expected


def test_percussion_shifts_notes_two_octaves_down():
    piano = build_patch_spec(_music(instrument="piano"))
    drums = build_patch_spec(_music(instrument="percussion"))
    assert drums.step_notes == [note - 24 for note in piano.step_notes]


def test_instrument_voices_use_expected_objects():
    assert build_patch_spec(_music(instrument="piano")).oscillators[0][0] == "cycle~"
    assert build_patch_spec(_music(instrument="guitar")).oscillators[0][0] == "tri~"
    assert build_patch_spec(_music(instrument="synth")).oscillators[0][0] == "saw~"
    voice_spec = build_patch_spec(_music(instrument="voice"))
    assert "+ 0.7" in _newobj_texts(voice_spec)  # detuned second oscillator
    mixed_spec = build_patch_spec(_music(instrument="mixed"))
    assert "+~" in _newobj_texts(mixed_spec)  # two-voice mixer
    assert "*~ 0.5" in _newobj_texts(mixed_spec)


def test_duration_maps_to_bar_count():
    # 60 bpm -> 1 s steps -> 8 s bars; 180 s -> ceil(22.5) = 23 bars
    spec = build_patch_spec(_music(bpm=60, duration_sec=180))
    assert spec.beat_ms == 1000
    assert spec.bars == 23


def test_lyrics_language_only_annotates_never_synthesizes():
    plain = build_patch_spec(_music(lyrics_language="none"))
    with_lyrics = build_patch_spec(_music(lyrics_language="chinese"))
    plain_comments = [b.text for b in plain.boxes if b.maxclass == "comment"]
    lyric_comments = [b.text for b in with_lyrics.boxes if b.maxclass == "comment"]
    assert not any("Lyrics language" in c for c in plain_comments)
    assert any("chinese" in c and "no voice synthesis" in c for c in lyric_comments)


# --------------------------------------------------------------- maxpat

def test_maxpat_is_valid_json_with_reference_header():
    parsed = json.loads(spec_to_maxpat(build_patch_spec(_music())))
    patcher = parsed["patcher"]
    assert patcher["fileversion"] == 1
    assert patcher["appversion"]["major"] >= 8
    assert patcher["classnamespace"] == "box"
    assert isinstance(patcher["gridsize"], list)
    assert isinstance(patcher["boxes"], list) and patcher["boxes"]
    assert isinstance(patcher["lines"], list) and patcher["lines"]


def test_maxpat_box_ids_unique_and_lines_resolve():
    patcher = json.loads(spec_to_maxpat(build_patch_spec(_music())))["patcher"]
    ids = [box["box"]["id"] for box in patcher["boxes"]]
    assert len(set(ids)) == len(ids)
    id_set = set(ids)
    for line in patcher["lines"]:
        patchline = line["patchline"]
        assert patchline["source"][0] in id_set
        assert patchline["destination"][0] in id_set
        assert len(patchline["source"]) == len(patchline["destination"]) == 2


def test_object_vocabulary_stays_within_whitelist():
    spec = build_patch_spec(_music(instrument="mixed", tonality="atonal"))
    assert {b.maxclass for b in spec.boxes} <= {"newobj", "message", "toggle", "comment", "ezdac~"}
    for text in _newobj_texts(spec):
        assert text.split()[0] in OBJECT_WHITELIST


def test_synthetic_and_trademark_labels_present():
    comments = " ".join(
        b.text for b in build_patch_spec(_music()).boxes if b.maxclass == "comment"
    )
    assert "Synthetic" in comments
    assert "Cycling '74" in comments
    assert "No therapeutic claim" in comments or "therapeutic" in comments


def test_patch_carries_auto_stop_wiring():
    spec = build_patch_spec(_music(bpm=60, duration_sec=60))  # 8 bars
    texts = _newobj_texts(spec)
    assert f"counter 0 {spec.bars - 1}" in texts  # bar counter
    stops = [b for b in spec.boxes if b.maxclass == "message" and b.text == "0"]
    assert stops  # stop message feeding the toggle


# ------------------------------------------------------------------- DOT

def test_wiring_dot_contains_every_box():
    spec = build_patch_spec(_music())
    dot = spec_to_wiring_dot(spec)
    assert dot.startswith("digraph")
    for box in spec.boxes:
        assert box.id in dot
    for role in {b.role for b in spec.boxes}:
        assert f"cluster_{role}" in dot


# --------------------------------------------------------------- preview

def test_preview_wav_decodes_with_capped_duration():
    spec = build_patch_spec(_music(bpm=60, duration_sec=180))  # 23 bars = 184 s
    data, sr = soundfile.read(io.BytesIO(spec_to_preview_wav(spec)))
    assert sr == PREVIEW_SAMPLE_RATE
    assert len(data) / sr == pytest.approx(PREVIEW_MAX_SEC, abs=0.05)


def test_preview_wav_duration_follows_shorter_plan():
    # 120 bpm -> 0.5 s steps -> 4 s bars; 60 s -> 15 bars -> 60 s plan, capped 30
    spec = build_patch_spec(_music(bpm=120, duration_sec=60))
    expected = min(spec.bars * STEPS_PER_BAR * spec.beat_ms / 1000.0, PREVIEW_MAX_SEC)
    data, sr = soundfile.read(io.BytesIO(spec_to_preview_wav(spec)))
    assert len(data) / sr == pytest.approx(expected, abs=0.05)


def test_preview_wav_is_audible_and_within_headroom():
    data, _sr = soundfile.read(io.BytesIO(spec_to_preview_wav(build_patch_spec(_music()))))
    peak = float(abs(data).max())
    assert peak > 0.01
    assert peak <= 0.95


def test_preview_reflects_volume_mapping():
    quiet, _ = soundfile.read(
        io.BytesIO(spec_to_preview_wav(build_patch_spec(_music(volume="low"))))
    )
    loud, _ = soundfile.read(
        io.BytesIO(spec_to_preview_wav(build_patch_spec(_music(volume="high"))))
    )
    assert float(abs(loud).max()) > float(abs(quiet).max())


def test_all_instruments_render_without_error():
    for instrument in VOICES:
        wav = spec_to_preview_wav(build_patch_spec(_music(instrument=instrument)))
        data, _ = soundfile.read(io.BytesIO(wav))
        assert float(abs(data).max()) > 0.01
