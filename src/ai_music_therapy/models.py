from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SensoryProfile(BaseModel):
    auditory_sensitivity: int = Field(ge=1, le=10)
    sensory_seeking: int = Field(ge=1, le=10)
    change_sensitivity: int = Field(ge=1, le=10)


class Persona(BaseModel):
    persona_id: str
    display_name: str
    age_years: int = Field(ge=4, le=18)
    synthetic: Literal[True] = True
    profile_summary: str
    support_profile: dict[str, str]
    sensory_profile: SensoryProfile
    communication_modes: list[str]
    music_preferences: list[str]
    known_triggers: list[str]
    preferred_supports: list[str]

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
