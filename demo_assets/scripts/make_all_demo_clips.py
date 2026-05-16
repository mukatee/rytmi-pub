"""One-shot generator for the Act 1 demo assets.

Renders into ``demo_assets/output/``:
    - ``act1_filomena_hook.wav``         — 10s clean cut starting at 32s
    - ``act1_filomena_hook_clicks.wav``  — same clip with librosa beat clicks
    - ``act1_title_slide.png``           — 1920×1080 project title card
    - ``act1_close_slide.png``           — 1920×1080 closing card

Run from repo root:
    .venv/bin/python demo_assets/scripts/make_all_demo_clips.py

If the Filomena source file is missing, the script exits non-zero and tells
you what it looked for so you can either drop the file in place or re-run
``./download_youtube.sh``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from cut_excerpt import cut  # noqa: E402
from make_click_overlay import make_overlay  # noqa: E402
from make_slide import render_slide  # noqa: E402


SONG = ROOT / "data/songs/eval_set/kizomba/Filomena_Maricoa_-_Teu_Toque_Official_Video [sKbWzD0mt6I].mp3"
OUT = ROOT / "demo_assets" / "output"
HOOK_START = 32.0
HOOK_DUR = 10.0


def main() -> int:
    if not SONG.exists():
        print(f"ERROR: source song not found: {SONG}", file=sys.stderr)
        print(
            "Drop the Filomena mp3 in place or run ./download_youtube.sh first.",
            file=sys.stderr,
        )
        return 1

    OUT.mkdir(parents=True, exist_ok=True)

    cut(
        SONG, HOOK_START, HOOK_DUR,
        OUT / "act1_filomena_hook.wav",
        fade_in=0.05, fade_out=0.4,
    )
    make_overlay(
        SONG, OUT / "act1_filomena_hook_clicks.wav",
        start=HOOK_START, duration=HOOK_DUR,
        click_volume=0.35,
    )
    render_slide(
        title="Rytmi",
        subtitle="Rhythm coaching for dancers — Gemma 4 explains the music, code finds the beat",
        footer="Kaggle Gemma 4 Good Hackathon",
        output=OUT / "act1_title_slide.png",
    )
    render_slide(
        title="Thank you",
        subtitle="github.com/your-handle/kaggle-gemma4-rytmi",
        footer="Built with librosa, Demucs, and Gemma 4",
        output=OUT / "act1_close_slide.png",
    )
    print("\nAll Act 1 assets rendered into demo_assets/output/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
