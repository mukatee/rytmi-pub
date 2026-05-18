"""Render the opening cover clip for the Rytmi demo master.

A short hold on the poster cover (the 16:9 video cover — couple + halo +
glowing E Magia waveform + verbatim Gemma line + the video title) with a
gentle fade-in from black. This replaces the old cold-open on Act 1's
personal-hook caption: the viewer now meets the project with its most
striking single frame before any text slides, then the master's 0.5 s
xfade dissolves it into Act 1.

Silent stereo aac so it stitches cleanly onto the audio-bearing acts in
`compose_master_reel.py` (same input shape as the pre-roll act).

    .venv/bin/python demo_assets/scripts/make_cover_intro.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "demo_assets" / "output"
OUTPUT_PATH = OUTPUT_DIR / "cover_intro.mp4"
COVER_PNG = ROOT / "demo_assets" / "cover_candidates" / "cover_video_help_me_hear.png"

WIDTH = 1920
HEIGHT = 1080
FPS = 30
VISIBLE_S = 4.0      # on-screen hold
FADE_IN_S = 0.7      # fade up from black at the very start
TAIL_S = 0.5         # extra tail the master's xfade dissolves into


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg not found on PATH.", file=sys.stderr)
        return 2
    if not COVER_PNG.exists():
        print(f"ERROR: missing {COVER_PNG}", file=sys.stderr)
        return 2

    total = VISIBLE_S + TAIL_S
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x07060a,"
        f"setsar=1,fps={FPS},format=yuv420p,"
        f"fade=t=in:st=0:d={FADE_IN_S}"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", f"{total:.3f}", "-i", str(COVER_PNG),
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
