"""S13 - audit trail: provenance completeness, duplicate/incomplete rejection,
filtering, and labeled export."""

import csv
import io
import json
import os
import uuid
from pathlib import Path

import psycopg
import pytest
from pydantic import ValidationError

from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.export import LIMITATIONS_TEXT, trials_to_csv, trials_to_json
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord
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


def _trial(persona_id: str, scene: str, engine: str = "deterministic") -> TrialRecord:
    reaction, seed = simulate(_persona(), _music(), scene)
    model_name = None if engine == "deterministic" else "test-model"
    return TrialRecord(
        trial_id=f"T-{uuid.uuid4().hex[:8].upper()}",
        persona_id=persona_id,
        scene=scene,
        music=_music(),
        reaction=reaction,
        engine=engine,
        model_name=model_name,
        prompt_version="2026-08-01.v1",
        seed=seed if engine == "deterministic" else None,
    )


@pytest.fixture
def seeded(repo):
    repo.upsert_persona(_persona())
    trials = [
        _trial("P-LILY", "sleep_support"),
        _trial("P-LILY", "focus_support"),
        _trial("P-LILY", "sleep_support", engine="openai"),
    ]
    for trial in trials:
        repo.save_trial(trial)
    return repo, trials


def test_every_trial_carries_full_provenance(seeded):
    repo, trials = seeded
    for trial in repo.list_trials():
        assert trial.engine in ("deterministic", "openai")
        assert trial.prompt_version
        assert trial.created_at
        assert trial.disclaimer  # fixed limitations text travels with the record
        assert trial.reaction.synthetic is True
        if trial.engine == "deterministic":
            assert trial.seed is not None
        else:
            assert trial.model_name is not None
            assert trial.seed is None


def test_duplicate_trial_id_is_rejected(seeded):
    repo, trials = seeded
    original = trials[0]
    duplicate = original.model_copy(deep=True)
    with pytest.raises(ValueError, match="Duplicate trial_id"):
        repo.save_trial(duplicate)
    assert len(repo.list_trials()) == 3  # unchanged; nothing overwritten


def test_incomplete_records_are_rejected(seeded):
    complete = seeded[1][0].model_dump()
    for missing in ("trial_id", "engine", "prompt_version", "reaction", "music"):
        incomplete = {k: v for k, v in complete.items() if k != missing}
        with pytest.raises(ValidationError):
            TrialRecord.model_validate(incomplete)


def test_get_trial_returns_full_record(seeded):
    repo, trials = seeded
    assert repo.get_trial(trials[0].trial_id) == trials[0]
    with pytest.raises(KeyError):
        repo.get_trial("T-DOES-NOT-EXIST")


def test_list_trials_filters_compose(seeded):
    repo, _ = seeded
    assert len(repo.list_trials()) == 3
    assert len(repo.list_trials(persona_id="P-LILY")) == 3
    assert len(repo.list_trials(scene="sleep_support")) == 2
    assert len(repo.list_trials(engine="openai")) == 1
    combined = repo.list_trials(persona_id="P-LILY", scene="sleep_support", engine="openai")
    assert len(combined) == 1
    assert repo.list_trials(persona_id="P-NOPE") == []


def test_csv_export_is_labeled_synthetic_with_limitations(seeded):
    _repo, trials = seeded
    rows = list(csv.DictReader(io.StringIO(trials_to_csv(trials))))
    assert len(rows) == 3
    for row in rows:
        assert row["synthetic"] == "true"
        assert row["limitations"] == LIMITATIONS_TEXT
        assert row["engine"] and row["prompt_version"] and row["created_at"]
    ai_row = next(r for r in rows if r["engine"] == "openai")
    assert ai_row["model_name"] == "test-model" and ai_row["seed"] == ""
    det = next(r for r in rows if r["engine"] == "deterministic")
    assert det["seed"]


def test_json_export_is_full_fidelity_and_labeled(seeded):
    _repo, trials = seeded
    document = json.loads(trials_to_json(trials))
    assert document["synthetic"] is True
    assert document["limitations"] == LIMITATIONS_TEXT
    assert document["count"] == 3
    exported = [TrialRecord.model_validate(t) for t in document["trials"]]
    assert sorted(t.trial_id for t in exported) == sorted(t.trial_id for t in trials)
    # Round-trip: the exported records are complete trial records with disclaimer.
    assert all(t.disclaimer for t in exported)
