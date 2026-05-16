"""Concatenate per-act MP4s into the final 3-minute Rytmi demo master.

Reads the six act files produced by:

- ``make_act1_video.py``                 → ``act1_hook.mp4``
- ``make_act2_video.py``                 → ``act2_architecture.mp4``
- ``make_act3a_preroll_video.py``        → ``act3a_preroll.mp4``
- ``make_act3a_unified_timeline_video.py``→ ``act3a_unified_timeline.mp4``
- ``compose_final_video.py``             → ``rytmi_demo_reel.mp4``
- ``make_close_video.py``                → ``close.mp4``

…and stitches them with 0.5 s xfade (video) + acrossfade (audio)
between acts into ``demo_assets/output/rytmi_demo_master.mp4``.

Why xfade instead of plain concat: a hard cut at the architecture
diagram → pre-roll panel boundary feels jarring; the soft fade reads
as a section break. The 0.5 s overlap loses ~2.5 s from the naive
sum, landing the master near 3:05 (matches the storyboard's
3-minute target within tolerance).

Each act remains independently re-rendered; this script just glues.
The ``ACTS`` list at the top is the swap point — change the order or
swap one MP4 for an alternate cut without touching the filter graph.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "demo_assets" / "output"
OUTPUT_PATH = OUTPUT_DIR / "rytmi_demo_master.mp4"

XFADE_S = 0.5
WIDTH = 1920
HEIGHT = 1080
FPS = 30

# Global watermark drawn over every frame of the master. Slate-400 at 60 %
# opacity so it reads as Rytmi/Gemma chrome without competing with the act
# content. A judge sampling any second of the reel sees the project + comp
# attribution; this is the cheapest way to make Gemma 4 framing universal.
WATERMARK_TEXT = "Rytmi  \u00b7  Gemma 4 Hackathon"
WATERMARK_FONTFILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WATERMARK_FONTSIZE = 20
WATERMARK_COLOR = "0x94a3b8@0.6"  # slate-400, 60 % opaque
WATERMARK_MARGIN = 28  # px from bottom-right corner


@dataclass(frozen=True)
class Act:
    path: Path
    label: str


ACTS: list[Act] = [
    Act(OUTPUT_DIR / "act1_hook.mp4", "Act 1 · hook"),
    Act(OUTPUT_DIR / "act2_architecture.mp4", "Act 2 · architecture"),
    # Act 2.5 (kizomba example case + audible misfire) retired in
    # clarity pass #5 to bring the master under the Kaggle 3:00 cap and
    # to reach the Gemma-coaching beef faster. The kizomba framing now
    # lands via Gemma's own rhythm_anatomy panel in Act 3a (stronger
    # attribution anyway); the audible misfire was a DSP-side beat that
    # needed kizomba ear-training to read and didn't earn its ~13 s.
    Act(OUTPUT_DIR / "act3a_preroll.mp4", "Act 3a · pre-roll panels"),
    Act(OUTPUT_DIR / "act3a_unified_timeline.mp4", "Act 3a · unified timeline"),
    Act(OUTPUT_DIR / "rytmi_demo_reel.mp4", "Act 3 · audio reel (Option Z)"),
    Act(OUTPUT_DIR / "close.mp4", "Close"),
]


def _probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nokey=1:noprint_wrappers=1",
        str(path),
    ])
    return float(out.decode().strip())


def _build_filter_graph(durations: list[float], xfade_s: float) -> tuple[str, float]:
    n = len(durations)
    if n == 0:
        raise ValueError("no acts")

    parts: list[str] = []
    # Normalize each input to a known size / sar / fps so xfade is happy.
    for i in range(n):
        parts.append(
            f"[{i}:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x0f172a,"
            f"setsar=1,fps={FPS},format=yuv420p[v{i}]"
        )
        parts.append(f"[{i}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{i}]")

    if n == 1:
        parts.append("[v0]null[vraw]")
        parts.append("[a0]anull[aout]")
    else:
        last_v = "v0"
        last_a = "a0"
        running_offset = durations[0] - xfade_s  # xfade `offset` is when the transition starts
        total = durations[0]
        for i in range(1, n):
            next_v = f"vx{i}"
            next_a = f"ax{i}"
            parts.append(
                f"[{last_v}][v{i}]xfade=transition=fade"
                f":duration={xfade_s}:offset={running_offset:.3f}[{next_v}]"
            )
            parts.append(
                f"[{last_a}][a{i}]acrossfade=d={xfade_s}:c1=tri:c2=tri[{next_a}]"
            )
            last_v = next_v
            last_a = next_a
            total = total + durations[i] - xfade_s
            running_offset = total - xfade_s

        parts.append(f"[{last_v}]null[vraw]")
        parts.append(f"[{last_a}]anull[aout]")

    # Global Rytmi · Gemma 4 watermark over every frame, anchored to the
    # bottom-right at low opacity so it never competes with act content.
    parts.append(
        f"[vraw]drawtext=fontfile={WATERMARK_FONTFILE}"
        f":text='{WATERMARK_TEXT}':fontsize={WATERMARK_FONTSIZE}"
        f":fontcolor={WATERMARK_COLOR}"
        f":x=w-tw-{WATERMARK_MARGIN}:y=h-th-{WATERMARK_MARGIN}[vout]"
    )
    return ";".join(parts), (durations[0] if n == 1 else total)


def _ffmpeg_cmd(acts: list[Act], total_s: float, video_filter: str) -> list[str]:
    cmd: list[str] = ["ffmpeg", "-y"]
    for act in acts:
        cmd.extend(["-i", str(act.path)])

    cmd.extend([
        "-filter_complex", video_filter,
        "-map", "[vout]",
        "-map", "[aout]",
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
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("ERROR: ffmpeg/ffprobe not found on PATH.", file=sys.stderr)
        return 2

    durations: list[float] = []
    print("Acts:")
    for act in ACTS:
        if not act.path.exists():
            print(f"ERROR: missing {act.path}", file=sys.stderr)
            return 2
        d = _probe_duration(act.path)
        durations.append(d)
        print(f"  {act.label:42s}  {d:6.2f} s  ({act.path.name})")

    video_filter, total = _build_filter_graph(durations, XFADE_S)
    naive_sum = sum(durations)
    print(f"\nNaive sum   : {naive_sum:6.2f} s ({naive_sum/60:.2f} min)")
    print(f"With xfades : {total:6.2f} s ({total/60:.2f} min)  "
          f"[lost {naive_sum - total:.2f} s to {len(ACTS) - 1} × {XFADE_S}s xfades]")

    cmd = _ffmpeg_cmd(ACTS, total, video_filter)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"ffmpeg exited with code {result.returncode}", file=sys.stderr)
        return result.returncode

    print(f"\nWrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
