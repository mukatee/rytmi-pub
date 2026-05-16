"""Render the unified-timeline panel for the Act 3a architectural-signature beat.

The unified timeline (`P1, T1, P2, T2, … P8`) interleaves the polished
`kizomba_tutor` phase lines (P#) with the `kizomba_transitions` boundary
lines (T#). It's the single most important visual in Act 3a — it
demonstrates the architectural argument:

    code identifies the boundaries → Gemma writes the lines → code
    verifies they cover the song.

This module renders the unified block as a 1920×1080 PNG panel matching
the rest of the deck. Two knobs let the orchestrator stage the beat:

- ``hide_transitions=True`` renders only the P# lines (T# hidden,
  vertical space *preserved* so the layout doesn't jump when T# fade
  in). Used for Stage A.
- ``pinned_caption=...`` overlays a violet banner near the bottom with
  the architectural-signature line. Used for Stage C.

The body is rendered in a lifted slate-800 rounded rect, just like
``make_notebook_panel``, so the panel reads as "verbatim notebook output"
to the audience.

Color coding: P# lines in slate-50 (FG), T# lines in violet-400 (ACCENT)
so the eye immediately separates the two scaffolds.

Re-renderable from caller scripts; line-list constants and per-stage
toggles are explicit at the call site, not hidden in this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# Project palette — must match make_caption_slide.py / make_notebook_panel.py.
BG = (15, 23, 42)              # slate-900
PANEL_BG = (30, 41, 59)        # slate-800
PANEL_BORDER = (51, 65, 85)    # slate-700
FG = (248, 250, 252)           # slate-50    — P# lines, headings
ACCENT = (167, 139, 250)       # violet-400  — T# lines, accent rule, pinned caption bar
ACCENT_DEEP = (124, 58, 237)   # violet-600  — caption banner background
MUTED = (148, 163, 184)        # slate-400   — footer
TAG_FG = (94, 234, 212)        # teal-300    — tag


_FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
_FONT_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
_FONT_MONO = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def _load_font(size: int, kind: str = "regular") -> ImageFont.FreeTypeFont:
    paths = {"regular": _FONT_REGULAR, "bold": _FONT_BOLD, "mono": _FONT_MONO}[kind]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


@dataclass(frozen=True)
class TimelineLine:
    """One line of the unified timeline.

    `kind` is "P" (phase) or "T" (transition). Used for color-coding
    and for the `hide_transitions` toggle.
    """
    kind: str
    text: str


def _wrap_mono_line(line: str, font: ImageFont.FreeTypeFont, max_w_px: int,
                    draw: ImageDraw.ImageDraw, indent: str = "    ") -> list[str]:
    """Word-wrap a single line; continuation lines are indented."""
    bbox = draw.textbbox((0, 0), line, font=font)
    if bbox[2] - bbox[0] <= max_w_px:
        return [line]
    words = line.split()
    if not words:
        return [line]
    out: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        cb = draw.textbbox((0, 0), candidate, font=font)
        if cb[2] - cb[0] <= max_w_px:
            current = candidate
        else:
            out.append(current)
            current = indent + word
    out.append(current)
    return out


def render_unified_timeline_panel(
    lines: list[TimelineLine],
    output: Path,
    *,
    heading: str = "Unified timeline — phases + transitions",
    tag: str | None = "[kizomba_tutor + kizomba_transitions]  Filomena – Teu Toque",
    cell_prompt: str | None = "In [14]:  format_unified_timeline(tutor, transitions)",
    footer: str = "notebooks/00_demo.ipynb · verbatim Gemma 4 output",
    hide_transitions: bool = False,
    pinned_caption: str | None = None,
    width: int = 1920,
    height: int = 1080,
    body_pt: int = 20,
    heading_pt: int = 40,
) -> None:
    """Render one frame of the unified-timeline beat.

    The vertical space for transition lines is *always reserved* — when
    `hide_transitions=True` those rows simply render as blank gaps so
    the layout doesn't shift between Stage A and Stage B (only the T
    text fades in via xfade at video stitch time).
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    margin_x = 100
    margin_top = 80

    heading_font = _load_font(heading_pt, "bold")
    cell_font = _load_font(20, "mono")
    tag_font = _load_font(24, "bold")
    body_font = _load_font(body_pt, "mono")
    footer_font = _load_font(20, "regular")
    caption_font = _load_font(34, "bold")

    y = margin_top

    if cell_prompt:
        draw.text((margin_x, y), cell_prompt, fill=MUTED, font=cell_font)
        y += 32

    draw.text((margin_x, y), heading, fill=FG, font=heading_font)
    y += heading_pt + 14

    draw.rectangle([(margin_x, y), (margin_x + 120, y + 4)], fill=ACCENT)
    y += 22

    if tag:
        draw.text((margin_x, y), tag, fill=TAG_FG, font=tag_font)
        y += 42

    body_inner_pad_x = 28
    body_inner_pad_y = 18
    body_max_w = width - 2 * margin_x - 2 * body_inner_pad_x

    # Wrap each line first so we know the final visual height.
    wrapped: list[tuple[str, list[str]]] = []
    for tl in lines:
        wrapped.append((tl.kind, _wrap_mono_line(tl.text, body_font, body_max_w, draw)))

    bbox = draw.textbbox((0, 0), "Hg", font=body_font)
    line_h = int((bbox[3] - bbox[1]) * 1.42)

    body_top = y
    total_visual_lines = sum(len(w) for _, w in wrapped)
    body_height = total_visual_lines * line_h + 2 * body_inner_pad_y

    draw.rounded_rectangle(
        [(margin_x - 20, body_top - 10),
         (width - margin_x + 20, body_top + body_height)],
        radius=14,
        fill=PANEL_BG,
        outline=PANEL_BORDER,
        width=2,
    )

    text_y = body_top + body_inner_pad_y
    for kind, sublines in wrapped:
        if kind == "T" and hide_transitions:
            # Reserve vertical space without drawing — keeps Stage A and
            # Stage B visually aligned.
            text_y += len(sublines) * line_h
            continue
        color = FG if kind == "P" else ACCENT
        for sl in sublines:
            draw.text((margin_x, text_y), sl, fill=color, font=body_font)
            text_y += line_h

    # Footer.
    footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    draw.text(
        ((width - footer_w) / 2, height - 50),
        footer,
        fill=MUTED,
        font=footer_font,
    )

    # Pinned caption banner (Stage C). Sits just above the footer so it
    # never overlaps the body panel's bottom rows.
    if pinned_caption:
        cap_bbox = draw.textbbox((0, 0), pinned_caption, font=caption_font)
        cap_w = cap_bbox[2] - cap_bbox[0]
        cap_h = cap_bbox[3] - cap_bbox[1]
        pad_x = 36
        pad_y = 18
        bx0 = (width - cap_w) / 2 - pad_x
        bx1 = (width + cap_w) / 2 + pad_x
        by0 = height - 50 - cap_h - 2 * pad_y - 24
        by1 = by0 + cap_h + 2 * pad_y
        draw.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=12, fill=ACCENT_DEEP)
        draw.text(((width - cap_w) / 2, by0 + pad_y - 4), pinned_caption,
                  fill=FG, font=caption_font)

    img.save(str(output), "PNG")
    print(f"wrote {output} ({width}x{height})  hide_transitions={hide_transitions}  "
          f"pinned_caption={'yes' if pinned_caption else 'no'}")
