"""Render `demo_assets/output/architecture.png` natively in matplotlib.

Replaces the dependency on Mermaid CLI for the Act 2 architecture beat —
no Node/npm needed. Layout mirrors the structure of
`demo_assets/diagrams/architecture.mmd` (kept around as the canonical
source-of-truth description) but is hand-laid here so it composes cleanly
into a 1920×1080 frame matching the project palette used by
`make_caption_slide.py` and `make_slide.py`.

Two flow lanes:

- **DSP lane (cyan-tinted):** audio → librosa DSP (beat tracking, HPSS,
  sections) and Demucs vocal stems → `RhythmAnalysis` dataclass.
- **LLM lane (violet-tinted):** `RhythmAnalysis` → prompt builder →
  Gemma 4 → verifier → coaching output. A dashed back-edge from the
  verifier to `RhythmAnalysis` shows the re-grounding step.

Style choices:

- Dark slate background matching the caption slides so the diagram cuts
  cleanly into the Act 2 video without a colour shift.
- DSP boxes filled cyan, LLM boxes filled violet, plain I/O boxes filled
  slate. Same hex values as the caption slide palette.
- Arrows use FancyArrowPatch with a soft slate stroke; the dashed
  re-grounding edge is the only visual departure to flag the loop.

Usage from repo root::

    .venv/bin/python demo_assets/scripts/make_architecture_diagram.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "demo_assets" / "output" / "architecture.png"

# Palette mirrors make_caption_slide.py / architecture.mmd.
BG = "#0f172a"          # slate-900
FG = "#f8fafc"          # slate-50
MUTED = "#94a3b8"       # slate-400
EDGE = "#64748b"        # slate-500
DSP_FILL = "#0e7490"    # cyan-700
DSP_EDGE = "#22d3ee"    # cyan-400
LLM_FILL = "#7c3aed"    # violet-600
LLM_EDGE = "#a78bfa"    # violet-400
IO_FILL = "#1e293b"     # slate-800
IO_EDGE = "#475569"     # slate-600

# Canvas: render at 1920×1080 (16:9) so the PNG drops into the act
# videos at native resolution. Use a 19.2 × 10.8 figure at 100 dpi.
FIG_W_IN = 19.2
FIG_H_IN = 10.8
DPI = 100


@dataclass(frozen=True)
class Box:
    """A rectangular labelled node in the diagram."""

    key: str
    cx: float        # centre x, in figure units (0..100)
    cy: float        # centre y, in figure units (0..100)
    w: float         # half-width
    h: float         # half-height
    title: str
    subtitle: str | None
    kind: str        # "dsp" | "llm" | "io"


# Layout grid is 0..100 horizontally, 0..100 vertically. The diagram flows
# left-to-right; vertical position separates the DSP sub-stages from the
# Demucs branch. Coordinates are in *data units*, NOT visually equal
# (16:9 canvas with auto aspect) — horizontal `w` is in % of width, vertical
# `h` is in % of height, so a `w=6` box and an `h=6` box look about the
# same on screen because the canvas is ~1.78× wider than tall.
BOXES: list[Box] = [
    Box("audio",   cx=6,  cy=46, w=5,   h=5.5,
        title="Audio file", subtitle="mp3 / wav", kind="io"),
    Box("dsp",     cx=22, cy=66, w=6.5, h=5.5,
        title="librosa DSP", subtitle=None, kind="dsp"),
    Box("beats",   cx=42, cy=82, w=8.5, h=5.5,
        title="beat tracking", subtitle="onsets · tempo · downbeat conf.", kind="dsp"),
    Box("hpss",    cx=42, cy=66, w=8.5, h=5.5,
        title="HPSS", subtitle="harmonic / percussive split", kind="dsp"),
    Box("sections",cx=42, cy=50, w=8.5, h=5.5,
        title="section structure", subtitle="energy · repetition · labels", kind="dsp"),
    Box("demucs",  cx=22, cy=26, w=6.5, h=5.5,
        title="Demucs", subtitle="vocal stems", kind="dsp"),
    Box("rhythm",  cx=63, cy=54, w=9, h=10,
        title="RhythmAnalysis",
        subtitle="phases · sections · beat-clarity\n+ tempo · downbeat conf.",
        kind="io"),
    Box("prompt",  cx=86, cy=82, w=8, h=5.5,
        title="Prompt builder", subtitle="style-aware · section-aware", kind="llm"),
    Box("gemma",   cx=86, cy=66, w=8, h=5.5,
        title="Gemma 4", subtitle="26B-A4B cloud or E4B local", kind="llm"),
    Box("verifier",cx=86, cy=50, w=8, h=5.5,
        title="Verifier", subtitle="re-grounds each line in DSP", kind="llm"),
    Box("output",  cx=86, cy=24, w=9, h=7,
        title="Coaching output",
        subtitle="tutor · drills · transitions\nunified timeline",
        kind="io"),
]
BOX_BY_KEY = {b.key: b for b in BOXES}

# Edges as (from_key, to_key, dashed?). Dashed edges flag dataflow that's
# a re-grounding loop rather than a forward production step.
EDGES: list[tuple[str, str, bool]] = [
    ("audio", "dsp", False),
    ("audio", "demucs", False),
    ("dsp", "beats", False),
    ("dsp", "hpss", False),
    ("dsp", "sections", False),
    ("demucs", "sections", False),     # vocal envelope feeds section labeller
    ("beats", "rhythm", False),
    ("hpss", "rhythm", False),
    ("sections", "rhythm", False),
    ("rhythm", "prompt", False),
    ("prompt", "gemma", False),
    ("gemma", "verifier", False),
    ("verifier", "output", False),
    ("rhythm", "verifier", True),      # re-grounding back-edge (dashed)
]


def _fill_for(kind: str) -> tuple[str, str]:
    if kind == "dsp":
        return DSP_FILL, DSP_EDGE
    if kind == "llm":
        return LLM_FILL, LLM_EDGE
    return IO_FILL, IO_EDGE


def _draw_box(ax: plt.Axes, box: Box) -> None:
    fill, edge = _fill_for(box.kind)
    rect = FancyBboxPatch(
        (box.cx - box.w, box.cy - box.h),
        2 * box.w,
        2 * box.h,
        boxstyle="round,pad=0.4,rounding_size=0.8",
        linewidth=2.2,
        facecolor=fill,
        edgecolor=edge,
        zorder=2,
    )
    ax.add_patch(rect)

    # Title (bold, near top of box) + optional subtitle (lighter, below).
    if box.subtitle:
        ax.text(
            box.cx, box.cy + box.h * 0.35, box.title,
            ha="center", va="center",
            fontsize=15, color=FG, fontweight="bold", zorder=3,
        )
        ax.text(
            box.cx, box.cy - box.h * 0.25, box.subtitle,
            ha="center", va="center",
            fontsize=11, color=FG, alpha=0.85, zorder=3,
        )
    else:
        ax.text(
            box.cx, box.cy, box.title,
            ha="center", va="center",
            fontsize=16, color=FG, fontweight="bold", zorder=3,
        )


def _edge_anchor(src: Box, dst: Box) -> tuple[tuple[float, float], tuple[float, float]]:
    """Pick anchor points on the box borders that face each other.

    Simple heuristic: choose the side based on the dominant axis of the
    centre-to-centre vector. Avoids arrows piercing through other boxes
    in the layouts used here.
    """
    dx = dst.cx - src.cx
    dy = dst.cy - src.cy
    if abs(dx) >= abs(dy):
        # Horizontal-dominant: use right/left sides.
        if dx >= 0:
            return ((src.cx + src.w, src.cy), (dst.cx - dst.w, dst.cy))
        return ((src.cx - src.w, src.cy), (dst.cx + dst.w, dst.cy))
    # Vertical-dominant: use top/bottom sides.
    if dy >= 0:
        return ((src.cx, src.cy + src.h), (dst.cx, dst.cy - dst.h))
    return ((src.cx, src.cy - src.h), (dst.cx, dst.cy + dst.h))


def _draw_edge(ax: plt.Axes, src: Box, dst: Box, dashed: bool) -> None:
    start, end = _edge_anchor(src, dst)
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=1.8,
        color=EDGE,
        linestyle=(0, (4, 3)) if dashed else "solid",
        zorder=1,
        shrinkA=2, shrinkB=2,
    )
    ax.add_patch(arrow)


def _draw_legend(ax: plt.Axes) -> None:
    """Tiny inline legend so DSP / LLM / I/O colour mapping is unambiguous."""
    items: list[tuple[str, str, str, bool]] = [
        ("DSP (librosa, Demucs)", DSP_FILL, DSP_EDGE, False),
        ("LLM (Gemma 4 + verifier)", LLM_FILL, LLM_EDGE, False),
        ("Data / output", IO_FILL, IO_EDGE, False),
        ("verifier re-grounds in DSP", BG, EDGE, True),
    ]
    # Right-anchor the legend in the figure footer band.
    y0 = 4
    sw = 2.6  # swatch width in data units
    sh = 2.4
    label_pad = 1.0
    item_gap = 1.5

    # Pre-measure label widths in *data units* by approximating font width.
    # 1 fontsize-12 char ≈ 0.55 data units wide on this 100-wide canvas at
    # 1920×1080 — close enough for layout. Using 0.7 as a safe upper bound.
    char_w = 0.7
    widths = [sw + label_pad + len(label) * char_w for label, *_ in items]
    total_w = sum(widths) + item_gap * (len(items) - 1)
    x = (100 - total_w) / 2
    for i, (label, fill, edge, dashed) in enumerate(items):
        if dashed:
            ax.plot([x, x + sw], [y0 + sh / 2, y0 + sh / 2],
                    color=edge, linestyle=(0, (4, 3)), linewidth=2.0, zorder=2)
        else:
            rect = FancyBboxPatch(
                (x, y0), sw, sh,
                boxstyle="round,pad=0.05,rounding_size=0.4",
                linewidth=1.5, facecolor=fill, edgecolor=edge, zorder=2,
            )
            ax.add_patch(rect)
        ax.text(x + sw + label_pad, y0 + sh / 2, label,
                ha="left", va="center", fontsize=12, color=FG, zorder=3)
        x += widths[i] + item_gap


def render(output_path: Path = OUTPUT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    # Deliberately *not* set_aspect("equal") — we want data units to fill
    # the 16:9 canvas. Box `w` and `h` are tuned per-axis so visual sizes
    # look balanced despite the unequal aspect.
    ax.axis("off")
    # Tight layout area within the figure (no margins around the axes).
    ax.set_position((0.0, 0.0, 1.0, 1.0))

    # Title at the top — keeps the slide self-explanatory if shown standalone.
    ax.text(50, 95, "Rytmi — DSP listens, Gemma 4 talks",
            ha="center", va="center",
            fontsize=22, color=FG, fontweight="bold")
    ax.text(50, 90.5, "audio → analysis → prompt → coaching, with the verifier looping back to the analysis",
            ha="center", va="center",
            fontsize=13, color=MUTED)

    for src_key, dst_key, dashed in EDGES:
        _draw_edge(ax, BOX_BY_KEY[src_key], BOX_BY_KEY[dst_key], dashed)
    for box in BOXES:
        _draw_box(ax, box)

    # Lane labels (clarity pass #5) — cyan "DSP" above the left lane,
    # violet "Gemma 4" above the right lane. Makes the diagram
    # self-attribute the two halves even in a single-frame screenshot,
    # without renaming the inner "librosa DSP" / "Gemma 4" boxes.
    ax.text(
        22, 87.5, "DSP",
        ha="center", va="center",
        fontsize=20, color=DSP_EDGE, fontweight="bold", alpha=0.9,
    )
    ax.text(
        86, 92, "Gemma 4",
        ha="center", va="center",
        fontsize=20, color=LLM_EDGE, fontweight="bold", alpha=0.9,
    )

    _draw_legend(ax)

    fig.savefig(output_path, dpi=DPI, facecolor=BG, bbox_inches=None,
                pad_inches=0)
    plt.close(fig)
    print(f"wrote {output_path} ({int(FIG_W_IN * DPI)}x{int(FIG_H_IN * DPI)})")


if __name__ == "__main__":
    render()
