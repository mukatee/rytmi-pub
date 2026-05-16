"""Harvest verbatim Gemma transition lines for the Phase-2 demo songs.

For each (song, dance_style) below we:
  1. Load + analyze the song (using the disk cache from `analysis_cache`),
  2. Extract the algorithmic transitions list,
  3. Ask the cloud Gemma endpoint (`RYTMI_API_BASE_URL` / `RYTMI_API_KEY`)
     for the matching `*_transitions` answer with the structural verifier on,
  4. Print the cleaned T# lines + a list of boundary candidates so the
     human can pick the most demoable [start, duration] window per song.

Run with the .venv interpreter so `rytmi` is importable. Requires the
cloud env vars to be exported in the launching shell.

    .venv/bin/python demo_assets/scripts/harvest_transitions.py
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from rytmi.dsp import extract_transitions  # noqa: E402
from rytmi.llm import explain_all, load_cloud_model  # noqa: E402

import make_timeline_video  # for prepare_analysis (reuses the analysis cache)  # noqa: E402

SONGS = [
    {
        "label": "romeo_propuesta",
        "path": ROOT / "data/songs/eval_set/bachata/Romeo_Santos_-_Propuesta_Indecente_Official_Video [QFs3PIZb3js].mp3",
        "style": "bachata",
        "transitions_key": "bachata_transitions",
    },
    {
        "label": "royce_corazon",
        "path": ROOT / "data/songs/eval_set/bachata/Prince_Royce_-_Corazon_Sin_Cara_Official_Video [XNGWDH-6yv8].mp3",
        "style": "bachata",
        "transitions_key": "bachata_transitions",
    },
    {
        "label": "mika_magico",
        "path": ROOT / "data/songs/eval_set/kizomba/MIKA_MENDES_-_MAGICO_2011 [ZM1GnUImrPw].mp3",
        "style": "kizomba",
        "transitions_key": "kizomba_transitions",
    },
]


def main() -> int:
    base_url = os.environ.get("RYTMI_API_BASE_URL")
    api_key = os.environ.get("RYTMI_API_KEY")
    model_id = os.environ.get("RYTMI_MODEL_ID", "google/gemma-4-26b-a4b-it")
    if not base_url or not api_key:
        print("ERROR: RYTMI_API_BASE_URL and RYTMI_API_KEY must be set in the environment.", file=sys.stderr)
        return 1

    print(f"Cloud endpoint: {base_url}  model={model_id}\n")
    client, model = load_cloud_model(model_id=model_id, base_url=base_url, api_key=api_key)

    out_dir = ROOT / "tmp"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "phase2_transitions.md"
    body_lines: list[str] = [f"# Phase 2 transitions harvest — model={model_id}\n"]

    for song in SONGS:
        path = song["path"]
        if not path.exists():
            print(f"  MISSING: {path}", file=sys.stderr)
            continue

        print(f"=== {song['label']}  ({song['style']}) ===")
        audio, analysis = make_timeline_video.prepare_analysis(path, dance_style=song["style"])
        transitions = extract_transitions(analysis.phases or [])
        print(f"  duration={audio.duration:.1f}s  phases={len(analysis.phases or [])}  transitions={len(transitions)}")
        for t in transitions:
            print(f"    T@ {t.boundary_time_s:6.1f}s  {t.from_label}→{t.to_label}  beat: {t.from_clarity}→{t.to_clarity}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results = explain_all(
                analysis,
                processor=client,
                model=model,
                max_new_tokens=1024,
                temperature=0.7,
                do_sample=True,
            )

        cleaned = results.get(song["transitions_key"], "")
        raw = results.get(f"{song['transitions_key']}_raw", "")
        stats = results.get(f"{song['transitions_key']}_verified_stats", "")

        body_lines.append(f"## {song['label']}  ({song['style']}, {audio.duration:.1f}s)\n")
        body_lines.append("### transitions list\n```")
        for t in transitions:
            body_lines.append(
                f"T@ {t.boundary_time_s:6.1f}s  {t.from_label}→{t.to_label}  "
                f"beat: {t.from_clarity}→{t.to_clarity}"
            )
        body_lines.append("```\n")
        body_lines.append("### Gemma transitions (verified)\n```")
        body_lines.append(cleaned.rstrip())
        body_lines.append("```\n")
        body_lines.append(f"### verifier stats\n`{stats}`\n")
        body_lines.append("### raw Gemma draft\n```")
        body_lines.append(raw.rstrip())
        body_lines.append("```\n")
        print()
        print(cleaned)
        print(f"  stats: {stats}\n")

    out_path.write_text("\n".join(body_lines), encoding="utf-8")
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
