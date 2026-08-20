# Trial Audit Trail and Provenance

Unit: S13 (2026-08-20). Implementation: `src/ai_music_therapy/repository.py`
(filtering, `get_trial`, duplicate rejection), `src/ai_music_therapy/export.py`,
audit UI in `src/ai_music_therapy/ui/trial.py`. Tests: `tests/test_provenance.py`.

## Provenance contract

Every persisted trial carries, by schema (not convention):

| Field | Meaning | Enforced |
|---|---|---|
| `trial_id` | Unique ID | DB primary key; duplicates rejected at insert, nothing overwritten |
| `persona_id` | Which synthetic persona | FK to `personas` |
| `scene` | Support scenario | Literal (5 scenarios) |
| `engine` | `deterministic` or `openai` | Literal |
| `model_name` | AI model (AI trials only) | present for AI trials by workflow contract |
| `prompt_version` | Frozen prompt version | required, non-empty |
| `seed` | Deterministic seed | non-null for deterministic trials; **always null for AI trials** (AI output is not reproducible - we never fake a seed) |
| `created_at` | UTC timestamp | required |
| `disclaimer` | Fixed limitations text | default, present on every record |
| `reaction` | Full validated `ReactionOutput` | schema-validated, complete start/middle/end sequence |

Additionally every row in the `trials` table carries the database-level
`CHECK (synthetic = 1)` guard (D017) - a non-synthetic trial cannot be stored
by any code path.

## Audit workflow (trial page)

1. Run a trial (deterministic or AI). Refused/invalid output is never saved.
2. The **Trial audit trail** section lists all accepted runs with composable
   filters: persona, scenario, engine.
3. **Inspect provenance**: select any trial ID to view its full record JSON.
4. **Export**: CSV (flat, one row per trial) or JSON (full-fidelity records).

## Export labeling

Both export formats carry the synthetic label and limitations text, so an
exported file cannot be mistaken for clinical data:

- **CSV**: a `synthetic=true` column and a `limitations` column on *every row*
  (rows can be copied out of context without losing the label).
- **JSON**: document-level `"synthetic": true`, `"limitations"`, and `"count"`,
  plus complete `TrialRecord` objects (each with its own `disclaimer`).

## Evidence capture

For accepted runs (e.g. the preregistered S16 batch), export the filtered set
and store it under `evidence/<UnitID>/`. The JSON export round-trips: exported
records re-validate as `TrialRecord` unchanged (tested).

## Integrity guarantees (tested)

- Duplicate `trial_id` insert raises `ValueError`; existing records are never
  overwritten (the count stays unchanged).
- Missing required fields (`trial_id`, `engine`, `prompt_version`, `reaction`,
  `music`) fail validation; incomplete records cannot be constructed, so they
  cannot be persisted.
- Filters compose (`persona AND scene AND engine`) and return only matching
  records; unknown filters return an empty set.

## Limitations (be able to state one)

The audit trail records what was saved, with full provenance - but there is no
immutable log (e.g. append-only hash chain): a database administrator could
edit rows. For an educational synthetic dataset this is proportionate; a real
research audit trail would need append-only storage.
