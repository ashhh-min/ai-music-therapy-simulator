from __future__ import annotations

from datetime import datetime, timezone
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
    genre: Literal["classical", "popular", "nature", "instrumental", "vocal"]
    bpm: int = Field(ge=40, le=120)
    volume: Literal["low", "medium", "high"]
    instrument: Literal["piano", "guitar", "percussion", "synth", "voice", "mixed"]
    tonality: Literal["major", "minor", "atonal"]
    duration_sec: int = Field(ge=60, le=300)
    lyrics_language: Literal["none", "english", "chinese"] = "none"


class TimeStage(BaseModel):
    stage: Literal["start", "middle", "end"]
    observation: str
    anxiety_level: int = Field(ge=1, le=10)
    engagement_level: int = Field(ge=1, le=10)


class ReactionOutput(BaseModel):
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


class TrialRecord(BaseModel):
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
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    disclaimer: str = (
        "Synthetic educational simulation; not a clinical prediction or treatment recommendation."
    )
