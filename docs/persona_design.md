# Persona Design

This document finalizes the multidimensional persona schema (S03) and records the neurodiversity safeguards and representation limitations for the five fictional profiles. It is a design note, not a clinical instrument.

## Scope and status

- The personas are **fictional and explicitly synthetic**. They exist to drive a deterministic and (optional) AI simulation for software and methods education.
- They are **not** representative of the autistic population and **not** based on any real child.
- No schema field provides a single high/medium/low functioning-level label.

## Schema (`src/ai_music_therapy/models.py`)

- `Persona` — the top-level fictional profile.
- `SupportProfile` — qualitative multidimensional support needs (communication, sensory, routine, social).
- `SensoryProfile` — quantitative sensory dimensions on 1–10 scales (auditory sensitivity, sensory seeking, change sensitivity).

Key fields of `Persona`: `persona_id` (must start with `P-`), `display_name`, `age_years` (4–18), `synthetic` (locked to `True`), `profile_summary`, `support_profile` (`SupportProfile`), `sensory_profile` (`SensoryProfile`), and four non-empty behavioural lists: `communication_modes`, `music_preferences`, `known_triggers`, `preferred_supports`.

## Representation of the five required dimensions

| Dimension | Where it is represented | Type |
|---|---|---|
| Communication | `SupportProfile.communication` + `communication_modes` | qualitative + list |
| Sensory | `SensoryProfile` (3 scales) + `SupportProfile.sensory` | quantitative + qualitative |
| Routine | `SupportProfile.routine` | qualitative |
| Trigger | `known_triggers` | list |
| Support | `preferred_supports` + `SupportProfile.social` | list + qualitative |

## Neurodiversity safeguards

1. **Synthetic is enforced, not optional.** `synthetic: Literal[True] = True` makes every persona carry an immutable synthetic marker.
2. **No functioning-level label.** Support is multidimensional (`SupportProfile` plus the behavioural lists). `model_config = ConfigDict(extra="forbid")` on `Persona`, `SupportProfile`, and `SensoryProfile` rejects any undeclared field, so a `functioning_level` (or similar) field cannot be introduced silently. A test asserts this rejection.
3. **No empty dimensions.** The behavioural lists and key text fields use `min_length=1`, so a persona cannot validate with blank communication modes, triggers, or supports.
4. **Bounded scales.** Sensory dimensions are constrained to 1–10 and age to 4–18, preventing out-of-range values.
5. **Stable identity.** `persona_id` must start with `P-`, giving each fictional profile a stable, anonymized reference for provenance.

## Validation

- `python scripts/smoke_test.py` loads and validates all five personas from `data/public/synthetic_personas.json`.
- `tests/test_models.py` asserts: five synthetic personas; all five dimensions present; `routine` required; `functioning_level` rejected; extra fields rejected; empty lists rejected; the `P-` id prefix enforced.
- The deterministic simulator is unchanged and continues to run with no API key.

## Stereotype and representation limitations

- **Not representative.** Five invented profiles cannot capture the heterogeneity of the autistic population. Any pattern across them is an artifact of the design, not a population finding.
- **Risk of stereotype.** Condensing a profile into a few dimensions and scales can flatten individuality and reinforce clichés (for example, associating a persona only with distress or only with a narrow preference). Outputs must be read as software behavior, not as a description of real autistic people.
- **No self-advocacy input.** These profiles were authored for a prototype and were not co-designed with autistic people. Identity-first language is used and a single functioning-level label is avoided (consistent with the S02 evidence base, including ASAN guidance), but authorship bias remains.
- **No clinical use.** Profiles and any derived scores are synthetic. They do not diagnose, predict a real child's response, recommend treatment, or establish effectiveness.
- **Future participation.** Any move toward real-world data or intervention work requires expert, autistic-community, guardian, institutional, and ethics review before proceeding (see `docs/ResearchEthics.md`).

## Provenance note

Every persona is stored with `synthetic = true`. Trial records built from these personas carry engine, model, prompt version, seed (when applicable), timestamp, and a fixed synthetic disclaimer, so synthetic status is preserved end to end (see `docs/Architecture.md`).
