"""S12 - trial execution workflow: both engines, temporal sequence, failure handling."""

import json
import os
import types
import uuid
from pathlib import Path

import psycopg
import pytest
from pydantic import ValidationError

from ai_music_therapy.ai_client import ai_trial
from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona, ReactionOutput, TrialRecord
from ai_music_therapy.repository import Repository

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator_test"
)


def _pg_available() -> bool:
    base = TEST_DATABASE_URL.rsplit("/", 1)[0]
    try:
        with psycopg.connect(base + "/postgres", connect_timeout=3):
            return True
    except psycopg.OperationalError:
        return False


@pytest.fixture
def repo():
    if not _pg_available():
        pytest.skip("PostgreSQL not reachable; start it with `docker compose up -d`")
    repository = Repository(TEST_DATABASE_URL)
    repository.initialize()
    with repository.connect() as conn:
        conn.execute("TRUNCATE trials, personas")
    return repository


def _persona() -> Persona:
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    return Persona.model_validate(payload[0])


def _music() -> MusicParameters:
    return MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180,
    )


def _trial(reaction, engine, model_name, seed, persona_id="P-LILY") -> TrialRecord:
    return TrialRecord(
        trial_id=f"T-{uuid.uuid4().hex[:8].upper()}",
        persona_id=persona_id,
        scene="sleep_support",
        music=_music(),
        reaction=reaction,
        engine=engine,
        model_name=model_name,
        prompt_version="test",
        seed=seed,
    )


def test_both_engines_share_the_same_validated_schema():
    deterministic, seed = simulate(_persona(), _music(), "sleep_support")
    assert isinstance(deterministic, ReactionOutput)
    # The AI path is schema-identical: its return type is the same validated
    # model (field sets must match exactly, so downstream code cannot tell the
    # engines apart except via provenance).
    assert set(type(deterministic).model_fields) == set(ReactionOutput.model_fields)
    assert deterministic.synthetic is True
    assert seed is not None
    # AI provenance contract: model name recorded, seed None (not reproducible).
    class _Fake:
        def __init__(self, reaction):
            self._reaction = reaction

        def __call__(self, persona, music, scene):
            return self._reaction

    reaction = simulate(_persona(), _music(), "focus_support")[0]
    import ai_music_therapy.ai_client as ai_client_module

    original = ai_client_module.simulate_with_openai
    ai_client_module.simulate_with_openai = _Fake(reaction)
    try:
        ai_reaction, model_name = ai_trial(_persona(), _music(), "focus_support")
    finally:
        ai_client_module.simulate_with_openai = original
    assert type(ai_reaction) is ReactionOutput
    assert set(type(ai_reaction).model_fields) == set(ReactionOutput.model_fields)
    assert model_name  # provenance model name always present for AI trials


def test_deterministic_trial_persists_with_full_provenance(repo):
    persona = _persona()
    repo.upsert_persona(persona)
    reaction, seed = simulate(persona, _music(), "sleep_support")
    trial = _trial(reaction, "deterministic", None, seed, persona.persona_id)
    repo.save_trial(trial)
    loaded = repo.list_trials()
    assert len(loaded) == 1
    assert loaded[0].seed == seed
    assert loaded[0].engine == "deterministic"
    assert loaded[0].model_name is None
    assert [s.stage for s in loaded[0].reaction.time_series] == ["start", "middle", "end"]


def test_ai_trial_persists_with_model_provenance(repo, monkeypatch):
    persona = _persona()
    repo.upsert_persona(persona)
    reaction, _ = simulate(persona, _music(), "sleep_support")
    monkeypatch.setattr(
        "ai_music_therapy.ai_client.simulate_with_openai",
        lambda p, m, s: reaction,
    )
    monkeypatch.setattr(
        "ai_music_therapy.ai_client.settings",
        types.SimpleNamespace(openai_model="test-model"),
    )
    ai_reaction, model_name = ai_trial(persona, _music(), "sleep_support")
    trial = _trial(ai_reaction, "openai", model_name, None, persona.persona_id)
    repo.save_trial(trial)
    loaded = repo.list_trials()[0]
    assert loaded.engine == "openai"
    assert loaded.model_name == "test-model"
    assert loaded.seed is None  # AI output is not reproducible - never faked


def test_refused_ai_output_is_not_persisted(repo, monkeypatch):
    persona = _persona()
    repo.upsert_persona(persona)

    def refuse(persona, music, scene):
        raise RuntimeError("AI output failed validation after retry; rejecting: ...")

    monkeypatch.setattr("ai_music_therapy.ai_client.simulate_with_openai", refuse)
    with pytest.raises(RuntimeError, match="failed validation"):
        ai_trial(persona, _music(), "sleep_support")
    assert repo.list_trials() == []  # nothing persisted on refusal


def test_time_series_must_be_complete_ordered_sequence():
    reaction, _ = simulate(_persona(), _music(), "sleep_support")
    data = reaction.model_dump()
    complete = ReactionOutput.model_validate(data)
    assert [s.stage for s in complete.time_series] == ["start", "middle", "end"]

    missing = dict(data)
    missing["time_series"] = data["time_series"][:2]
    with pytest.raises(ValidationError, match="start.*middle.*end"):
        ReactionOutput.model_validate(missing)

    reordered = dict(data)
    reordered["time_series"] = list(reversed(data["time_series"]))
    with pytest.raises(ValidationError, match="start.*middle.*end"):
        ReactionOutput.model_validate(reordered)

    duplicated = dict(data)
    duplicated["time_series"] = data["time_series"] + [data["time_series"][0]]
    with pytest.raises(ValidationError, match="start.*middle.*end"):
        ReactionOutput.model_validate(duplicated)


def test_uncertainty_and_flags_present_on_every_output():
    for scene in ("sleep_support", "anxiety_support", "focus_support",
                  "engagement_support", "regulation_support"):
        reaction, _ = simulate(_persona(), _music(), scene)
        assert reaction.uncertainty_note  # always visible in the UI
        assert isinstance(reaction.safety_flags, list)
