import json
import types
from pathlib import Path

import pytest

from ai_music_therapy.ai_client import simulate_with_openai
from ai_music_therapy.models import MusicParameters, Persona, ReactionOutput


def _persona() -> Persona:
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    return Persona.model_validate(payload[0])


def _music() -> MusicParameters:
    return MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180,
    )


def _settings(**overrides):
    base = dict(
        openai_api_key="test-key",
        openai_model="test-model",
        openai_base_url="https://api.test.example/v1",
    )
    base.update(overrides)
    return types.SimpleNamespace(**base)


class _FakeResponse:
    def __init__(self, text: str):
        self.output_text = text


def _valid_payload() -> dict:
    return {
        "anxiety_level": 3,
        "engagement_level": 6,
        "mood_score": 5,
        "regulation_score": 6,
        "attention_duration_sec": 120,
        "physical_observations": ["Synthetic observation."],
        "communication_observations": ["Synthetic response."],
        "time_series": [
            {"stage": "start", "observation": "Orientation.",
             "anxiety_level": 4, "engagement_level": 5},
            {"stage": "middle", "observation": "Settling.",
             "anxiety_level": 3, "engagement_level": 6},
            {"stage": "end", "observation": "End state.",
             "anxiety_level": 3, "engagement_level": 6},
        ],
        "research_notes": "Synthetic note.",
        "uncertainty_note": "High uncertainty.",
        "safety_flags": [],
    }


def _patch_transport(monkeypatch, replies):
    """Replace the OpenAI client with a fake returning `replies` in order.

    Returns the list of captured request kwargs so tests can assert on them.
    """
    calls: list[dict] = []

    class _FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            reply = replies[min(len(calls) - 1, len(replies) - 1)]
            return _FakeResponse(reply)

    class _FakeClient:
        def __init__(self, **kwargs):
            self.responses = _FakeResponses()

    monkeypatch.setattr("ai_music_therapy.ai_client.OpenAI", _FakeClient)
    return calls


def test_ai_client_raises_without_key(monkeypatch):
    # Force the no-key condition regardless of the local environment; the call must
    # fail before any network access, so the test never depends on a live API.
    monkeypatch.setattr("ai_music_therapy.ai_client.settings", _settings(openai_api_key=None))
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        simulate_with_openai(_persona(), _music(), "sleep_support")


def test_valid_output_parses_and_validates(monkeypatch):
    monkeypatch.setattr("ai_music_therapy.ai_client.settings", _settings())
    calls = _patch_transport(monkeypatch, [json.dumps(_valid_payload())])
    reaction = simulate_with_openai(_persona(), _music(), "sleep_support")
    assert isinstance(reaction, ReactionOutput)
    assert reaction.synthetic is True
    assert [s.stage for s in reaction.time_series] == ["start", "middle", "end"]
    # Acceptance: Responses API + storage disabled + configured model.
    assert calls[0]["store"] is False
    assert calls[0]["model"] == "test-model"
    assert calls[0]["text"] == {"format": {"type": "json_object"}}


def test_provider_drift_is_sanitized(monkeypatch):
    monkeypatch.setattr("ai_music_therapy.ai_client.settings", _settings())
    payload = _valid_payload()
    payload["hypothesis_id"] = "RH-1"          # unknown key -> dropped
    payload["physical_observations"] = "One string."  # bare string -> wrapped
    payload["time_series"] = list(reversed(payload["time_series"]))  # order fixed
    for stage in payload["time_series"]:
        stage["extra"] = "dropped"
    calls = _patch_transport(monkeypatch, [json.dumps(payload)])
    reaction = simulate_with_openai(_persona(), _music(), "sleep_support")
    assert reaction.physical_observations == ["One string."]
    assert [s.stage for s in reaction.time_series] == ["start", "middle", "end"]
    assert len(calls) == 1  # drift alone must not consume the retry


def test_invalid_json_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr("ai_music_therapy.ai_client.settings", _settings())
    calls = _patch_transport(
        monkeypatch, ["not json at all", json.dumps(_valid_payload())]
    )
    reaction = simulate_with_openai(_persona(), _music(), "sleep_support")
    assert isinstance(reaction, ReactionOutput)
    assert len(calls) == 2
    assert "failed validation" in calls[1]["input"][1]["content"]


def test_out_of_range_score_is_rejected_not_clamped(monkeypatch):
    monkeypatch.setattr("ai_music_therapy.ai_client.settings", _settings())
    payload = _valid_payload()
    payload["anxiety_level"] = 12  # out of range: sanitizer must not repair this
    calls = _patch_transport(monkeypatch, [json.dumps(payload), json.dumps(payload)])
    with pytest.raises(RuntimeError, match="failed validation"):
        simulate_with_openai(_persona(), _music(), "sleep_support")
    assert len(calls) == 2  # retried once with feedback, then rejected


def test_missing_required_field_is_rejected(monkeypatch):
    monkeypatch.setattr("ai_music_therapy.ai_client.settings", _settings())
    payload = _valid_payload()
    del payload["mood_score"]
    _patch_transport(monkeypatch, [json.dumps(payload), json.dumps(payload)])
    with pytest.raises(RuntimeError, match="failed validation"):
        simulate_with_openai(_persona(), _music(), "sleep_support")
