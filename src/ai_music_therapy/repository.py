from __future__ import annotations

import sqlite3
from pathlib import Path

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
    seed INTEGER,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    synthetic INTEGER NOT NULL CHECK (synthetic = 1),
    FOREIGN KEY(persona_id) REFERENCES personas(persona_id)
);
"""


class Repository:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def upsert_persona(self, persona: Persona) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO personas(persona_id, payload_json, synthetic) VALUES (?, ?, 1) "
                "ON CONFLICT(persona_id) DO UPDATE SET payload_json=excluded.payload_json",
                (persona.persona_id, persona.model_dump_json()),
            )

    def list_personas(self) -> list[Persona]:
        with self.connect() as conn:
            rows = conn.execute("SELECT payload_json FROM personas ORDER BY persona_id").fetchall()
        return [Persona.model_validate_json(row["payload_json"]) for row in rows]

    def get_persona(self, persona_id: str) -> Persona:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM personas WHERE persona_id = ?", (persona_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown persona: {persona_id}")
        return Persona.model_validate_json(row["payload_json"])

    def save_trial(self, trial: TrialRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO trials(
                    trial_id, persona_id, scene, engine, model_name, prompt_version,
                    seed, created_at, payload_json, synthetic
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
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

    def list_trials(self) -> list[TrialRecord]:
        with self.connect() as conn:
            rows = conn.execute("SELECT payload_json FROM trials ORDER BY created_at").fetchall()
        return [TrialRecord.model_validate_json(row["payload_json"]) for row in rows]
