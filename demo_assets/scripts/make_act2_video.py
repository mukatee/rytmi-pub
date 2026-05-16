"""Render Act 2 of the Rytmi demo video — the 30s architecture beat.

Implements `Act 2 — Architecture insight (0:30–1:00)` from
`docs/demo_storyboard.md`.

Sequence (with 0.5s crossfades between scenes):

- 0:00–0:07  caption 1: *"Rytmi splits the problem in two.
             DSP listens. Gemma talks."*
- 0:07–0:15  architecture diagram (full screen, no overlaid text — the
             diagram speaks for itself; it has its own title bar).
- 0:15–0:23  caption 2: *"librosa detects beats, sections, beat-clarity,
             downbeat confidence. Gemma turns that into language a
             learner can use."*
- 0:23–0:30  caption 3: *"Tried Gemma-as-listener first. It missed
             obvious percussion. DSP earns its keep."*

Output: `demo_assets/output/act2_architecture.mp4` (1920×1080 / 30 fps /
h264 + silent aac so the act stitches cleanly onto Acts 1 and 3 which
do carry audio).

Re-runnable: deletes prior caption PNGs in the output dir before
rendering. Architecture diagram is rendered separately by
`make_architecture_diagram.py` (called automatically here if missing,
otherwise reused).

Usage from repo root::

    .venv/bin/python demo_assets/scripts/make_act2_video.py
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
from make_architecture_diagram import render as render_architecture  # noqa: E402

OUTPUT_DIR = ROOT / "demo_assets" / "output"

ARCHITECTURE_PNG = OUTPUT_DIR / "architecture.png"
OUTPUT_PATH = OUTPUT_DIR / "act2_architecture.mp4"

CAPTION_PNG_1 = OUTPUT_DIR / "_act2_caption1.png"
CAPTION_PNG_2 = OUTPUT_DIR / "_act2_caption2.png"
CAPTION_PNG_3 = OUTPUT_DIR / "_act2_caption3.png"

XFADE_S = 0.5
WIDTH = 1920
HEIGHT = 1080
FPS = 30


@dataclass(frozen=True)
class Scene:
    png: Path
    visible_s: float
    label: str


# Visible-second budget after clarity pass #5 trim (was 7/8/8/5.5 = 30.0 s):
#   total = 5.5 + (0.5 + 8) + (0.5 + 6.5) + (0.5 + 4.5) = 26.0 s
# Architecture diagram (scene 2) keeps its full 8.0 s of read time —
# every other beat is shorter caption text that reads cleanly faster.
SCENES: list[Scene] = [
    Scene(CAPTION_PNG_1, visible_s=5.5, label="caption1 (split in two)"),
    Scene(ARCHITECTURE_PNG, visible_s=8.0, label="architecture diagram"),
    Scene(CAPTION_PNG_2, visible_s=6.5, label="caption2 (what each side does)"),
    Scene(CAPTION_PNG_3, visible_s=4.5, label="caption3 (negative result → architecture)"),
]


def _render_caption_pngs() -> None:
    """Render Act 2's three caption slides. Idempotent."""
    render_caption_slide(
        primary="Rytmi splits the problem in two.",
        secondary="DSP listens. Gemma talks.",
        footer=None,
        output=CAPTION_PNG_1,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=98,
        secondary_pt=72,
    )
    render_caption_slide(
        primary="DSP finds beats, sections, beat-clarity, downbeat confidence.",
        secondary="Gemma 4 turns that into language a learner can use.",
        footer=None,
        output=CAPTION_PNG_2,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=64,
        secondary_pt=56,
    )
    render_caption_slide(
        primary="Tried Gemma-as-listener first.",
        secondary="It missed obvious percussion. DSP earns its keep.",
        footer=None,
        output=CAPTION_PNG_3,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=80,
        secondary_pt=58,
    )


def _build_filter_graph(scenes: list[Scene], xfade_s: float) -> tuple[str, float]:
    """Build the xfade chain — same pattern as `make_act1_video`."""
    n = len(scenes)
    if n == 0:
        raise ValueError("no scenes")

    parts: list[str] = []
    for i, _ in enumerate(scenes):
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

    # Generate `total_s` of silent stereo audio so the act has an audio
    # track (needed for clean concat with Acts 1 & 3 in the master reel).
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

    if not ARCHITECTURE_PNG.exists():
        print(f"Architecture diagram missing — rendering {ARCHITECTURE_PNG.name} …")
        render_architecture(ARCHITECTURE_PNG)

    print("Rendering caption PNGs …")
    _render_caption_pngs()

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
