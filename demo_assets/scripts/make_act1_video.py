"""Render Act 1 of the Rytmi demo video — the silent personal hook.

Implements `Act 1 — The hook` from `docs/demo_storyboard.md` after the
2026-05-16 clarity-pass-2 reorder. Three silent caption scenes (xfade =
0.5 s between):

- caption 1 (hook):   *"I wanted to dance to the music and hear the beat.*
                       *It kept slipping."*
- title slide:         the existing `act1_title_slide.png` lifted from the
                       end of the act so the Rytmi/Gemma framing arrives
                       within the first 10 seconds of the master.
- caption 2 (bridge): *"A beat tracker can find pulses. A dancer needs
                       more — phrasing, transitions, what the music is
                       doing."* / *"Rytmi uses Gemma 4 to explain it."*

No audible music in this act anymore: the audible-failure-mode beat
(generic-tracker clicks over Filomena) moved to the new Act 2.5, where
it lands *after* the architecture has been established and the kizomba
example case is named.

Output: `demo_assets/output/act1_hook.mp4` (1920×1080 / 30 fps / h264 +
silent stereo aac).

Re-runnable: rerenders the caption PNGs each call; ffmpeg re-encodes the
short act in seconds.

Usage from repo root::

    .venv/bin/python demo_assets/scripts/make_act1_video.py
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

# The title slide PNG is rendered by `make_all_demo_clips.py` (slate +
# accent-bar style) and reused here as the middle scene of the act so
# the Rytmi + Gemma framing lands within ~10 s of the master starting.
TITLE_SLIDE_PNG = OUTPUT_DIR / "act1_title_slide.png"

OUTPUT_PATH = OUTPUT_DIR / "act1_hook.mp4"

# Generated PNG paths (re-rendered each run from the captions below).
# Only two caption PNGs now — the third ("Kizomba's pulse is subtle…")
# moved to Act 2.5 (`make_act2_5_video.py`) where it has the architectural
# context to land properly.
CAPTION_PNG_1 = OUTPUT_DIR / "_act1_caption1.png"
CAPTION_PNG_2 = OUTPUT_DIR / "_act1_caption2.png"

XFADE_S = 0.5  # crossfade duration between scenes
WIDTH = 1920
HEIGHT = 1080
FPS = 30


@dataclass(frozen=True)
class Scene:
    """One slide in the act, with the duration it should be fully visible."""

    png: Path
    visible_s: float  # full-visibility duration; crossfades extend at boundaries
    label: str


# Scenes in narrative order. The `visible_s` is the time the slide is fully
# on screen (not counting the half-second crossfade at each boundary).
# Sum + (n-1) * xfade ≠ total because the xfade overlaps each pair —
# the running-output timeline below is what the ffmpeg offsets compute against.
#
# Order, post clarity-pass-2: hook → Rytmi/Gemma title → bridge. The title
# slide is intentionally the middle beat so a viewer dropping in within
# the first ten seconds knows what project this is.
SCENES: list[Scene] = [
    Scene(CAPTION_PNG_1, visible_s=5.5, label="caption1 (personal hook)"),
    Scene(TITLE_SLIDE_PNG, visible_s=4.0, label="title slide (Rytmi + Gemma 4)"),
    Scene(CAPTION_PNG_2, visible_s=9.0, label="caption2 (bridge: dancer needs more)"),
]


def _render_caption_pngs() -> None:
    """Render the two caption slides. Idempotent."""
    render_caption_slide(
        primary="I wanted to dance to the music and hear the beat.",
        secondary="It kept slipping.",
        footer=None,
        output=CAPTION_PNG_1,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=84,
        secondary_pt=64,
    )
    # Bridge slide — ties the personal frustration to the Rytmi/Gemma
    # promise and explicitly names the hackathon model. Primary is the
    # longer setup; secondary is the punchy product line.
    render_caption_slide(
        primary=(
            "A beat tracker can find pulses. "
            "A dancer needs more \u2014 phrasing, transitions, "
            "what the music is doing."
        ),
        secondary="Rytmi uses Gemma 4 to explain it.",
        footer=None,
        output=CAPTION_PNG_2,
        width=WIDTH,
        height=HEIGHT,
        primary_pt=64,
        secondary_pt=56,
    )


def _build_filter_graph(scenes: list[Scene], xfade_s: float) -> tuple[str, float]:
    """Build the xfade chain over N PNG inputs.

    Returns (filter_graph, total_video_duration_s). The PNG inputs must be
    declared in the same order as `scenes` and assumed to be inputs 0..N-1
    on the ffmpeg command line; the audio input follows at index N.
    """
    n = len(scenes)
    if n == 0:
        raise ValueError("no scenes")

    parts: list[str] = []
    # Force every PNG into the canvas size + fps + sar so xfade joins cleanly.
    for i, scene in enumerate(scenes):
        parts.append(
            f"[{i}:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x0f172a,"
            f"setsar=1,fps={FPS},format=yuv420p[s{i}]"
        )

    if n == 1:
        parts.append("[s0]null[v]")
        return ";".join(parts), scenes[0].visible_s

    # Chain xfades. After xfade(prev, next, duration=x, offset=O) the running
    # output length is O + (length_of_next_input). We pad each next input via
    # the scale chain above by relying on ffmpeg's `-loop 1 -t <T>` on the
    # command line, where T = scene.visible_s + xfade_s for safety.
    last_label = "s0"
    running_offset = scenes[0].visible_s
    for i in range(1, n):
        next_label = f"v{i}"
        parts.append(
            f"[{last_label}][s{i}]xfade=transition=fade"
            f":duration={xfade_s}:offset={running_offset:.3f}[{next_label}]"
        )
        last_label = next_label
        # The xfade output's running length grows by `visible_s + xfade_s`
        # because the next scene is fully visible after the fade ends and
        # then its visible_s plays out.
        running_offset += xfade_s + scenes[i].visible_s

    parts.append(f"[{last_label}]null[v]")
    return ";".join(parts), running_offset


def _ffmpeg_cmd(scenes: list[Scene], total_s: float) -> list[str]:
    cmd: list[str] = ["ffmpeg", "-y"]

    # Each PNG is loaded as a still image, padded to (visible + xfade) seconds
    # so xfade has enough frames at the boundary.
    n = len(scenes)
    for i, scene in enumerate(scenes):
        if not scene.png.exists():
            raise FileNotFoundError(scene.png)
        # Pad each input by xfade_s except the last (no trailing xfade).
        pad = XFADE_S if i < n - 1 else 0.0
        input_dur = scene.visible_s + pad + 0.5  # +0.5s safety
        cmd.extend(["-loop", "1", "-t", f"{input_dur:.3f}", "-i", str(scene.png)])

    # Silent stereo track so the master stitch's acrossfade has something
    # to chain against. Length is the act total; aresample + aformat keep
    # codec params identical to the other acts.
    cmd.extend(["-f", "lavfi", "-t", f"{total_s:.3f}",
                "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"])

    video_filter, _computed_total = _build_filter_graph(scenes, XFADE_S)
    audio_index = n  # zero-based input index for the silent source
    audio_filter = (
        f"[{audio_index}:a]aresample=44100,aformat=channel_layouts=stereo,"
        f"atrim=0:{total_s:.3f},asetpts=PTS-STARTPTS[a]"
    )
    filter_complex = f"{video_filter};{audio_filter}"

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
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
    if not TITLE_SLIDE_PNG.exists():
        print(f"ERROR: missing prerequisite: {TITLE_SLIDE_PNG}", file=sys.stderr)
        print("  Run `make_all_demo_clips.py` to generate the title slide.",
              file=sys.stderr)
        return 2

    print("Rendering caption PNGs …")
    _render_caption_pngs()

    _, total_s = _build_filter_graph(SCENES, XFADE_S)
    print(f"Scenes ({len(SCENES)}), total video = {total_s:.2f} s:")
    for s in SCENES:
        print(f"  {s.label}  visible {s.visible_s:.2f} s  ({s.png.name})")
    print("Audio: silent (audible-failure beat moved to Act 2.5).")

    cmd = _ffmpeg_cmd(SCENES, total_s)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"ffmpeg exited with code {result.returncode}", file=sys.stderr)
        return result.returncode

    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
