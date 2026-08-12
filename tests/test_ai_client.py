import types

import pytest

from ai_music_therapy.ai_client import simulate_with_openai
from ai_music_therapy.models import MusicParameters


def _music() -> MusicParameters:
    return MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180,
    )


def test_ai_client_raises_without_key(monkeypatch):
    # Force the no-key condition regardless of the local environment; the call must
    # fail before any network access, so the test never depends on a live API.
    monkeypatch.setattr(
        "ai_music_therapy.ai_client.settings",
        types.SimpleNamespace(openai_api_key=None, openai_model="gpt-test"),
    )
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        simulate_with_openai(None, _music(), "sleep_support")
