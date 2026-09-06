from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SensoryProfile(BaseModel):
    """Quantitative sensory dimensions on 1-10 scales; not a clinical assessment."""

    model_config = ConfigDict(extra="forbid")

    auditory_sensitivity: int = Field(ge=1, le=10)
    sensory_seeking: int = Field(ge=1, le=10)
    change_sensitivity: int = Field(ge=1, le=10)


class SupportProfile(BaseModel):
    """Qualitative multidimensional support needs.

    Support is modelled as several named dimensions. A single
    high/medium/low functioning-level field is deliberately excluded, and
    ``extra='forbid'`` prevents one from being introduced.
    """

    model_config = ConfigDict(extra="forbid")

    communication: str = Field(min_length=1)
    sensory: str = Field(min_length=1)
    routine: str = Field(min_length=1)
    social: str = Field(min_length=1)


class Persona(BaseModel):
    """A fictional, explicitly synthetic autistic-persona profile.

    Neurodiversity safeguards: ``synthetic`` is locked to ``True``; support is
    multidimensional (SupportProfile plus named behavioural lists); and
    ``extra='forbid'`` rejects any undeclared field, so a single
    functioning-level label cannot be introduced. Every persona is fictional
    and is not representative of the autistic population.
    """

    model_config = ConfigDict(extra="forbid")

    persona_id: str
    display_name: str = Field(min_length=1)
    age_years: int = Field(ge=4, le=18)
    synthetic: Literal[True] = True
    profile_summary: str = Field(min_length=1)
    support_profile: SupportProfile
    sensory_profile: SensoryProfile
    communication_modes: list[str] = Field(min_length=1)
    music_preferences: list[str] = Field(min_length=1)
    known_triggers: list[str] = Field(min_length=1)
    preferred_supports: list[str] = Field(min_length=1)

    @field_validator("persona_id")
    @classmethod
    def persona_id_prefix(cls, value: str) -> str:
        if not value.startswith("P-"):
            raise ValueError("persona_id must start with P-")
        return value


class MusicParameters(BaseModel):
    """Controlled music-stimulus vocabulary for a synthetic trial.

    Allowed values are bounded by Pydantic ``Literal``/``Field`` constraints,
    which are the runtime-enforced source of truth. The same vocabulary is
    declared in ``config/music_ontology.json`` (kept consistent by tests) and
    documented in ``docs/scenario_rubric.md``. These are simulated inputs, not
    a prescription for a delivered clinical intervention.
    """

    genre: Literal["classical", "popular", "nature", "instrumental", "vocal"]
    bpm: int = Field(ge=40, le=120)
    volume: Literal["low", "medium", "high"]
    instrument: Literal["piano", "guitar", "percussion", "synth", "voice", "mixed"]
    tonality: Literal["major", "minor", "atonal"]
    duration_sec: int = Field(ge=60, le=300)
    lyrics_language: Literal["none", "english", "chinese"] = "none"


class AudioExtraction(BaseModel):
    """Descriptive DSP features extracted from an uploaded audio file.

    Estimates, not ground truth: tempo/mode detection are heuristics and the
    volume bucket is a researcher-defined threshold over RMS energy. Raw audio
    is never persisted anywhere in the system; only this profile and the
    source-file hash may be stored (S19 decision, D028).
    """

    model_config = ConfigDict(extra="forbid")

    duration_sec: float = Field(ge=0)
    tempo_bpm: float | None = None
    rms_db: float
    volume_bucket: Literal["low", "medium", "high"]
    spectral_centroid_hz: float = Field(ge=0)
    mode_estimate: Literal["major", "minor"] | None = None
    extractor: str = Field(min_length=1)


class TrackEntry(BaseModel):
    """An approved uploaded track: reviewed parameters + extraction provenance.

    Write-once by repository policy (duplicate ``track_id`` is refused; there
    is no update path). ``music`` is the final reviewed parameter set used to
    run trials; ``extraction`` records what the DSP actually observed and
    ``overridden_fields`` which parameters the reviewer changed. The raw
    audio file is deliberately absent: only the profile and the source-file
    sha256 are kept, so an approved track stays reproducible without hosting
    user audio (S19 decision, D028).
    """

    model_config = ConfigDict(extra="forbid")

    track_id: str
    display_name: str = Field(min_length=1)
    approved_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    source_file_name: str = Field(min_length=1)
    source_file_sha256: str = Field(min_length=64, max_length=64)
    music: MusicParameters
    extraction: AudioExtraction
    overridden_fields: list[str] = []
    notes: str = ""
    synthetic: Literal[True] = True

    @field_validator("track_id")
    @classmethod
    def track_id_prefix(cls, value: str) -> str:
        if not value.startswith("TRK-"):
            raise ValueError("track_id must start with TRK-")
        return value


class TimeStage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: Literal["start", "middle", "end"]
    observation: str
    anxiety_level: int = Field(ge=1, le=10)
    engagement_level: int = Field(ge=1, le=10)


class ReactionOutput(BaseModel):
    """Synthetic, non-clinical reaction hypothesis for one trial.

    The numeric fields are researcher-defined descriptive software signals
    constructed from a synthetic persona and music parameters. They are not
    validated clinical instruments and must not be reported as clinical
    evidence (see ``config/music_ontology.json`` outcome_dimensions).
    """

    model_config = ConfigDict(extra="forbid")

    anxiety_level: int = Field(ge=1, le=10)
    engagement_level: int = Field(ge=1, le=10)
    mood_score: int = Field(ge=1, le=10)
    regulation_score: int = Field(ge=1, le=10)
    attention_duration_sec: int = Field(ge=0, le=1800)
    physical_observations: list[str]
    communication_observations: list[str]
    time_series: list[TimeStage]
    research_notes: str
    uncertainty_note: str
    safety_flags: list[str] = []
    synthetic: Literal[True] = True

    @field_validator("time_series")
    @classmethod
    def time_series_complete(cls, value: list[TimeStage]) -> list[TimeStage]:
        """A reaction must carry exactly one start, middle, and end stage, in order."""
        stages = [stage.stage for stage in value]
        if stages != ["start", "middle", "end"]:
            raise ValueError(
                f"time_series must be exactly ['start', 'middle', 'end'], got {stages}"
            )
        return value


class TrialRecord(BaseModel):
    """One synthetic trial with full provenance.

    ``scene`` is one of the five support scenarios whose software outcome
    rubric and stop conditions are defined in ``docs/scenario_rubric.md`` and
    ``config/music_ontology.json``. Every record carries engine/model/prompt/
    seed/timestamp provenance and a fixed synthetic disclaimer.
    """

    model_config = ConfigDict(extra="forbid")

    trial_id: str
    persona_id: str
    scene: Literal[
        "sleep_support",
        "anxiety_support",
        "focus_support",
        "engagement_support",
        "regulation_support",
    ]
    music: MusicParameters
    reaction: ReactionOutput
    engine: Literal["deterministic", "openai"]
    model_name: str | None = None
    prompt_version: str
    seed: int | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    disclaimer: str = (
        "Synthetic educational simulation; not a clinical prediction or treatment recommendation."
    )
