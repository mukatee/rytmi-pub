"""Render the Close (final beat) of the Rytmi demo video.

Implements `Close (2:40–3:00)` from `docs/demo_storyboard.md`.

Three captions over a slate background, ending on the project's closing
line:

- Scene 1 (5.5 s): *"What ships now: section labels, beat-clarity tags,
  phase coaching, transitions, drills — verified end-to-end."*
- Scene 2 (5.5 s): *"What's next: less templated coaching — phases and
  transitions that reference each other, drills tied to what makes a
  section distinct."*
- Scene 3 (5.0 s): *"DSP listens. Gemma talks."* with the project name
  ``Rytmi`` underneath as a small footer.

Total: 16.0 s with two 0.5 s xfades. The master stitcher can shave
1–2 s by adjusting the boundary xfade with the preceding audio reel.

Output: `demo_assets/output/close.mp4` (1920×1080, 30 fps, h264 +
silent stereo aac for clean concat).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from make_caption_slide import render_caption_slide  # noqa: E402

OUTPUT_DIR = ROOT / "demo_assets" / "output"
OUTPUT_PATH = OUTPUT_DIR / "close.mp4"

SLIDE_1 = OUTPUT_DIR / "_close_what_ships.png"
SLIDE_2 = OUTPUT_DIR / "_close_what_next.png"
SLIDE_3 = OUTPUT_DIR / "_close_signature.png"

XFADE_S = 0.5
WIDTH = 1920
HEIGHT = 1080
FPS = 30


@dataclass(frozen=True)
class Scene:
    png: Path
    visible_s: float
    label: str


SCENES: list[Scene] = [
    Scene(SLIDE_1, visible_s=5.5, label="what ships now"),
    Scene(SLIDE_2, visible_s=9.5, label="what's next (4 grounded bullets)"),
    Scene(SLIDE_3, visible_s=5.0, label="closing signature line"),
]


def _render_slides() -> None:
    render_caption_slide(
        primary="What ships now",
        secondary=(
            "Section labels · beat-clarity tags · phase coaching · "
            "transitions · drills — verified end-to-end."
        ),
        footer=None,
        output=SLIDE_1,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=96,
        secondary_pt=46,
    )
    # Clarity pass #4: replace the single generic "less templated
    # coaching" sentence with 4 concrete future-work bullets balanced
    # across DSP-side (input quality) and Gemma-side (output
    # personalisation) so the slide sits naturally above the
    # "DSP listens. Gemma talks." signature. Each bullet is grounded
    # in a real limitation called out in the experiment notes.
    render_caption_slide(
        primary="What's next",
        secondary=(
            "·  Sharper beat & downbeat grid — meter votes + surfaced "
            "confidence\n"
            "·  Real-music tap-based eval, replacing synthetic-click "
            "calibration\n"
            "·  Per-boundary cues for Gemma 4 — less templated "
            "transition coaching\n"
            "·  Gemma 4 learner levels — beginner vs improver drills, "
            "local-first E4B"
        ),
        footer=None,
        output=SLIDE_2,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=88,
        secondary_pt=36,
        secondary_align="left",
    )
    render_caption_slide(
        primary="DSP listens. Gemma talks.",
        secondary=None,
        footer="Rytmi  ·  github.com — Gemma 4 Good Hackathon",
        output=SLIDE_3,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=120,
        secondary_pt=46,
        footer_pt=28,
    )


def _build_filter_graph(scenes: list[Scene], xfade_s: float) -> tuple[str, float]:
    n = len(scenes)
    if n == 0:
        raise ValueError("no scenes")

    parts: list[str] = []
    for i in range(n):
        parts.append(
            f"[{i}:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x0f172a,"
            f"setsar=1,fps={FPS},format=yuv420p[s{i}]"
        )

    if n == 1:
        parts.append("[s0]null[v]")
        return ";".join(parts), scenes[0].visible_s

    last_label = "s0"
    running_offset = scenes[0].visible_s
    for i in range(1, n):
        next_label = f"v{i}"
        parts.append(
            f"[{last_label}][s{i}]xfade=transition=fade"
            f":duration={xfade_s}:offset={running_offset:.3f}[{next_label}]"
        )
        last_label = next_label
        running_offset += xfade_s + scenes[i].visible_s

    parts.append(f"[{last_label}]null[v]")
    return ";".join(parts), running_offset


def _ffmpeg_cmd(scenes: list[Scene], total_s: float) -> list[str]:
    cmd: list[str] = ["ffmpeg", "-y"]
    n = len(scenes)
    for i, scene in enumerate(scenes):
        if not scene.png.exists():
            raise FileNotFoundError(scene.png)
        pad = XFADE_S if i < n - 1 else 0.0
        input_dur = scene.visible_s + pad + 0.5
        cmd.extend(["-loop", "1", "-t", f"{input_dur:.3f}", "-i", str(scene.png)])

    cmd.extend([
        "-f", "lavfi",
        "-t", f"{total_s:.3f}",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
    ])

    video_filter, _ = _build_filter_graph(scenes, XFADE_S)

    cmd.extend([
        "-filter_complex", video_filter,
        "-map", "[v]",
        "-map", f"{n}:a",
        "-t", f"{total_s:.3f}",
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

    print("Rendering Close slides …")
    _render_slides()

    _, total_s = _build_filter_graph(SCENES, XFADE_S)
    print(f"Scenes ({len(SCENES)}), total video = {total_s:.2f} s:")
    for s in SCENES:
        print(f"  {s.label}  visible {s.visible_s:.2f} s  ({s.png.name})")

    cmd = _ffmpeg_cmd(SCENES, total_s)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"ffmpeg exited with code {result.returncode}", file=sys.stderr)
        return result.returncode

    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
