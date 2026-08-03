# Test Plan

## Unit tests

- Persona schemas reject missing synthetic markers and invalid scores.
- Music parameters enforce allowed ranges and categories.
- Deterministic engine is reproducible for identical inputs.
- All reaction values remain within declared bounds.
- Repository round-trips Pydantic records.
- Composite index remains between 0 and 1.

## Integration checks

- Seed command creates five persona records.
- A deterministic trial can be saved and reloaded.
- Dashboard handles empty and non-empty datasets.
- AI mode is disabled gracefully when the key is absent.
- AI response is rejected if structured validation fails.

## Research checks

- Every output is labeled synthetic.
- Every trial records engine/model/prompt/seed provenance.
- No report section converts synthetic scores into clinical claims.
- 75-run matrix has exactly 5 × 5 × 3 unique design cells.

## Release checks

- `pytest` passes.
- `ruff check src tests scripts` passes.
- `python scripts/smoke_test.py` passes.
- No secret/private-data scan findings.
- Manual five-to-seven-minute demo passes in deterministic mode.
