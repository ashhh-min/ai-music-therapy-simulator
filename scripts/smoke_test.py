import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ai_music_therapy.deterministic_simulator import simulate  # noqa: E402
from ai_music_therapy.models import MusicParameters, Persona  # noqa: E402

# 1) Five fictional personas validate and are explicitly synthetic.
path = Path("data/public/synthetic_personas.json")
payload = json.loads(path.read_text(encoding="utf-8"))
personas = [Persona.model_validate(item) for item in payload]
assert len(personas) == 5
assert all(p.synthetic for p in personas)

# 2) The deterministic engine produces a valid, reproducible, synthetic reaction
#    without any API key.
music = MusicParameters(
    genre="instrumental", bpm=60, volume="low", instrument="piano",
    tonality="major", duration_sec=180,
)
first, seed1 = simulate(personas[0], music, "sleep_support")
second, seed2 = simulate(personas[0], music, "sleep_support")
assert seed1 == seed2
assert first == second
assert first.synthetic is True
assert len(first.time_series) == 3
assert all(
    1 <= s.anxiety_level <= 10 and 1 <= s.engagement_level <= 10 for s in first.time_series
)

# 3) The preregistered trial matrix is present with exactly 75 design cells.
rows = list(csv.DictReader(Path("config/trial_matrix.csv").open(encoding="utf-8")))
assert len(rows) == 75

print(
    "Smoke test passed: 5 synthetic personas, deterministic engine reproducible, "
    "75-cell matrix present."
)
