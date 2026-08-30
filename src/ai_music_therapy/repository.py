from __future__ import annotations

from collections.abc import Callable

import psycopg

from .db import ConnectionFactory, PooledConnectionManager, get_manager
from .models import Persona, TrialRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS personas (
    persona_id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    synthetic INTEGER NOT NULL CHECK (synthetic = 1)
);
CREATE TABLE IF NOT EXISTS trials (
    trial_id TEXT PRIMARY KEY,
    persona_id TEXT NOT NULL,
    scene TEXT NOT NULL,
    engine TEXT NOT NULL,
    model_name TEXT,
    prompt_version TEXT NOT NULL,
    seed BIGINT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    synthetic INTEGER NOT NULL CHECK (synthetic = 1),
    FOREIGN KEY(persona_id) REFERENCES personas(persona_id)
);
"""


class Repository:
    """PostgreSQL persistence for synthetic personas and trial records.

    All operations run through a pooled connection manager
    (factory -> pool -> transaction -> retry/timeout; see ``db.py``), so
    concurrent users share a bounded set of connections instead of opening a
    fresh one per operation. The pool opens lazily on first use: constructing
    a ``Repository`` (e.g. at Streamlit page import) never requires a
    reachable database.
    """

    def __init__(
        self,
        database_url: str,
        manager: PooledConnectionManager | None = None,
    ):
        self.database_url = database_url
        # explicit manager wins (tests inject their own); otherwise the
        # process-wide cached pool for this URL is shared across reruns/threads
        self.manager = manager or get_manager(database_url)

    def connect(self) -> psycopg.Connection:
        """Open one direct (non-pooled) connection; kept for tooling/tests."""
        return ConnectionFactory(self.database_url).connect()

    def _run(self, operation: Callable[[psycopg.Connection], object]) -> object:
        return self.manager.run(operation)

    def initialize(self) -> None:
        def op(conn: psycopg.Connection) -> None:
            with conn.cursor() as cur:
                cur.execute(SCHEMA)

        self._run(op)

    def upsert_persona(self, persona: Persona) -> None:
        def op(conn: psycopg.Connection) -> None:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO personas(persona_id, payload_json, synthetic) "
                    "VALUES (%s, %s, 1) "
                    "ON CONFLICT(persona_id) DO UPDATE "
                    "SET payload_json=excluded.payload_json",
                    (persona.persona_id, persona.model_dump_json()),
                )

        self._run(op)

    def list_personas(self) -> list[Persona]:
        def op(conn: psycopg.Connection) -> list[Persona]:
            with conn.cursor() as cur:
                cur.execute("SELECT payload_json FROM personas ORDER BY persona_id")
                rows = cur.fetchall()
            return [Persona.model_validate_json(row["payload_json"]) for row in rows]

        return self._run(op)  # type: ignore[return-value]

    def get_persona(self, persona_id: str) -> Persona:
        def op(conn: psycopg.Connection) -> Persona | None:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload_json FROM personas WHERE persona_id = %s",
                    (persona_id,),
                )
                row = cur.fetchone()
            return (
                Persona.model_validate_json(row["payload_json"]) if row else None
            )

        persona = self._run(op)
        if persona is None:
            raise KeyError(f"Unknown persona: {persona_id}")
        return persona  # type: ignore[return-value]

    def save_trial(self, trial: TrialRecord) -> None:
        def op(conn: psycopg.Connection) -> None:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO trials(
                            trial_id, persona_id, scene, engine, model_name,
                            prompt_version, seed, created_at, payload_json, synthetic
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                        """,
                        (
                            trial.trial_id,
                            trial.persona_id,
                            trial.scene,
                            trial.engine,
                            trial.model_name,
                            trial.prompt_version,
                            trial.seed,
                            trial.created_at,
                            trial.model_dump_json(),
                        ),
                    )
                except psycopg.errors.UniqueViolation as error:
                    raise ValueError(
                        f"Duplicate trial_id {trial.trial_id}: each trial record must "
                        "have a unique ID; nothing was overwritten"
                    ) from error

        self._run(op)

    def get_trial(self, trial_id: str) -> TrialRecord:
        def op(conn: psycopg.Connection) -> TrialRecord | None:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload_json FROM trials WHERE trial_id = %s", (trial_id,)
                )
                row = cur.fetchone()
            return (
                TrialRecord.model_validate_json(row["payload_json"]) if row else None
            )

        trial = self._run(op)
        if trial is None:
            raise KeyError(f"Unknown trial: {trial_id}")
        return trial  # type: ignore[return-value]

    def list_trials(
        self,
        persona_id: str | None = None,
        scene: str | None = None,
        engine: str | None = None,
    ) -> list[TrialRecord]:
        """List trials, optionally filtered (audit view).

        Filters compose; each is ignored when None.
        """
        clauses, params = [], []
        if persona_id is not None:
            clauses.append("persona_id = %s")
            params.append(persona_id)
        if scene is not None:
            clauses.append("scene = %s")
            params.append(scene)
        if engine is not None:
            clauses.append("engine = %s")
            params.append(engine)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        def op(conn: psycopg.Connection) -> list[TrialRecord]:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT payload_json FROM trials {where} ORDER BY created_at",
                    params,
                )
                rows = cur.fetchall()
            return [TrialRecord.model_validate_json(row["payload_json"]) for row in rows]

        return self._run(op)  # type: ignore[return-value]
