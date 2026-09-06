"""Local, deterministic audio feature extraction for uploaded tracks (S19).

Pure DSP over in-memory bytes (librosa + soundfile); no network, no API key,
and the raw audio is consumed and discarded - only the resulting
``AudioExtraction`` profile may ever be persisted (D028).

Everything here is an ESTIMATE, presented as such: tempo and mode detection
are heuristics, and the volume bucket is a researcher-defined threshold over
RMS energy. The extraction is descriptive signal processing; it says nothing
about therapeutic properties of the music.
"""

from __future__ import annotations

import io
import math

import librosa
import numpy as np
from soundfile import LibsndfileError

from .models import AudioExtraction, MusicParameters

#: Researcher-defined RMS thresholds (dBFS) for the ordinal volume bucket.
#: They are a design choice, not calibrated loudness standards.
RMS_DB_LOW_MAX = -30.0
RMS_DB_MEDIUM_MAX = -14.0

#: Uploaded audio beyond this is rejected (the UI also enforces a file-size cap).
MAX_DURATION_SEC = 600.0

#: Minimum signal length for a meaningful tempo/mode estimate.
MIN_DURATION_SEC = 0.5

# Krumhansl-Kessler key profiles (correlate against the mean chroma).
_MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
_MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)
#: Minimum chroma concentration (peak/mean) for a major/minor call. Measured
#: gap: tonal chords concentrate chroma ~4x and above, broadband noise stays
#: near 1.1 - below this threshold the pitch structure is too flat to call.
_MODE_CONCENTRATION_MIN = 2.0


class AudioExtractionError(Exception):
    """Base for user-facing extraction failures (nothing is persisted)."""


class CorruptAudioError(AudioExtractionError):
    """The bytes are not decodable audio."""


class EmptyAudioError(AudioExtractionError):
    """The audio is silent, empty, or too short to analyze."""


class TooLongError(AudioExtractionError):
    """The audio exceeds the supported duration."""


def volume_bucket_for_rms_db(rms_db: float) -> str:
    """Map RMS energy (dBFS) to the ontology's ordinal volume bucket."""
    if rms_db < RMS_DB_LOW_MAX:
        return "low"
    if rms_db < RMS_DB_MEDIUM_MAX:
        return "medium"
    return "high"


def _estimate_mode(y: np.ndarray, sr: int) -> str | None:
    """Heuristic major/minor estimate from mean chroma; None if unreliable.

    Reliability gate: the chroma profile must be concentrated (clear pitch
    structure). Broadband/noisy material has nearly flat chroma, where any
    major/minor call would be a coin flip, so it yields None instead.
    """
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    profile = chroma.mean(axis=1)
    if not np.isfinite(profile).all() or float(profile.sum()) <= 0:
        return None
    concentration = float(profile.max() / (profile.mean() + 1e-9))
    if concentration < _MODE_CONCENTRATION_MIN:
        return None
    scores = [
        (float(np.corrcoef(np.roll(profile, -shift), _MAJOR_PROFILE)[0, 1]), "major")
        for shift in range(12)
    ] + [
        (float(np.corrcoef(np.roll(profile, -shift), _MINOR_PROFILE)[0, 1]), "minor")
        for shift in range(12)
    ]
    scores.sort(key=lambda item: item[0], reverse=True)
    return scores[0][1]


def extract_audio_profile(data: bytes) -> AudioExtraction:
    """Extract the descriptive feature profile from in-memory audio bytes.

    Deterministic for a given file and library version. Raises a typed
    ``AudioExtractionError`` subclass for undecodable, silent/short, or
    over-long input; callers show the message and persist nothing.
    """
    try:
        y, sr = librosa.load(io.BytesIO(data), sr=22050, mono=True)
    except (LibsndfileError, RuntimeError, ValueError) as error:
        raise CorruptAudioError(
            f"Could not decode the file as audio ({type(error).__name__}). "
            "Supported formats: wav, flac, ogg."
        ) from error

    if y.size == 0 or float(np.abs(y).max()) == 0.0:
        raise EmptyAudioError("The file contains no audible signal (empty or silent).")

    duration_sec = float(len(y) / sr)
    if duration_sec < MIN_DURATION_SEC:
        raise EmptyAudioError(
            f"Audio is shorter than {MIN_DURATION_SEC:.1f}s; too short to analyze."
        )
    if duration_sec > MAX_DURATION_SEC:
        raise TooLongError(
            f"Audio is {duration_sec:.0f}s long; the maximum supported duration "
            f"is {MAX_DURATION_SEC:.0f}s."
        )

    tempo, _beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo_value = float(np.atleast_1d(tempo)[0])
    tempo_bpm = round(tempo_value, 1) if math.isfinite(tempo_value) else None

    rms = float(np.sqrt(np.mean(y**2)))
    rms_db = round(20.0 * math.log10(max(rms, 1e-10)), 2)

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_hz = round(float(np.mean(centroid)), 1)

    return AudioExtraction(
        duration_sec=round(duration_sec, 2),
        tempo_bpm=tempo_bpm,
        rms_db=rms_db,
        volume_bucket=volume_bucket_for_rms_db(rms_db),
        spectral_centroid_hz=centroid_hz,
        mode_estimate=_estimate_mode(y, sr),
        extractor=f"librosa {librosa.__version__}",
    )


#: MusicParameters fields the DSP can actually estimate; every other field is
#: a reviewer choice, which is what ``overridden_fields`` on approval records.
_ESTIMABLE_FIELDS = ("bpm", "volume", "tonality")


def estimated_music_defaults(profile: AudioExtraction) -> dict[str, object]:
    """Best-effort MusicParameters values from the extraction.

    Only fields with a real DSP basis are returned; ``bpm`` is included only
    when the estimate exists AND falls inside the ontology range (estimates
    are never clamped into range - an out-of-range tempo is the reviewer's
    explicit choice). Review widgets initialize from these values.
    """
    defaults: dict[str, object] = {"volume": profile.volume_bucket}
    if profile.tempo_bpm is not None and 40.0 <= profile.tempo_bpm <= 120.0:
        defaults["bpm"] = int(round(profile.tempo_bpm))
    if profile.mode_estimate is not None:
        defaults["tonality"] = profile.mode_estimate
    return defaults


def merge_music(
    final_values: dict[str, object], profile: AudioExtraction
) -> tuple[MusicParameters, list[str]]:
    """Validate the reviewer's final parameters and compute provenance.

    Returns the validated ``MusicParameters`` and the sorted list of fields
    that did NOT come unchanged from a DSP estimate (i.e. the reviewer chose
    or changed them). Raises on out-of-ontology values - estimates are never
    silently clamped.
    """
    music = MusicParameters.model_validate(final_values)
    estimates = estimated_music_defaults(profile)
    overridden = [
        field
        for field in MusicParameters.model_fields
        if not (field in _ESTIMABLE_FIELDS and final_values.get(field) == estimates.get(field))
    ]
    return music, sorted(overridden)
