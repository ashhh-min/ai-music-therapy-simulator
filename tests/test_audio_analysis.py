"""S19 audio extraction tests over GENERATED fixtures only.

No real music files are committed (licensing + privacy): every input is a
synthesized signal with known properties.
"""

import io

import numpy as np
import pytest
import soundfile
from pydantic import ValidationError

from ai_music_therapy import audio_analysis
from ai_music_therapy.audio_analysis import (
    CorruptAudioError,
    EmptyAudioError,
    TooLongError,
    estimated_music_defaults,
    extract_audio_profile,
    merge_music,
    volume_bucket_for_rms_db,
)
from ai_music_therapy.models import AudioExtraction

SR = 22050


def _wav_bytes(signal: np.ndarray, sr: int = SR) -> bytes:
    buffer = io.BytesIO()
    soundfile.write(buffer, signal.astype(np.float32), sr, format="WAV")
    return buffer.getvalue()


def _click_track(bpm: float = 120.0, seconds: float = 10.0) -> bytes:
    """Impulse every beat - a clean tempo reference."""
    y = np.zeros(int(seconds * SR))
    step = int(SR * 60.0 / bpm)
    y[::step] = 1.0
    return _wav_bytes(y)


def _sine(freq: float = 440.0, seconds: float = 3.0, amplitude: float = 0.5) -> bytes:
    t = np.arange(int(seconds * SR)) / SR
    return _wav_bytes(amplitude * np.sin(2 * np.pi * freq * t))


def _chord(freqs: list[float], seconds: float = 5.0) -> bytes:
    t = np.arange(int(seconds * SR)) / SR
    y = sum(0.3 * np.sin(2 * np.pi * f * t) for f in freqs)
    return _wav_bytes(y / np.abs(y).max())


# ------------------------------------------------------------- extraction

def test_extracts_tempo_from_click_track():
    profile = extract_audio_profile(_click_track(bpm=120.0))
    assert profile.tempo_bpm is not None
    assert 105.0 <= profile.tempo_bpm <= 135.0


def test_extracts_duration():
    profile = extract_audio_profile(_sine(seconds=4.0))
    assert profile.duration_sec == pytest.approx(4.0, abs=0.1)


@pytest.mark.parametrize(
    ("amplitude", "bucket"),
    [(0.01, "low"), (0.2, "medium"), (0.9, "high")],
)
def test_volume_bucket_from_rms(amplitude, bucket):
    profile = extract_audio_profile(_sine(amplitude=amplitude))
    assert profile.volume_bucket == bucket


def test_volume_bucket_thresholds():
    assert volume_bucket_for_rms_db(-40.0) == "low"
    assert volume_bucket_for_rms_db(-20.0) == "medium"
    assert volume_bucket_for_rms_db(-5.0) == "high"


def test_mode_estimate_for_major_chord():
    # C major triad: C4, E4, G4
    profile = extract_audio_profile(_chord([261.63, 329.63, 392.0]))
    assert profile.mode_estimate == "major"


def test_mode_estimate_is_always_valid_or_none():
    rng = np.random.default_rng(7)
    profile = extract_audio_profile(_wav_bytes(rng.standard_normal(SR * 3)))
    assert profile.mode_estimate in (None, "major", "minor")


def test_profile_provenance_fields():
    profile = extract_audio_profile(_sine())
    assert profile.extractor.startswith("librosa")
    assert profile.spectral_centroid_hz > 0
    assert isinstance(profile, AudioExtraction)


def test_extracts_from_mp3_without_extra_dependencies():
    # libsndfile (bundled with soundfile) decodes mp3 natively; the same
    # extraction path must work for compressed uploads.
    buffer = io.BytesIO()
    sr = SR
    t = np.arange(int(4.0 * sr)) / sr
    signal = (0.4 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
    soundfile.write(buffer, signal, sr, format="MP3")
    profile = extract_audio_profile(buffer.getvalue())
    assert profile.duration_sec == pytest.approx(4.0, abs=0.15)
    assert profile.volume_bucket in ("low", "medium", "high")


# ----------------------------------------------------------- error paths

def test_corrupt_bytes_raise_typed_error():
    with pytest.raises(CorruptAudioError):
        extract_audio_profile(b"this is not audio data at all")


def test_silence_raises():
    with pytest.raises(EmptyAudioError):
        extract_audio_profile(_wav_bytes(np.zeros(SR * 2)))


def test_too_short_raises():
    with pytest.raises(EmptyAudioError):
        extract_audio_profile(_sine(seconds=0.1))


def test_too_long_raises(monkeypatch):
    monkeypatch.setattr(audio_analysis, "MAX_DURATION_SEC", 2.0)
    with pytest.raises(TooLongError):
        extract_audio_profile(_sine(seconds=3.0))


# ------------------------------------------------- defaults and mapping

def _profile(**overrides) -> AudioExtraction:
    values = dict(
        duration_sec=95.5, tempo_bpm=92.0, rms_db=-21.3, volume_bucket="medium",
        spectral_centroid_hz=1234.5, mode_estimate="major", extractor="librosa test",
    )
    values.update(overrides)
    return AudioExtraction(**values)


def test_defaults_include_only_estimated_fields():
    defaults = estimated_music_defaults(_profile())
    assert defaults == {"bpm": 92, "volume": "medium", "tonality": "major"}


def test_defaults_drop_out_of_range_tempo_without_clamping():
    defaults = estimated_music_defaults(_profile(tempo_bpm=150.0))
    assert "bpm" not in defaults  # reviewer must choose; never silently clamped


def test_defaults_drop_missing_mode():
    defaults = estimated_music_defaults(_profile(mode_estimate=None))
    assert "tonality" not in defaults


def test_merge_music_validates_and_computes_provenance():
    profile = _profile()
    final = {
        "genre": "instrumental", "bpm": 92, "volume": "medium",
        "instrument": "mixed", "tonality": "major", "duration_sec": 180,
        "lyrics_language": "none",
    }
    music, overridden = merge_music(final, profile)
    assert music.bpm == 92
    # bpm/volume/tonality came unchanged from estimates; the rest are choices
    assert overridden == [
        "duration_sec", "genre", "instrument", "lyrics_language",
    ]


def test_merge_music_records_reviewer_change():
    profile = _profile()
    final = {
        "genre": "classical", "bpm": 80, "volume": "low",
        "instrument": "piano", "tonality": "minor", "duration_sec": 60,
        "lyrics_language": "none",
    }
    _music, overridden = merge_music(final, profile)
    assert overridden == sorted(final)  # every field differs from the estimate


def test_merge_music_rejects_out_of_ontology_values():
    profile = _profile()
    final = {
        "genre": "instrumental", "bpm": 200, "volume": "medium",
        "instrument": "mixed", "tonality": "major", "duration_sec": 180,
        "lyrics_language": "none",
    }
    with pytest.raises(ValidationError):  # never silently clamped into range
        merge_music(final, profile)
