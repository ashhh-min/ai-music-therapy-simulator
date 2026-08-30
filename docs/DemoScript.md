# Demo Script - 5 to 7 Minutes

Designed to run **fully offline** in deterministic mode. Never depend on a
live API during the final presentation; AI mode is described, not performed.
Every persona and every output shown is synthetic - say so, and let the
disclaimers on screen say it again.

## Setup (before the demo starts)

- `docker compose up -d` (local PostgreSQL), `.venv` active.
- `python -m ai_music_therapy.seed_demo` already ran (5 personas present).
- Optional: run 2-3 deterministic trials beforehand so the Dashboard has
  data on first open, or run one live in step 4.
- No `OPENAI_API_KEY` in the environment - deterministic mode is provable,
  not just claimed.

## Script

1. **Problem and observation (~45 s)** - One musical approach does not
   produce the same experience for every autistic person. The project asks a
   bounded software question (see `docs/ResearchReport.md`): how stable and
   attributable are simulated responses across personas, scenarios, engines,
   and time?
2. **Project boundary (~30 s)** - Point at the sidebar disclaimer: this is a
   synthetic educational simulator, not a clinical predictor. No real
   children, no clinical claims.
3. **Persona design (~45 s)** - Personas page: show multidimensional sensory,
   communication, routine, and support fields of 1-2 of the five fictional
   personas. Emphasize: researcher-designed, not derived from real children,
   not representative.
4. **Music trial (~60 s)** - Run a Trial page: configure genre, BPM, volume,
   instrument, tonality, duration, lyrics, and scenario; run it. Show the
   reaction plus the full provenance block: trial ID, engine, model, prompt
   version, seed, timestamp, synthetic label.
5. **Two engines (~45 s)** - Explain, do not call live: the deterministic
   engine is seeded rule arithmetic (same seed, same output, verified 75/75
   reproducible); the optional AI engine returns structured JSON through a
   strict validation boundary (schema, ranges, sanitizer - reject, never
   clamp) and is non-reproducible by design.
6. **Dashboard (~60 s)** - Heatmap (persona x scenario), same-music
   comparison across personas, radar profile, temporal stage view, rankings,
   and per-trial uncertainty notes. Every chart carries the non-clinical
   caption; empty cells are shown empty, never imputed.
7. **Audit trail and export (~30 s)** - Show the stored trial in the trial
   table, download one CSV export, and mention the write-once batch bundles
   (`data/local/batch_runs/<run_id>/` with trials.csv, trials.json,
   manifest.json) that no later step may overwrite.
8. **Batch and research result (~45 s)** - `scripts/run_batch.py` ran the
   frozen 75-cell matrix (5 personas x 5 scenarios x 3 variants) and a 5-cell
   AI comparison. Report highlights from `docs/analysis_notebook.md`:
   deterministic 75/75 reproducible; AI cell differs run-to-run (e.g.
   composite 0.7056 / 0.8167 / 0.7833 on one cell); 0 safety flags. Present
   patterns only as synthetic model behavior - descriptive, no inference.
9. **Limitations (~45 s)** - From `docs/limitations.md`: five fictional
   profiles do not represent autistic people; AI results depend on provider
   and prompt; no human participants; no clinical conclusion is possible.
10. **Future work (~30 s)** - Participatory design with autistic people and
    experts, validated instruments, real ethics review - before any
    real-person data could ever enter scope.

## Offline fallbacks

- Database down: the trial page shows a clear error; restart
  `docker compose up -d` and rerun `seed_demo`. The batch bundles and the
  Research Report need no database at all - pivot to them.
- Streamlit will not start: show the frozen bundle files and
  `docs/ResearchReport.md` in an editor; the narrative is identical.
- Question about AI mode without a key: show
  `docs/DeploymentGuide_StreamlitCloud_Neon.md` / README section instead of a
  live call.

## Claims discipline - what NOT to say

- Do not say the simulator predicts, diagnoses, treats, or measures anything
  real; do not call composite scores "outcomes", "effects", or "improvement"
  in a clinical sense.
- Do not present the personas as case studies or the rankings as
  recommendations.
- Do not imply the deterministic engine models people; it models the rules we
  wrote. A "finding" is a property of the rules.
- Do not report the cloud deployment as live unless Part C/D of
  `docs/DeploymentRunbook.md` has actually been executed with evidence.
