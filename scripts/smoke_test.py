from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ai_music_therapy.models import Persona

path = Path("data/public/synthetic_personas.json")
payload = json.loads(path.read_text(encoding="utf-8"))
items = [Persona.model_validate(item) for item in payload]
assert len(items) == 5
assert all(item.synthetic for item in items)
print("Smoke test passed: five validated synthetic personas.")
