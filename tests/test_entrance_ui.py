"""S19 entrance UI tests: AppTest with session_state-seeded proposals.

``st.file_uploader`` cannot be driven headless, so the review/approve flows
are exercised by seeding ``st.session_state`` with a proposal (the same shape
the pages produce after extraction) and clicking through the staged buttons.
All pages run against the test database; the review stages must leave it
untouched, and only approval may persist.
"""

import hashlib
import io
import os
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
import soundfile
from streamlit.testing.v1 import AppTest

from ai_music_therapy.models import AudioExtraction, Persona

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator_test"
)

ROOT = Path(__file__).resolve().parents[1]
TRACK_PAGE = str(ROOT / "src/ai_music_therapy/ui/upload_track.py")
PERSONA_PAGE = str(ROOT / "src/ai_music_therapy/ui/propose_persona.py")
TRIAL_PAGE = str(ROOT / "src/ai_music_therapy/ui/trial.py")

RUN_TIMEOUT = 60  # first run imports librosa, which is slow to load


def _postgres_available() -> bool:
    import psycopg

    base, _, _dbname = TEST_DATABASE_URL.rpartition("/")
    try:
        with psycopg.connect(base + "/postgres", connect_timeout=3):
            return True
    except psycopg.OperationalError:
        return False


@pytest.fixture()
def repo(monkeypatch):
    """Point the pages at the test database and start from clean tables."""
    if not _postgres_available():
        pytest.skip("PostgreSQL not reachable; start it with `docker compose up -d`")
    from ai_music_therapy import config
    from ai_music_therapy.config import Settings
    from ai_music_therapy.repository import Repository

    monkeypatch.setattr(
        config, "settings", Settings(database_url=TEST_DATABASE_URL, openai_api_key=None)
    )
    repository = Repository(TEST_DATABASE_URL)
    repository.initialize()
    with repository.connect() as conn:
        conn.execute("TRUNCATE tracks, trials, personas")
    repository.upsert_persona(_seed_persona())
    return repository


def _seed_persona(persona_id: str = "P-UITEST") -> Persona:
    return Persona(
        persona_id=persona_id,
        display_name="UI Test Persona",
        age_years=8,
        profile_summary="A synthetic persona used only by the UI test suite.",
        support_profile={
            "communication": "uses picture cards with familiar partners",
            "sensory": "prefers dim lighting and soft textures",
            "routine": "benefits from a visual schedule",
            "social": "joins small-group activities with warm-up time",
        },
        sensory_profile={
            "auditory_sensitivity": 7,
            "sensory_seeking": 4,
            "change_sensitivity": 6,
        },
        communication_modes=["picture-cards"],
        music_preferences=["gentle piano"],
        known_triggers=["sudden loud noises"],
        preferred_supports=["predictable routine"],
    )


def _demo_wav_bytes() -> bytes:
    """A generated 2-second 440 Hz tone (no real music files are committed)."""
    sr = 22050
    t = np.arange(sr * 2) / sr
    signal = (0.3 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
    buffer = io.BytesIO()
    soundfile.write(buffer, signal, sr, format="WAV")
    return buffer.getvalue()


def _extraction_dict() -> dict:
    return AudioExtraction(
        duration_sec=95.5,
        tempo_bpm=92.0,
        rms_db=-21.3,
        volume_bucket="medium",
        spectral_centroid_hz=1234.5,
        mode_estimate="major",
        extractor="librosa test",
    ).model_dump()


def _seed_track_proposal(at: AppTest) -> None:
    """Seed the page state exactly as the upload+extract step would leave it."""
    at.session_state["track_proposal"] = {
        "extraction": _extraction_dict(),
        "source_file_name": "demo.wav",
        "source_file_sha256": hashlib.sha256(b"demo").hexdigest(),
        "state": "under_review",
    }
    at.session_state["tk_genre"] = "instrumental"
    at.session_state["tk_bpm"] = 92
    at.session_state["tk_volume"] = "medium"
    at.session_state["tk_instrument"] = "mixed"
    at.session_state["tk_tonality"] = "major"
    at.session_state["tk_duration"] = 180
    at.session_state["tk_lyrics"] = "none"
    at.session_state["tk_track_id"] = "TRK-UITEST"
    at.session_state["tk_display_name"] = "UI Test Track"
    at.session_state["tk_notes"] = ""


def _start_track_page(repo) -> AppTest:
    at = AppTest.from_file(TRACK_PAGE)
    at.run(timeout=RUN_TIMEOUT)
    return at


# ------------------------------------------------------------ track entrance

@pytest.mark.usefixtures("repo")
def test_track_page_upload_stage_renders(repo):
    at = _start_track_page(repo)
    assert not at.exception
    assert at.file_uploader(key="track_uploader")
    assert repo.list_tracks() == []


@pytest.mark.usefixtures("repo")
def test_track_upload_extract_creates_proposal_without_persisting(repo):
    at = _start_track_page(repo)
    wav = _demo_wav_bytes()
    at.file_uploader(key="track_uploader").set_value(("demo.wav", wav, "audio/wav"))
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="extract").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert "track_proposal" in at.session_state
    proposal = at.session_state["track_proposal"]
    assert proposal["state"] == "under_review"
    assert proposal["source_file_sha256"] == hashlib.sha256(wav).hexdigest()
    assert proposal["extraction"]["tempo_bpm"] is not None
    assert repo.list_tracks() == []  # extraction alone persists nothing


@pytest.mark.usefixtures("repo")
def test_track_approval_persists_write_once_entry(repo):
    at = _start_track_page(repo)
    _seed_track_proposal(at)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="approve_track").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    tracks = repo.list_tracks()
    assert len(tracks) == 1
    entry = tracks[0]
    assert entry.track_id == "TRK-UITEST"
    assert entry.display_name == "UI Test Track"
    assert entry.music.bpm == 92
    assert entry.source_file_sha256 == hashlib.sha256(b"demo").hexdigest()
    assert entry.synthetic is True
    # provenance: fields the reviewer had to choose (no DSP basis) are recorded
    assert set(entry.overridden_fields) == {
        "genre", "instrument", "lyrics_language", "duration_sec",
    }


@pytest.mark.usefixtures("repo")
def test_track_rejection_persists_nothing(repo):
    at = _start_track_page(repo)
    _seed_track_proposal(at)
    at.run(timeout=RUN_TIMEOUT)
    at.button(key="reject_track").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert repo.list_tracks() == []
    assert repo.list_trials() == []


@pytest.mark.usefixtures("repo")
def test_confirmation_trial_runs_in_memory_only(repo):
    at = _start_track_page(repo)
    _seed_track_proposal(at)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    # deterministic no-key mode: the openai engine must not be offered
    assert at.radio(key="trial_engine").options == ["deterministic"]
    at.button(key="run_confirmation").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert "track_confirmation" in at.session_state
    # the review trial never reaches the database
    assert repo.list_trials() == []
    assert at.session_state["track_proposal"]["state"] == "trial_confirmed"
    # approval from trial_confirmed still works and then persists exactly once
    at.button(key="approve_track").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert len(repo.list_tracks()) == 1


# ---------------------------------------------------------- persona entrance

def _seed_persona_draft(at: AppTest, persona: Persona, source: str = "json-upload") -> None:
    at.session_state["persona_draft_payload"] = {
        "persona": persona.model_dump(),
        "source": source,
        "created_at": datetime.now(UTC).isoformat(),
    }
    at.session_state["pp_summary"] = persona.profile_summary


def _start_persona_page(repo) -> AppTest:
    at = AppTest.from_file(PERSONA_PAGE)
    at.run(timeout=RUN_TIMEOUT)
    return at


@pytest.mark.usefixtures("repo")
def test_persona_page_renders_and_ai_draft_is_key_gated(repo):
    at = _start_persona_page(repo)
    assert not at.exception
    generate = at.button(key="generate_ai")
    assert generate.disabled  # no OPENAI_API_KEY in this test environment


@pytest.mark.usefixtures("repo")
def test_persona_json_upload_reaches_review_without_saving(repo):
    at = _start_persona_page(repo)
    draft = _seed_persona(persona_id="P-JSONUP").model_copy(
        update={
            "display_name": "JSON Upload Persona",
            "communication_modes": ["spoken-words"],
            "known_triggers": ["bright flashing lights"],
            "preferred_supports": ["noise-cancelling headphones"],
            "support_profile": {
                "communication": "uses short spoken phrases",
                "sensory": "prefers quiet rooms",
                "routine": "likes advance warning before changes",
                "social": "enjoys parallel play",
            },
        }
    )
    payload = draft.model_dump_json().encode()
    at.file_uploader(key="persona_uploader").set_value(
        ("persona.json", payload, "application/json")
    )
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="validate_json").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert "persona_draft_payload" in at.session_state
    assert repo.list_personas() == [_seed_persona()]  # upload alone saves nothing


@pytest.mark.usefixtures("repo")
def test_persona_json_upload_rejects_invalid_json(repo):
    at = _start_persona_page(repo)
    at.file_uploader(key="persona_uploader").set_value(
        ("persona.json", b"{not valid json", "application/json")
    )
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="validate_json").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert "persona_draft_payload" not in at.session_state
    assert any("Not valid JSON" in e.value for e in at.error)


@pytest.mark.usefixtures("repo")
def test_persona_json_upload_rejects_schema_violation(repo):
    at = _start_persona_page(repo)
    at.file_uploader(key="persona_uploader").set_value(
        ("persona.json", b'{"persona_id": "NOPE", "extra_field": 1}', "application/json")
    )
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="validate_json").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert "persona_draft_payload" not in at.session_state
    assert any("Persona schema" in e.value for e in at.error)


@pytest.mark.usefixtures("repo")
def test_persona_approval_saves_through_existing_path(repo):
    at = _start_persona_page(repo)
    draft = _seed_persona(
        persona_id="P-NEWUI",
    ).model_copy(
        update={
            "display_name": "Another UI Persona",
            "communication_modes": ["spoken-words"],
            "known_triggers": ["bright flashing lights"],
            "support_profile": {
                "communication": "uses short spoken phrases",
                "sensory": "prefers quiet rooms",
                "routine": "likes advance warning before changes",
                "social": "enjoys parallel play",
            },
        }
    )
    _seed_persona_draft(at, draft)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="approve_persona").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    ids = [p.persona_id for p in repo.list_personas()]
    assert "P-NEWUI" in ids


@pytest.mark.usefixtures("repo")
def test_persona_hard_flag_blocks_approval(repo):
    at = _start_persona_page(repo)
    draft = _seed_persona(persona_id="P-FLAGGED").model_copy(
        update={"profile_summary": "A profile that never says the required word."}
    )
    _seed_persona_draft(at, draft)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert at.button(key="approve_persona").disabled
    assert repo.list_personas() == [_seed_persona()]  # only the fixture persona


@pytest.mark.usefixtures("repo")
def test_persona_existing_id_never_overwritten(repo):
    at = _start_persona_page(repo)
    # Same ID as the fixture persona but structurally different content.
    draft = _seed_persona(persona_id="P-UITEST").model_copy(
        update={
            "display_name": "Impostor",
            "communication_modes": ["spoken-words"],
            "music_preferences": ["drums"],
            "known_triggers": ["crowds"],
            "preferred_supports": ["headphones"],
            "support_profile": {
                "communication": "speaks in full sentences",
                "sensory": "seeks movement",
                "routine": "flexible with changes",
                "social": "prefers large groups",
            },
        }
    )
    _seed_persona_draft(at, draft)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="approve_persona").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    personas = repo.list_personas()
    assert len(personas) == 1
    assert personas[0].display_name == "UI Test Persona"  # untouched
    assert any("already exists" in e.value for e in at.error)


# ------------------------------------------------- trial page track selection

@pytest.mark.usefixtures("repo")
def test_approved_track_selectable_on_trial_page(repo):
    from ai_music_therapy.models import MusicParameters
    from ai_music_therapy.track_service import (
        UNDER_REVIEW,
        TrackProposal,
        finalize_track,
    )

    proposal = TrackProposal(
        extraction=AudioExtraction(**_extraction_dict()),
        source_file_name="demo.wav",
        source_file_sha256=hashlib.sha256(b"demo").hexdigest(),
        state=UNDER_REVIEW,
    )
    entry = finalize_track(
        proposal, "TRK-TRIAL", "Trial Page Track",
        MusicParameters(
            genre="instrumental", bpm=92, volume="medium", instrument="mixed",
            tonality="major", duration_sec=180, lyrics_language="none",
        ),
        [],
    )
    repo.save_track(entry)

    at = AppTest.from_file(TRIAL_PAGE)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    sources = [r for r in at.radio if r.label == "Music source"]
    assert sources and sources[0].options == [
        "Manual parameters", "Approved track (TrackBase)",
    ]
