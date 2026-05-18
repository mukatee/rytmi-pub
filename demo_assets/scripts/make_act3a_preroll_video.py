"""Render Act 3a of the Rytmi demo video — the 50s pre-roll panels.

Implements `Act 3 — Rytmi in action (1:00–2:30)` opening segment from
`docs/demo_storyboard.md`. This act shows that *Gemma 4 itself produces
real, useful, grounded language about a real song*, before the unified
timeline visual and the audio/visual demo reel take over.

The panels mimic Jupyter notebook output cells (Option (b), see
storyboard Open questions, dated decision 2026-05-16). Each panel is
verbatim text from `notebooks/00_demo_outputs.md` against
*Filomena Maricoa — Teu Toque (kizomba)*.

Sequence (with 0.5s crossfades between scenes):

- 0:00–0:11  panel 1: rhythm_anatomy — "What kind of music is this?"
- 0:11–0:23  panel 2: describe_sections — "Where are the sections?"
             (truncated to header + first 6 rows + ellipsis to stay
             readable on screen at 1080p; full table lives in the
             notebook).
- 0:23–0:36  panel 3: listening_guide — "Where will the pulse be hardest?"
- 0:36–0:50  panel 4: song_arc — "What makes this song distinct?"

Output: `demo_assets/output/act3a_preroll.mp4` (1920×1080 / 30 fps /
h264 + silent aac so the act stitches cleanly onto the surrounding
audio-bearing acts in the master reel).

Each PNG is rendered to `demo_assets/output/_act3a_*.png` and is
re-orderable / re-skinnable independently — swap the renderer or change
text in the constants below without touching the ffmpeg chain.

Usage from repo root::

    .venv/bin/python demo_assets/scripts/make_act3a_preroll_video.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from make_notebook_panel import render_notebook_panel  # noqa: E402

OUTPUT_DIR = ROOT / "demo_assets" / "output"
OUTPUT_PATH = OUTPUT_DIR / "act3a_preroll.mp4"

PANEL_PNG_1 = OUTPUT_DIR / "_act3a_rhythm_anatomy.png"
PANEL_PNG_2 = OUTPUT_DIR / "_act3a_describe_sections.png"
PANEL_PNG_3 = OUTPUT_DIR / "_act3a_listening_guide.png"
PANEL_PNG_4 = OUTPUT_DIR / "_act3a_song_arc.png"

XFADE_S = 0.5
WIDTH = 1920
HEIGHT = 1080
FPS = 30


# Verbatim Gemma output, copied from notebooks/00_demo_outputs.md.
# Keep these in sync if the canonical notebook is re-run; the storyboard
# treats this as the single source of truth.

RHYTHM_ANATOMY_BODY = (
    "Kizomba typically operates within a tempo range of 85–110 BPM in a "
    "4/4 time signature. Rather than relying on a heavy percussive grid, "
    "the pulse is often carried by a deep, driving bass line that "
    "dictates the rhythmic foundation. While some tracks feature melodic "
    "syncopation, the primary rhythmic emphasis is felt through the bass "
    "rather than sharp drum hits. A standard track follows a structural "
    "arc beginning with an intro, moving through main sections of "
    "varying energy, often encountering a break or pause, before "
    "reaching a peak and settling into an outro."
)

# Truncated for legibility at 1080p — full 18-row table is in the
# notebook. We show the header + first 6 data rows and an ellipsis row;
# this is enough for the audience to read "low/medium/high energy",
# "intro/main/break/outro", and the per-section signals. The ellipsis
# also signals there is more substance behind the cell.
DESCRIBE_SECTIONS_BODY = (
    "tempo=92.3 BPM | beats=316 | sections=18 | duration=208.9s | vocal_env=yes\n"
    "\n"
    "Section table — 92 BPM, 4/4, 8-count phrases, 18 sections\n"
    "  downbeat offset = 2 (confidence = 0.14)\n"
    " #  label          energy   time (s)        dur     signals\n"
    "------------------------------------------------------------------------\n"
    " 0  intro          low        0.0– 11.7    11.7s   RMS×0.39  H×0.40  P×0.36\n"
    " 1  main           medium    11.7– 22.0    10.3s   RMS×1.05  H×1.03  P×1.00\n"
    " 5  main           high      59.4– 69.7    10.3s   RMS×1.18  H×1.11  P×1.23\n"
    "11  main           high     121.3–131.3    10.0s   RMS×1.18  H×1.18  P×1.16\n"
    "13  break[severe]  low      147.7–159.2    11.6s   RMS×0.30  H×0.45  P×0.28\n"
    "15  main           high     174.9–185.2    10.3s   RMS×1.19  H×1.16  P×1.18\n"
    "17  outro          low      195.4–208.9    13.5s   RMS×0.82  H×0.81  P×0.79\n"
    "        … 11 more rows in notebook …"
)

LISTENING_GUIDE_BODY = (
    "This 208.9-second track maintains a steady tempo of 92 BPM. The "
    "musical journey begins with a quiet intro, moves through several "
    "main sections of varying energy, encounters a brief break, and "
    "eventually winds down through an outro. Because the percussiveness "
    "is unusually low, the rhythm is not driven by a heavy drum kit; "
    "instead, the melodic and harmonic content carries the pulse, "
    "making the bass line the primary guide for the rhythm.\n"
    "\n"
    "The pulse remains clear throughout most of the track, so your main "
    "challenge will be sustaining attention rather than recovering from "
    "a rhythmic dip. However, you may find the pulse more subtle during "
    "the intro and the break, specifically around 148s, where the "
    "energy drops and the rhythm feels less defined. During these "
    "quieter stretches, trust the bass line to find the underlying pulse."
)

SONG_ARC_BODY = (
    "The track begins with a low-energy intro from 0s to 12s, inviting "
    "you to focus on connection through minimal movement. The energy "
    "builds into a medium-level steady pulse that reaches high-energy "
    "peaks during the middle sections, specifically around 59s and "
    "121s. After a sudden drop into a low-energy break at 148s, the "
    "music surges back into a final high-energy phase before resolving "
    "into a gentle, low-energy outro at 195s.\n"
    "\n"
    "This track is distinguished from typical kizomba by its unusually "
    "low percussiveness, meaning the rhythm is carried more by melodic "
    "or harmonic content than by drums."
)


@dataclass(frozen=True)
class Scene:
    png: Path
    visible_s: float
    label: str


# Visible-second budget — 4 scenes with 3 xfades of 0.5 s each:
#   total = 11.0 + (0.5 + 12.0) + (0.5 + 13.0) + (0.5 + 12.0) = 49.5 s
# The master stitcher can extend this with a brief hold if needed.
# Sparkler re-cut (2026-05-18): 4 → 2 panels. The old four said the same
# thing three ways (kizomba / bass-driven / low-percussion / intro-main-
# break-outro arc) and pushed the live reel out to ~2:00. We keep the two
# that earn their seconds and don't repeat each other:
#   • rhythm_anatomy  — Gemma 4 says *what kind of music this is*
#   • listening_guide — Gemma 4 *coaches where the pulse is hard*
# describe_sections (DSP table) is dropped: the structure is shown far
# more vividly by the unified-timeline + audio reel that follow. song_arc
# is dropped: it restates rhythm_anatomy + listening_guide.
SCENES: list[Scene] = [
    Scene(PANEL_PNG_1, visible_s=9.5, label="rhythm_anatomy"),
    Scene(PANEL_PNG_3, visible_s=11.0, label="listening_guide"),
]


def _render_panel_pngs() -> None:
    """Render Act 3a's four notebook panels. Idempotent.

    Heading text is the load-bearing attribution channel — a viewer
    landing on any single panel needs to know whether what they're
    reading is Gemma's prose or the DSP table that *feeds* Gemma. The
    cell-tag (teal) line below the heading carries the function name;
    the footer carries the source. Three Gemma panels share the default
    "verbatim Gemma 4 output" footer; the DSP `describe_sections` panel
    overrides the footer to make the data-flow direction explicit.
    """
    render_notebook_panel(
        heading="Gemma 4 explains the music style",
        tag="[rhythm_anatomy]  genre=kizomba",
        cell_prompt="In [4]:  rhythm_anatomy('kizomba')",
        body=RHYTHM_ANATOMY_BODY,
        output=PANEL_PNG_1,
        body_pt=30,
    )
    # `describe_sections` is DSP output, not Gemma — it's the structured
    # table that Gemma's later panels consume. Heading + footer both
    # disambiguate so the architectural split (code listens, Gemma talks)
    # reads off any single frame of this panel.
    render_notebook_panel(
        heading="Code finds the sections (input to Gemma)",
        tag="[describe_sections]  Filomena – Teu Toque",
        cell_prompt="In [7]:  describe_sections(audio, sections, beats)",
        body=DESCRIBE_SECTIONS_BODY,
        output=PANEL_PNG_2,
        body_pt=22,
        footer="notebooks/00_demo.ipynb · verbatim Rytmi DSP output — fed to Gemma below",
    )
    render_notebook_panel(
        heading="Gemma 4 coaches: where to listen",
        tag="[listening_guide]  Filomena – Teu Toque",
        cell_prompt="In [9]:  listening_guide(sections, beats, vocals)",
        body=LISTENING_GUIDE_BODY,
        output=PANEL_PNG_3,
        body_pt=28,
    )
    render_notebook_panel(
        heading="Gemma 4 narrates the song's arc",
        tag="[song_arc]  Filomena – Teu Toque",
        cell_prompt="In [11]:  song_arc(sections, rhythm_features)",
        body=SONG_ARC_BODY,
        output=PANEL_PNG_4,
        body_pt=30,
    )


def _build_filter_graph(scenes: list[Scene], xfade_s: float) -> tuple[str, float]:
    """Build the xfade chain — same pattern as `make_act{1,2}_video`."""
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

    print("Rendering Act 3a notebook panels …")
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
