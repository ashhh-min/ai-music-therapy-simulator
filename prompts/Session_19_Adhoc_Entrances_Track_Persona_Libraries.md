# S19 - Ad-hoc Entrances: Staged Review and Approved Track/Persona Libraries

## Role
Act as the implementation partner for this bounded extension session in `ai-music-therapy-simulator`. This unit extends the completed S01-S18 plan at the student's request; it is bounded the same way: one unit, evidence-first, stop and report.

## Decisions already made by the student (do not reopen)
1. Approved tracks store the **extracted parameter profile + source-file hash only**. Raw audio files are never persisted (not on disk, not in the database).
2. Confirmation trials during the review stage are **not persisted**: shown in-memory only, like S11's unsaved persona drafts.
3. The persona entrance supports **three input modes**: JSON upload, AI-assisted draft (reusing the S11 pipeline), and a manual form editor.
4. Nothing enters a library without explicit approval; approved entries are write-once; existing IDs (personas, tracks) are never overwritten.

## Read First
- `README.md`, `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`
- `docs/AuthoritativePlan.md`, `docs/Architecture.md`, `docs/TestPlan.md`
- `docs/DataGovernance.md`, `docs/ResearchEthics.md`, `docs/ai_boundary.md`
- `docs/persona_design.md`, `docs/persona_review_checklist.md` (S11 gates)
- `config/music_ontology.json` (S04 frozen contract) and `docs/scenario_rubric.md`
- `src/ai_music_therapy/persona_service.py` (existing draft/lint/approve pipeline)
- `src/ai_music_therapy/db.py` + `repository.py` (pooled persistence layer, D027)
- `prompts/GlobalEngineeringContract.md`; latest entries in `docs/decisions.md` and `docs/CoBuildLog.md`

## Prior-State Check
- Confirm `S18` is accepted and the working tree is clean.
- Confirm `S19` is the only active unit in `TASKS.md`.
- Record the pre-unit Git checkpoint.
- Run the currently passing baseline checks before editing (234 tests, ruff, smoke).

## Session Objective
Give the student two first-class ad-hoc entrances that share one staged workflow: **propose -> review (editable) -> confirmation trial (in-memory only) -> explicit approval -> write-once library entry**. Track entrance: upload a sound/music file, extract parameters, review them, confirm behavior with a trial, and only after approval add the track to a TrackBase for future analysis. Persona entrance: propose a new persona via JSON upload, AI-assisted draft, or manual form; same staged gates; approved personas join the persona set.

## Shared Staged Workflow (the core contract)
States for both entrances: `proposed -> under_review -> trial_confirmed -> approved | rejected`.
- Review state lives in `st.session_state` (ephemeral). The database is written **only at approval**.
- Rejection persists nothing (no library entry, no trial, no uploaded content).
- Approval commits a write-once entry; modifying an approved entry later means a new version entry, never a silent overwrite.
- Every screen of the flow keeps the synthetic/non-clinical framing; "confirming effects" means confirming simulator behavior, and the UI says so.

## Track Entrance
1. Upload: `st.file_uploader`, wav/flac/ogg only, ~20 MB cap, in-memory. Show a short rights note: the uploader declares they may use this file; the site stores no audio.
2. Extract (local, deterministic, no API): tempo/BPM, RMS energy -> volume bucket (low/medium/high), duration, spectral centroid, major/minor heuristic from chroma. Use librosa + soundfile (add to `pyproject.toml` and `requirements.txt`). Extraction must be pure-function, testable, and raise clean typed errors for corrupt/empty/oversized input.
3. Map to `MusicParameters` (the S04 ontology): estimates fill what DSP can know; the student overrides what it cannot (genre, instrument, tonality confidence, lyrics language). Record per-field estimated-vs-override provenance. If the ontology needs a value (e.g. an `unclassified` instrument/genre), that is a decision entry plus a contract-test update - the ontology stays the guarded single source of truth.
4. Review stage: extracted values displayed with their signal evidence, all editable. Nothing persisted.
5. Confirmation trial: run persona x scenario x engine with the pending profile; result shown in-memory only, never saved.
6. Approval: commit a TrackBase entry: `track_id`, display name, approved-at, source-file sha256, final `MusicParameters`, extraction provenance (feature values, extractor + library versions, which fields were overridden), synthetic label. New `tracks` table following the Repository pattern with the same `CHECK (synthetic = 1)` guard.
7. Future use: approved tracks selectable in the trial page and available for analysis as an explicitly-labelled exploratory cohort.

## Persona Entrance
Three input modes into the same staged workflow:
1. **JSON upload** - validated against the frozen `Persona` schema (`extra="forbid"`); invalid files rejected with the validation error shown; works with no API key.
2. **AI-assisted draft** - reuse `persona_service.py` (Responses API, strict validation, lint flags, near-duplicate check); still optional and key-gated.
3. **Manual form editor** - build/edit every persona field in the UI; the same schema validates on submit.
Gates (existing S11 logic, applied at review and again at save): stereotype lint hard flags block approval; missing synthetic statement blocks approval; near-duplicate requires explicit confirmation; existing `persona_id`s are never overwritten. Approval saves through the existing `personas` path.

## Boundaries that must not move
- The frozen 75-cell matrix and preregistration stay untouched. Uploaded tracks/personas form a separate, explicitly-labelled exploratory cohort; they never enter the official matrix or bundle findings, and any analysis of them is reported as exploratory.
- Raw audio is never written to disk or database anywhere in the pipeline (including temp files).
- Review-stage trials never reach the database.
- Deterministic no-key operation keeps working end-to-end (JSON-upload track path and manual/JSON persona path must work with no API key).
- Every persona and track stays explicitly synthetic; clinical claims boundary unchanged.

## Files to Create or Modify
- `src/ai_music_therapy/audio_analysis.py` (new)
- `src/ai_music_therapy/track_service.py` or equivalent staged-library module (new)
- `src/ai_music_therapy/ui/upload_track.py`, `src/ai_music_therapy/ui/propose_persona.py` (new pages; register in `app.py`)
- `src/ai_music_therapy/models.py`, `repository.py`, `db.py` only as needed (TrackBase entry model, `tracks` table, repository methods)
- `src/ai_music_therapy/persona_service.py` only if reuse requires small extension
- `config/music_ontology.json` only with a decision entry + contract-test update
- `pyproject.toml`, `requirements.txt` (librosa/soundfile)
- `tests/` (new test module(s))
- `docs/DataGovernance.md` (upload handling + no-retention rule), other docs only where behavior changed
- `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`, `docs/decisions.md`, `docs/CoBuildLog.md`, `evidence/S19/`

## Implementation Order (land incrementally; report if scope forces a split)
1. Staged-workflow state machine + TrackBase persistence (table, model, repository methods, write-once tests).
2. Audio extraction + mapping + track entrance UI end-to-end.
3. Persona entrance: JSON upload, then AI draft reuse, then manual form.
4. Docs + control docs + release scans.

## Tests and Checks
- Generated audio fixtures only (e.g. synthesized click track at known BPM, silence, corrupt bytes) - never commit real music files.
- Extraction tests (tempo tolerance, volume-bucket boundaries, duration), typed errors for bad input.
- State-machine tests: reject -> zero persistence; approve -> write-once; second approval of same ID refused; review trials never persisted (assert DB unchanged).
- Persona entrance tests: JSON schema rejection, lint hard-flag block, overwrite refusal, manual-form schema validation.
- Existing suite stays green; run smallest relevant tests first, then full `pytest`, `python scripts/smoke_test.py`, `ruff check src tests scripts`, `git diff --check`.
- Scan changed files for secrets, private data, unlabelled synthetic output, unsupported clinical claims.
- Save truthful command output under `evidence/S19/`.

## Acceptance Criteria
- Upload -> extract -> review (edit) -> confirmation trial -> approval persists a TrackBase entry with full provenance; rejection persists nothing.
- Raw audio is verifiably never persisted.
- All three persona input modes reach the same gates; approval saves, rejection does not, existing IDs never overwritten.
- Deterministic no-key path works for both entrances (AI draft correctly key-gated).
- Frozen matrix, preregistration, and bundle immutability untouched.
- Full suite + ruff + smoke green; clean checkout still runs deterministic.
- `TASKS.md`, `STATUS.md`, decisions (D028), co-build log, tests, and evidence agree.

## Do Not Do
- Do not persist raw audio or review-stage trials.
- Do not modify the frozen matrix, preregistration, or existing immutable bundles.
- Do not overwrite approved entries or existing personas.
- Do not present extracted values as more precise than they are (they are estimates; show them as estimates).
- Do not add credentials, real-person data, medical advice, or fabricated evidence.
- Do not implement future units or out-of-scope analytics.
- Do not report a deployment, experiment, or test as successful unless it was actually completed.

## TASKS.md Update
Mark `S19` complete only after every acceptance item passes. Record changed files, actual test results, evidence path, unresolved issues, and prepare the next step without implementing it.

## Stop Condition
Stop after `S19`. Report the diff, tests, evidence, issues, and next step; do not begin anything else.
