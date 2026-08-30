"""Tests for the S18 connection hardening: pool, transaction, retry, concurrency.

These exercise the layered database stack directly (factory -> pooled manager
-> transaction -> retry) plus the multi-user simulated deployment test. They
need a reachable PostgreSQL and skip with a message otherwise, mirroring
``tests/test_repository.py``.
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import psycopg
import pytest

from ai_music_therapy.db import ConnectionFactory, PooledConnectionManager
from ai_music_therapy.models import Persona

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator_test"
)


def _postgres_available() -> bool:
    base, _, _dbname = TEST_DATABASE_URL.rpartition("/")
    try:
        with psycopg.connect(base + "/postgres", connect_timeout=3):
            return True
    except psycopg.OperationalError:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not reachable; start it with `docker compose up -d`",
)


@pytest.fixture()
def manager() -> PooledConnectionManager:
    manager = PooledConnectionManager(TEST_DATABASE_URL, min_size=1, max_size=4)
    yield manager
    manager.close()


def _count_rows(conn: psycopg.Connection, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) AS n FROM {table}")
        return cur.fetchone()["n"]


def test_pool_reuses_connections_across_operations(manager: PooledConnectionManager):
    def op(conn: psycopg.Connection) -> int:
        return _count_rows(conn, "personas")

    for _ in range(20):
        manager.run(op)
    # 20 sequential operations must not open 20 connections
    assert manager._factory.connections_opened <= 2


def test_transaction_commits_and_rolls_back(manager: PooledConnectionManager):
    manager.run(lambda conn: conn.execute("DELETE FROM trials"))
    manager.run(lambda conn: conn.execute("DELETE FROM personas"))

    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    persona = Persona.model_validate(payload[0])

    manager.run(lambda conn: conn.execute("SELECT 1"))  # ensure schema init upstream
    from ai_music_therapy.repository import Repository

    repository = Repository(TEST_DATABASE_URL, manager=manager)
    repository.initialize()
    repository.upsert_persona(persona)

    # committed work is visible
    assert repository.get_persona(persona.persona_id).persona_id == persona.persona_id

    # an operation that raises mid-transaction rolls everything back
    def failing_op(conn: psycopg.Connection) -> None:
        conn.execute(
            "INSERT INTO personas(persona_id, payload_json, synthetic) "
            "VALUES ('P-ROLLBACK', %s, 1)",
            (persona.model_dump_json(),),
        )
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        manager.run(failing_op)
    with pytest.raises(KeyError):
        repository.get_persona("P-ROLLBACK")


def test_run_retries_transient_connection_errors():
    manager = PooledConnectionManager(
        "postgresql://unreachable.invalid:5432/x", max_attempts=3, retry_backoff=0.0
    )
    # replace the transaction path: first two attempts lose the connection,
    # the third succeeds - proving retry semantics without a real server
    original = manager.transaction
    attempt_counter = {"n": 0}

    def flaky_transaction():
        from contextlib import contextmanager

        @contextmanager
        def _tx():
            attempt_counter["n"] += 1
            if attempt_counter["n"] < 3:
                raise psycopg.OperationalError("server closed the connection")
            yield "connection"

        return _tx()

    manager.transaction = flaky_transaction  # type: ignore[method-assign]
    result = manager.run(lambda conn: "ok")
    assert result == "ok"
    assert attempt_counter["n"] == 3
    manager.transaction = original  # type: ignore[method-assign]


def test_run_propagates_non_retryable_errors_immediately(manager: PooledConnectionManager):
    def bad_sql(conn: psycopg.Connection) -> None:
        conn.execute("SELECT * FROM table_that_does_not_exist")

    with pytest.raises(psycopg.errors.UndefinedTable):
        manager.run(bad_sql)


def test_connection_factory_counts_and_configures():
    factory = ConnectionFactory(TEST_DATABASE_URL, connect_timeout=2)
    assert factory.connect_timeout == 2
    with factory.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS one")
            assert cur.fetchone()["one"] == 1
    assert factory.connections_opened == 1


def test_multi_user_simulated_deployment(manager: PooledConnectionManager):
    """Simulated concurrent users: threads share one bounded pool.

    8 simulated users x 4 operations each (mix of writes and reads) through a
    single manager with max_size=4. Every operation must succeed, no checkout
    may time out, and the pool must never have opened more than max_size
    connections.
    """
    import json
    import uuid

    from ai_music_therapy.deterministic_simulator import simulate
    from ai_music_therapy.models import MusicParameters, TrialRecord
    from ai_music_therapy.repository import Repository

    repository = Repository(TEST_DATABASE_URL, manager=manager)
    repository.initialize()
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    persona = Persona.model_validate(payload[0])
    repository.upsert_persona(persona)

    def user_session(user_index: int) -> int:
        repo = Repository(TEST_DATABASE_URL, manager=manager)
        music = MusicParameters(
            genre="instrumental", bpm=60, volume="low", instrument="piano",
            tonality="major", duration_sec=180, lyrics_language="none",
        )
        for op_index in range(4):
            if op_index % 2 == 0:  # write
                reaction, seed = simulate(persona, music, "sleep_support")
                repo.save_trial(
                    TrialRecord(
                        trial_id=f"T-S18-{user_index}-{op_index}-{uuid.uuid4().hex[:6]}",
                        persona_id=persona.persona_id,
                        scene="sleep_support",
                        music=music,
                        reaction=reaction,
                        engine="deterministic",
                        prompt_version="s18-test",
                        seed=seed,
                    )
                )
            else:  # read
                if not repo.list_trials(persona_id=persona.persona_id):
                    raise AssertionError("expected stored trials to be readable")
        return 4

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(user_session, range(8)))
    assert results == [4] * 8  # 32 operations, all succeeded
    stats = manager.stats()
    assert stats["pool_size"] <= 4, stats
    assert manager._factory.connections_opened <= 4


def test_get_manager_is_cached_per_url():
    from ai_music_therapy.db import get_manager

    first = get_manager(TEST_DATABASE_URL)
    second = get_manager(TEST_DATABASE_URL)
    assert first is second  # one process-wide pool per database URL
