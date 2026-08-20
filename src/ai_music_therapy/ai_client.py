from __future__ import annotations

import json

from openai import OpenAI
from pydantic import ValidationError

from .config import settings
from .models import MusicParameters, Persona, ReactionOutput, TimeStage

SYSTEM_BOUNDARY = (
    """You are generating synthetic educational research content for a software prototype.
Never claim to predict a real autistic child's behavior, diagnose anyone, prescribe treatment,
or establish therapeutic effectiveness. Use respectful neurodiversity language. Treat the
provided persona as fictional. Return only the requested structured object as JSON.
The object must contain EXACTLY these fields and no others: {_FIELDS}.
All numeric scores are integers between 1 and 10. physical_observations and
communication_observations are arrays of strings. time_series is an array with exactly
three objects whose stage values are start, middle, and end in that order.
Include uncertainty_note and safety_flags (empty array if none).""".format(
        _FIELDS=", ".join(ReactionOutput.model_fields)
    )
)

_LIST_FIELDS = ("physical_observations", "communication_observations")
_STAGE_ORDER = ("start", "middle", "end")


def _sanitize(data: object) -> object:
    """Drop unknown keys and tolerate common provider JSON drift.

    Never repairs values that fail validation: out-of-range scores, wrong types,
    or missing required fields still raise, so invalid AI output can never pass
    the boundary. Only shape drift that carries no semantic change is fixed:
    unknown keys (dropped), a bare string where a list is expected, and
    time-series stages returned out of order.
    """
    if not isinstance(data, dict):
        return data
    known = set(ReactionOutput.model_fields)
    out = {k: v for k, v in data.items() if k in known}
    for field in _LIST_FIELDS:
        if isinstance(out.get(field), str):
            out[field] = [out[field]]
    stages = out.get("time_series")
    if isinstance(stages, list):
        stage_known = set(TimeStage.model_fields)
        cleaned = []
        for stage in stages:
            if isinstance(stage, dict):
                cleaned.append({k: v for k, v in stage.items() if k in stage_known})
        by_stage = {s.get("stage"): s for s in cleaned if s.get("stage") in _STAGE_ORDER}
        if sorted(by_stage) == sorted(_STAGE_ORDER):
            out["time_series"] = [by_stage[name] for name in _STAGE_ORDER]
    return out


def _user_message(
    persona: Persona, music: MusicParameters, scene: str, feedback: str | None
) -> str:
    message = (
        "Create one synthetic reaction hypothesis.\n"
        f"Scene: {scene}\n"
        f"Persona JSON: {persona.model_dump_json()}\n"
        f"Music JSON: {music.model_dump_json()}\n"
        "The time_series must include start, middle, and end exactly once."
    )
    if feedback:
        message += (
            "\nYour previous attempt failed validation. Fix it and return only the "
            f"corrected JSON object. Validation errors:\n{feedback}"
        )
    return message


def simulate_with_openai(persona: Persona, music: MusicParameters, scene: str) -> ReactionOutput:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured; use deterministic mode.")

    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    feedback: str | None = None
    last_error: Exception | None = None
    for _attempt in range(2):
        response = client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_BOUNDARY},
                {"role": "user", "content": _user_message(persona, music, scene, feedback)},
            ],
            text={"format": {"type": "json_object"}},
            store=False,
        )
        try:
            data = json.loads(response.output_text)
            return ReactionOutput.model_validate(_sanitize(data))
        except (json.JSONDecodeError, ValidationError) as error:
            last_error = error
            feedback = str(error)[:2000]
    raise RuntimeError(f"AI output failed validation after retry; rejecting: {last_error}")


def ai_trial(
    persona: Persona, music: MusicParameters, scene: str
) -> tuple[ReactionOutput, str | None]:
    """Run one AI trial and return the validated reaction plus provenance model name.

    Centralizes the provenance contract used by the trial workflow: AI trials
    record the configured model name and no seed (AI output is not reproducible).
    """
    return simulate_with_openai(persona, music, scene), settings.openai_model
