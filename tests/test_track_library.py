"""S19 TrackBase: models, staged workflow, and write-once persistence.

Repository tests need a reachable PostgreSQL and skip with a message
otherwise, mirroring ``tests/test_repository.py``.
"""

import hashlib
import os

import pytest
from pydantic import ValidationError

from ai_music_therapy.models import (
    AudioExtraction,
    MusicParameters,
    TrackEntry,
)
from ai_music_therapy.track_service import (
    APPROVED,
    REJECTED,
    TRIAL_CONFIRMED,
    UNDER_REVIEW,
    TrackProposal,
    advance,
    file_sha256,
    finalize_track,
    reject,
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator_test"
)


def _postgres_available() -> bool:
    import psycopg

    base, _, _dbname = TEST_DATABASE_URL.rpartition("/")
    try:
        with psycopg.connect(base + "/postgres", connect_timeout=3):
            return True
    except psycopg.OperationalError:
        return False


def _extraction(**overrides) -> AudioExtraction:
    values = dict(
        duration_sec=95.5,
        tempo_bpm=92.0,
        rms_db=-21.3,
        volume_bucket="medium",
        spectral_centroid_hz=1234.5,
        mode_estimate="major",
        extractor="librosa test",
    )
    values.update(overrides)
    return AudioExtraction(**values)


def _music(**overrides) -> MusicParameters:
    values = dict(
        genre="instrumental", bpm=92, volume="medium", instrument="mixed",
        tonality="major", duration_sec=180, lyrics_language="none",
    )
    values.update(overrides)
    return MusicParameters(**values)


def _proposal(**overrides) -> TrackProposal:
    values = dict(
        extraction=_extraction(),
        source_file_name="demo.wav",
        source_file_sha256=hashlib.sha256(b"demo").hexdigest(),
    )
    values.update(overrides)
    return TrackProposal(**values)


# ---------------------------------------------------------------- models

def test_track_entry_requires_trk_prefix():
    with pytest.raises(ValidationError):
        TrackEntry(
            track_id="TRACK-1", display_name="x",
            source_file_name="a.wav", source_file_sha256="a" * 64,
            music=_music(), extraction=_extraction(),
        )


def test_track_entry_synthetic_is_locked():
    with pytest.raises(ValidationError):
        TrackEntry(
            track_id="TRK-1", display_name="x",
            source_file_name="a.wav", source_file_sha256="a" * 64,
            music=_music(), extraction=_extraction(), synthetic=False,
        )


def test_track_entry_sha256_must_be_64_chars():
    with pytest.raises(ValidationError):
        TrackEntry(
            track_id="TRK-1", display_name="x",
            source_file_name="a.wav", source_file_sha256="short",
            music=_music(), extraction=_extraction(),
        )


def test_track_entry_round_trip():
    entry = TrackEntry(
        track_id="TRK-ROUND", display_name="Round trip",
        source_file_name="a.flac", source_file_sha256="b" * 64,
        music=_music(), extraction=_extraction(),
        overridden_fields=["genre", "instrument"],
    )
    assert TrackEntry.model_validate_json(entry.model_dump_json()) == entry
    assert entry.synthetic is True


def test_audio_extraction_bounds():
    with pytest.raises(ValidationError):
        AudioExtraction(
            duration_sec=-1.0, rms_db=-20.0, volume_bucket="low",
            spectral_centroid_hz=0.0, extractor="x",
        )


# ------------------------------------------------------ staged workflow

def test_advance_accepts_valid_transitions_only():
    proposal = _proposal()
    assert advance(proposal, UNDER_REVIEW) == UNDER_REVIEW
    assert advance(proposal, TRIAL_CONFIRMED) == TRIAL_CONFIRMED
    assert advance(proposal, APPROVED) == APPROVED

    fresh = _proposal()
    with pytest.raises(ValueError):
        advance(fresh, APPROVED)  # cannot skip review
    with pytest.raises(ValueError):
        advance(fresh, TRIAL_CONFIRMED)

    approved = _proposal()
    advance(approved, UNDER_REVIEW)
    advance(approved, APPROVED)
    with pytest.raises(ValueError):
        advance(approved, UNDER_REVIEW)  # approved is terminal

    rejected = _proposal()
    advance(rejected, UNDER_REVIEW)
    advance(rejected, REJECTED)
    with pytest.raises(ValueError):
        advance(rejected, UNDER_REVIEW)  # rejected is terminal


def test_finalize_requires_review_state():
    proposal = _proposal()  # still PROPOSED
    with pytest.raises(ValueError, match="under review"):
        finalize_track(proposal, "TRK-X", "x", _music(), [])


def test_finalize_builds_entry_and_marks_approved():
    proposal = _proposal()
    advance(proposal, UNDER_REVIEW)
    entry = finalize_track(
        proposal, "TRK-OK", "Approved track", _music(bpm=90),
        ["bpm", "genre"], notes="reviewed",
    )
    assert entry.track_id == "TRK-OK"
    assert entry.music.bpm == 90
    assert entry.overridden_fields == ["bpm", "genre"]
    assert entry.source_file_sha256 == proposal.source_file_sha256
    assert proposal.state == APPROVED
    # approved is terminal: no re-finalize
    with pytest.raises(ValueError):
        finalize_track(proposal, "TRK-AGAIN", "x", _music(), [])


def test_reject_blocks_later_finalize():
    proposal = _proposal()
    advance(proposal, UNDER_REVIEW)
    reject(proposal)
    assert proposal.state == REJECTED
    with pytest.raises(ValueError):
        finalize_track(proposal, "TRK-NO", "x", _music(), [])
    with pytest.raises(ValueError):
        reject(proposal)  # cannot reject twice


def test_file_sha256():
    assert file_sha256(b"demo") == hashlib.sha256(b"demo").hexdigest()


# ------------------------------------------------- repository (gated DB)


@pytest.fixture()
def repo():
    if not _postgres_available():
        pytest.skip("PostgreSQL not reachable; start it with `docker compose up -d`")
    from ai_music_therapy.repository import Repository

    repository = Repository(TEST_DATABASE_URL)
    repository.initialize()
    with repository.connect() as conn:
        conn.execute("TRUNCATE tracks")
    return repository


def _approved_entry(track_id: str = "TRK-DB") -> TrackEntry:
    proposal = _proposal()
    advance(proposal, UNDER_REVIEW)
    return finalize_track(proposal, track_id, f"Track {track_id}", _music(), [])


@pytest.mark.usefixtures("repo")
class TestTrackRepository:
    def test_track_round_trip(self, repo):
        entry = _approved_entry()
        repo.save_track(entry)
        assert repo.get_track(entry.track_id) == entry
        assert repo.list_tracks() == [entry]

    def test_approved_track_is_write_once(self, repo):
        repo.save_track(_approved_entry("TRK-ONCE"))
        with pytest.raises(ValueError, match="write-once"):
            repo.save_track(_approved_entry("TRK-ONCE"))
        assert len(repo.list_tracks()) == 1  # nothing was overwritten

    def test_tracks_synthetic_only_guard(self, repo):
        import psycopg

        with pytest.raises(psycopg.errors.CheckViolation):
            with repo.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO tracks(track_id, display_name, approved_at, "
                        "payload_json, synthetic) VALUES ('TRK-BAD', 'x', 'now', '{}', 0)"
                    )

    def test_get_unknown_track_raises(self, repo):
        with pytest.raises(KeyError):
            repo.get_track("TRK-MISSING")

    def test_approval_boundary_only_save_finalizes_persist(self, repo):
        """The database is written only by an explicit save of a finalized entry."""
        proposal = _proposal()
        advance(proposal, UNDER_REVIEW)
        # review stage only: nothing may be in the table
        assert repo.list_tracks() == []
        entry = finalize_track(proposal, "TRK-SAVE", "x", _music(), [])
        repo.save_track(entry)
        assert len(repo.list_tracks()) == 1
