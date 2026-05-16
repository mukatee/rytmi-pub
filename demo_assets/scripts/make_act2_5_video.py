"""Render Act 2.5 of the Rytmi demo video — the kizomba framing slide.

Sits in the master between Act 2 (architecture) and Act 3a (the four
Gemma panels for Filomena). One purpose only: name the example song's
style explicitly for any viewer who doesn't know what kizomba is, so
the next ~90 s of Filomena content has a genre frame.

History: an earlier 12.5 s version of this act also contained an
"audible misfire" beat (clicks overlay over the Filomena hook to
demonstrate generic-tracker failure). That beat was retired in
clarity-pass-5 because it needed kizomba ear-training to read and ate
~13 s. The kizomba-framing scene was then dropped too, but the result
was a context cliff: the master jumped from architecture diagram
straight into Gemma's `rhythm_anatomy` panel for an unnamed song. This
single-slide version restores the framing without the audible misfire.

Single scene (~5 s, silent): *"Example case: kizomba."* /
*"An Afro-Latin partner-dance style where the pulse a dancer steps
on hides behind a syncopated kick."*

Output: ``demo_assets/output/act2_5_kizomba_intro.mp4``  (1920×1080 /
30 fps / h264 + silent aac). The silent stereo track is required so
the master stitch's acrossfade has something to chain against, same
pattern as `make_act1_video.py`.

Re-runnable: re-renders the caption PNG each call.

Usage from repo root::

    .venv/bin/python demo_assets/scripts/make_act2_5_video.py
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

OUTPUT_PATH = OUTPUT_DIR / "act2_5_kizomba_intro.mp4"
CAPTION_PNG = OUTPUT_DIR / "_act2_5_caption1.png"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

VISIBLE_S = 5.0  # total act duration; single scene so no internal xfade


def _render_caption_png() -> None:
    render_caption_slide(
        primary="Example case: kizomba.",
        secondary=(
            "An Afro-Latin partner-dance style where the pulse a dancer "
            "steps on hides behind a syncopated kick."
        ),
        footer=None,
        output=CAPTION_PNG,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=92,
        secondary_pt=46,
    )


def _ffmpeg_cmd() -> list[str]:
    if not CAPTION_PNG.exists():
        raise FileNotFoundError(CAPTION_PNG)

    cmd: list[str] = ["ffmpeg", "-y"]
    cmd.extend(["-loop", "1", "-t", f"{VISIBLE_S:.3f}", "-i", str(CAPTION_PNG)])
    cmd.extend([
        "-f", "lavfi", "-t", f"{VISIBLE_S:.3f}",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
    ])

    video_filter = (
        f"[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x0f172a,"
        f"setsar=1,fps={FPS},format=yuv420p[v]"
    )
    audio_filter = (
        f"[1:a]aresample=44100,aformat=channel_layouts=stereo,"
        f"atrim=0:{VISIBLE_S:.3f},asetpts=PTS-STARTPTS[a]"
    )
    filter_complex = f"{video_filter};{audio_filter}"

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-t", f"{VISIBLE_S:.3f}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUTPUT_PATH),
    ])
    return cmd


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg not found on PATH.", file=sys.stderr)
        return 2

    print("Rendering caption PNG …")
    _render_caption_png()

    print(f"Single scene, visible {VISIBLE_S:.2f} s ({CAPTION_PNG.name})")

    cmd = _ffmpeg_cmd()
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"ffmpeg exited with code {result.returncode}", file=sys.stderr)
        return result.returncode

    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
