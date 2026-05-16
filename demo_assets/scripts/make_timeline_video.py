"""Render a windowed timeline video with a moving playhead, synced to audio.

Builds the existing ``rytmi.viz.plot_timeline`` figure for a song, restricts
the view to a chosen ``[start_s, start_s + duration_s]`` window, animates a
vertical playhead line across that window at the song's true playback rate,
and muxes the original audio slice underneath so the result plays in any
video player or PowerPoint.

Per-song Demucs analysis is the slow part (~30–60 s on CPU); the actual
rendering is fast. Section labels stay accurate because we always analyze
the **full** song and only crop the viewport.

Used by ``make_all_demo_videos.py`` as a single-clip primitive. Can also be
run standalone:

    .venv/bin/python demo_assets/scripts/make_timeline_video.py \\
        "data/songs/eval_set/kizomba/Filomena_Maricoa_-_Teu_Toque_Official_Video [sKbWzD0mt6I].mp3" \\
        --start 32 --duration 10 \\
        --out demo_assets/output/timeline_filomena_main.mp4 \\
        --title "Filomena — main section"
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from rytmi.audio import load_audio  # noqa: E402
from rytmi.dsp import analyze  # noqa: E402
from rytmi.viz import plot_timeline  # noqa: E402
import analysis_cache  # noqa: E402

DPI = 110


def _build_vocal_env(audio):
    """Return a Demucs vocal envelope, or None if unavailable. Cached per session."""
    try:
        from rytmi.vocal_activity import default_vocal_activity_source
        src = default_vocal_activity_source(prefer="demucs")
        return src.compute(audio)
    except Exception as exc:  # pragma: no cover — best-effort
        print(f"  (vocal env unavailable: {exc}; sections may be coarser)", file=sys.stderr)
        return None


def _add_caption_strip(fig, caption: str, *, speaker: str | None = "Gemma 4") -> None:
    """Add a dark semi-transparent caption band at the bottom of ``fig``.

    The figure is grown vertically so existing timeline panels keep their
    aspect; existing axes are re-anchored upward in figure coordinates so
    the new band sits below them with white wrapped text. The band is
    static — the playhead animation never touches it.

    If ``speaker`` is set (default: ``"Gemma 4"``), it is rendered as an
    inline violet-bold prefix on the first caption line ("Gemma 4: …"),
    so the attribution sits on the same baseline as the words it's
    attributing — readable from a single frame, no matter when a viewer
    drops in. Pass ``speaker=None`` to suppress it.
    """
    cur_w, cur_h = fig.get_size_inches()
    n_lines = max(1, caption.count("\n") + 1)
    extra_h = 0.55 + 0.32 * n_lines  # inches — scales with line count
    new_h = cur_h + extra_h

    # Snapshot existing axes positions (figure-fraction) BEFORE resizing.
    prior = [(ax, ax.get_position().bounds) for ax in fig.axes]

    # Constrained_layout would override any manual placement we do here,
    # so disable it and switch to fixed positions for both old and new axes.
    try:
        fig.set_layout_engine("none")
    except Exception:
        pass

    fig.set_size_inches(cur_w, new_h)
    band_frac = extra_h / new_h
    scale = (1.0 - band_frac) / 1.0  # compress old [0,1] into [band_frac, 1]

    for ax, (x0, y0, w, h) in prior:
        new_y0 = band_frac + y0 * scale
        new_h_ax = h * scale
        ax.set_position([x0, new_y0, w, new_h_ax])

    cap_ax = fig.add_axes([0.0, 0.0, 1.0, band_frac])
    cap_ax.set_facecolor((0.05, 0.05, 0.07))
    cap_ax.set_xticks([])
    cap_ax.set_yticks([])
    for spine in cap_ax.spines.values():
        spine.set_visible(False)

    # Render caption with two-tone provenance attribution.
    #
    # The captions for the transition clips have the form:
    #   "T1: 12s  [intro → main, beat: clear → clear]\n
    #    — when the bass kicks in, walk-step the basic on the first ..."
    # where the FIRST line is the verifier-re-rendered DSP scaffold
    # (T# index, timestamp, from/to labels, beat clarity — all from
    # `extract_transitions` and `_format_transition_line`) and the
    # remaining lines are Gemma's free-text coaching prose. Showing
    # both rows under one "Gemma 4:" prefix overclaims Gemma's role.
    #
    # When we detect the T# scaffold pattern we render two rows:
    #   row 1: teal "Rytmi DSP:" prefix + the structured header
    #   row 2: violet "Gemma 4:" prefix + the coaching prose
    # (leading "— " stripped from prose since the prefix replaces it).
    #
    # For captions that don't match the pattern (hybrid notebook quotes,
    # paraphrased context lines) we fall back to a single "Gemma 4:"
    # prefix on the first line — same behavior as before.
    from matplotlib.offsetbox import (  # local import: not used elsewhere
        AnchoredOffsetbox, HPacker, TextArea, VPacker,
    )
    import re

    lines = caption.split("\n")
    body_props = {"color": "white", "fontsize": 15, "family": "DejaVu Sans"}
    gemma_props = {
        **body_props, "color": "#a78bfa", "weight": "bold",  # violet-400
    }
    dsp_props = {
        **body_props, "color": "#5eead4", "weight": "bold",  # teal-300
    }

    _T_HEADER = re.compile(r"^T\d+:\s.*\[.*\]\s*$")
    has_dsp_header = (
        speaker is not None
        and len(lines) >= 2
        and _T_HEADER.match(lines[0].strip())
    )

    stacked_kids: list = []
    if has_dsp_header:
        # Row 1 — DSP scaffold
        row1_kids = [
            TextArea("Rytmi DSP:", textprops=dsp_props),
            TextArea(lines[0].strip(), textprops=body_props),
        ]
        stacked_kids.append(
            HPacker(children=row1_kids, pad=0, sep=8, align="baseline")
        )
        # Row 2 — Gemma prose. Strip the leading "— " continuation
        # marker because the violet "Gemma 4:" prefix now anchors the
        # row instead of the em-dash.
        gemma_text = lines[1].lstrip()
        if gemma_text.startswith("— "):
            gemma_text = gemma_text[2:]
        elif gemma_text.startswith("—"):
            gemma_text = gemma_text[1:].lstrip()
        row2_kids = [
            TextArea(f"{speaker}:", textprops=gemma_props),
            TextArea(gemma_text, textprops=body_props),
        ]
        stacked_kids.append(
            HPacker(children=row2_kids, pad=0, sep=8, align="baseline")
        )
        # Any further lines render plain (rare).
        for line in lines[2:]:
            stacked_kids.append(TextArea(line, textprops=body_props))
    else:
        first_row_kids: list = []
        if speaker:
            first_row_kids.append(TextArea(f"{speaker}:", textprops=gemma_props))
        first_row_kids.append(TextArea(lines[0], textprops=body_props))
        stacked_kids.append(
            HPacker(children=first_row_kids, pad=0, sep=8, align="baseline")
        )
        for line in lines[1:]:
            stacked_kids.append(TextArea(line, textprops=body_props))

    box = VPacker(children=stacked_kids, pad=0, sep=8, align="left")
    cap_ax.add_artist(
        AnchoredOffsetbox(
            loc="center", child=box, frameon=False,
            bbox_to_anchor=(0.5, 0.5), bbox_transform=cap_ax.transAxes,
        )
    )


def prepare_analysis(song_path: Path, dance_style: str | None = None):
    """Load audio + run the slow Demucs/analyze pass once. Returns (audio, analysis).

    Disk-cached on (path, mtime, size, dance_style); reruns are instant.
    """
    if not song_path.exists():
        raise FileNotFoundError(f"song not found: {song_path}")

    cached = analysis_cache.load(song_path, dance_style)
    if cached is not None:
        print(f"  cache hit: {song_path.name}")
        return cached

    print(f"  loading audio: {song_path.name}")
    audio = load_audio(str(song_path))
    print("  analyzing (Demucs vocals)…")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        vocal_env = _build_vocal_env(audio)
        analysis = analyze(audio, dance_style=dance_style, vocal_env=vocal_env)

    payload = (audio, analysis)
    analysis_cache.save(song_path, dance_style, payload)
    return payload


def render_from_analysis(
    song_path: Path,
    audio,
    analysis,
    start_s: float,
    duration_s: float,
    out_path: Path,
    *,
    title: str = "",
    fps: int = 30,
    caption: str | None = None,
) -> None:
    """Render an MP4 using a precomputed analysis (skips Demucs).

    Renders the timeline figure to a single PNG (matplotlib runs once),
    then ffmpeg loops the PNG and animates the playhead with a `drawbox`
    expression. ~100× faster than the previous FuncAnimation+FFMpegWriter
    path because matplotlib never has to redraw per-frame.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    end_s = min(start_s + duration_s, audio.duration)
    actual_dur = end_s - start_s
    if actual_dur <= 0:
        raise ValueError(f"window [{start_s}, {end_s}] is empty for {song_path.name}")

    fig = plot_timeline(analysis, title=title or song_path.stem, show_phrases=True)
    ax_wave, ax_str = fig.axes[0], fig.axes[1]
    ax_wave.set_xlim(start_s, end_s)
    ax_str.set_xlim(start_s, end_s)

    if caption:
        _add_caption_strip(fig, caption)

    # Force layout to settle so axis bboxes are accurate.
    fig.canvas.draw()

    # Display-pixel bboxes of the two timeline panels (origin: bottom-left).
    bbox_wave = ax_wave.get_window_extent()
    bbox_str = ax_str.get_window_extent()
    fig_h_px = int(round(fig.get_size_inches()[1] * DPI))

    # ffmpeg uses top-left origin; convert.
    x0_px = bbox_wave.x0  # both axes share xlim, same x mapping
    x1_px = bbox_wave.x1
    y_top_px = fig_h_px - bbox_wave.y1   # top of the wave panel
    y_bot_px = fig_h_px - bbox_str.y0    # bottom of the strength panel
    play_h_px = max(2, int(round(y_bot_px - y_top_px)))
    play_w_px = 3

    with tempfile.TemporaryDirectory() as tmpd:
        bg_png = Path(tmpd) / "bg.png"
        tmp_audio = Path(tmpd) / "slice.wav"

        print(f"  rendering background frame -> {bg_png.name}")
        fig.savefig(str(bg_png), dpi=DPI, facecolor=fig.get_facecolor())
        plt.close(fig)

        print(f"  slicing audio: {start_s:.2f}s + {actual_dur:.2f}s -> {tmp_audio.name}")
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-ss", f"{start_s}", "-t", f"{actual_dur}",
                "-i", str(song_path),
                "-vn", "-ac", "2", "-ar", "44100",
                str(tmp_audio),
            ],
            check=True,
        )

        # Animate the playhead via `overlay` (per-frame x evaluation).
        # ffmpeg's drawbox in 6.1 doesn't support per-frame expressions,
        # so we synthesize a small magenta bar with lavfi and slide it.
        # `t` is the current frame timestamp in seconds.
        x_expr = (
            f"{x0_px:.2f}+(t/{actual_dur:.4f})*"
            f"({x1_px - x0_px:.2f}-{play_w_px})"
        )
        filt = (
            f"[1:v]format=rgba,colorchannelmixer=aa=0.95[bar];"
            f"[0:v][bar]overlay=x='{x_expr}':y={int(y_top_px)}:eval=frame,"
            f"pad=ceil(iw/2)*2:ceil(ih/2)*2[v]"
        )

        print(f"  muxing -> {out_path}  (ffmpeg overlay playhead, {fps} fps)")
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-loop", "1", "-framerate", str(fps),
                "-t", f"{actual_dur:.4f}",
                "-i", str(bg_png),
                "-f", "lavfi",
                "-t", f"{actual_dur:.4f}",
                "-i", f"color=c=0xe91e63:s={play_w_px}x{play_h_px}:r={fps}",
                "-i", str(tmp_audio),
                "-filter_complex", filt,
                "-map", "[v]", "-map", "2:a",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(out_path),
            ],
            check=True,
        )

    print(f"  done: {out_path}  ({out_path.stat().st_size / 1024:.0f} KB)")


def render_timeline_video(
    song_path: Path,
    start_s: float,
    duration_s: float,
    out_path: Path,
    *,
    title: str = "",
    fps: int = 30,
    dance_style: str | None = None,
    caption: str | None = None,
) -> None:
    """Render a single windowed timeline MP4 with a moving playhead and audio."""
    audio, analysis = prepare_analysis(song_path, dance_style=dance_style)
    render_from_analysis(
        song_path, audio, analysis, start_s, duration_s, out_path,
        title=title, fps=fps, caption=caption,
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    p.add_argument("song", type=Path, help="path to source mp3/wav")
    p.add_argument("--start", type=float, required=True, help="window start in seconds")
    p.add_argument("--duration", type=float, required=True, help="window duration in seconds")
    p.add_argument("--out", type=Path, required=True, help="output mp4 path")
    p.add_argument("--title", type=str, default="", help="title shown above the timeline")
    p.add_argument("--fps", type=int, default=30, help="video frame rate (default 30)")
    p.add_argument("--style", type=str, default=None, help="dance style hint (e.g. kizomba, bachata)")
    p.add_argument("--caption", type=str, default=None, help="caption text baked into the bottom strip (\\n for line breaks)")
    return p.parse_args()


def main() -> int:
    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg not found on PATH", file=sys.stderr)
        return 1
    args = _parse_args()
    try:
        caption = args.caption.replace("\\n", "\n") if args.caption else None
        render_timeline_video(
            args.song, args.start, args.duration, args.out,
            title=args.title, fps=args.fps, dance_style=args.style,
            caption=caption,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
