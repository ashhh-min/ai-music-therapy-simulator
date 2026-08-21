"""Batch experiment runner for the frozen 75-cell synthetic trial matrix.

Runs every cell of ``config/trial_matrix.csv`` with the deterministic engine
(the single source of truth shared with the tests), optionally adds a small
AI-engine comparison subset, validates completeness (missing or duplicate
cells fail the run), and exports an immutable, synthetic-labeled run bundle
under ``data/local/batch_runs/``. No findings or analysis are written here:
analysis belongs to a later unit.

Usage:
    python scripts/run_batch.py                 # 75 deterministic cells
    python scripts/run_batch.py --ai-subset 5   # + 5 AI comparison trials
    python scripts/run_batch.py --dry-run       # validate matrix only
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from ai_music_therapy.ai_client import ai_trial
from ai_music_therapy.config import settings
from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.export import LIMITATIONS_TEXT, trials_to_csv, trials_to_json
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord

MATRIX_PATH = Path("config/trial_matrix.csv")
PERSONAS_PATH = Path("data/public/synthetic_personas.json")
EXPECTED_CELLS = 75


class BatchError(Exception):
    """Raised when the matrix or the produced run fails validation."""


def load_matrix(path: Path = MATRIX_PATH) -> list[dict]:
    """Load the frozen trial matrix rows in file order."""
    if not path.exists():
        raise BatchError(
            f"Matrix file not found at {path} - run this script from the repo root."
        )
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def music_from_cell(cell: dict) -> MusicParameters:
    """Convert one matrix row into validated music parameters."""
    return MusicParameters(
        genre=cell["genre"],
        bpm=int(cell["bpm"]),
        volume=cell["volume"],
        instrument=cell["instrument"],
        tonality=cell["tonality"],
        duration_sec=int(cell["duration_sec"]),
        lyrics_language=cell["lyrics_language"],
    )


def validate_matrix(cells: list[dict]) -> None:
    """Fail unless the matrix is the frozen 75-cell 5x5x3 grid with unique ids."""
    if len(cells) != EXPECTED_CELLS:
        raise BatchError(
            f"Matrix has {len(cells)} cells; expected exactly {EXPECTED_CELLS}."
        )
    cell_ids = [cell["cell_id"] for cell in cells]
    duplicates = sorted({c for c in cell_ids if cell_ids.count(c) > 1})
    if duplicates:
        raise BatchError(f"Duplicate cell_id values in matrix: {duplicates}")
    personas = {cell["persona_id"] for cell in cells}
    scenes = {cell["scene"] for cell in cells}
    variants = {cell["variant_id"] for cell in cells}
    if len(personas) * len(scenes) * len(variants) != EXPECTED_CELLS:
        raise BatchError(
            f"Matrix is not the full product: {len(personas)} personas x "
            f"{len(scenes)} scenes x {len(variants)} variants."
        )
    expected = {
        f"{persona}__{scene}__{variant}"
        for persona in personas
        for scene in scenes
        for variant in variants
    }
    missing = sorted(expected - set(cell_ids))
    if missing:
        raise BatchError(f"Matrix is missing cells: {missing}")
    for cell in cells:
        music_from_cell(cell)  # raises pydantic ValidationError on bad parameters


def load_personas(path: Path = PERSONAS_PATH) -> dict[str, Persona]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    personas = [Persona.model_validate(item) for item in payload]
    return {persona.persona_id: persona for persona in personas}


def validate_personas_cover_matrix(
    personas: dict[str, Persona], cells: list[dict]
) -> None:
    matrix_ids = {cell["persona_id"] for cell in cells}
    unknown = sorted(matrix_ids - set(personas))
    if unknown:
        raise BatchError(f"Matrix references unknown personas: {unknown}")


def select_ai_cells(cells: list[dict], subset_size: int) -> list[dict]:
    """Pick a deterministic, spread-out subset for the optional AI comparison.

    Evenly strided indices over the matrix order, so a subset of 5 lands on one
    cell per persona instead of clustering on the first persona.
    """
    if subset_size < 0:
        raise BatchError("--ai-subset must be >= 0.")
    if subset_size > len(cells):
        raise BatchError(
            f"--ai-subset {subset_size} exceeds the {len(cells)} matrix cells."
        )
    return [cells[index * len(cells) // subset_size] for index in range(subset_size)]


def run_deterministic(
    cells: list[dict], personas: dict[str, Persona]
) -> list[TrialRecord]:
    """Simulate every matrix cell with the seeded deterministic engine."""
    trials = []
    for cell in cells:
        music = music_from_cell(cell)
        reaction, seed = simulate(personas[cell["persona_id"]], music, cell["scene"])
        trials.append(
            TrialRecord(
                trial_id=f"B-{cell['cell_id']}",
                persona_id=cell["persona_id"],
                scene=cell["scene"],
                music=music,
                reaction=reaction,
                engine="deterministic",
                prompt_version=settings.prompt_version,
                seed=seed,
            )
        )
    return trials


def run_ai_comparison(
    cells: list[dict], personas: dict[str, Persona]
) -> list[TrialRecord]:
    """Simulate the selected cells with the AI engine (requires an API key)."""
    if not settings.openai_api_key:
        raise BatchError(
            "--ai-subset requires OPENAI_API_KEY (set in .env.local); "
            "the default deterministic run needs no key."
        )
    trials = []
    for cell in cells:
        music = music_from_cell(cell)
        persona = personas[cell["persona_id"]]
        reaction, model_name = ai_trial(persona, music, cell["scene"])
        trials.append(
            TrialRecord(
                trial_id=f"B-AI-{cell['cell_id']}",
                persona_id=cell["persona_id"],
                scene=cell["scene"],
                music=music,
                reaction=reaction,
                engine="openai",
                model_name=model_name,
                prompt_version=settings.prompt_version,
                seed=None,
            )
        )
    return trials


def validate_results(
    cells: list[dict],
    trials: list[TrialRecord],
    expected_ai: int = 0,
) -> None:
    """Fail unless the run covers every matrix cell exactly once.

    Deterministic trials must cover all 75 cells; AI comparison trials are
    additional and must match the requested subset size.
    """
    deterministic = [trial for trial in trials if trial.engine == "deterministic"]
    ai = [trial for trial in trials if trial.engine == "openai"]
    trial_ids = [trial.trial_id for trial in trials]
    duplicates = sorted({t for t in trial_ids if trial_ids.count(t) > 1})
    if duplicates:
        raise BatchError(f"Duplicate trial_id values in run: {duplicates}")
    covered = {trial.trial_id.removeprefix("B-") for trial in deterministic}
    expected = {cell["cell_id"] for cell in cells}
    missing = sorted(expected - covered)
    if missing:
        raise BatchError(f"Run is missing matrix cells: {missing}")
    extra = sorted(covered - expected)
    if extra:
        raise BatchError(f"Run contains cells outside the matrix: {extra}")
    if len(deterministic) != EXPECTED_CELLS:
        raise BatchError(
            f"Expected exactly {EXPECTED_CELLS} deterministic trials, "
            f"got {len(deterministic)}."
        )
    if len(ai) != expected_ai:
        raise BatchError(
            f"Expected {expected_ai} AI comparison trials, got {len(ai)}."
        )


def matrix_sha256(path: Path = MATRIX_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_run(
    trials: list[TrialRecord],
    output_root: Path,
    run_id: str,
    matrix_checksum: str,
    ai_subset_size: int,
    ai_model: str | None,
) -> Path:
    """Write the immutable run bundle; refuse to overwrite an existing run."""
    run_dir = output_root / run_id
    if run_dir.exists():
        raise BatchError(f"Run directory already exists (immutable): {run_dir}")
    run_dir.mkdir(parents=True)
    manifest = {
        "run_id": run_id,
        "created_at": datetime.now(UTC).isoformat(),
        "synthetic": True,
        "matrix_path": str(MATRIX_PATH),
        "matrix_sha256": matrix_checksum,
        "n_matrix_cells": EXPECTED_CELLS,
        "n_deterministic": sum(t.engine == "deterministic" for t in trials),
        "n_ai_comparison": sum(t.engine == "openai" for t in trials),
        "requested_ai_subset": ai_subset_size,
        "ai_model": ai_model,
        "prompt_version": settings.prompt_version,
        "engines": sorted({t.engine for t in trials}),
        "limitations": LIMITATIONS_TEXT,
        "findings": None,
        "findings_note": (
            "No findings are written at the batch stage; analysis is a later unit."
        ),
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (run_dir / "trials.csv").write_text(trials_to_csv(trials), encoding="utf-8")
    (run_dir / "trials.json").write_text(trials_to_json(trials), encoding="utf-8")
    return run_dir


def default_run_id(checksum: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{checksum[:8]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/local/batch_runs"),
        help="Directory that holds immutable per-run bundles.",
    )
    parser.add_argument(
        "--ai-subset",
        type=int,
        default=0,
        help="Optional: also run N spread-out cells with the AI engine.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Override the run id (default: UTC timestamp + matrix checksum).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the matrix and exit without simulating or writing.",
    )
    args = parser.parse_args(argv)

    cells = load_matrix()
    try:
        validate_matrix(cells)
        personas = load_personas()
        validate_personas_cover_matrix(personas, cells)
        ai_cells = select_ai_cells(cells, args.ai_subset)
    except BatchError as error:
        print(f"BATCH FAILED: {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(
            f"Matrix valid: {len(cells)} cells, "
            f"{len({c['persona_id'] for c in cells})} personas, "
            f"{len({c['scene'] for c in cells})} scenes, "
            f"{len({c['variant_id'] for c in cells})} variants."
        )
        return 0

    try:
        trials = run_deterministic(cells, personas)
        ai_trials = run_ai_comparison(ai_cells, personas)
        trials.extend(ai_trials)
        validate_results(cells, trials, expected_ai=args.ai_subset)
        checksum = matrix_sha256()
        run_id = args.run_id or default_run_id(checksum)
        run_dir = write_run(
            trials,
            args.output_root,
            run_id,
            checksum,
            ai_subset_size=args.ai_subset,
            ai_model=settings.openai_model if ai_trials else None,
        )
    except BatchError as error:
        print(f"BATCH FAILED: {error}", file=sys.stderr)
        return 1

    print(
        f"Batch run complete: {len(trials)} trials "
        f"({len(trials) - args.ai_subset} deterministic + {args.ai_subset} AI "
        f"comparison) written to {run_dir}"
    )
    print(f"Matrix sha256: {checksum}")
    print("All outputs are labeled synthetic; no findings are written at this stage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
