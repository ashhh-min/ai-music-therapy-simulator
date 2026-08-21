"""Tests for the S16 batch runner: matrix contract, completeness, immutable export."""

import csv
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_batch  # noqa: E402

from ai_music_therapy.models import MusicParameters  # noqa: E402


@pytest.fixture(scope="module")
def cells() -> list[dict]:
    return run_batch.load_matrix()


@pytest.fixture(scope="module")
def personas() -> dict:
    return run_batch.load_personas()


def test_frozen_matrix_validates(cells):
    run_batch.validate_matrix(cells)
    assert len(cells) == 75
    ids = [cell["cell_id"] for cell in cells]
    assert len(set(ids)) == 75  # unique cell ids
    assert len({cell["persona_id"] for cell in cells}) == 5
    assert len({cell["scene"] for cell in cells}) == 5
    assert len({cell["variant_id"] for cell in cells}) == 3


def test_every_cell_parses_to_valid_music(cells):
    for cell in cells:
        music = run_batch.music_from_cell(cell)
        assert isinstance(music, MusicParameters)
        assert music.duration_sec == int(cell["duration_sec"])


def test_matrix_validation_rejects_missing_cell(cells):
    renamed = dict(cells[0])
    renamed["cell_id"] = "P-LILY__sleep_support__V9"  # unique id, combination now uncovered
    broken = [renamed] + cells[1:]
    with pytest.raises(run_batch.BatchError, match="missing cells"):
        run_batch.validate_matrix(broken)


def test_matrix_validation_rejects_wrong_size(cells):
    with pytest.raises(run_batch.BatchError, match="expected exactly 75"):
        run_batch.validate_matrix(cells[:-1])


def test_matrix_validation_rejects_duplicate_cell(cells):
    broken = cells[:-1] + [cells[0]]  # still 75 rows, but one id appears twice
    with pytest.raises(run_batch.BatchError, match="Duplicate cell_id"):
        run_batch.validate_matrix(broken)


def test_full_deterministic_run_covers_every_cell(cells, personas):
    run_batch.validate_personas_cover_matrix(personas, cells)
    trials = run_batch.run_deterministic(cells, personas)
    run_batch.validate_results(cells, trials, expected_ai=0)
    assert len(trials) == 75
    assert all(trial.engine == "deterministic" for trial in trials)
    assert all(trial.seed is not None for trial in trials)


def test_missing_trial_fails_completeness(cells, personas):
    trials = run_batch.run_deterministic(cells, personas)
    dropped = trials[:-1]
    cell_id = trials[-1].trial_id.removeprefix("B-")
    with pytest.raises(run_batch.BatchError, match=cell_id):
        run_batch.validate_results(cells, dropped, expected_ai=0)


def test_duplicate_trial_fails_completeness(cells, personas):
    trials = run_batch.run_deterministic(cells, personas)
    with pytest.raises(run_batch.BatchError, match="Duplicate trial_id"):
        run_batch.validate_results(cells, trials + [trials[0]], expected_ai=0)


def test_extra_cell_fails_completeness(cells, personas):
    trials = run_batch.run_deterministic(cells, personas)
    extra = trials[0].model_copy(update={"trial_id": "B-UNKNOWN__x__V1"})
    with pytest.raises(run_batch.BatchError, match="outside the matrix"):
        run_batch.validate_results(cells, trials + [extra], expected_ai=0)


def test_deterministic_run_is_reproducible(cells, personas):
    first = run_batch.run_deterministic(cells, personas)
    second = run_batch.run_deterministic(cells, personas)
    key = lambda t: (t.trial_id, t.seed, t.reaction.model_dump())  # noqa: E731
    assert [key(t) for t in first] == [key(t) for t in second]


def test_ai_subset_selection_spreads_personas(cells):
    subset = run_batch.select_ai_cells(cells, 5)
    assert len(subset) == 5
    assert len({cell["persona_id"] for cell in subset}) == 5  # one per persona
    assert subset == run_batch.select_ai_cells(cells, 5)  # deterministic choice
    assert run_batch.select_ai_cells(cells, 0) == []
    with pytest.raises(run_batch.BatchError, match="exceeds"):
        run_batch.select_ai_cells(cells, 76)
    with pytest.raises(run_batch.BatchError, match="must be"):
        run_batch.select_ai_cells(cells, -1)


def test_ai_comparison_requires_api_key(cells, personas, monkeypatch):
    import dataclasses

    no_key = dataclasses.replace(run_batch.settings, openai_api_key=None)
    monkeypatch.setattr(run_batch, "settings", no_key)
    with pytest.raises(run_batch.BatchError, match="OPENAI_API_KEY"):
        run_batch.run_ai_comparison(cells[:1], personas)


def test_write_run_bundle_is_labeled_and_immutable(tmp_path, cells, personas):
    trials = run_batch.run_deterministic(cells, personas)
    checksum = run_batch.matrix_sha256()
    run_dir = run_batch.write_run(trials, tmp_path, "testrun", checksum, 0, None)

    rows = list(csv.DictReader((run_dir / "trials.csv").open(encoding="utf-8")))
    assert len(rows) == 75
    assert all(row["synthetic"] == "true" for row in rows)
    assert all(row["limitations"] for row in rows)

    document = json.loads((run_dir / "trials.json").read_text(encoding="utf-8"))
    assert document["synthetic"] is True
    assert document["count"] == 75

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["synthetic"] is True
    assert manifest["matrix_sha256"] == checksum
    assert manifest["n_deterministic"] == 75
    assert manifest["n_ai_comparison"] == 0
    assert manifest["findings"] is None  # no findings at the batch stage

    with pytest.raises(run_batch.BatchError, match="immutable"):
        run_batch.write_run(trials, tmp_path, "testrun", checksum, 0, None)


def test_main_dry_run_validates_without_writing(capsys):
    assert run_batch.main(["--dry-run"]) == 0
    assert "Matrix valid: 75 cells" in capsys.readouterr().out
