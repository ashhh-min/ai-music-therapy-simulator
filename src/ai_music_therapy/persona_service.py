from __future__ import annotations

import json
from dataclasses import dataclass, field

from openai import OpenAI
from pydantic import ValidationError

from .config import settings
from .models import Persona
from .repository import Repository

SYSTEM_BOUNDARY = (
    "You are drafting a fictional, explicitly synthetic persona profile for an "
    "educational software prototype about music-based support scenarios.\n"
    "Hard rules: the persona is fictional and must never resemble a real child; "
    "profile_summary must state that the profile is synthetic; use respectful "
    "neurodiversity language; do NOT use functioning-level labels such as "
    "high-functioning or low-functioning; support must be described "
    "multidimensionally (communication, sensory, routine, social); do not "
    "pathologize or use deficit-only framing; never claim the profile represents "
    "the autistic population.\n"
    f"The object must contain EXACTLY these fields and no others: "
    f"{', '.join(Persona.model_fields)}.\n"
    "Nested object shapes: sensory_profile has auditory_sensitivity, "
    "sensory_seeking, change_sensitivity - each an INTEGER from 1 to 10, never "
    "prose. support_profile has communication, sensory, routine, social - each "
    "a descriptive string.\n"
    "persona_id must start with P- and must be unique. age_years is between 4 "
    "and 18. communication_modes, music_preferences, known_triggers, and "
    "preferred_supports are non-empty arrays of strings. Return only JSON."
)

# Heuristic stereotype markers a reviewer must resolve before acceptance.
# Deliberately plain-worded: this lint is a safety net, not the review itself.
_STEREOTYPE_MARKERS = (
    "high-functioning",
    "low-functioning",
    "functioning level",
    "suffers from",
    "suffers from autism",
    "afflicted",
    "deficient",
    "normal child",
    "cured",
    "cure autism",
    "tragic",
    "burden",
)

_HARD_KEYS = ("stereotype", "synthetic-wording")


@dataclass
class PersonaDraft:
    """A candidate persona awaiting human review. Never persisted by itself."""

    persona: Persona
    source: str
    created_at: str
    flags: list[str] = field(default_factory=list)


class DraftRejected(Exception):
    """A draft cannot be accepted in its current state."""


def lint_persona(persona: Persona, existing: list[Persona]) -> list[str]:
    """Return human-review flags for a candidate persona.

    Two flag kinds: hard flags (stereotype wording, missing synthetic wording)
    block acceptance until the text is revised; soft flags (near-duplicate)
    require explicit confirmation. The lint is heuristic - the human reviewer,
    not this code, makes the final call.
    """
    flags: list[str] = []
    texts = " ".join(
        [persona.profile_summary, *persona.communication_modes,
         *persona.music_preferences, *persona.known_triggers,
         *persona.preferred_supports]
    ).lower()
    for marker in _STEREOTYPE_MARKERS:
        if marker in texts:
            flags.append(f"stereotype: wording '{marker}' requires revision")
    if "synthetic" not in persona.profile_summary.lower():
        flags.append("synthetic-wording: profile_summary must state the profile is synthetic")
    for other in existing:
        same_support = persona.support_profile == other.support_profile
        same_modes = set(persona.communication_modes) == set(other.communication_modes)
        same_triggers = set(persona.known_triggers) == set(other.known_triggers)
        if same_support and same_modes and same_triggers:
            flags.append(
                f"near-duplicate: profile structurally matches approved persona "
                f"{other.persona_id} ({other.display_name}); confirm diversity"
            )
            break
    return flags


def draft_persona_with_openai(brief: str) -> PersonaDraft:
    """Ask the AI for a candidate persona. Requires a key; never saves anything."""
    from datetime import UTC, datetime

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured; personas can still be written by hand."
        )

    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    feedback: str | None = None
    last_error: Exception | None = None
    for _attempt in range(2):
        user = f"Draft one synthetic persona. Design brief: {brief}"
        if feedback:
            user += (
                "\nYour previous attempt failed validation. Fix it and return only "
                f"the corrected JSON object. Validation errors:\n{feedback}"
            )
        response = client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_BOUNDARY},
                {"role": "user", "content": user},
            ],
            text={"format": {"type": "json_object"}},
            store=False,
        )
        try:
            data = json.loads(response.output_text)
            if isinstance(data, dict):
                data.pop("synthetic", None)  # locked to True by the schema anyway
            persona = Persona.model_validate(data)
            return PersonaDraft(
                persona=persona,
                source="ai",
                created_at=datetime.now(UTC).isoformat(),
                flags=lint_persona(persona, []),
            )
        except (json.JSONDecodeError, ValidationError) as error:
            last_error = error
            feedback = str(error)[:2000]
    raise RuntimeError(f"AI persona draft failed validation after retry; rejecting: {last_error}")


def approve_and_save(
    repo: Repository,
    draft: PersonaDraft,
    existing: list[Persona],
    confirm_similar: bool = False,
) -> Persona:
    """Run the review gates and save only on an explicit, human-driven accept.

    Gates: schema (already enforced by the Persona type); stereotype/synthetic
    wording must be re-linted clean after any revision; near-duplicate requires
    confirm_similar; and an approved persona_id can never be overwritten - only
    genuinely new IDs are saved.
    """
    flags = lint_persona(draft.persona, existing)
    hard = [f for f in flags if f.split(":")[0] in _HARD_KEYS]
    if hard:
        raise DraftRejected("revise first: " + "; ".join(hard))
    soft = [f for f in flags if f.split(":")[0] not in _HARD_KEYS]
    if soft and not confirm_similar:
        raise DraftRejected("confirm required: " + "; ".join(soft))
    if any(p.persona_id == draft.persona.persona_id for p in existing):
        raise DraftRejected(
            f"persona_id {draft.persona.persona_id} already exists; approved "
            "personas cannot be overwritten - choose a new ID"
        )
    repo.upsert_persona(draft.persona)
    return draft.persona
