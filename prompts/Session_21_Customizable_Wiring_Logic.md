# Session 21 - OPTIONAL: Customizable Wiring Logic for the Patch Generator

## Status of this unit
PREPARED 2026-09-17 at the student's request ("please add one optional S21 for
customize the wiring logic as will. I will implement S21 in the future sometime").
This unit is OPTIONAL and DEFERRED: NOTHING in this file is executed until the
student explicitly says to start S21. If the student kicks it off, re-read this
prompt fresh, run the Prior-State Check, and re-confirm the scope below (the
student's wishes may have evolved since 2026-09-17).

## Role
You are the AI co-builder in a student-led, evidence-first course workflow. One
bounded unit at a time; stop and report after the gates pass; wait for the
student's acceptance before any further unit. All standing rules from
`TASKS.md` Global Rules apply (no secrets committed, synthetic labels
everywhere, no clinical claims, no invented evidence, modify only what the unit
needs, evidence under `evidence/S21/`).

## Prior-State Check (run before any edit)
- S20 is ACCEPTED (2026-09-17): parameter-to-Max/MSP patch generation; one
  deterministic PatchSpec -> .maxpat + wiring DOT + preview WAV; suite 312
  green (junit, 0 skips with PostgreSQL up); D029 recorded; evidence at
  `evidence/S20/check_outputs.txt`; implementation commit a1d1f09.
- Confirm with `git log --oneline -5` and a full-suite run (baseline 312).
- PostgreSQL for DB-gated AppTests: `colima start` then `docker compose up -d`.
- Interpreter: `.venv/bin/python` (3.13.x). System python3 is too old.
- This environment swallows pytest's console count line: use `--junitxml`.

## Student's intention (verbatim, 2026-09-17)
Asked why "the generated wiring logic is fixed" and whether it can be
customized; after the design rationale was explained (determinism gate,
.maxpat loadability risk, closed object whitelist), the student chose to
accept S20 as-is and defer customization to an optional future unit.

## Session Objective
Make the patch generator's musical wiring customizable "as will" from the
existing "Generate a Max Patch" page, WITHOUT breaking the two invariants that
define the feature: (1) determinism - identical inputs (including identical
customizations) produce byte-identical PatchSpec/.maxpat/DOT/WAV; (2)
loadability discipline - the closed object whitelist and the verified Max 9
header shape are untouched.

## Proposed scope (RE-CONFIRM with the student at kickoff)
New optional inputs, each defaulting to exactly today's S20 behavior:
1. Root note (today: fixed ROOT_MIDI 57 = A3).
2. Steps per bar (today: fixed 8) with the step pattern length following it.
3. Custom degree pattern per generation (today: fixed per-genre patterns);
   a "use genre default" toggle preserves S20 behavior.
4. Scale choice beyond major/minor/atonal (e.g., dorian, pentatonic) as
   additional semitone tables; custom semitone sets stretch goal.
5. Gain table (today: fixed low 0.18 / medium 0.35 / high 0.60).
6. Envelope shape presets (e.g., fast decay / pluck / soft pad / percussive);
   today the instrument fixes the envelope.
7. Auto-stop on/off (today: always on) and bar-count override.
8. Optional voice structure toggles that stay inside the whitelist (e.g.,
   detune pair on/off for any instrument, mixer on/off).
Explicitly OUT unless the student re-scopes: drag-and-drop graph editing (that
is Max's job - the .maxpat remains freely editable inside Max), Max execution
claims, Pd/MIDI export, persisting customization presets anywhere (session
state + downloads only, like S20), new audio-sample playback, copyrighted
material of any kind.

## Decisions already made (design constraints carried from S20/D029)
- Single PatchSpec source of truth stays: customization extends
  `build_patch_spec` inputs; the three derivations remain pure functions.
- ALL customization values join the seed input (canonical JSON of parameters
  PLUS customization), so same-customization -> byte-identical artifacts and
  any change -> a new seed. The seed formula will therefore differ from S20's
  for customized specs; DEFAULT specs must keep the exact S20 seeds
  (backward compatibility gate: the probe parameters instrumental/68/low/
  piano/major/180/none must still yield seed prefix 1ab48c73 and byte-identical
  maxpat/WAV vs `evidence/S20/synthetic_patch_1ab48c73.maxpat`).
- Input validation is explicit and bounded (Pydantic, extra=forbid): pattern
  length == steps per bar, degrees within the chosen scale or chromatic range,
  gains in (0, 1], root MIDI in a sane range, bars >= 1; invalid input is
  rejected in the UI with a clear message, never silently clamped.
- The object whitelist and patcher header shape do not change; new toggles may
  only add/remove boxes from the already-whitelisted vocabulary.
- Honest verification boundary unchanged: automated tests cover structure,
  determinism, validation, and backward compatibility; "opens and plays in
  Max" remains a MANUAL student step. Every customized patch carries the same
  synthetic + trademark annotation comments.
- The page's "nothing is persisted" property is absolute: no DB writes, no
  files written by the site.

## Implementation order (draft; re-confirm at kickoff)
1. Extend `patch_generation.py`: a `WiringCustomization` model (all fields
   optional with S20 defaults) threaded through `build_patch_spec`; seed
   covers it; defaults reproduce S20 byte-for-byte.
2. Tests first for backward compatibility (default == S20 artifacts, seed
   1ab48c73 probe) and for each customization knob (determinism, validation
   rejection, visible effect on spec/maxpat/DOT/WAV).
3. Page: a collapsed "Customize wiring (optional)" expander; untouched
   expander == today's page behavior.
4. Docs: README section update, decisions entry, CoBuildLog entry,
   limitations update if any boundary moved.
5. Gates: full suite (312 + new, 0 skips), ruff, smoke, `git diff --check`,
   release scans (no binaries committed, labels present), clean checkout
   no-key, evidence capture at `evidence/S21/check_outputs.txt`, control-doc
   flips (dash-free anchors, sub1 assert-once pattern), commit + push.

## Acceptance gates
- Default path is byte-identical to accepted S20 output (seed 1ab48c73 probe).
- Every customization knob: deterministic, validated, and visibly reflected in
  all three artifacts (patch text, DOT, preview WAV).
- Whitelist and header shape unchanged; synthetic + trademark labels intact.
- Nothing persisted; frozen matrix/preregistration/bundles untouched.
- Suite + ruff + smoke + clean checkout green; evidence captured honestly,
  including the unverified-in-Max boundary.

## Stop and report
After the gates pass, stop. Report: what was customized, the backward-
compatibility proof, test counts, honest Max-loadability status, evidence
paths, and the commit hash. Wait for the student's acceptance.
