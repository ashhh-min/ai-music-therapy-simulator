"""S20 patch-generator page tests (AppTest, DB-gated like the S19 UI suite).

The page must render with no tracks (manual parameters only), produce all
three artifacts from one deterministic spec on click, persist NOTHING, and
offer approved TrackBase tracks as a parameter source when they exist.
"""

import hashlib
import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ai_music_therapy.models import AudioExtraction, MusicParameters
from ai_music_therapy.patch_generation import PatchSpec, spec_to_maxpat

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mt_simulator_test"
)

ROOT = Path(__file__).resolve().parents[1]
PATCH_PAGE = str(ROOT / "src/ai_music_therapy/ui/generate_patch.py")

RUN_TIMEOUT = 60


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
    return repository


def _seed_track(repo, track_id: str = "TRK-PATCHUI") -> None:
    from ai_music_therapy.track_service import UNDER_REVIEW, TrackProposal, finalize_track

    proposal = TrackProposal(
        extraction=AudioExtraction(
            duration_sec=95.5, tempo_bpm=92.0, rms_db=-21.3, volume_bucket="medium",
            spectral_centroid_hz=1234.5, mode_estimate="major", extractor="librosa test",
        ),
        source_file_name="demo.wav",
        source_file_sha256=hashlib.sha256(b"demo").hexdigest(),
        state=UNDER_REVIEW,
    )
    entry = finalize_track(
        proposal, track_id, "Patch Page Track",
        MusicParameters(
            genre="classical", bpm=92, volume="medium", instrument="guitar",
            tonality="minor", duration_sec=180, lyrics_language="none",
        ),
        [],
    )
    repo.save_track(entry)


@pytest.mark.usefixtures("repo")
def test_page_renders_manual_only_without_tracks(repo):
    at = AppTest.from_file(PATCH_PAGE)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    assert repo.list_tracks() == []
    # No tracks -> no source radio; the manual widgets are shown.
    assert not [r for r in at.radio if r.label == "Parameter source"]
    assert at.slider(key="gp_bpm")
    assert at.button(key="gp_generate")
    assert any("Cycling '74" in c.value for c in at.caption)


@pytest.mark.usefixtures("repo")
def test_generate_creates_all_artifacts_and_persists_nothing(repo):
    at = AppTest.from_file(PATCH_PAGE)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="gp_generate").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception

    assert "patch_spec_payload" in at.session_state
    spec = PatchSpec.model_validate(at.session_state["patch_spec_payload"])
    assert spec.source == "manual"
    # The .maxpat artifact is derivable and structurally valid JSON.
    import json

    patcher = json.loads(spec_to_maxpat(spec))["patcher"]
    assert patcher["boxes"] and patcher["lines"]
    # Nothing persisted anywhere: no tracks, no trials, no personas written.
    assert repo.list_tracks() == []
    assert repo.list_trials() == []
    # The artifacts section rendered with both download buttons.
    downloads = at.get("download_button")
    assert len(downloads) == 2
    assert any("Wiring logic" in m.value for m in at.markdown)


@pytest.mark.usefixtures("repo")
def test_approved_track_usable_as_parameter_source(repo):
    _seed_track(repo)
    at = AppTest.from_file(PATCH_PAGE)
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    sources = [r for r in at.radio if r.label == "Parameter source"]
    assert sources and sources[0].options == [
        "Manual parameters", "Approved track (TrackBase)",
    ]
    at.radio(key="gp_music_source").set_value("Approved track (TrackBase)")
    at.run(timeout=RUN_TIMEOUT)
    assert not at.exception
    at.button(key="gp_generate").click().run(timeout=RUN_TIMEOUT)
    assert not at.exception
    spec = PatchSpec.model_validate(at.session_state["patch_spec_payload"])
    assert spec.source == "track:TRK-PATCHUI"
    assert spec.music.genre == "classical"  # the reviewed track parameters
    # Still nothing new persisted by the page itself.
    assert len(repo.list_tracks()) == 1
    assert repo.list_trials() == []
