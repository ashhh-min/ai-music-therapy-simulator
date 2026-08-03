from __future__ import annotations

from openai import OpenAI

from .config import settings
from .models import MusicParameters, Persona, ReactionOutput


SYSTEM_BOUNDARY = """
You are generating synthetic educational research content for a software prototype.
Never claim to predict a real autistic child's behavior, diagnose anyone, prescribe treatment,
or establish therapeutic effectiveness. Use respectful neurodiversity language. Treat the
provided persona as fictional. Return only the requested structured object. Include uncertainty
and safety flags when the configured sound could be distressing.
""".strip()


def simulate_with_openai(persona: Persona, music: MusicParameters, scene: str) -> ReactionOutput:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured; use deterministic mode.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_BOUNDARY},
            {
                "role": "user",
                "content": (
                    "Create one synthetic reaction hypothesis.\n"
                    f"Scene: {scene}\n"
                    f"Persona JSON: {persona.model_dump_json()}\n"
                    f"Music JSON: {music.model_dump_json()}\n"
                    "The time_series must include start, middle, and end exactly once."
                ),
            },
        ],
        text_format=ReactionOutput,
        store=False,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model did not return a parsed structured output.")
    return response.output_parsed
