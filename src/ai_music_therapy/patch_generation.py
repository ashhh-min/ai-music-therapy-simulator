"""Deterministic MusicParameters -> Max/MSP patch generation (S20).

The REVERSED S19 flow: instead of audio in -> parameters out, this module
turns reviewed ``MusicParameters`` into ONE deterministic ``PatchSpec`` and
derives three synchronized artifacts from it:

1. ``spec_to_maxpat``   - a `.maxpat` patch file (JSON) for desktop Max/MSP.
2. ``spec_to_wiring_dot`` - Graphviz DOT of the same wiring logic.
3. ``spec_to_preview_wav`` - an in-memory WAV preview rendered locally with
   numpy/soundfile. The preview APPROXIMATES the patch's intended material;
   it is not Max/MSP audio output. Max renders the definitive version when
   the student opens the patch on the desktop.

Everything is a pure function: no network, no API key, no persistence, no
files written. The mapping is a researcher-defined demonstration of software
behavior, not music theory and not a therapeutic claim.

`.maxpat` has no official public specification; the structure here follows a
real Max 9 export (patcher header keys, boxes/lines wrappers, obj-N ids,
patching_rect, source/destination pairs) and uses a deliberately minimal,
conservative object vocabulary. Box metadata (numinlets/numoutlets/
outlettype) is best-effort: Max re-instantiates objects from their text.
Max and Max/MSP are trademarks of Cycling '74; this project is not affiliated
with or endorsed by Cycling '74.
"""

from __future__ import annotations

import io
import json
import math
from hashlib import sha256

import numpy as np
import soundfile
from pydantic import BaseModel, Field

from .models import MusicParameters

SPEC_VERSION = "1.0.0"
GENERATOR = "patch_generation"

#: Preview rendering constants (in-memory only; never persisted).
PREVIEW_SAMPLE_RATE = 22050
PREVIEW_MAX_SEC = 30.0
PREVIEW_PEAK = 0.89  # ~ -1 dBFS headroom after normalization

#: Musical constants of the demonstration mapping (researcher-defined).
ROOT_MIDI = 57  # A3 = 220 Hz, fixed so output stays deterministic
STEPS_PER_BAR = 8

SCALES: dict[str, list[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "atonal": list(range(12)),
}

#: Volume bucket -> linear amplitude for the constant gain stage. Mirrors the
#: honesty of S19's RMS thresholds: researcher-defined, not calibrated loudness.
VOLUME_AMPLITUDE: dict[str, float] = {"low": 0.18, "medium": 0.35, "high": 0.6}

#: Genre -> 8-step pattern as scale-degree indices (degree >= len(scale) wraps
#: up an octave). nature plays the same pattern at half speed (double step time)
#: with a soft sustained envelope.
GENRE_PATTERNS: dict[str, list[int]] = {
    "instrumental": [0, 1, 2, 3, 4, 5, 6, 7],
    "classical": [0, 2, 4, 2, 0, 2, 4, 7],
    "popular": [0, 4, 0, 4, 5, 4, 0, 4],
    "nature": [0, 0, 4, 4, 0, 0, 2, 2],
    "vocal": [0, 1, 2, 3, 4, 5, 6, 7],
}

#: Atonal override: a chromatic walk rotated by a seed-derived offset, so the
#: choice is reproducible from the parameters alone.
_ATONAL_BASE = list(range(8))

#: Instrument -> additive voice definition: list of (waveform object, gain,
#: detune Hz) plus the amp-envelope (line~ ramp pairs [target, ms]) and an
#: optional semitone shift applied to every step note.
VOICES: dict[str, dict[str, object]] = {
    "piano": {"oscs": [("cycle~", 1.0, 0.0)], "envelope": [[0.9, 5], [0.0, 550]], "shift": 0},
    "guitar": {"oscs": [("tri~", 1.0, 0.0)], "envelope": [[0.85, 10], [0.0, 420]], "shift": 0},
    # Pitched percussion: the step note sounds two octaves down as a short tone.
    "percussion": {"oscs": [("osc~", 1.0, 0.0)], "envelope": [[1.0, 2], [0.0, 140]], "shift": -24},
    "synth": {"oscs": [("saw~", 1.0, 0.0)], "envelope": [[0.75, 140], [0.0, 480]], "shift": 0},
    "voice": {"oscs": [("cycle~", 1.0, 0.0), ("cycle~", 0.5, 0.7)],
              "envelope": [[0.8, 90], [0.0, 500]], "shift": 0},
    "mixed": {"oscs": [("cycle~", 1.0, 0.0), ("tri~", 0.5, 0.0)],
              "envelope": [[0.85, 20], [0.0, 420]], "shift": 0},
}

#: Conservative object vocabulary the generator may emit (Max 8/9 core).
OBJECT_WHITELIST = frozenset(
    {"metro", "counter", "sel", "mtof", "cycle~", "tri~", "saw~", "osc~",
     "line~", "*~", "+~", "+", "ezdac~"}
)

TRADEMARK_LINE = (
    "Max and Max/MSP are trademarks of Cycling '74. This project is not "
    "affiliated with or endorsed by Cycling '74."
)

#: Patcher header verified against a real Max 9 export (the format has no
#: official public specification; see module docstring).
_PATCHER_HEADER = {
    "fileversion": 1,
    "appversion": {
        "major": 9, "minor": 0, "revision": 0,
        "architecture": "x64", "modernui": 1,
    },
    "classnamespace": "box",
    "rect": [34.0, 99.0, 1280.0, 640.0],
    "gridsize": [15.0, 15.0],
}

#: Best-effort box metadata per object name: (numinlets, numoutlets, outlettype).
_BOX_META: dict[str, tuple[int, int, list[str]]] = {
    "metro": (2, 1, ["bang"]),
    "counter": (5, 4, ["int", "bang", "int", "int"]),
    "sel": (1, 9, ["bang"] * 8 + ["int"]),
    "mtof": (1, 1, ["float"]),
    "+": (2, 1, ["float"]),
    "cycle~": (2, 1, ["signal"]),
    "tri~": (2, 1, ["signal"]),
    "saw~": (2, 1, ["signal"]),
    "osc~": (2, 1, ["signal"]),
    "line~": (2, 2, ["signal", "bang"]),
    "*~": (2, 1, ["signal"]),
    "+~": (2, 1, ["signal"]),
}


class PatchBox(BaseModel):
    """One box in the generated patcher (a Max object, message, toggle, or comment)."""

    id: str
    maxclass: str  # newobj | message | toggle | comment | ezdac~
    role: str  # timing | pitch | voice | envelope | amplitude | output | annotation
    text: str | None = None
    patching_rect: list[float] = Field(min_length=4, max_length=4)


class PatchLine(BaseModel):
    """One patchline (wire) between two boxes."""

    source: str
    source_outlet: int = 0
    destination: str
    destination_inlet: int = 0
    order: int = 0


class PatchSpec(BaseModel):
    """The single deterministic source for all three artifacts.

    The musical plan fields (step_notes, beat_ms, bars, oscillators, envelope,
    amplitude) drive BOTH the generated patcher and the local preview, so the
    artifacts can never disagree about what the patch is supposed to play.
    """

    spec_version: str = SPEC_VERSION
    generator: str = GENERATOR
    source: str  # "manual" or "track:<track_id>"
    seed: str  # sha256 of the canonical MusicParameters JSON (provenance)
    music: MusicParameters
    root_midi: int = ROOT_MIDI
    scale_name: str
    step_notes: list[int]  # STEPS_PER_BAR MIDI note numbers, shift included
    beat_ms: int  # final step time (genre may double it)
    bars: int
    oscillators: list[tuple[str, float, float]]  # (object, gain, detune Hz)
    envelope: list[list[float]]  # line~ ramp pairs [target, ms]
    amplitude: float
    boxes: list[PatchBox]
    lines: list[PatchLine]


def _degree_to_midi(degree: int, scale: list[int], shift: int) -> int:
    octave, index = divmod(degree, len(scale))
    return ROOT_MIDI + scale[index] + 12 * octave + shift


def build_patch_spec(music: MusicParameters, source: str = "manual") -> PatchSpec:
    """Build the deterministic PatchSpec for reviewed music parameters.

    Pure function: identical parameters always yield an identical spec (and
    therefore identical `.maxpat`, DOT, and preview bytes).
    """
    seed = sha256(music.model_dump_json().encode("utf-8")).hexdigest()
    voice = VOICES[music.instrument]
    scale_name = music.tonality
    scale = SCALES[scale_name]
    shift = int(voice["shift"])  # type: ignore[arg-type]

    if scale_name == "atonal":
        rotation = int(seed[:8], 16) % 12
        pattern = [(degree + rotation) % 12 for degree in _ATONAL_BASE]
    else:
        pattern = GENRE_PATTERNS[music.genre]
    step_notes = [_degree_to_midi(degree, scale, shift) for degree in pattern]

    beat_ms = int(round(60000.0 / music.bpm))
    if music.genre == "nature":
        beat_ms *= 2  # half-speed pad feel
    envelope = [list(pair) for pair in voice["envelope"]]  # type: ignore[arg-type]
    if music.genre == "nature":
        envelope = [[0.6, 200.0], [0.0, float(beat_ms) * 1.8]]

    step_sec = beat_ms / 1000.0
    bars = max(1, math.ceil(music.duration_sec / (STEPS_PER_BAR * step_sec)))

    spec = PatchSpec(
        source=source,
        seed=seed,
        music=music,
        scale_name=scale_name,
        step_notes=step_notes,
        beat_ms=beat_ms,
        bars=bars,
        oscillators=[tuple(osc) for osc in voice["oscs"]],  # type: ignore[arg-type]
        envelope=envelope,
        amplitude=VOLUME_AMPLITUDE[music.volume],
        boxes=[],
        lines=[],
    )
    spec.boxes, spec.lines = _build_graph(spec)
    return spec


# ------------------------------------------------------------ patch graph

def _box_meta(object_name: str) -> tuple[int, int, list[str]]:
    return _BOX_META.get(object_name.split()[0], (1, 1, ["signal"]))


class _GraphBuilder:
    """Deterministic box/line assembly with a simple role-column layout."""

    def __init__(self) -> None:
        self._n = 0
        self.boxes: list[PatchBox] = []
        self.lines: list[PatchLine] = []

    def add(self, maxclass: str, role: str, rect: list[float],
            text: str | None = None) -> str:
        self._n += 1
        box_id = f"obj-{self._n}"
        self.boxes.append(
            PatchBox(id=box_id, maxclass=maxclass, role=role, text=text,
                     patching_rect=rect)
        )
        return box_id

    def add_object(self, text: str, role: str, rect: list[float]) -> str:
        return self.add("newobj", role, rect, text)

    def connect(self, source: str, destination: str,
                source_outlet: int = 0, destination_inlet: int = 0) -> None:
        order = sum(1 for ln in self.lines if ln.source == source
                    and ln.source_outlet == source_outlet)
        self.lines.append(
            PatchLine(source=source, source_outlet=source_outlet,
                      destination=destination, destination_inlet=destination_inlet,
                      order=order)
        )


def _newobj_rect(text: str, x: float, y: float) -> list[float]:
    return [x, y, max(50.0, 8.0 * len(text) + 24.0), 22.0]


def _build_graph(spec: PatchSpec) -> tuple[list[PatchBox], list[PatchLine]]:
    g = _GraphBuilder()

    # -- annotation (top rows)
    g.add("comment", "annotation", [20.0, 15.0, 620.0, 22.0],
          f"Synthetic patch generated by ai-music-therapy-simulator (S20, spec {SPEC_VERSION}).")
    g.add("comment", "annotation", [20.0, 37.0, 620.0, 22.0],
          "Educational prototype: demonstrates a parameter mapping. No therapeutic claim.")
    g.add("comment", "annotation", [20.0, 59.0, 620.0, 22.0], TRADEMARK_LINE)
    g.add("comment", "annotation", [20.0, 81.0, 620.0, 22.0],
          f"Parameters: {spec.music.genre}, {spec.music.bpm} BPM, {spec.music.volume}, "
          f"{spec.music.instrument}, {spec.music.tonality}, {spec.music.duration_sec} s | "
          f"source {spec.source} | seed {spec.seed[:8]}")
    g.add("comment", "annotation", [20.0, 103.0, 620.0, 22.0],
          f"Plays {spec.bars} bar(s) of {STEPS_PER_BAR} steps then auto-stops. "
          "Click the toggle to start; enable audio in ezdac~.")
    if spec.music.lyrics_language != "none":
        g.add("comment", "annotation", [20.0, 125.0, 620.0, 22.0],
              f"Lyrics language: {spec.music.lyrics_language} - text annotation only; "
              "no voice synthesis and no real lyrics.")

    # -- timing column
    toggle = g.add("toggle", "timing", [20.0, 170.0, 24.0, 24.0])
    metro = g.add_object(f"metro {spec.beat_ms}", "timing",
                         _newobj_rect(f"metro {spec.beat_ms}", 20.0, 210.0))
    steps = g.add_object(f"counter 0 {STEPS_PER_BAR - 1}", "timing",
                         _newobj_rect(f"counter 0 {STEPS_PER_BAR - 1}", 20.0, 250.0))
    stop = g.add("message", "timing", [20.0, 340.0, 30.0, 22.0], "0")
    g.connect(toggle, metro)
    g.connect(metro, steps)
    if spec.bars > 1:
        bars_box = g.add_object(f"counter 0 {spec.bars - 1}", "timing",
                                _newobj_rect(f"counter 0 {spec.bars - 1}", 20.0, 295.0))
        g.connect(steps, bars_box, source_outlet=1)  # step carry advances bars
        g.connect(bars_box, stop, source_outlet=1)    # final bar carry stops
    else:
        g.connect(steps, stop, source_outlet=1)
    g.connect(stop, toggle)

    # -- pitch column: step count -> note messages -> mtof
    sel_text = "sel " + " ".join(str(i) for i in range(STEPS_PER_BAR))
    sel = g.add_object(sel_text, "pitch", _newobj_rect(sel_text, 180.0, 250.0))
    g.connect(steps, sel)
    mtof = g.add_object("mtof", "pitch", _newobj_rect("mtof", 480.0, 250.0))
    for i, note in enumerate(spec.step_notes):
        msg = g.add("message", "pitch", [320.0, 150.0 + 40.0 * i, 44.0, 22.0], str(note))
        g.connect(sel, msg, source_outlet=i)
        g.connect(msg, mtof)

    # -- voice column: oscillators (+ detune / gain / mixer when needed)
    osc_rects = [[620.0, 210.0], [620.0, 330.0]]
    osc_ids: list[str] = []
    for index, (wave, _gain, detune) in enumerate(spec.oscillators):
        freq_src = mtof
        if detune:
            det = g.add_object(f"+ {detune}", "voice",
                               _newobj_rect(f"+ {detune}", 480.0, 300.0))
            g.connect(mtof, det)
            freq_src = det
        osc = g.add_object(wave, "voice", _newobj_rect(wave, *osc_rects[index]))
        g.connect(freq_src, osc)
        osc_ids.append(osc)
    if len(osc_ids) == 1:
        voice_out = osc_ids[0]
    else:
        mixer = g.add_object("+~", "voice", _newobj_rect("+~", 760.0, 250.0))
        g.connect(osc_ids[0], mixer, destination_inlet=0)
        second_gain = g.add_object(
            f"*~ {spec.oscillators[1][1]}", "voice",
            _newobj_rect(f"*~ {spec.oscillators[1][1]}", 620.0, 380.0),
        )
        g.connect(osc_ids[1], second_gain)
        g.connect(second_gain, mixer, destination_inlet=1)
        voice_out = mixer

    # -- envelope: metro bangs the line~ ramp message every step
    env_text = ", ".join(
        f"{target:g} {ms:g}" for target, ms in spec.envelope
    )
    env_msg = g.add(
        "message", "envelope",
        [620.0, 130.0, max(70.0, 8.0 * len(env_text) + 24.0), 22.0],
        env_text,
    )
    line = g.add_object("line~", "envelope", _newobj_rect("line~", 760.0, 130.0))
    g.connect(metro, env_msg)
    g.connect(env_msg, line)
    env_mult = g.add_object("*~", "envelope", _newobj_rect("*~", 900.0, 210.0))
    g.connect(voice_out, env_mult, destination_inlet=0)
    g.connect(line, env_mult, destination_inlet=1)

    # -- amplitude: constant gain from the volume bucket
    amp_msg = g.add("message", "amplitude", [900.0, 300.0, 52.0, 22.0],
                    f"{spec.amplitude:g}")
    amp_mult = g.add_object("*~", "amplitude", _newobj_rect("*~", 1040.0, 210.0))
    g.connect(amp_msg, amp_mult, destination_inlet=1)
    g.connect(env_mult, amp_mult, destination_inlet=0)

    # -- output
    ezdac = g.add("ezdac~", "output", [1180.0, 210.0, 36.0, 36.0])
    g.connect(amp_mult, ezdac, destination_inlet=0)
    g.connect(amp_mult, ezdac, destination_inlet=1)

    return g.boxes, g.lines


# ------------------------------------------------------------ artifact 1: maxpat

def _box_to_json(box: PatchBox) -> dict:
    if box.maxclass == "newobj":
        object_name = (box.text or "").split()[0]
        inlets, outlets, outlettype = _box_meta(object_name)
        if object_name == "sel" and box.text:
            outlets = len(box.text.split()) - 1 + 1  # one bang per arg + unmatched
            outlettype = ["bang"] * (outlets - 1) + ["int"]
    elif box.maxclass == "message":
        content = box.text or ""
        try:
            int(content.replace(",", " ").split()[0])
            outlettype = ["list"] if "," in content else ["int"]
        except ValueError:
            outlettype = ["list"] if "," in content else ["float"]
        inlets, outlets = 2, 1
    elif box.maxclass == "toggle":
        inlets, outlets, outlettype = 1, 1, ["int"]
    elif box.maxclass == "comment":
        inlets, outlets, outlettype = 1, 0, []
    elif box.maxclass == "ezdac~":
        inlets, outlets, outlettype = 2, 0, []
    else:  # pragma: no cover - vocabulary is closed
        raise ValueError(f"unsupported maxclass: {box.maxclass}")
    return {
        "box": {
            "id": box.id,
            "maxclass": box.maxclass,
            "numinlets": inlets,
            "numoutlets": outlets,
            "outlettype": outlettype,
            "patching_rect": box.patching_rect,
            **({"text": box.text} if box.text is not None else {}),
        }
    }


def spec_to_maxpat(spec: PatchSpec) -> str:
    """Serialize the spec's graph as `.maxpat` JSON text (Max-importable file)."""
    patcher = dict(_PATCHER_HEADER)
    patcher["boxes"] = [_box_to_json(box) for box in spec.boxes]
    patcher["lines"] = [
        {
            "patchline": {
                "destination": [line.destination, line.destination_inlet],
                "order": line.order,
                "source": [line.source, line.source_outlet],
            }
        }
        for line in spec.lines
    ]
    patcher["originid"] = "pat-1"
    patcher["dependency_cache"] = []
    patcher["autosave"] = 0
    return json.dumps({"patcher": patcher}, indent=2, ensure_ascii=True)


# ------------------------------------------------------------ artifact 2: wiring

_ROLE_ORDER = ("timing", "pitch", "voice", "envelope", "amplitude", "output", "annotation")


def spec_to_wiring_dot(spec: PatchSpec) -> str:
    """Render the same wiring logic as Graphviz DOT (client-side rendering in
    Streamlit via ``st.graphviz_chart``; no server-side graphviz dependency)."""
    parts = [
        "digraph patch {",
        '  rankdir=LR; node [shape=box, fontname="Helvetica", fontsize=10];',
        f'  label="Synthetic patch wiring - seed {spec.seed[:8]} ({spec.source}). '
        'Educational demonstration, not a therapeutic device."; labelloc=t;',
    ]
    for role in _ROLE_ORDER:
        members = [b for b in spec.boxes if b.role == role]
        if not members:
            continue
        parts.append(f"  subgraph cluster_{role} {{")
        parts.append(f'    label="{role}"; style=dashed; color="#888888";')
        for box in members:
            label = (box.text or box.maxclass).replace('"', "'")
            parts.append(f'    "{box.id}" [label="{box.id}\\n{label}"];')
        parts.append("  }")
    for line in spec.lines:
        ports = ""
        if line.source_outlet or line.destination_inlet:
            ports = f' [label="{line.source_outlet}->{line.destination_inlet}", fontsize=8];'
        else:
            ports = ";"
        parts.append(f'  "{line.source}" -> "{line.destination}"{ports}')
    parts.append("}")
    return "\n".join(parts)


# ------------------------------------------------------------ artifact 3: preview

def _waveform(name: str, phase: np.ndarray) -> np.ndarray:
    if name in ("cycle~", "osc~"):
        return np.sin(phase)
    if name == "tri~":
        return (2.0 / math.pi) * np.arcsin(np.sin(phase))
    if name == "saw~":
        wrapped = (phase / (2.0 * math.pi)) % 1.0
        return 2.0 * wrapped - 1.0
    raise ValueError(f"unsupported waveform: {name}")  # pragma: no cover


def _envelope_curve(envelope: list[list[float]], n_samples: int) -> np.ndarray:
    """Piecewise-linear amp curve mirroring the line~ ramp message."""
    curve = np.zeros(n_samples)
    if n_samples == 0:
        return curve
    points = [(0.0, 0.0)]  # line~ starts from rest for each note in the preview
    t = 0.0
    for target, ms in envelope:
        t += ms / 1000.0
        points.append((t, float(target)))
    times = np.array([p[0] for p in points])
    values = np.array([p[1] for p in points])
    sample_times = np.arange(n_samples) / PREVIEW_SAMPLE_RATE
    curve = np.interp(sample_times, times, values, right=0.0)
    return curve


def spec_to_preview_wav(spec: PatchSpec) -> bytes:
    """Render the in-memory WAV preview of the spec's musical plan.

    An APPROXIMATION of the patch's intended material (same notes, timing,
    voice gains, envelope shape, and amplitude), rendered locally - NOT
    Max/MSP audio output. Deterministic: identical specs yield identical
    bytes. Never persisted; callers may stream or offer it for download.
    """
    step_sec = spec.beat_ms / 1000.0
    total_sec = min(spec.bars * STEPS_PER_BAR * step_sec, PREVIEW_MAX_SEC)
    n_total = int(round(total_sec * PREVIEW_SAMPLE_RATE))
    buffer = np.zeros(n_total + PREVIEW_SAMPLE_RATE)  # ring-out tail

    env_len_sec = sum(ms for _, ms in spec.envelope) / 1000.0
    total_steps = spec.bars * STEPS_PER_BAR
    for step in range(total_steps):
        t0 = step * step_sec
        if t0 >= total_sec:
            break
        start = int(round(t0 * PREVIEW_SAMPLE_RATE))
        n_note = int(round(env_len_sec * PREVIEW_SAMPLE_RATE)) + 1
        end = min(start + n_note, buffer.size)
        if end <= start:
            break
        window = np.arange(end - start) / PREVIEW_SAMPLE_RATE
        curve = _envelope_curve(spec.envelope, end - start)
        freq = 440.0 * 2.0 ** ((spec.step_notes[step % STEPS_PER_BAR] - 69) / 12.0)
        note = np.zeros(end - start)
        for wave, gain, detune in spec.oscillators:
            phase = 2.0 * math.pi * (freq + detune) * window
            note += gain * _waveform(wave, phase)
        buffer[start:end] += note * curve

    buffer = buffer[:n_total]
    peak = float(np.abs(buffer).max())
    if peak > 0:
        buffer = buffer * (spec.amplitude * PREVIEW_PEAK / peak)
    pcm = io.BytesIO()
    soundfile.write(pcm, buffer.astype(np.float32), PREVIEW_SAMPLE_RATE,
                    format="WAV", subtype="PCM_16")
    return pcm.getvalue()
