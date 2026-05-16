"""Stitch the Phase-44 captioned clips into a single submission-ready reel.

Implements **Act 3 shape Z** from `docs/demo_storyboard.md`:
  - 3a Filomena Maricoa — *Teu Toque* (kizomba deep-dive, intro → main)
  - 3b Charbel — *E Magia* (kizomba contrast, vocal break)
  - 3c Prince Royce — *Corazón Sin Cara* (cross-style proof, main → outro)

Output: ``demo_assets/output/rytmi_demo_reel.mp4`` — ~41 s with 0.5 s
crossfades between clips and per-clip ``loudnorm`` so Filomena, E Magia
and Royce don't have wildly different audio levels.

This is the **minimum viable reel**: just the Act 3 evidence beat,
back-to-back, audio-normalised, crossfaded. No title cards, no Act 1 /
Act 2 framing — those belong in a longer stitch driven by the storyboard
spine, not in this script. The captioned clips already carry their own
on-screen text (verbatim Gemma transition lines), so the stitch is
self-explanatory at submission time.

Usage from repo root::

    .venv/bin/python demo_assets/scripts/compose_final_video.py

Re-run is cheap — ffmpeg processes ~41 s of 1760x790 h264 in seconds.

Decisions encoded here that may want revisiting:

- **Crossfade transition ``fade``** (the default) is the most neutral
  choice. ``fadeblack`` would punctuate the style change at clip 3
  (kizomba → bachata) more dramatically; consider it if the cross-style
  beat needs more weight in the cut.
- **``loudnorm`` is single-pass**, applied per clip independently. A
  two-pass measure-then-apply would give tighter level matching but the
  clips here are short enough that one-pass is fine. Revisit if level
  mismatch is audible after the first render.
- **No title / outro cards.** The captions baked into each clip carry
  the meaning. Add cards if a longer cut (with Act 1 hook + Act 2
  architecture beats) is being assembled.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "demo_assets" / "output"


@dataclass(frozen=True)
class Clip:
    """One source clip in the stitched reel.

    ``banner_text`` feeds the top context strip drawn by
    ``_build_filter_graph``. The banner is the narrative through-line of
    the reel: rather than just labelling each clip with its genre/tempo,
    each banner explicitly frames *what this clip is showing* relative
    to the previous one ("same style, softer song", "different style,
    same pattern"), so a viewer dropping in mid-reel sees the
    *comparison* the act is making, not just three isolated examples.

    Banners are rendered as-is (no upper-casing) so the prose reads
    naturally; emphasis comes from the slate-800 strip and the bold
    DejaVu face, not from shouty caps.
    """

    stem: str  # filename stem under demo_assets/output/, captioned variant
    duration_s: float
    banner_text: str = ""  # descriptive context strip; empty disables banner


# Each entry is one of the captioned 14 s timeline videos rendered by
# `make_all_demo_videos.py`. Order is the Act-3 narrative order.
#
# Banner wording locked in clarity-pass-2: each banner says how *this*
# clip relates to the previous one, so the cross-clip pattern (same
# coaching shape works on different songs/styles) is unmissable.
CLIPS: list[Clip] = [
    Clip(
        stem="timeline_filomena_intro_to_main_captioned",
        duration_s=14.0,
        banner_text=(
            "Example Gemma 4 coaching for an intro \u2192 main transition  \u00b7  kizomba"
        ),
    ),
    Clip(
        stem="timeline_e_magia_vocal_break_captioned",
        duration_s=14.0,
        banner_text=(
            "Same kizomba style, softer song  \u00b7  coaching for the vocal break"
        ),
    ),
    Clip(
        stem="timeline_royce_corazon_main_to_outro_captioned",
        duration_s=14.0,
        banner_text=(
            "Different style: bachata  \u00b7  same coaching pattern still works"
        ),
    ),
]

# Top context banner styling. Translucent slate-800 strip with white
# DejaVu-Bold text. Height/font sized to read from a thumbnail without
# crowding the timeline panels below.
BANNER_HEIGHT_PX = 56
BANNER_FONTSIZE = 26
BANNER_BG_COLOR = "0x1e293b@0.82"   # slate-800, 82% opaque
BANNER_FG_COLOR = "white"
BANNER_FONTFILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _banner_text(clip: Clip) -> str:
    """Return the clip's banner string (may be empty to disable banner)."""
    return clip.banner_text


def _drawtext_escape(text: str) -> str:
    """Escape characters that have meaning inside an ffmpeg filter graph."""
    # Order matters: backslash first, then the filter-special chars.
    return (
        text.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\u2019")  # cheap apostrophe swap; we have none here
            .replace(",", "\\,")
    )

XFADE_DURATION_S = 0.5
XFADE_TRANSITION = "fade"  # see module docstring for alternatives
OUTPUT_NAME = "rytmi_demo_reel.mp4"


def _input_path(clip: Clip) -> Path:
    """Resolve a clip's source MP4 path."""
    return OUTPUT_DIR / f"{clip.stem}.mp4"


def _build_filter_graph(clips: list[Clip], xfade_s: float, transition: str) -> str:
    """Build the ffmpeg ``-filter_complex`` graph for an N-clip reel.

    Crossfades video with ``xfade`` and audio with ``acrossfade``; applies
    ``loudnorm`` to each input audio stream first so levels match across
    the source recordings before the crossfade combines them.

    For N clips of equal duration ``d`` and crossfade ``x`` the offsets are
    ``d - x``, ``2*d - 2*x``, ``3*d - 3*x``, … which is what the chained
    xfade nodes need (``offset`` measures from the start of the *running*
    chain output, not from the start of each new input).
    """
    if not clips:
        raise ValueError("CLIPS is empty; nothing to stitch.")

    n = len(clips)
    parts: list[str] = []

    # Per-input audio normalisation. loudnorm is set with library defaults;
    # the I/LRA/TP arguments could be exposed if needed. The output stays
    # stereo at the source sample rate.
    for i in range(n):
        parts.append(f"[{i}:a]loudnorm[a{i}]")

    # Per-input video: optionally paint a top context banner so the genre,
    # tempo, and analysis point are unmissable to a viewer dropping in
    # mid-reel. Uses drawbox (filled translucent slate-800) + drawtext
    # (DejaVu-Bold). The banner is static across the full clip duration
    # so the playhead beneath it is the only moving element.
    for i, clip in enumerate(clips):
        text = _banner_text(clip)
        if not text:
            parts.append(f"[{i}:v]null[v{i}b]")
            continue
        esc = _drawtext_escape(text)
        parts.append(
            f"[{i}:v]"
            f"drawbox=x=0:y=0:w=iw:h={BANNER_HEIGHT_PX}"
            f":color={BANNER_BG_COLOR}:t=fill,"
            f"drawtext=fontfile={BANNER_FONTFILE}"
            f":text='{esc}':fontsize={BANNER_FONTSIZE}:fontcolor={BANNER_FG_COLOR}"
            f":x=(w-text_w)/2:y=({BANNER_HEIGHT_PX}-text_h)/2"
            f"[v{i}b]"
        )

    if n == 1:
        # Trivial path: re-encode + normalise audio, no fades.
        parts.append("[v0b]null[v]")
        return ";".join(parts) + ";[a0]anull[a]"

    running_duration = clips[0].duration_s
    last_v = "v0b"
    last_a = "a0"

    for i in range(1, n):
        offset = running_duration - xfade_s
        next_v_label = f"v{i:02d}"
        next_a_label = f"a{i:02d}out"
        parts.append(
            f"[{last_v}][v{i}b]xfade=transition={transition}"
            f":duration={xfade_s}:offset={offset:.3f}[{next_v_label}]"
        )
        parts.append(
            f"[{last_a}][a{i}]acrossfade=d={xfade_s}[{next_a_label}]"
        )
        last_v = next_v_label
        last_a = next_a_label
        running_duration += clips[i].duration_s - xfade_s

    # Final outputs labelled [v] and [a] for the -map flags below.
    parts.append(f"[{last_v}]null[v]")
    parts.append(f"[{last_a}]anull[a]")
    return ";".join(parts)


def _ffmpeg_cmd(clips: list[Clip], output_path: Path) -> list[str]:
    """Assemble the full ffmpeg command line."""
    cmd: list[str] = ["ffmpeg", "-y"]
    for clip in clips:
        cmd.extend(["-i", str(_input_path(clip))])
    filter_graph = _build_filter_graph(clips, XFADE_DURATION_S, XFADE_TRANSITION)
    cmd.extend([
        "-filter_complex", filter_graph,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path),
    ])
    return cmd


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg not found on PATH.", file=sys.stderr)
        return 2

    missing = [str(_input_path(c)) for c in CLIPS if not _input_path(c).exists()]
    if missing:
        print("ERROR: missing source clips:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print(
            "Hint: run `demo_assets/scripts/make_all_demo_videos.py` first.",
            file=sys.stderr,
        )
        return 2

    output_path = OUTPUT_DIR / OUTPUT_NAME
    cmd = _ffmpeg_cmd(CLIPS, output_path)

    expected_duration = (
        sum(c.duration_s for c in CLIPS) - XFADE_DURATION_S * (len(CLIPS) - 1)
    )
    print(f"Stitching {len(CLIPS)} clips → {output_path.relative_to(ROOT)}")
    for c in CLIPS:
        print(f"  {c.stem}.mp4  ({c.duration_s:.1f} s)")
    print(
        f"Crossfade: {XFADE_TRANSITION} @ {XFADE_DURATION_S} s; "
        f"expected output ≈ {expected_duration:.1f} s"
    )

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(
            f"ffmpeg exited with code {result.returncode}; see output above.",
            file=sys.stderr,
        )
        return result.returncode

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
