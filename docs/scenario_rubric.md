# Music Parameter Ontology and Scenario Rubric

This document (S04) defines the controlled music-parameter vocabulary, the five support scenarios, and the **non-clinical** software outcome rubric and stop conditions. It is a software/methods specification, not a clinical protocol.

The machine-readable declaration lives in `config/music_ontology.json`; the runtime-enforced allowed values live in `src/ai_music_therapy/models.py` (`MusicParameters`, `TrialRecord`). A test asserts the two stay in agreement.

## Non-clinical statement

Every rubric and outcome dimension below is a **descriptive software signal** constructed from a synthetic persona and music parameters. None is a validated clinical measure. None diagnoses, predicts a real child's response, recommends treatment, or establishes effectiveness. "Favorable" means a favorable pattern in the *simulated* output, nothing more.

## Controlled music vocabulary

| Parameter | Allowed values / range | Notes |
|---|---|---|
| `genre` | classical, popular, nature, instrumental, vocal | Broad musical character. |
| `bpm` | 40–120 (beats/min) | Bounded to a calm-to-moderate range. |
| `volume` | low, medium, high | `high` triggers an explicit caution flag. |
| `instrument` | piano, guitar, percussion, synth, voice, mixed | Primary timbre/texture. |
| `tonality` | major, minor, atonal | `atonal` can raise the simulated abruptness signal. |
| `duration_sec` | 60–300 (seconds) | 1–5 minute simulated trial. |
| `lyrics_language` | none (default), english, chinese | Non-`none` adds a simulated cognitive-load signal. |

## Outcome dimensions (ReactionOutput)

All are synthetic, non-clinical signals: `anxiety_level` (1–10, higher = more simulated distress), `engagement_level` (1–10), `mood_score` (1–10), `regulation_score` (1–10), and `attention_duration_sec` (0–1800). They are researcher-defined descriptive indices, not validated instruments.

## The five support scenarios

Each scenario lists the simulated outcome it targets, its software rubric, and its stop conditions. Stop-condition language is surfaced via `safety_flags` on the reaction and must be displayed whenever a distress-like synthetic score appears (see `docs/Architecture.md`).

### sleep_support
- **Targets:** simulated anxiety (lower), regulation and mood (higher).
- **Rubric:** favorable = lower simulated anxiety with higher simulated regulation/mood across start/middle/end.
- **Stop conditions:** simulated `anxiety_level >= 8` → show the high-simulated-distress flag and a stop control; `volume == high` → show the high-volume caution.
- **Clinical note:** not a measure of sleep and not a treatment for sleep disturbance.

### anxiety_support
- **Targets:** simulated anxiety (lower), regulation and mood (higher).
- **Rubric:** favorable = reduction in simulated anxiety with stable/improved regulation and mood.
- **Stop conditions:** same distress/volume rules as above.
- **Clinical note:** not a validated anxiety measure and not an anxiety treatment.

### focus_support
- **Targets:** simulated engagement (higher), attention duration (longer), regulation.
- **Rubric:** favorable = higher simulated engagement and longer simulated attention with adequate regulation.
- **Stop conditions:** same distress/volume rules as above.
- **Clinical note:** not a validated measure of attention and not a treatment for attention-related conditions.

### engagement_support
- **Targets:** simulated engagement and mood (higher), richer simulated communication observations.
- **Rubric:** favorable = higher simulated engagement/mood and more varied simulated communication observations (model-generated text constrained by the persona's listed modes).
- **Stop conditions:** same distress/volume rules as above.
- **Clinical note:** not a validated measure of social engagement/communication and not a communication intervention.

### regulation_support
- **Targets:** simulated regulation and mood (higher), anxiety (lower).
- **Rubric:** favorable = higher simulated regulation/mood with lower simulated anxiety (simulated recovery/co-regulation).
- **Stop conditions:** same distress/volume rules as above.
- **Clinical note:** not a validated regulation measure and not a treatment for dysregulation.

## Limitations

- The rubric reads **simulated** signals; patterns across scenarios reflect software and prompt/model behavior, not real responses.
- The vocabulary is intentionally narrow (a controlled teaching ontology) and omits many real musical and contextual variables.
- Stop conditions are software display rules triggered by constructed scores; they are safeguards against misreading outputs as clinical, not clinical safety protocols.
