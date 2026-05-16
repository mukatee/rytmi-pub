"""Visualization: waveform, spectrogram, onset/beat overlays."""

from __future__ import annotations

import uuid

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from rytmi.types import AudioData, BeatData, OnsetData, RhythmAnalysis


def plot_waveform(audio: AudioData, ax: Axes | None = None) -> Axes:
    """Plot the audio waveform."""
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 3))
    times = np.arange(len(audio.samples)) / audio.sr
    ax.plot(times, audio.samples, linewidth=0.5, color="steelblue")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Waveform")
    ax.set_xlim(0, audio.duration)
    return ax


def plot_spectrogram(audio: AudioData, ax: Axes | None = None) -> Axes:
    """Plot a mel spectrogram."""
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 3))
    S = librosa.feature.melspectrogram(y=audio.samples, sr=audio.sr)
    S_db = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_db, sr=audio.sr, x_axis="time", y_axis="mel", ax=ax)
    ax.set_title("Mel Spectrogram")
    return ax


def plot_onsets(
    audio: AudioData,
    onsets: OnsetData,
    ax: Axes | None = None,
) -> Axes:
    """Plot waveform with onset markers."""
    ax = plot_waveform(audio, ax=ax)
    for t in onsets.times:
        ax.axvline(x=t, color="red", alpha=0.6, linewidth=0.8)
    ax.set_title("Waveform + Onsets")
    return ax


def plot_beats(
    audio: AudioData,
    beats: BeatData,
    ax: Axes | None = None,
) -> Axes:
    """Plot waveform with beat markers."""
    ax = plot_waveform(audio, ax=ax)
    for t in beats.times:
        ax.axvline(x=t, color="green", alpha=0.7, linewidth=1.2, linestyle="--")
    ax.set_title(f"Waveform + Beats ({beats.tempo:.0f} BPM)")
    return ax


def plot_onset_strength(onsets: OnsetData, ax: Axes | None = None) -> Axes:
    """Plot the onset strength envelope."""
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 2))
    times = librosa.frames_to_time(np.arange(len(onsets.strength)), sr=onsets.sr)
    ax.plot(times, onsets.strength, color="orange", linewidth=0.8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Strength")
    ax.set_title("Onset Strength")
    return ax


def plot_analysis(analysis: RhythmAnalysis) -> Figure:
    """Multi-panel overview: waveform+beats, onset strength, spectrogram."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 9), constrained_layout=True)

    # Panel 1: waveform + beats + onsets
    plot_waveform(analysis.audio, ax=axes[0])
    for t in analysis.beats.times:
        axes[0].axvline(x=t, color="green", alpha=0.6, linewidth=1.2, linestyle="--")
    for t in analysis.onsets.times:
        axes[0].axvline(x=t, color="red", alpha=0.4, linewidth=0.6)
    axes[0].set_title(
        f"Waveform + Beats (green) + Onsets (red) | {analysis.tempo:.0f} BPM"
    )

    # Panel 2: onset strength
    plot_onset_strength(analysis.onsets, ax=axes[1])

    # Panel 3: spectrogram
    plot_spectrogram(analysis.audio, ax=axes[2])

    return fig


PHRASE_COLOR = "#7030a0"  # purple for dancer 8-count

# Section/phase band colors — translucent background per section type.
# These are muted enough to not overpower the waveform or beat markers.
SECTION_COLORS: dict[str, str] = {
    "spoken_intro": "#34495e",  # dark blue-grey — speech (not singing) before the music starts
    "intro": "#4fc3f7",        # light blue
    "main": "#d0d0d0",         # neutral grey (most common; kept muted)
    "break": "#f4d03f",        # warm yellow
    "short_break": "#e67e22",  # warm orange — distinct from break (yellow) and build (saturated orange)
    "build": "#f39c12",        # saturated orange
    "peak": "#e74c3c",         # deeper red
    "instrumental": "#16a085",  # teal — vocal-quiet, energy-present passages
    "outro": "#7b5aa6",        # saturated purple — stays distinct from main at low alpha
}

# Energy-level encoding on phase bands.  Alpha scales with energy so a
# learner can see at a glance where a phase sits on the low→high scale,
# independent of its categorical label.
_ENERGY_ALPHA: dict[str, float] = {
    "low": 0.15,
    "medium": 0.30,
    "high": 0.50,
}
_ENERGY_CHIP: dict[str, str] = {
    "low": "\u2581",   # ▁
    "medium": "\u2584",  # ▄
    "high": "\u2588",  # █
}
_ENERGY_RANK: dict[str, int] = {"low": 1, "medium": 2, "high": 3}
_RANK_ENERGY: dict[int, str] = {1: "low", 2: "medium", 3: "high"}


def _dominant_energy(energy_levels: list[str]) -> str:
    """Pick a single representative energy from a list of per-section levels.

    Uses the mean numeric rank (low=1, medium=2, high=3) rounded to the
    nearest integer.  Ties round up — a phase containing [medium, high] is
    rendered as high, since the learner cares more about the peak than the
    average when a phase mixes energy levels.
    """
    if not energy_levels:
        return "medium"
    ranks = [_ENERGY_RANK.get(e, 2) for e in energy_levels]
    mean_rank = sum(ranks) / len(ranks)
    rounded = int(mean_rank + 0.5)  # round half up
    return _RANK_ENERGY.get(max(1, min(3, rounded)), "medium")


def plot_timeline(
    analysis: RhythmAnalysis,
    title: str = "",
    show_phrases: bool = True,
    pixels_per_second: float | None = None,
) -> Figure:
    """Rich timeline showing waveform, beats, downbeats, onsets, and beat numbers.

    - Waveform in light grey background
    - Onsets as thin red lines
    - Beats as green dashed lines with beat number labels (1, 2, 3, 4, ...)
    - Downbeats ("the one") as bold orange lines with measure numbers
    - When ``show_phrases`` is True, a second row of dancer 8-counts (1-8) in
      purple, and bold purple phrase lines every ``phrase_length`` beats
    - Onset strength envelope below
    """
    downbeats = analysis.downbeats
    bpm = analysis.beats_per_measure
    phrase_length = analysis.phrase_length if show_phrases else 0
    # Measures per phrase (e.g. 8 dancer counts / 4 beats per measure = 2)
    measures_per_phrase = (phrase_length // bpm) if bpm > 0 else 0

    downbeat_set = set()
    if downbeats is not None:
        downbeat_set = set(np.round(downbeats, 4))

    # Figure width: either fixed (default 16 in) or scaled to a target pixel
    # density so each second of audio gets a stable number of pixels.  At
    # the default dpi=100, e.g. pixels_per_second=60 + duration=30 s =>
    # width = 18 in => 1800 px, which horizontal-scrolls well in notebooks.
    if pixels_per_second is not None:
        fig_width = max(12.0, (analysis.audio.duration * pixels_per_second) / 100.0)
    else:
        fig_width = 16.0
    fig_height = 6 if show_phrases else 5
    fig, axes = plt.subplots(
        2, 1, figsize=(fig_width, fig_height), constrained_layout=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    ax_wave = axes[0]
    ax_str = axes[1]

    # --- Panel 1: waveform + markers ---
    times = np.arange(len(analysis.audio.samples)) / analysis.audio.sr

    # Section/phase color bands (behind waveform).  Alpha encodes the
    # phase's dominant energy level — learners can see the energy arc at
    # a glance even when the categorical label is "main" everywhere.
    phases = getattr(analysis, "phases", None) or []
    section_labels_in_plot: set[str] = set()
    energies_in_plot: set[str] = set()
    if phases:
        for ph in phases:
            color = SECTION_COLORS.get(ph.label, "#e0e0e0")
            energy = _dominant_energy(getattr(ph, "energy_levels", []) or [])
            alpha = _ENERGY_ALPHA.get(energy, 0.25)
            ax_wave.axvspan(
                ph.start_s, ph.end_s, color=color, alpha=alpha, zorder=0,
            )
            ax_str.axvspan(
                ph.start_s, ph.end_s, color=color, alpha=alpha, zorder=0,
            )
            section_labels_in_plot.add(ph.label)
            energies_in_plot.add(energy)

    ax_wave.fill_between(
        times, analysis.audio.samples, color="lightsteelblue", alpha=0.5,
    )
    ax_wave.plot(times, analysis.audio.samples, linewidth=0.3, color="steelblue")

    # Onsets: thin red
    for t in analysis.onsets.times:
        ax_wave.axvline(x=t, color="red", alpha=0.3, linewidth=0.5)

    # Waveform visual band is +/- amp_max. Labels live OUTSIDE that band
    # so they never overlap the audio trace. Generous headroom.
    amp_max = float(np.max(np.abs(analysis.audio.samples)))
    y_section_label = amp_max * (1.65 if show_phrases else 1.18)
    if show_phrases:
        y_headroom = 1.95 if phases else 1.75  # extra room for section labels
    else:
        y_headroom = 1.35 if phases else 1.30
    ax_wave.set_ylim(-amp_max * y_headroom, amp_max * y_headroom)

    # Phase boundary labels (top of the waveform area)
    if phases:
        for i, ph in enumerate(phases, 1):
            count_str = f" ×{ph.section_count}" if ph.section_count > 1 else ""
            energy = _dominant_energy(getattr(ph, "energy_levels", []) or [])
            chip = _ENERGY_CHIP.get(energy, "")
            time_str = f"{ph.start_s:.0f}–{ph.end_s:.0f}s"
            mid_t = (ph.start_s + ph.end_s) / 2
            ax_wave.text(
                mid_t, y_section_label,
                f"S{i}: {ph.label}{count_str} {chip}\n{time_str}",
                fontsize=8, ha="center", va="center",
                color="black",
                fontweight="bold", alpha=0.9,
                bbox=dict(boxstyle="round,pad=0.2",
                          facecolor=SECTION_COLORS.get(ph.label, "white"),
                          edgecolor="#999", alpha=0.45),
            )
            # Phase boundary tick (subtle dashed line at start)
            if ph.start_s > 0:
                ax_wave.axvline(
                    x=ph.start_s, color="#999", alpha=0.4,
                    linewidth=0.8, linestyle=":",
                )

    # Label y-positions (all outside the +/- amp_max waveform band)
    y_m_label = amp_max * 1.12      # measure M1, M2, ...  (just above wave)
    y_p_label = amp_max * 1.45      # phrase P1, P2, ...   (top row)
    y_beat_label = -amp_max * 1.12  # beat-in-measure 1-4  (just below wave)
    y_dancer_label = -amp_max * 1.45  # dancer 8-count      (bottom row)

    # Beats: green dashed, numbered. Also track 8-count and phrase.
    # Use rel = i - offset so the grid anchors to the detected downbeat.
    offset = analysis.downbeat_offset or 0

    # Pickup marker: dotted purple line half a beat before first real downbeat
    if offset > 0 and offset < len(analysis.beats.times):
        median_ibi = float(np.median(np.diff(analysis.beats.times))) if len(analysis.beats.times) > 1 else 0.5
        marker_t = analysis.beats.times[offset] - 0.5 * median_ibi
        if marker_t > 0:
            ax_wave.axvline(
                x=marker_t, color=PHRASE_COLOR, alpha=0.6,
                linewidth=1.5, linestyle=":",
            )

    prev_phrase = 0

    for i, t in enumerate(analysis.beats.times):
        rel = i - offset
        is_pickup = rel < 0

        if is_pickup:
            # Pickup beats: grey, lighter alpha
            ax_wave.axvline(
                x=t, color="grey", alpha=0.3, linewidth=1.0, linestyle="--",
            )
            ax_wave.text(
                t, y_beat_label, "·",
                fontsize=10, color="grey",
                ha="center", va="center", fontweight="bold",
            )
            if show_phrases and phrase_length > 0:
                dancer_count = (phrase_length + (rel % phrase_length)) % phrase_length + 1
                ax_wave.text(
                    t, y_dancer_label, str(dancer_count),
                    fontsize=10, color="grey", alpha=0.5,
                    ha="center", va="center", fontweight="bold",
                )
            continue

        beat_in_measure = (rel % bpm) + 1
        measure = (rel // bpm) + 1
        dancer_count = (rel % phrase_length) + 1 if phrase_length > 0 else 1
        phrase = (rel // phrase_length) + 1 if phrase_length > 0 else 1
        is_downbeat = beat_in_measure == 1
        is_phrase_start = (
            show_phrases
            and is_downbeat
            and measures_per_phrase > 0
            and (measure - 1) % measures_per_phrase == 0
        )

        if is_phrase_start and phrase != prev_phrase:
            ax_wave.axvline(x=t, color=PHRASE_COLOR, alpha=0.85, linewidth=3.5)
            ax_wave.text(
                t, y_p_label, f"P{phrase}",
                fontsize=11, fontweight="bold", color=PHRASE_COLOR,
                ha="left", va="center",
            )
            prev_phrase = phrase

        if is_downbeat:
            ax_wave.axvline(x=t, color="darkorange", alpha=0.9, linewidth=2.5)
            ax_wave.text(
                t, y_m_label, f"M{measure}",
                fontsize=10, fontweight="bold", color="darkorange",
                ha="left", va="center",
            )
        else:
            ax_wave.axvline(
                x=t, color="green", alpha=0.5, linewidth=1.0, linestyle="--",
            )

        ax_wave.text(
            t, y_beat_label, str(beat_in_measure),
            fontsize=10, color="green" if not is_downbeat else "darkorange",
            ha="center", va="center", fontweight="bold",
        )

        if show_phrases and phrase_length > 0:
            ax_wave.text(
                t, y_dancer_label, str(dancer_count),
                fontsize=10, color=PHRASE_COLOR,
                ha="center", va="center", fontweight="bold",
            )

    # Row labels on the left margin so the reader knows what each row is
    if phases:
        ax_wave.text(-0.006, y_section_label, "section",
                     transform=ax_wave.get_yaxis_transform(),
                     ha="right", va="center", fontsize=9,
                     color="black", fontweight="bold")
    if show_phrases:
        ax_wave.text(-0.006, y_p_label, "phrase",
                     transform=ax_wave.get_yaxis_transform(),
                     ha="right", va="center", fontsize=9,
                     color=PHRASE_COLOR, fontweight="bold")
    ax_wave.text(-0.006, y_m_label, "measure",
                 transform=ax_wave.get_yaxis_transform(),
                 ha="right", va="center", fontsize=9,
                 color="darkorange", fontweight="bold")
    ax_wave.text(-0.006, y_beat_label, "beat",
                 transform=ax_wave.get_yaxis_transform(),
                 ha="right", va="center", fontsize=9,
                 color="green", fontweight="bold")
    if show_phrases:
        ax_wave.text(-0.006, y_dancer_label, "8-count",
                     transform=ax_wave.get_yaxis_transform(),
                     ha="right", va="center", fontsize=9,
                     color=PHRASE_COLOR, fontweight="bold")

    ax_wave.set_xlim(0, analysis.audio.duration)
    ax_wave.set_yticks([])  # amplitude scale not meaningful with label rows
    display_title = title or (analysis.audio.filepath or "")
    title_extra = (
        f"   {phrase_length}-count" if show_phrases and phrase_length > 0 else ""
    )
    ax_wave.set_title(
        f"{display_title}   |   {analysis.tempo:.0f} BPM   "
        f"{bpm}/4 time{title_extra}   {len(analysis.beats.times)} beats   "
        f"{len(analysis.onsets.times)} onsets",
        fontsize=11,
    )

    # Legend
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = [
        Line2D([0], [0], color="darkorange", linewidth=2.5, label="Downbeat (the one)"),
        Line2D([0], [0], color="green", linewidth=1, linestyle="--", label="Beat"),
        Line2D([0], [0], color="red", linewidth=0.8, alpha=0.5, label="Onset"),
    ]
    if show_phrases:
        legend_elements.insert(
            0,
            Line2D([0], [0], color=PHRASE_COLOR, linewidth=3.5,
                   label=f"Phrase ({phrase_length}-count)"),
        )
    # Section color swatches (only for labels present in this track)
    for label in ["spoken_intro", "intro", "main", "break", "short_break", "build", "peak", "instrumental", "outro"]:
        if label in section_labels_in_plot:
            legend_elements.append(
                Patch(facecolor=SECTION_COLORS[label], alpha=0.35, label=label),
            )
    # Energy-level swatches (grey at the three alpha levels) so the band
    # transparency is interpretable without cross-referencing the chip text.
    if phases:
        for energy in ["low", "medium", "high"]:
            if energy in energies_in_plot:
                legend_elements.append(
                    Patch(facecolor="#666", alpha=_ENERGY_ALPHA[energy],
                          label=energy),
                )
    # Beat clarity legend (bottom strip): red=hard, green=clear
    sections = getattr(analysis, "sections", None) or []
    if sections:
        from matplotlib.patches import Patch as _Patch
        legend_elements.append(
            _Patch(facecolor="#e74c3c", alpha=0.7, label="BC low"),
        )
        legend_elements.append(
            _Patch(facecolor="#27ae60", alpha=0.7, label="BC high"),
        )
    ax_wave.legend(handles=legend_elements, loc="upper right", fontsize=8, ncol=2)

    # --- Panel 2: onset strength ---
    str_times = librosa.frames_to_time(
        np.arange(len(analysis.onsets.strength)), sr=analysis.onsets.sr,
    )
    ax_str.fill_between(str_times, analysis.onsets.strength, color="orange", alpha=0.3)
    ax_str.plot(str_times, analysis.onsets.strength, color="darkorange", linewidth=0.8)

    # Mark downbeats on strength panel too
    for t in (downbeats if downbeats is not None else []):
        ax_str.axvline(x=t, color="darkorange", alpha=0.6, linewidth=1.5)

    # Phase boundary ticks on strength panel
    for ph in phases:
        if ph.start_s > 0:
            ax_str.axvline(x=ph.start_s, color="#999", alpha=0.4, linewidth=0.8,
                           linestyle=":")

    # Beat-clarity color strip along the bottom of the onset-strength panel.
    # Each section gets a thin band colored from red (low BC) to green (high BC).
    if sections:
        import matplotlib.colors as mcolors

        # red→yellow→green gradient for BC 0→0.25→0.5+
        bc_cmap = mcolors.LinearSegmentedColormap.from_list(
            "bc", ["#e74c3c", "#f4d03f", "#27ae60"],
        )
        str_ylim = ax_str.get_ylim()
        strip_h = (str_ylim[1] - str_ylim[0]) * 0.06
        for sec in sections:
            bc = sec.rhythm_features.beat_clarity if sec.rhythm_features else 0.0
            # Clamp to [0, 0.5] range for color mapping (scores rarely exceed 0.5)
            bc_normed = min(bc / 0.5, 1.0)
            ax_str.axvspan(
                sec.start_s, sec.end_s,
                ymin=0, ymax=strip_h / (str_ylim[1] - str_ylim[0]),
                color=bc_cmap(bc_normed), alpha=0.7, zorder=2,
            )

    ax_str.set_xlim(0, analysis.audio.duration)
    ax_str.set_xlabel("Time (s)")
    ax_str.set_ylabel("Onset strength")

    return fig


_CACHE_DIR_NAME = "_timeline_cache"


def _timeline_cache_dir() -> "Path":
    """Return the project-level cache directory for timeline assets.

    We write image and audio to this directory as real files rather than
    inlining them as base64 data URIs.  Reason: Jupyter imposes a per-cell
    output size cap (~1 MB default) that base64-encoded audio easily
    exceeds.  File-referenced assets bypass that cap entirely.
    """
    from pathlib import Path
    # Project root is two levels up from this file: src/rytmi/viz.py -> project
    project_root = Path(__file__).resolve().parent.parent.parent
    cache_dir = project_root / "data" / _CACHE_DIR_NAME
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _save_fig(fig: Figure, path: "Path") -> None:
    """Save a matplotlib figure to ``path`` as PNG and close it."""
    fig.savefig(path, format="png", dpi=100)
    plt.close(fig)


def _save_audio(audio: AudioData, path: "Path") -> None:
    """Write audio samples as a 16-bit WAV to ``path``."""
    import soundfile as sf

    sf.write(str(path), audio.samples, audio.sr, format="WAV", subtype="PCM_16")


def interactive_timeline(
    analysis: RhythmAnalysis,
    title: str = "",
    show_phrases: bool = True,
    pixels_per_second: float = 60.0,
) -> str:
    """Return an HTML string with timeline image, audio player, and moving cursor.

    The image is rendered at ``pixels_per_second`` px/s of audio so long
    tracks stay readable instead of getting squished.  The image lives in
    a horizontally-scrolling container; the cursor moves in image pixel
    space, not the scroll viewport, so scrolling and seeking both work.

    Image and audio are written to ``data/_timeline_cache/`` as real files
    (not base64 data URIs) to avoid Jupyter's per-cell output size cap.

    Display in Jupyter with ``IPython.display.HTML(interactive_timeline(...))``.
    """
    widget_id = uuid.uuid4().hex[:10]
    cache_dir = _timeline_cache_dir()

    # Render the static timeline at a target pixel density
    fig = plot_timeline(
        analysis,
        title=title,
        show_phrases=show_phrases,
        pixels_per_second=pixels_per_second,
    )
    # Measure the plot area in figure-fraction coordinates so the cursor
    # aligns correctly with the time axis.  Must draw first so
    # constrained_layout finalises axes positions.
    fig.canvas.draw()
    ax_wave = fig.axes[0]
    bbox = ax_wave.get_position()  # in figure fraction
    fig_width_in = fig.get_size_inches()[0]
    img_path = cache_dir / f"timeline_{widget_id}.png"
    _save_fig(fig, img_path)

    # Persist audio next to the image.  Use a WAV file for max browser
    # compatibility; some notebook renderers choke on embedded data URIs.
    audio_path = cache_dir / f"audio_{widget_id}.wav"
    _save_audio(analysis.audio, audio_path)

    duration = analysis.audio.duration
    # Plot area edges as % of image width
    left_pct = bbox.x0 * 100
    right_pct = bbox.x1 * 100
    img_width_px = int(fig_width_in * 100)  # dpi=100

    # Relative paths: the notebook runs from notebooks/ so ../data/... works.
    # Encode spaces just in case.
    img_src = f"../data/{_CACHE_DIR_NAME}/{img_path.name}"
    audio_src = f"../data/{_CACHE_DIR_NAME}/{audio_path.name}"

    return f"""\
<div id="w_{widget_id}" style="width:100%;">
  <div id="scroll_{widget_id}" style="
    overflow-x:auto; overflow-y:hidden; width:100%;
    border:1px solid #ddd; position:relative;
  ">
    <div id="inner_{widget_id}" style="
      position:relative; width:{img_width_px}px;
    ">
      <img id="img_{widget_id}" src="{img_src}"
           style="width:{img_width_px}px; display:block; cursor:pointer;" />
      <div id="cur_{widget_id}" style="
        position:absolute; top:0; height:100%;
        width:2px; background:red; opacity:0.8;
        pointer-events:none; left:{left_pct:.2f}%; display:none;
      "></div>
    </div>
  </div>
  <audio id="aud_{widget_id}" src="{audio_src}" preload="auto"></audio>
  <div style="margin-top:4px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
    <button id="btn_{widget_id}"
      style="padding:4px 16px; font-size:14px; cursor:pointer;">Play</button>
    <button id="rst_{widget_id}"
      style="padding:4px 12px; font-size:14px; cursor:pointer;">Reset</button>
    <input id="seek_{widget_id}" type="range" min="0" max="{duration:.1f}"
      step="0.1" value="0" style="flex:1; min-width:120px; cursor:pointer;" />
    <span id="time_{widget_id}" style="font-family:monospace; font-size:13px;">
      0:00 / {int(duration)//60}:{int(duration)%60:02d}
    </span>
    <span style="font-family:monospace; font-size:12px; color:#666;">
      (click timeline to seek)
    </span>
  </div>
</div>
<script>
(function() {{
  var aud = document.getElementById("aud_{widget_id}");
  var cur = document.getElementById("cur_{widget_id}");
  var img = document.getElementById("img_{widget_id}");
  var scroll = document.getElementById("scroll_{widget_id}");
  var btn = document.getElementById("btn_{widget_id}");
  var rst = document.getElementById("rst_{widget_id}");
  var seek = document.getElementById("seek_{widget_id}");
  var tmr = document.getElementById("time_{widget_id}");
  var dur = {duration};
  var lp = {left_pct};
  var rp = {right_pct};
  var raf;

  function pctFromTime(t) {{
    return lp + (t / dur) * (rp - lp);
  }}

  function fmtTime(s) {{
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ":" + (sec < 10 ? "0" : "") + sec;
  }}

  function updateDisplay(t) {{
    var p = pctFromTime(t);
    cur.style.left = p + "%";
    cur.style.display = "block";
    seek.value = t;
    tmr.textContent = fmtTime(t) + " / " + fmtTime(dur);
  }}

  function autoScroll() {{
    // Keep the cursor visible as playback advances
    var cursorPx = (pctFromTime(aud.currentTime) / 100) * img.offsetWidth;
    var viewLeft = scroll.scrollLeft;
    var viewRight = viewLeft + scroll.clientWidth;
    if (cursorPx < viewLeft + 50 || cursorPx > viewRight - 50) {{
      scroll.scrollLeft = Math.max(0, cursorPx - scroll.clientWidth / 2);
    }}
  }}

  function tick() {{
    if (!aud.paused) {{
      updateDisplay(aud.currentTime);
      autoScroll();
      raf = requestAnimationFrame(tick);
    }}
  }}

  btn.onclick = function() {{
    if (aud.paused) {{
      aud.play(); btn.textContent = "Pause";
      raf = requestAnimationFrame(tick);
    }} else {{
      aud.pause(); btn.textContent = "Play";
      cancelAnimationFrame(raf);
    }}
  }};

  rst.onclick = function() {{
    aud.pause();
    aud.currentTime = 0;
    btn.textContent = "Play";
    cur.style.display = "none";
    seek.value = 0;
    tmr.textContent = fmtTime(0) + " / " + fmtTime(dur);
    cancelAnimationFrame(raf);
    scroll.scrollLeft = 0;
  }};

  seek.oninput = function() {{
    var t = parseFloat(seek.value);
    aud.currentTime = t;
    updateDisplay(t);
  }};

  aud.onended = function() {{
    btn.textContent = "Play";
    cur.style.display = "none";
    cancelAnimationFrame(raf);
  }};

  img.onclick = function(e) {{
    var rect = img.getBoundingClientRect();
    var xPct = ((e.clientX - rect.left) / rect.width) * 100;
    if (xPct >= lp && xPct <= rp) {{
      var t = ((xPct - lp) / (rp - lp)) * dur;
      aud.currentTime = t;
      updateDisplay(t);
      if (aud.paused) {{
        aud.play(); btn.textContent = "Pause";
        raf = requestAnimationFrame(tick);
      }}
    }}
  }};
}})();
</script>"""
