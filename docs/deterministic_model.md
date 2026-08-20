# Deterministic Reference Simulator

Unit: S09 (2026-08-20). Implementation: `src/ai_music_therapy/deterministic_simulator.py`.
Tests: `tests/test_deterministic_simulator.py` (full 75-cell preregistered matrix coverage).

## What this is - and is not

> **The rules below are fictional and non-clinical.** They are researcher-defined
> arithmetic over synthetic personas and music parameters, written to produce a
> reproducible software fixture for offline testing and demonstration. The scores
> are **not** validated clinical measures, carry no diagnostic or predictive
> validity for any real child, and must never be reported as clinical evidence
> (see `docs/ResearchEthics.md` and the fixed disclaimer on every trial record).

## Purpose

The simulator is the default ("deterministic") engine. It runs with no API key,
always produces the same output for the same input, and provides the reference
behavior that the optional AI engine (S10) will be compared against.

## Determinism pipeline

1. **Stable seed**: `stable_seed(persona_id, scene, music)` hashes the
   `sha256` of `persona_id | scene | music JSON`, taking the first 8 hex digits
   as an integer. Identical inputs yield an identical seed; changing any one of
   the three inputs changes the seed (guarded by test).
2. **Seeded RNG jitter**: `random.Random(seed)` contributes only small bounded
   jitter (±0.8 engagement, ±0.6 mood). The seed is recorded in every
   `TrialRecord` as provenance, so any persisted trial can be replayed exactly.
3. **Rule arithmetic**: bounded, clamped formulas (below) map the persona's
   sensory profile and the music parameters to four 1-10 scores.

## The rules (summary)

Inputs from the persona's `SensoryProfile`: `auditory_sensitivity`,
`sensory_seeking`, `change_sensitivity`. Inputs from `MusicParameters`:
`volume`, `bpm`, `tonality`, `lyrics_language`, `instrument`, `duration_sec`.

- **Anxiety** rises with auditory sensitivity, volume pressure (low=2 /
  medium=5 / high=8), tempo distance from the persona's preferred tempo
  (85 for high seekers, else 62), atonal tonality, and presence of lyrics.
- **Engagement** rises with sensory seeking and falls with tempo distance and
  anxiety; percussion adds engagement for high seekers.
- **Mood** tracks engagement positively and anxiety negatively.
- **Regulation** improves with mood and low volume, and degrades with anxiety.
- **Attention duration** is a fraction of the trial duration (0.35 to ~0.97)
  scaled by engagement, bounded to `[15, duration_sec]`.
- Every score is clamped to `[1, 10]` integers by `_clamp`.

Two override rules model extreme sensory interactions: high volume with high
auditory sensitivity raises anxiety and cuts engagement; high
change-sensitivity with atonal tonality adds anxiety.

## Time stages

Every output contains a complete `start -> middle -> end` time series
(`TimeStage`), each with in-range anxiety and engagement scores and a
non-empty observation string. Stage observations are fixed synthetic strings -
the numeric trajectory is what varies between trials.

## Safety flags (stop conditions)

Mirroring `docs/scenario_rubric.md` and `config/music_ontology.json`:

- simulated anxiety >= 8 -> "high simulated distress score; stop-condition
  should be shown";
- volume == high -> "high-volume setting requires explicit caution".

Both are enforced by tests across all matrix cells: the distress flag appears
**iff** anxiety >= 8, and the volume flag **iff** volume == high. The
preregistered 75-cell matrix deliberately contains no high-volume cells
(50 low / 25 medium); the volume flag is tested with a constructed input.

## Bounds and completeness guarantees (tested)

For every one of the 75 preregistered matrix cells (`config/trial_matrix.csv`):

- the returned seed equals `stable_seed(...)` for that exact input;
- re-simulation returns an identical `ReactionOutput` and seed;
- all four scores are integers in `[1, 10]`;
- attention duration is in `[15, duration_sec]`;
- the time series is exactly the three stages in order, each in range;
- `synthetic is True` and a non-empty `uncertainty_note` is present.

## Relationship to other components

- `scripts/smoke_test.py` runs one end-to-end `simulate()` call as its
  reproducibility check.
- `tests/test_repository.py` uses `simulate()` to build persisted trial
  fixtures, so persistence provenance is exercised with real engine output.
- `scripts/run_batch_demo.py` uses the deterministic engine for batch
  demonstration output.
- The scenario rubric's stop conditions (S04) and this engine's flags are kept
  aligned by design; drift is guarded by the flag-consistency tests above.

## Limitations (be able to state one)

- The formulas are invented for teaching; their coefficients have no empirical
  basis, and no validation study exists or is claimed.
- Jitter means two personas with identical profiles but different IDs produce
  different outputs - deliberate, so seed provenance is meaningful, but it
  means the rules are not a pure function of the profile alone.
- Only three sensory dimensions influence scores; communication, routine, and
  social support dimensions affect the persona schema but not the arithmetic.
- The engine models a single session; no carry-over effects between trials.
