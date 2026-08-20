import json
import os
from pathlib import Path

import pytest

from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord
from ai_music_therapy.repository import Repository

# Tests need a reachable PostgreSQL (docker compose up -d). They are skipped
# with an explicit message when it is not running so key-free local checks and
# CI-without-DB remain green.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator_test"
)


def _postgres_available() -> bool:
    import psycopg

    # Probe the maintenance database, not the (possibly not-yet-created) test DB.
    base, _, _dbname = TEST_DATABASE_URL.rpartition("/")
    try:
        with psycopg.connect(base + "/postgres", connect_timeout=3):
            return True
    except psycopg.OperationalError:
        return False


# Create the dedicated test database once per session (connect to the default
# maintenance DB, CREATE DATABASE, then use it for every test).
@pytest.fixture(scope="session", autouse=True)
def _test_database():
    if not _postgres_available():
        pytest.skip("PostgreSQL not reachable; start it with `docker compose up -d`")
    base, _, dbname = TEST_DATABASE_URL.rpartition("/")
    if not dbname:
        pytest.skip("TEST_DATABASE_URL must include a database name")
    import psycopg

    with psycopg.connect(base + "/postgres", connect_timeout=3, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{dbname}"')
    yield


@pytest.fixture
def repo(_test_database) -> Repository:
    repo = Repository(TEST_DATABASE_URL)
    repo.initialize()
    with repo.connect() as conn:
        conn.execute("TRUNCATE trials, personas")
    return repo


def _persona() -> Persona:
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    return Persona.model_validate(payload[0])


def _build_trial(persona: Persona) -> TrialRecord:
    music = MusicParameters(
        genre="instrumental", bpm=60, volume="low", instrument="piano",
        tonality="major", duration_sec=180,
    )
    reaction, seed = simulate(persona, music, "sleep_support")
    return TrialRecord(
        trial_id="T-RT", persona_id=persona.persona_id, scene="sleep_support",
        music=music, reaction=reaction, engine="deterministic",
        prompt_version="test", seed=seed,
    )


def test_repository_round_trip(repo):
    persona = _persona()
    repo.upsert_persona(persona)
    assert repo.get_persona(persona.persona_id) == persona


def test_upsert_persona_is_idempotent(repo):
    persona = _persona()
    repo.upsert_persona(persona)
    repo.upsert_persona(persona)
    assert len(repo.list_personas()) == 1


def test_trial_round_trip(repo):
    persona = _persona()
    repo.upsert_persona(persona)
    trial = _build_trial(persona)
    repo.save_trial(trial)
    trials = repo.list_trials()
    assert len(trials) == 1
    assert trials[0] == trial


def test_initialize_is_idempotent(repo):
    repo.initialize()
    repo.initialize()
    assert repo.list_personas() == []


def test_seed_demo_is_idempotent(repo, monkeypatch, capsys):
    import dataclasses

    from ai_music_therapy import seed_demo

    monkeypatch.setattr(
        seed_demo, "settings", dataclasses.replace(seed_demo.settings,
                                                   database_url=TEST_DATABASE_URL)
    )
    seed_demo.main()
    seed_demo.main()
    personas = repo.list_personas()
    assert len(personas) == 5
    assert len({p.persona_id for p in personas}) == 5
    assert "5 synthetic personas" in capsys.readouterr().out


def test_synthetic_only_guard_is_enforced_by_database(repo):
    import psycopg
    import pytest as _pytest

    repo.upsert_persona(_persona())
    with _pytest.raises(psycopg.errors.CheckViolation):
        with repo.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO personas(persona_id, payload_json, synthetic) "
                    "VALUES ('P-FAKE', '{}', 0)"
                )


def test_persisted_trial_preserves_provenance(repo):
    import json

    persona = _persona()
    repo.upsert_persona(persona)
    trial = _build_trial(persona)
    trial.trial_id = "T-PROV"
    repo.save_trial(trial)

    with repo.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT trial_id, persona_id, scene, engine, model_name, "
                "prompt_version, seed, created_at, synthetic, payload_json "
                "FROM trials WHERE trial_id = 'T-PROV'"
            )
            row = cur.fetchone()

    payload = json.loads(row["payload_json"])
    for key in (
        "trial_id", "persona_id", "scene", "music", "reaction",
        "engine", "model_name", "prompt_version", "seed", "created_at",
        "disclaimer",
    ):
        assert key in payload, f"missing provenance key: {key}"
    assert row["synthetic"] == 1
    assert row["engine"] == trial.engine == payload["engine"]
    assert row["prompt_version"] == trial.prompt_version == payload["prompt_version"]
    assert row["seed"] == trial.seed == payload["seed"]
