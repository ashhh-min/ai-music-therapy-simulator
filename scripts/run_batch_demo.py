from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from uuid import uuid4

from ai_music_therapy.analytics import composite_score
from ai_music_therapy.deterministic_simulator import simulate
from ai_music_therapy.models import MusicParameters, Persona, TrialRecord


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/local/batch_demo.csv")
    args = parser.parse_args()

    personas = [
        Persona.model_validate(item)
        for item in json.loads(
            Path("data/public/synthetic_personas.json").read_text(encoding="utf-8")
        )
    ]
    scenes = [
        "sleep_support",
        "anxiety_support",
        "focus_support",
        "engagement_support",
        "regulation_support",
    ]
    variants = [
        MusicParameters(
            genre="instrumental", bpm=54, volume="low", instrument="piano",
            tonality="major", duration_sec=180,
        ),
        MusicParameters(
            genre="instrumental", bpm=82, volume="medium", instrument="percussion",
            tonality="major", duration_sec=180,
        ),
        MusicParameters(
            genre="nature", bpm=64, volume="low", instrument="mixed",
            tonality="atonal", duration_sec=180,
        ),
    ]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for persona, scene, music in ((p, s, m) for p in personas for s in scenes for m in variants):
        reaction, seed = simulate(persona, music, scene)
        trial = TrialRecord(
            trial_id=f"B-{uuid4().hex[:10].upper()}",
            persona_id=persona.persona_id,
            scene=scene,
            music=music,
            reaction=reaction,
            engine="deterministic",
            prompt_version="batch-demo.v1",
            seed=seed,
        )
        rows.append({
            "trial_id": trial.trial_id,
            "persona_id": trial.persona_id,
            "scene": trial.scene,
            "variant": music.model_dump_json(),
            "anxiety_level": reaction.anxiety_level,
            "engagement_level": reaction.engagement_level,
            "mood_score": reaction.mood_score,
            "regulation_score": reaction.regulation_score,
            "attention_duration_sec": reaction.attention_duration_sec,
            "composite_score": composite_score(trial),
            "synthetic": True,
        })

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} clearly synthetic deterministic rows to {output}")


if __name__ == "__main__":
    main()
