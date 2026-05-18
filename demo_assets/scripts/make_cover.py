"""Build cover-image candidates for the Kaggle submission + demo video.

Replaces the "nerd-boring" architecture diagram as the project's face. The
cover pairs the project's *real* signature artifact — the rendered E Magia
vocal-break transition waveform (real samples, real section bands, real
transition marker) — re-themed dark and glowing, with a backlit kizomba
silhouette and the verbatim Gemma coaching line for that exact moment.

Honest by construction: every waveform sample, the section boundary at
165 s, and the coaching text are the actual pipeline output for
Charbel — E Magia, just rendered at poster grade instead of notebook grade.

    .venv/bin/python demo_assets/scripts/make_cover.py

Outputs PNGs to demo_assets/cover_candidates/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from rytmi.viz import SECTION_COLORS  # noqa: E402
import analysis_cache  # noqa: E402

SONG = ROOT / "data/songs/eval_set/kizomba/Charbel_-_E_Magia_Official_Video_4K [QkfyDj8aJRM].mp3"
SILHOUETTE = ROOT / "kizomba-silhouettes/Backlit silhouette of a kizomba couple dancing in close embr (4).jpg"
OUT_DIR = ROOT / "demo_assets/cover_candidates"

WIN_START, WIN_END = 159.0, 173.0
TRANSITION_T = 165.0  # T5 main -> break

DSP_LINE = "T5 · 165s · main → break · beat: clear → moderate"
GEMMA_LINE = "as the energy fades and the percussion thins,\nkeep a small pulse in the body and listen."

WAVE_GLOW = "#22d3ee"   # cyan-300 — the luminous trace
WAVE_CORE = "#e0fbff"   # near-white core
MARKER = "#f472b6"      # pink-400 — the transition
TEAL = "#5eead4"        # Rytmi DSP provenance
VIOLET = "#a78bfa"      # Gemma 4 provenance
INK = "#07060a"         # canvas near-black
INK_RGB = (7 / 255, 6 / 255, 10 / 255)

STROKE = [pe.withStroke(linewidth=3, foreground=INK)]


def load_window():
    payload = analysis_cache.load(SONG, "kizomba")
    if payload is None:
        raise SystemExit(
            "No cached analysis for E Magia. Run make_all_demo_videos.py first "
            "to populate data/_analysis_cache/."
        )
    audio, analysis = payload
    sr = audio.sr
    s0, s1 = int(WIN_START * sr), int(WIN_END * sr)
    samples = np.asarray(audio.samples[s0:s1], dtype=float)
    t = WIN_START + np.arange(len(samples)) / sr
    peak = float(np.max(np.abs(samples))) or 1.0
    samples = samples / peak
    phases = [
        p for p in (getattr(analysis, "phases", None) or [])
        if p.end_s > WIN_START and p.start_s < WIN_END
    ]
    return t, samples, phases


def _ink_grad(ax, extent, where, *, amax=1.0, n=256):
    """Smooth INK alpha gradient (no colormap → no grey slab artifacts).

    ``where`` ∈ {'bottom','top','left'}: the dark end of the ramp.
    """
    if where in ("bottom", "top"):
        a = np.linspace(amax, 0.0, n)
        if where == "top":
            a = a[::-1]
        rgba = np.zeros((n, 2, 4))
        rgba[..., :3] = INK_RGB
        rgba[..., 3] = a[:, None]
    else:  # left
        a = np.linspace(amax, 0.0, n)
        rgba = np.zeros((2, n, 4))
        rgba[..., :3] = INK_RGB
        rgba[..., 3] = a[None, :]
    ax.imshow(rgba, extent=extent, origin="lower", aspect="auto", zorder=10)


def draw_waveform(ax, t, samples, phases, *, band_alpha=0.16, lw_scale=1.0):
    """Glowing waveform on a transparent axes. No ticks, spines, or labels."""
    ax.set_xlim(WIN_START, WIN_END)
    ax.set_ylim(-1.35, 1.35)
    ax.set_facecolor("none")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    for ph in phases:
        c = SECTION_COLORS.get(ph.label, "#888")
        ax.axvspan(max(ph.start_s, WIN_START), min(ph.end_s, WIN_END),
                   color=c, alpha=band_alpha, zorder=0, linewidth=0)

    for lw, a in [(11, 0.06), (7, 0.10), (4, 0.18), (2.2, 0.35)]:
        ax.fill_between(t, samples, -samples, color=WAVE_GLOW,
                        alpha=a * 0.5, linewidth=0, zorder=2)
        ax.plot(t, samples, color=WAVE_GLOW, lw=lw * lw_scale,
                alpha=a, solid_capstyle="round", zorder=3)
    ax.plot(t, samples, color=WAVE_CORE, lw=0.7 * lw_scale,
            alpha=0.9, zorder=4)

    for lw, a in [(14, 0.10), (7, 0.18), (3, 0.5)]:
        ax.axvline(TRANSITION_T, color=MARKER, lw=lw, alpha=a, zorder=5)
    ax.axvline(TRANSITION_T, color="#ffe3f1", lw=1.0, alpha=0.95, zorder=6)


def _silhouette():
    return mpimg.imread(str(SILHOUETTE))


def _title_block(fig, x, y, *, big=64, sub=30, ha="left", gap=0.082):
    fig.text(x, y, "Rytmi", fontsize=big, fontweight="bold", color="white",
             ha=ha, va="top", family="DejaVu Sans",
             path_effects=[pe.withStroke(linewidth=5, foreground=INK)])
    fig.text(x, y - gap, "Hear the Beat, Feel the Song", fontsize=sub,
             color="#e6edf3", ha=ha, va="top", family="DejaVu Sans",
             path_effects=STROKE)


def _caption_two_tone(fig, cx, y, *, scale=1.0):
    """Centered two-tone provenance caption: teal DSP chip + violet Gemma."""
    fig.text(cx, y + 0.075, DSP_LINE, fontsize=15 * scale, color=TEAL,
             ha="center", va="center", family="DejaVu Sans",
             fontweight="bold", path_effects=STROKE)
    fig.text(cx, y, f"“{GEMMA_LINE}”", fontsize=22 * scale, color="white",
             ha="center", va="center", family="DejaVu Sans",
             linespacing=1.4, fontstyle="italic",
             path_effects=[pe.withStroke(linewidth=4, foreground=INK)])
    fig.text(cx, y - 0.072, "Gemma 4 — coaching this exact moment",
             fontsize=13 * scale, color=VIOLET, ha="center", va="center",
             family="DejaVu Sans", fontweight="bold", path_effects=STROKE)


def candidate_A():
    """Landscape poster — silhouette right on an ink panel, title left."""
    t, s, ph = load_window()
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(INK)

    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    bg.set_facecolor(INK)
    img = _silhouette()
    bg.imshow(img, extent=[0.44, 1.02, 0.0, 1.0], aspect="auto", zorder=0)
    # Smooth seam: ink fades in from the image's left edge leftward.
    _ink_grad(bg, [0.40, 0.70, 0, 1], "left", amax=1.0)

    wave = fig.add_axes([0.0, 0.30, 1.0, 0.40])
    draw_waveform(wave, t, s, ph, band_alpha=0.12, lw_scale=1.0)
    wave.patch.set_alpha(0)

    _title_block(fig, 0.05, 0.95, big=84, sub=33, gap=0.105)
    fig.text(0.05, 0.205,
             "DSP listens honestly · Gemma 4 turns it\ninto something you can move to",
             fontsize=19, color="#aab4c0", ha="left", va="top",
             family="DejaVu Sans", linespacing=1.45, path_effects=STROKE)

    # Bottom scrim so the caption reads over wave + silhouette legs.
    sc = fig.add_axes([0, 0, 1, 0.30]); sc.axis("off")
    sc.set_xlim(0, 1); sc.set_ylim(0, 1)
    _ink_grad(sc, [0, 1, 0, 1], "bottom", amax=0.92)
    _caption_two_tone(fig, 0.55, 0.115, scale=1.05)
    fig.text(0.985, 0.028, "Gemma 4 Good Hackathon", fontsize=13,
             color="#6b7480", ha="right", va="bottom", family="DejaVu Sans")

    out = OUT_DIR / "cover_A_poster.png"
    fig.savefig(out, dpi=100, facecolor=INK)
    plt.close(fig)
    return out


def candidate_B():
    """Square — silhouette centered with full halo, waveform as the floor."""
    t, s, ph = load_window()
    fig = plt.figure(figsize=(14, 14), dpi=100)
    fig.patch.set_facecolor(INK)

    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    img = _silhouette()
    bg.imshow(img, extent=[0.04, 0.96, 0.15, 1.0], aspect="auto", zorder=0)

    wave = fig.add_axes([0.0, 0.13, 1.0, 0.24])
    draw_waveform(wave, t, s, ph, band_alpha=0.18, lw_scale=1.1)
    wave.patch.set_alpha(0)

    # Scrim across the lower third behind the caption.
    sc = fig.add_axes([0, 0, 1, 0.30]); sc.axis("off")
    sc.set_xlim(0, 1); sc.set_ylim(0, 1)
    _ink_grad(sc, [0, 1, 0, 1], "bottom", amax=0.93)

    _title_block(fig, 0.5, 0.965, big=78, sub=33, ha="center")
    _caption_two_tone(fig, 0.5, 0.105, scale=1.12)

    out = OUT_DIR / "cover_B_square.png"
    fig.savefig(out, dpi=100, facecolor=INK)
    plt.close(fig)
    return out


def candidate_C():
    """Landscape minimal — full-bleed silhouette (heads kept), wave + line.

    No big title: leaves Kaggle / YouTube free to overlay their own.
    """
    t, s, ph = load_window()
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(INK)

    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    img = _silhouette()
    h, w = img.shape[:2]
    # 16:9 from a 1:1 source — crop the FLOOR, keep the heads + halo.
    crop_h = int(w * 9 / 16)
    bg.imshow(img[0:crop_h], extent=[0, 1, 0, 1], aspect="auto", zorder=0)
    # Gentle global darken so the glow doesn't blow out the text.
    dk = np.zeros((2, 2, 4)); dk[..., 3] = 0.30
    dk[..., :3] = INK_RGB
    bg.imshow(dk, extent=[0, 1, 0, 1], aspect="auto", zorder=1)

    wave = fig.add_axes([0.0, 0.30, 1.0, 0.30])
    draw_waveform(wave, t, s, ph, band_alpha=0.10, lw_scale=1.0)
    wave.patch.set_alpha(0)

    sc = fig.add_axes([0, 0, 1, 0.32]); sc.axis("off")
    sc.set_xlim(0, 1); sc.set_ylim(0, 1)
    _ink_grad(sc, [0, 1, 0, 1], "bottom", amax=0.90)

    fig.text(0.5, 0.155, f"“{GEMMA_LINE}”", fontsize=27, color="white",
             ha="center", va="center", family="DejaVu Sans",
             fontstyle="italic", linespacing=1.4,
             path_effects=[pe.withStroke(linewidth=4, foreground=INK)])
    fig.text(0.5, 0.06,
             "Rytmi  ·  Gemma 4 names the moment, code finds the beat",
             fontsize=15, color=VIOLET, ha="center", va="center",
             family="DejaVu Sans", fontweight="bold", path_effects=STROKE)

    out = OUT_DIR / "cover_C_minimal.png"
    fig.savefig(out, dpi=100, facecolor=INK)
    plt.close(fig)
    return out


def candidate_video():
    """16:9 video cover — the *video* title ("Help Me Hear the Song").

    Same visual language as the chosen square cover (centered silhouette +
    halo, waveform as a floor of light, the verbatim Gemma line) but in the
    YouTube/landscape form factor and fronted by the video title rather than
    the writeup title. Big, high-contrast type so it survives thumbnail size.
    """
    t, s, ph = load_window()
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(INK)

    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    bg.set_facecolor(INK)
    img = _silhouette()
    # Square source kept un-stretched, scaled large and dropped slightly so
    # the heads clear the title band. The source's top corners are pure
    # black, so the vertical edges blend into the ink with no seam — no
    # side gradient needed (that was causing faint banding).
    hfrac = 1.06
    wfrac = hfrac * (10.8 / 19.2)  # equal pixels both ways → no distortion
    x0 = 0.5 - wfrac / 2
    bg.imshow(img, extent=[x0, x0 + wfrac, -0.13, hfrac - 0.13],
              aspect="auto", zorder=0)

    wave = fig.add_axes([0.0, 0.16, 1.0, 0.26])
    draw_waveform(wave, t, s, ph, band_alpha=0.11, lw_scale=1.0)
    wave.patch.set_alpha(0)

    # Title block — video title is the hero; "Rytmi" is the eyebrow.
    fig.text(0.5, 0.965, "R Y T M I", fontsize=30, fontweight="bold",
             color=TEAL, ha="center", va="top", family="DejaVu Sans",
             path_effects=STROKE)
    fig.text(0.5, 0.93, "Help Me Hear the Song", fontsize=82,
             fontweight="bold", color="white", ha="center", va="top",
             family="DejaVu Sans",
             path_effects=[pe.withStroke(linewidth=7, foreground=INK)])

    sc = fig.add_axes([0, 0, 1, 0.26]); sc.axis("off")
    sc.set_xlim(0, 1); sc.set_ylim(0, 1)
    _ink_grad(sc, [0, 1, 0, 1], "bottom", amax=0.92)

    fig.text(0.5, 0.115, f"“{GEMMA_LINE}”", fontsize=24, color="white",
             ha="center", va="center", family="DejaVu Sans",
             fontstyle="italic", linespacing=1.4,
             path_effects=[pe.withStroke(linewidth=4, foreground=INK)])
    fig.text(0.5, 0.038,
             "Gemma 4 names the moment · code finds the beat",
             fontsize=15, color=VIOLET, ha="center", va="center",
             family="DejaVu Sans", fontweight="bold", path_effects=STROKE)

    out = OUT_DIR / "cover_video_help_me_hear.png"
    fig.savefig(out, dpi=100, facecolor=INK)
    plt.close(fig)
    return out


def candidate_card():
    """Kaggle submission card/thumbnail — exactly 560×280 (2:1).

    Tiny target: the two-tone provenance caption is illegible here, so this
    is the minimal cut — couple + halo right, big title left, the waveform
    glowing across as the floor. Rendered at 4× then Lanczos-downsampled to
    exactly 560×280 so the type stays crisp at thumbnail size.
    """
    from PIL import Image  # local: only this candidate needs a resize

    t, s, ph = load_window()
    fig = plt.figure(figsize=(5.6, 2.8), dpi=400)  # 4× → 2240×1120
    fig.patch.set_facecolor(INK)

    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    bg.set_facecolor(INK)
    img = _silhouette()
    # Square at full height on the right half; left half is title space.
    hfrac = 1.18
    wfrac = hfrac * (2.8 / 5.6)  # square, no distortion
    x0 = 1.0 - wfrac + 0.02
    bg.imshow(img, extent=[x0, x0 + wfrac, -0.12, hfrac - 0.12],
              aspect="auto", zorder=0)
    _ink_grad(bg, [x0 - 0.10, x0 + 0.14, 0, 1], "left", amax=1.0)

    wave = fig.add_axes([0.0, 0.28, 1.0, 0.40])
    draw_waveform(wave, t, s, ph, band_alpha=0.11, lw_scale=0.7)
    wave.patch.set_alpha(0)

    fig.text(0.045, 0.90, "Rytmi", fontsize=58, fontweight="bold",
             color="white", ha="left", va="top", family="DejaVu Sans",
             path_effects=[pe.withStroke(linewidth=4, foreground=INK)])
    fig.text(0.05, 0.55, "Hear the Beat,\nFeel the Song", fontsize=27,
             color="#e6edf3", ha="left", va="top", family="DejaVu Sans",
             linespacing=1.25,
             path_effects=[pe.withStroke(linewidth=3, foreground=INK)])
    fig.text(0.05, 0.07, "DSP listens · Gemma 4 coaches",
             fontsize=13, color=TEAL, ha="left", va="bottom",
             family="DejaVu Sans", fontweight="bold", path_effects=STROKE)

    big = OUT_DIR / "_card_4x.png"
    fig.savefig(big, dpi=400, facecolor=INK)
    plt.close(fig)

    out = OUT_DIR / "cover_card_560x280.png"
    Image.open(big).convert("RGB").resize((560, 280), Image.LANCZOS).save(out)
    big.unlink(missing_ok=True)
    return out


def candidate_card_dual():
    """560×280 Kaggle card engineered for a crop-safe square thumbnail.

    Kaggle then makes you pick a SQUARE region of the card for the
    thumbnail. So nothing may straddle the midline: the full title lockup
    lives entirely inside the LEFT 280×280 square, the couple + halo lives
    entirely inside the RIGHT 280×280 square, the waveform glows across
    both (atmosphere, crop-agnostic). Result — three clean choices from
    one card:

      • left square  → title lockup thumbnail
      • right square → couple thumbnail
      • full card    → the 560×280 banner

    Emits the card plus the three 280×280 crop previews so the actual
    thumbnail each selection yields is visible without guessing.
    """
    from PIL import Image

    t, s, ph = load_window()
    fig = plt.figure(figsize=(5.6, 2.8), dpi=400)  # 4× → 2240×1120
    fig.patch.set_facecolor(INK)

    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    bg.set_facecolor(INK)
    img = _silhouette()
    # Couple square: fully inside the RIGHT half (x ∈ [0.5, 1.0]).
    # Square source, un-stretched, centered on the right square's centre.
    hpx = 1.04 * 280  # display height in card px
    wfrac = (hpx / 560)
    cx = 0.75
    bg.imshow(img, extent=[cx - wfrac / 2, cx + wfrac / 2, -0.04, 1.0],
              aspect="auto", zorder=0)
    # Feather the couple's left edge so it never bleeds into the title
    # square even if the user's crop drifts a few px past the midline.
    _ink_grad(bg, [0.42, 0.56, 0, 1], "left", amax=1.0)

    wave = fig.add_axes([0.0, 0.0, 1.0, 0.30])
    draw_waveform(wave, t, s, ph, band_alpha=0.10, lw_scale=0.7)
    wave.patch.set_alpha(0)

    # Title lockup — centred in the LEFT square (x≈0.25). Sizes chosen so
    # the WIDEST line ("Feel the Song") clears the 280-px square with
    # margin, so a left-square crop frames the whole lockup cleanly and
    # nothing crosses the x=0.5 midline into the couple square.
    fig.text(0.25, 0.80, "Rytmi", fontsize=44, fontweight="bold",
             color="white", ha="center", va="center", family="DejaVu Sans",
             path_effects=[pe.withStroke(linewidth=4, foreground=INK)])
    fig.text(0.25, 0.50, "Hear the Beat,\nFeel the Song", fontsize=21,
             color="#e6edf3", ha="center", va="center", family="DejaVu Sans",
             linespacing=1.3,
             path_effects=[pe.withStroke(linewidth=3, foreground=INK)])
    fig.text(0.25, 0.20, "DSP + Gemma 4", fontsize=14, color=TEAL,
             ha="center", va="center", family="DejaVu Sans",
             fontweight="bold", path_effects=STROKE)

    big = OUT_DIR / "_carddual_4x.png"
    fig.savefig(big, dpi=400, facecolor=INK)
    plt.close(fig)

    card = OUT_DIR / "cover_card_dual_560x280.png"
    im = Image.open(big).convert("RGB").resize((560, 280), Image.LANCZOS)
    im.save(card)
    big.unlink(missing_ok=True)

    # 280×280 crop previews: left (title) / center / right (couple).
    crops = {
        "left_title": (0, 0, 280, 280),
        "center": (140, 0, 420, 280),
        "right_couple": (280, 0, 560, 280),
    }
    for name, box in crops.items():
        im.crop(box).save(OUT_DIR / f"cover_card_dual_crop_{name}.png")
    return card


def candidate_card_story(short: bool = False, *, airy: bool = False):
    """Trial: right square carries the *story* (Gemma coaching + a DSP line)
    instead of the left carrying tool names.

    Left square = title lockup only. Right square = couple + halo +
    waveform, with the verbatim Gemma coaching quote sitting just above a
    short DSP attribution line — so the right-square thumbnail reads as
    "the waveform is DSP, the words are Gemma, the couple is the why",
    not "DSP + Gemma 4". ``short=True`` uses a punchier one-line coaching
    fragment that survives tiny grid sizes; ``short=False`` keeps the full
    two-line quote (richer, but small at thumbnail scale).
    """
    from PIL import Image

    t, s, ph = load_window()
    fig = plt.figure(figsize=(5.6, 2.8), dpi=400)
    fig.patch.set_facecolor(INK)

    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.set_xlim(0, 1); bg.set_ylim(0, 1)
    bg.set_facecolor(INK)
    img = _silhouette()
    hpx = 1.04 * 280
    wfrac = hpx / 560
    cx = 0.75
    bg.imshow(img, extent=[cx - wfrac / 2, cx + wfrac / 2, -0.04, 1.0],
              aspect="auto", zorder=0)
    _ink_grad(bg, [0.42, 0.56, 0, 1], "left", amax=1.0)

    wave = fig.add_axes([0.0, 0.0, 1.0, 0.30])
    draw_waveform(wave, t, s, ph, band_alpha=0.10, lw_scale=0.7)
    wave.patch.set_alpha(0)

    # ``airy``: let the pulse/couple read through — much lighter scrim,
    # semi-transparent text, and a thin soft halo instead of a hard ink
    # outline (the hard stroke was acting like a slab over the waveform).
    scrim_amax = 0.40 if airy else 0.90
    txt_alpha = 0.86 if airy else 1.0
    if airy:
        story_stroke = [pe.withStroke(linewidth=2.2,
                                      foreground=(0, 0, 0, 0.45))]
    else:
        story_stroke = [pe.withStroke(linewidth=3, foreground=INK)]

    # Bottom scrim on the RIGHT half only, so the story text reads over
    # the couple's lower body / waveform without dimming the embrace.
    sc = fig.add_axes([0.5, 0.0, 0.5, 0.40]); sc.axis("off")
    sc.set_xlim(0, 1); sc.set_ylim(0, 1)
    _ink_grad(sc, [0, 1, 0, 1], "bottom", amax=scrim_amax)

    # Left square: title only (no tool-name tag in this variant).
    fig.text(0.25, 0.72, "Rytmi", fontsize=46, fontweight="bold",
             color="white", ha="center", va="center", family="DejaVu Sans",
             path_effects=[pe.withStroke(linewidth=4, foreground=INK)])
    fig.text(0.25, 0.40, "Hear the Beat,\nFeel the Song", fontsize=22,
             color="#e6edf3", ha="center", va="center", family="DejaVu Sans",
             linespacing=1.3,
             path_effects=[pe.withStroke(linewidth=3, foreground=INK)])

    # Right square: Gemma coaching just above a short DSP line.
    if short:
        coaching = "“keep a small pulse\nin the body, and listen.”"
        c_fs, c_y = 16, 0.27
    else:
        coaching = ("“as the energy fades and\n"
                    "the percussion thins, keep a\n"
                    "small pulse in the body, listen.”")
        c_fs, c_y = 12.5, 0.27
    fig.text(0.75, c_y, coaching, fontsize=c_fs, color="white",
             ha="center", va="center", family="DejaVu Sans",
             fontstyle="italic", linespacing=1.3, alpha=txt_alpha,
             path_effects=story_stroke)
    fig.text(0.75, 0.075, "DSP · 165s  main → break", fontsize=11.5,
             color=TEAL, ha="center", va="center", family="DejaVu Sans",
             fontweight="bold", alpha=txt_alpha, path_effects=story_stroke)

    tag = "short" if short else "full"
    if airy:
        tag += "_airy"
    big = OUT_DIR / f"_cardstory_{tag}_4x.png"
    fig.savefig(big, dpi=400, facecolor=INK)
    plt.close(fig)

    card = OUT_DIR / f"cover_card_story_{tag}_560x280.png"
    im = Image.open(big).convert("RGB").resize((560, 280), Image.LANCZOS)
    im.save(card)
    big.unlink(missing_ok=True)
    im.crop((280, 0, 560, 280)).save(
        OUT_DIR / f"cover_card_story_{tag}_crop_right.png")
    im.crop((0, 0, 280, 280)).save(
        OUT_DIR / f"cover_card_story_{tag}_crop_left.png")
    return card


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for fn in (candidate_A, candidate_B, candidate_C, candidate_video,
               candidate_card, candidate_card_dual,
               lambda: candidate_card_story(short=False),
               lambda: candidate_card_story(short=True),
               lambda: candidate_card_story(short=True, airy=True)):
        out = fn()
        print(f"  wrote {out.relative_to(ROOT)}  "
              f"({out.stat().st_size / 1024:.0f} KB)")
    print(f"\nCandidates in {OUT_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
