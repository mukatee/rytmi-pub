"""Render the one-line structure→dance framing slide.

Sits between Act 3a's Gemma pre-roll panels and the unified-timeline act.
Names, in plain language, the thing the rest of the demo shows but never
states: a song has parts, and the tool coaches each part — and the moment
between — differently. Grounded: this is exactly what the unified
timeline that follows shows (per-section P# coaching + per-boundary T#
coaching). No claim the pipeline doesn't back.

Silent stereo aac, same input shape as the other acts so
`compose_master_reel.py` stitches it with a plain xfade.

    .venv/bin/python demo_assets/scripts/make_structure_framing_video.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from make_caption_slide import render_caption_slide  # noqa: E402

OUTPUT_DIR = ROOT / "demo_assets" / "output"
SLIDE_PNG = OUTPUT_DIR / "_structure_framing.png"
OUTPUT_PATH = OUTPUT_DIR / "structure_framing.mp4"

WIDTH = 1920
HEIGHT = 1080
FPS = 30
VISIBLE_S = 4.5
TAIL_S = 0.5  # extra tail the master's xfade dissolves into


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg not found on PATH.", file=sys.stderr)
        return 2

    render_caption_slide(
        primary="A song isn't one thing.",
        secondary="Each part — and the moment between — asks you to move differently.",
        footer=None,
        output=SLIDE_PNG,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=96,
        secondary_pt=48,
    )

    total = VISIBLE_S + TAIL_S
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x0f172a,"
        f"setsar=1,fps={FPS},format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", f"{total:.3f}", "-i", str(SLIDE_PNG),
        "-f", "lavfi", "-t", f"{total:.3f}",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-t", f"{total:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUTPUT_PATH),
    ]
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"ffmpeg exited with code {result.returncode}", file=sys.stderr)
        return result.returncode
    print(f"Wrote {OUTPUT_PATH}  ({total:.2f}s incl. {TAIL_S:.1f}s xfade tail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
