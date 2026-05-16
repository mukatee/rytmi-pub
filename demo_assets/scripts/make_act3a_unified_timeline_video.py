"""Render the unified-timeline beat for Act 3a (1:50–2:10).

Implements the storyboard's *architectural-signature beat*:

    code identifies the boundaries → Gemma writes the lines → code
    verifies they cover the song.

Three stages (with 0.5s crossfades between):

- **Stage A** (5.0 s): P# lines only. T# rows reserve vertical space
  but are blank, so the layout doesn't shift when they appear.
- **Stage B** (10.0 s): full unified block with T# lines slotted in
  (violet) between the P# lines (slate-50).
- **Stage C** (5.0 s): same block + pinned violet banner caption
  *"Code identifies the boundaries. Gemma writes the lines. Code
  verifies they cover the song."*

Total: 20.0 s — matches storyboard 1:50–2:10 exactly.

Output: `demo_assets/output/act3a_unified_timeline.mp4` (1920×1080,
30 fps, h264 + silent aac for clean concat with adjacent acts).

Each PNG is rendered to `demo_assets/output/_act3a_unified_*.png` and
is independently re-renderable. The verbatim Gemma lines live in
``LINES`` at the top of this module — that's the swap point for
substituting another song or re-running.

Usage from repo root::

    .venv/bin/python demo_assets/scripts/make_act3a_unified_timeline_video.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from make_unified_timeline_panel import (  # noqa: E402
    TimelineLine,
    render_unified_timeline_panel,
)

OUTPUT_DIR = ROOT / "demo_assets" / "output"
OUTPUT_PATH = OUTPUT_DIR / "act3a_unified_timeline.mp4"

PANEL_A = OUTPUT_DIR / "_act3a_unified_a_phases_only.png"
PANEL_B = OUTPUT_DIR / "_act3a_unified_b_full.png"
PANEL_C = OUTPUT_DIR / "_act3a_unified_c_pinned.png"

XFADE_S = 0.5
WIDTH = 1920
HEIGHT = 1080
FPS = 30


# Verbatim from notebooks/00_demo_outputs.md (Filomena Maricoa — Teu Toque).
# Order is the canonical interleave: P1, T1, P2, T2, … P8.
LINES: list[TimelineLine] = [
    TimelineLine("P", "P1: 0s-12s, intro [beat: clear] — Feel the bass through your connection; stay in a close embrace and find the pulse in your feet."),
    TimelineLine("T", "T1: 12s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear pulse."),
    TimelineLine("P", "P2: 12s-59s, main ×4 [beat: clear] — Establish your rhythm; use a smooth, grounded walk to settle into the steady pulse."),
    TimelineLine("T", "T2: 59s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention to your movement."),
    TimelineLine("P", "P3: 59s-80s, main ×2 [beat: clear] — Maintain your flow; keep your steps even and let the bass guide your weight transfers."),
    TimelineLine("T", "T3: 80s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame to reconnect."),
    TimelineLine("P", "P4: 80s-121s, main ×4 [beat: clear] — Build momentum; the pulse is very stable, so you can begin to increase your travel."),
    TimelineLine("T", "T4: 121s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention."),
    TimelineLine("P", "P5: 121s-148s, main ×2 [beat: clear] — Hold the energy; keep your frame firm and match your steps to the driving bass."),
    TimelineLine("T", "T5: 148s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset."),
    TimelineLine("P", "P6: 148s-159s, break [beat: clear] — Reset your position; reduce your travel and keep a small pulse in the body to prepare for the return."),
    TimelineLine("T", "T6: 159s [break → main, beat: clear → clear] — walk-step on the first clear bass hit; don't chase the percussion that comes back loudest."),
    TimelineLine("P", "P7: 159s-195s, main ×3 [beat: clear] — Re-enter the groove; re-establish your walk-step and reconnect with the steady rhythm."),
    TimelineLine("T", "T7: 195s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close."),
    TimelineLine("P", "P8: 195s-209s, outro [beat: clear] — Close the dance; contract your movements and let the session end with gentle, small steps."),
]

PINNED_CAPTION_C = (
    "Code identifies the boundaries. Gemma writes the lines. "
    "Code verifies they cover the song."
)

# Per-stage panel headings (clarity pass #4). Pass #3 added pinned
# violet banners at the bottom of stages A/B to attribute the P# and
# T# lines to Gemma, but a watch review showed attention lands on the
# heading and table first, missing the bottom strip. The attribution
# now lives in the heading itself for stages A and B; stage C reverts
# to the neutral heading so its bottom architectural-signature banner
# (PINNED_CAPTION_C) reads as a distinct closing thought.
HEADING_A = "Gemma 4 names each phase"
HEADING_B = "Gemma 4 coaches the transitions"
HEADING_C = "Unified timeline — phases + transitions"


@dataclass(frozen=True)
class Scene:
    png: Path
    visible_s: float
    label: str


SCENES: list[Scene] = [
    Scene(PANEL_A, visible_s=5.0, label="A · phases only + heading attribution"),
    Scene(PANEL_B, visible_s=10.0, label="B · full block + transitions heading"),
    Scene(PANEL_C, visible_s=5.0, label="C · architectural-signature banner"),
]


def _render_panel_pngs() -> None:
    """Render the 3 stage PNGs. Idempotent."""
    render_unified_timeline_panel(
        LINES,
        output=PANEL_A,
        hide_transitions=True,
        heading=HEADING_A,
        pinned_caption=None,
    )
    render_unified_timeline_panel(
        LINES,
        output=PANEL_B,
        hide_transitions=False,
        heading=HEADING_B,
        pinned_caption=None,
    )
    render_unified_timeline_panel(
        LINES,
        output=PANEL_C,
        hide_transitions=False,
        heading=HEADING_C,
        pinned_caption=PINNED_CAPTION_C,
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

    print("Rendering unified-timeline panels …")
    _render_panel_pngs()

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
