# S20 - Parameter to Patch: Max/MSP Generation with Wiring View and Local Preview

## Role
Act as the implementation partner for this bounded extension session in `ai-music-therapy-simulator`. This unit extends the completed S01-S18 plan (and S19's entrances) at the student's request; it is bounded the same way: one unit, evidence-first, stop and report.

## The student's idea (as stated)
Apply Max/MSP to the site in the REVERSED direction of the S19 track entrance: instead of audio in -> parameters out, take the input music parameters and (a) generate a short sample music via Max/MSP and (b) provide the logic wiring at the same time.

## Reality constraint (fact, not a preference - do not design around it)
Max/MSP is a commercial desktop application (Cycling '74). It has no web runtime, no browser embedding, and no supported headless/server-side rendering mode. The site therefore CANNOT execute Max or produce Max's actual audio output. What IS possible, and what this unit builds:

1. The site deterministically GENERATES a Max patch file (`.maxpat`, which is JSON) from `MusicParameters` - a real, loadable patch the student opens in desktop Max, where Max itself renders the sample music.
2. The site shows the LOGIC WIRING of that patch (diagram + patch JSON) so the pedagogy is visible without Max.
3. The site renders a LOCAL PYTHON PREVIEW of the same patch specification (numpy/soundfile, in-memory wav, `st.audio` + `st.download_button`) - so the student hears and downloads a short sample music file directly from the site, in a format every audio program can open. It is explicitly labeled as an approximation of the patch's intended material, NOT Max/MSP audio; Max renders the definitive version when the student opens the `.maxpat` on the desktop.

All three artifacts derive from ONE deterministic patch specification, so they can never disagree about structure.

## Decisions already made (do not reopen)
1. One shared `PatchSpec` (pydantic model) is the single source: `.maxpat` text, wiring diagram, and preview wav are all pure functions of it. Determinism: same `MusicParameters` (+ generator version) -> byte-identical spec and patch.
2. Inputs are the frozen S04 `MusicParameters` only - manual widgets or an approved TrackBase track (reusing S19's music-source pattern). No ontology change; S20 is a read-only consumer.
3. Nothing is persisted: generated patches, previews, and specs live in `st.session_state` and user-initiated downloads only. No database writes, no audio files written to disk or committed to the repo (test fixtures are generated in-memory signals, as in S19).
4. Every artifact carries the synthetic/educational/non-clinical framing: the generated music demonstrates software behavior of a parameter mapping; it makes no therapeutic claim, and the page says so.
5. Trademark/attribution: "Max and Max/MSP are trademarks of Cycling '74. This project is not affiliated with or endorsed by Cycling '74. Opening generated patches requires a Max license (or trial)." This line appears on the page and in the README section.
6. Honest verification boundary: automated tests assert STRUCTURAL invariants only (valid JSON, unique box ids, patchlines referencing existing ids, whitelisted object vocabulary, determinism, preview signal properties). "Opens in Max and makes sound" is a MANUAL acceptance step performed by the student on a desktop Max install; if unavailable, the limitation is documented truthfully and the unit does NOT claim Max-verified patches.

## Known facts about the format (from research, verify in the spike)
- `.maxpat` is JSON since Max 6: `{"patcher": {..., "boxes": [{"box": {"id": "obj-N", "maxclass": "newobj", "text": "osc~ 440", "numinlets":…, "numoutlets":…, "patching_rect": [x,y,w,h]}}], "lines": [{"patchline": {"source": ["obj-N", 0], "destination": ["obj-M", 0], "order": i}}]}}`. There is NO official public schema; generators work from real-file templates and must preserve the patcher header/metadata. Malformed JSON makes Max open the file as TEXT instead of a patcher. Max 9 shifted some key names versus Max 8.
- `py2max` (github.com/shakfu/py2max) is a maintained pure-Python library that generates `.maxpat` offline with a Patcher/Box/Patchline model. Decide in the spike: adopt `py2max` as a dependency, or hand-roll a minimal template-based generator (fewer dependencies, more control). Record the decision in `docs/decisions.md` (D029) with the evidence that drove it.
- Target a conservative object vocabulary that works across Max 8/9: e.g. `metro`, `counter`/`uzi`, `makenote`/`noteout` NOT required (audio-only preferred: `osc~`/`cycle~`, `line~`/`function` envelopes, `gain~`/`*~`, `ezdac~`/`dac~`, `toggle`, `s`/`r`, `select`, `coll`/`itable` for scale tables, `print`). Signal-rate audio only; no MIDI hardware assumptions.

## Read First
- `README.md`, `TASKS.md`, `STATUS.md`, `SESSION_STATE.md`
- `docs/AuthoritativePlan.md`, `docs/Architecture.md`, `docs/TestPlan.md`
- `docs/DataGovernance.md`, `docs/ResearchEthics.md`, `docs/ai_boundary.md`
- `config/music_ontology.json` (frozen contract; read-only here)
- `src/ai_music_therapy/models.py` (`MusicParameters`), `audio_analysis.py` (S19 DSP + in-memory wav patterns), `track_service.py`, `ui/upload_track.py`, `ui/trial.py` (music-source radio pattern), `ui/confirm_trial.py`
- `docs/decisions.md` (D028 + both corrections), `docs/CoBuildLog.md` latest entries, `prompts/GlobalEngineeringContract.md`

## Prior-State Check
- Confirm `S19` is ACCEPTED (both review revisions landed) and the working tree is clean.
- Confirm `S20` is the only active unit in `TASKS.md` (append; never overwrite wholesale).
- Record the pre-unit Git checkpoint.
- Run the passing baseline before editing (284 tests via junit, ruff, smoke).

## Session Objective
Add one new page, **"Generate a Max Patch (Experimental)"**, plus a pure-function module `src/ai_music_therapy/patch_generation.py`, implementing the reversed S19 flow: choose music parameters (manual or an approved TrackBase track) -> deterministic `PatchSpec` -> three synchronized artifacts (downloadable `.maxpat`, wiring view, local preview audio), with provenance and synthetic labeling, persisting nothing.

## The PatchSpec contract
`PatchSpec` records: `spec_version` (constant), `source` ("manual" or "track:<track_id>"), the originating `MusicParameters`, a `seed` = sha256 of the canonical parameters JSON (drives any pseudo-random choices so output stays deterministic), a boxes list (id, object text, role, rect) and a patchlines list (source, destination, order). Pure functions:
- `build_patch_spec(music, source) -> PatchSpec`
- `spec_to_maxpat(spec) -> str` (valid `.maxpat` JSON text; preserves the template header; ids `obj-N`)
- `spec_to_wiring_dot(spec) -> str` (Graphviz DOT for `st.graphviz_chart`, which renders client-side in Streamlit - no new dependency; nodes = boxes with object text, edges = patchlines, grouped by role: timing / pitch / amplitude / output)
- `spec_to_preview_wav(spec) -> bytes` (in-memory wav via soundfile, <= 30 s preview regardless of `duration_sec`, sample rate 22050, mono, peak-normalized with headroom)

## Parameter-to-patch mapping (deterministic, documented on the page)
Researcher-defined and explicitly a demonstration mapping, not music theory:
- `bpm` -> `metro` interval (60000/bpm ms) driving a step sequencer.
- `tonality` -> scale table: major/minor semitone sets; `atonal` -> chromatic walk from the seed. Pitch root fixed (e.g. A3 = 220 Hz) to stay deterministic.
- `instrument` -> oscillator voice: piano = `cycle~` with fast-decay `line~` envelope; guitar = triangle-ish (`tri~` or summed partials) pluck; percussion = filtered noise bursts (`noise~` + `line~`); synth = `saw~`/`phasor~` with slow filter; voice = detuned sine pair (formant gesture, no singing claim); mixed = two-voice blend.
- `volume` -> output `gain~` in dB: low/medium/high mapped to documented fixed values (e.g. -18/-12/-6 dB) - same "researcher-defined thresholds" honesty as S19's RMS buckets.
- `genre` -> pattern/texture knob: classical = arpeggio over the scale table; popular = bass+chord alternation; nature = slow pad / lowpassed `noise~` bed; instrumental = straight sequence; vocal = sequence plus a text comment box showing that lyrics language (display only, no voice synthesis).
- `duration_sec` -> number of sequencer bars (preview is capped at 30 s; the patch itself loops/ends per `duration_sec` via the transport/`uzi` count).
- `lyrics_language` != none -> a comment box in the patch with the language label; never synthesized singing, never real lyrics.

## Boundaries and exclusions
- No Max execution, no RNBO, no `thispatcher` runtime scripting (requires running Max), no MIDI hardware, no Pure Data export (different format) - all recorded as exclusions.
- No copyrighted or sampled audio: synthesis from primitives only; no audio binaries committed.
- No therapeutic/clinical claim about generated music; no personal data; synthetic labels on every artifact; no affiliation with Cycling '74.
- Frozen 75-cell matrix, preregistration, bundles, ontology, and TrackBase schema untouched; no DB writes of any kind.

## Implementation order
1. Spike (record in D029): validate a minimal generated `.maxpat` structure - decide `py2max` vs hand-rolled template (if `py2max` is adopted, add to `pyproject.toml` + `requirements.txt`; check its Max-version compatibility). Student opens the spike patch in desktop Max if available and reports; otherwise document the unverified-in-Max limitation honestly.
2. `patch_generation.py`: PatchSpec + the four pure functions.
3. UI page + `app.py` registration (Lab section, after "Propose a Persona"): source radio (manual parameters / approved track), mapping table shown as a caption/expander, generate button, artifacts: `st.download_button` (`.maxpat`, filename `synthetic_patch_<seed8>.maxpat`), `st.graphviz_chart` wiring, `st.audio` preview + `st.download_button` for the same preview bytes (`synthetic_preview_<seed8>.wav`, playable in any audio software), patch-JSON expander, provenance line (spec_version, seed, source, generator timestamp), synthetic/non-clinical + trademark captions.
4. Tests: determinism (same params -> identical spec/maxpat bytes; different params -> different seed); structural invariants (JSON parses, `patcher` header present, unique ids, every patchline endpoint exists, object vocabulary within whitelist); mapping tests (bpm->metro text, volume->gain dB, tonality->scale table, instrument->voice objects); preview tests (wav bytes decode via soundfile, duration <= 30 s, non-silent, peak within headroom); AppTest page render + end-to-end generate + download presence + approved-track source; no-network guarantee (nothing imports openai in this module).
5. Docs: README section (with trademark line), `docs/decisions.md` D029, `docs/CoBuildLog.md` entry, `docs/DataGovernance.md` (generated patches/previews = synthetic artifacts, session-only, never persisted), `docs/limitations.md` (preview is an approximation; Max-loadability verified manually or documented as unverified).
6. Gates: full suite via junit (284 baseline + new), ruff, smoke, `git diff --check`, clean-checkout no-key verification, release scans (no secrets, no clinical claims, synthetic labels, zero audio binaries committed), `evidence/S20/check_outputs.txt` captured truthfully, control docs updated (append-only), commit + push.

## Acceptance gates (all must be true, evidence captured)
- New page generates all three artifacts from manual parameters AND from an approved TrackBase track; deterministic for identical inputs.
- `.maxpat` output passes every structural test; Max-loadability status reported honestly (manually verified by the student, or explicitly recorded as unverified).
- Preview wav is in-memory only, capped at 30 s, labeled as an approximation, and downloadable (`.wav`) alongside the `.maxpat`; nothing persisted anywhere; downloads are user-initiated.
- Full suite green via junit with zero skips for DB-gated tests that can run, ruff clean, smoke PASS, clean checkout with no key and no `.env.local` green.
- Synthetic/non-clinical framing and Cycling '74 trademark/attribution line visible on the page and in the README.
- Frozen matrix, preregistration, ontology, bundles, and database schema untouched.

## Stop and report
After the gates pass, stop. Report: what was built, the spike decision and its evidence, mapping summary, test counts, honest statement of Max-loadability verification status, evidence paths, and the commit hash. Wait for the student's acceptance before any further unit.
