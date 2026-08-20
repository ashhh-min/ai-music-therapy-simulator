import json
import os
import types
from pathlib import Path

import pytest

from ai_music_therapy.models import Persona
from ai_music_therapy.persona_service import (
    DraftRejected,
    approve_and_save,
    draft_persona_with_openai,
    lint_persona,
)
from ai_music_therapy.repository import Repository

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator_test"
)


def _pg_available() -> bool:
    import psycopg

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


def _load_all() -> list[Persona]:
    payload = json.loads(Path("data/public/synthetic_personas.json").read_text(encoding="utf-8"))
    return [Persona.model_validate(item) for item in payload]


def _clone(persona: Persona, **updates) -> Persona:
    data = persona.model_dump()
    data.update(updates)
    return Persona.model_validate(data)


def _approved_clone(persona: Persona) -> Persona:
    return _clone(
        persona,
        persona_id="P-NEW",
        display_name="New Draft",
        profile_summary="Synthetic profile: fictional child for the demo lab.",
    )


def test_clean_draft_has_no_flags():
    base = _load_all()[0]
    draft = _clone(
        base,
        persona_id="P-NEW",
        profile_summary="Synthetic educational profile: a fictional child who loves rhythm.",
        known_triggers=["different trigger"],  # diverge from near-duplicate
    )
    assert lint_persona(draft, _load_all()) == []


def test_stereotype_wording_is_flagged():
    base = _load_all()[0]
    draft = _clone(
        base,
        persona_id="P-NEW",
        profile_summary="Synthetic profile of a high-functioning fictional child.",
    )
    flags = lint_persona(draft, _load_all())
    assert any(f.startswith("stereotype") for f in flags)


def test_missing_synthetic_wording_is_flagged():
    base = _load_all()[0]
    draft = _clone(
        base,
        persona_id="P-NEW",
        profile_summary="A fictional child who loves rhythm and predictable melodies.",
    )
    flags = lint_persona(draft, _load_all())
    assert any(f.startswith("synthetic-wording") for f in flags)


def test_near_duplicate_is_flagged():
    approved = _load_all()
    near = _approved_clone(approved[0])  # identical support/modes/triggers
    flags = lint_persona(near, approved)
    assert any(f.startswith("near-duplicate") for f in flags)


def test_approve_and_save_persists_new_persona(repo):
    approved = _load_all()
    draft_persona = _clone(
        approved[0],
        persona_id="P-REVIEWED",
        profile_summary="Synthetic profile: fictional child, rhythm-focused.",
        known_triggers=["sudden loud noises"],  # diverge from near-duplicate
    )
    from ai_music_therapy.persona_service import PersonaDraft

    draft = PersonaDraft(persona=draft_persona, source="ai", created_at="2026-08-20T00:00:00")
    saved = approve_and_save(repo, draft, approved)
    assert saved.persona_id == "P-REVIEWED"
    assert repo.get_persona("P-REVIEWED") == draft_persona


def test_approve_never_overwrites_approved_fixture(repo):
    approved = _load_all()
    repo.upsert_persona(approved[0])
    from ai_music_therapy.persona_service import PersonaDraft

    impostor = _clone(
        approved[0],
        profile_summary="Synthetic profile: rewritten by an AI draft.",
        known_triggers=["different trigger"],
    )
    draft = PersonaDraft(persona=impostor, source="ai", created_at="2026-08-20T00:00:00")
    with pytest.raises(DraftRejected, match="cannot be overwritten"):
        approve_and_save(repo, draft, approved)
    assert repo.get_persona(approved[0].persona_id) == approved[0]  # untouched


def test_hard_flags_block_acceptance(repo):
    approved = _load_all()
    from ai_music_therapy.persona_service import PersonaDraft

    flagged = _clone(
        approved[0],
        persona_id="P-BAD",
        profile_summary="A high-functioning fictional child.",  # stereotype + no 'synthetic'
        known_triggers=["different trigger"],
    )
    draft = PersonaDraft(persona=flagged, source="ai", created_at="2026-08-20T00:00:00")
    with pytest.raises(DraftRejected, match="revise first"):
        approve_and_save(repo, draft, approved)
    with pytest.raises(KeyError):
        repo.get_persona("P-BAD")


def test_near_duplicate_requires_confirmation(repo):
    approved = _load_all()
    near = _approved_clone(approved[0])
    from ai_music_therapy.persona_service import PersonaDraft

    draft = PersonaDraft(persona=near, source="ai", created_at="2026-08-20T00:00:00")
    with pytest.raises(DraftRejected, match="confirm required"):
        approve_and_save(repo, draft, approved)
    saved = approve_and_save(repo, draft, approved, confirm_similar=True)
    assert saved.persona_id == "P-NEW"


def _patch_transport(monkeypatch, replies):
    class _FakeResponse:
        def __init__(self, text):
            self.output_text = text

    class _FakeResponses:
        def __init__(self):
            self.calls = 0

        def create(self, **kwargs):
            reply = replies[min(self.calls, len(replies) - 1)]
            self.calls += 1
            return _FakeResponse(reply)

    fake = _FakeResponses()

    class _FakeClient:
        def __init__(self, **kwargs):
            self.responses = fake

    monkeypatch.setattr("ai_music_therapy.persona_service.OpenAI", _FakeClient)
    return fake


def test_ai_draft_requires_key(monkeypatch):
    monkeypatch.setattr(
        "ai_music_therapy.persona_service.settings",
        types.SimpleNamespace(openai_api_key=None, openai_model="m", openai_base_url=None),
    )
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        draft_persona_with_openai("anything")


def test_ai_draft_returns_unsaved_validated_draft(monkeypatch):
    monkeypatch.setattr(
        "ai_music_therapy.persona_service.settings",
        types.SimpleNamespace(openai_api_key="test-key", openai_model="m", openai_base_url="u"),
    )
    persona = _clone(
        _load_all()[0],
        persona_id="P-AIDRAFT",
        profile_summary="Synthetic profile: fictional, rhythm-seeking, AAC user.",
        known_triggers=["different trigger"],
    )
    transport = _patch_transport(monkeypatch, [persona.model_dump_json()])
    draft = draft_persona_with_openai("rhythm seeker")
    assert draft.source == "ai"
    assert draft.persona == persona
    assert draft.flags == []
    assert transport.calls == 1  # validated on first attempt


def test_ai_draft_rejects_invalid_after_retry(monkeypatch):
    monkeypatch.setattr(
        "ai_music_therapy.persona_service.settings",
        types.SimpleNamespace(openai_api_key="test-key", openai_model="m", openai_base_url="u"),
    )
    _patch_transport(monkeypatch, ["not json", "also not json"])
    with pytest.raises(RuntimeError, match="failed validation after retry"):
        draft_persona_with_openai("rhythm seeker")
