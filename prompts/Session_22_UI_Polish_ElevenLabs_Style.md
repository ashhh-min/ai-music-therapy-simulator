# Session 22 - UI Polish: ElevenLabs-Style Minimal Monochrome Theme

## Status of this unit
KICKED OFF by the student 2026-09-17: "could you polish the look-and-feel of
this music therapy site with modern simple style like elevenLab?" Theme mode
chosen by the student via review question: **Follow system** (light minimal by
day, dark studio at night, one CSS layer with prefers-color-scheme overrides).
The student also asked (mid-unit) for a Streamlit Community Cloud deployment
guide after the polish lands - delivered as a report step, since cloud go-live
itself remains the student's own session (needs their accounts).

## Prior state
S20 ACCEPTED 2026-09-17 (commit a1d1f09; acceptance flip ead8c02); suite 312
green; S21 (customizable wiring) prepared and DEFERRED. Streamlit 1.60.0,
which supports `base = "system"`, per-mode `[theme.light]`/`[theme.dark]`
palettes, `baseRadius`/`buttonRadius` ("full" = pill), `borderColor`, and
`showWidgetBorder` natively - so the ElevenLabs look is mostly configuration,
plus a thin CSS layer for typography, chrome-hiding, and inverted pill buttons.

## Session objective (cosmetic only - hard boundaries)
1. Modern minimal monochrome look inspired by elevenlabs.io: white/near-black
   backgrounds, achromatic accent (black pill buttons on light, white on dark),
   hairline borders, generous rounding, system-ui/Inter typography, Streamlit
   chrome (hamburger menu, footer) hidden.
2. Theme lives in `.streamlit/config.toml` (committable; secrets.toml stays
   gitignored) + `src/ai_music_therapy/ui/theme_css.py` injected ONCE from
   `app.py`. NO page file is modified, so all 312 tests (which AppTest page
   files directly, never app.py) are structurally unaffected.
3. FROZEN boundaries: the global sidebar disclaimer stays visible on every
   page (restyled, never hidden); no content, claim, label, or wording change;
   no widget key/label changes; frozen matrix/preregistration/bundles untouched;
   no new dependencies.
4. Cloud-readiness: `.streamlit/config.toml` ships in the repo, so Streamlit
   Community Cloud picks the theme up automatically; CSS uses only system
   fonts (no external font fetch, no CDN).

## Acceptance gates
- Full suite unchanged (312 via junit, 0 skips with PostgreSQL up), ruff clean,
  smoke PASS, `git diff --check` clean.
- Server starts on :8501 with the theme applied (HTTP 200, no config warnings
  in the log); light AND dark variants render (verified by the student's
  browser and/or OS-level switch; honest note: no screenshot tooling exists in
  this environment, so pixel-level visual acceptance is the student's step).
- Disclaimer caption/warning still present on every page (AppTest-verified via
  existing page tests; visually confirmed by the student).
- Evidence captured at `evidence/S22/check_outputs.txt`; control docs flipped;
  stop and report (including the requested deployment guide).
