"""Render a 1920×1080 caption slide for the act videos.

Distinct from `make_slide.py` (project-name / divider style with big title +
subtitle + accent bar). This is for **in-act caption beats** that hold a
single sentence or two over a dark background while audio or other visuals
play underneath. Shares the project palette so the deck reads as one piece.

Used by `make_act1_video.py` (and intended for Act 2 / Close when those
are built). Each slide carries:

- a primary line (the headline caption — bold, large)
- an optional secondary line (continuation or subordinate detail — lighter)
- an optional small footer (e.g. the source song attribution while audio
  plays, so viewers know what they're hearing)

Word-wraps the primary/secondary lines to a max width and centres them
vertically as a block. Keeps the dark theme and accent palette from
`make_slide.py`.

Example::

    python demo_assets/scripts/make_caption_slide.py \\
        --primary "I wanted to hear the beat." \\
        --secondary "It kept slipping." \\
        --footer "Filomena Maricoa — Teu Toque" \\
        --output demo_assets/output/act1_caption1.png
"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# Project palette — mirrors make_slide.py / diagrams/architecture.mmd.
BG = (15, 23, 42)              # slate-900
FG = (248, 250, 252)           # slate-50
ACCENT = (167, 139, 250)       # violet-400
MUTED = (148, 163, 184)        # slate-400


_FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]
_FONT_REGULAR_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/Library/Fonts/Arial.ttf",
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in _FONT_BOLD_CANDIDATES if bold else _FONT_REGULAR_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _wrap_to_width(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width_px: int,
    draw: ImageDraw.ImageDraw,
) -> list[str]:
    """Greedy word-wrap that respects pixel width (not just char count)."""
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width_px:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _draw_block_centered(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    canvas_width: int,
    top_y: int,
    line_spacing: float = 1.25,
    align: str = "center",
) -> int:
    """Draw `lines` centred horizontally, top-anchored at `top_y`.

    Returns the y coordinate just below the rendered block so the caller
    can stack additional content underneath. When ``align='left'``, each
    line shares the left edge of the widest line, and the whole block is
    centred horizontally as a unit (used for bullet lists so wrapped
    continuation text doesn't float mid-canvas).
    """
    bbox = draw.textbbox((0, 0), "Hg", font=font)
    line_h = int((bbox[3] - bbox[1]) * line_spacing)
    if align == "left":
        block_w = 0
        for line in lines:
            lb = draw.textbbox((0, 0), line, font=font)
            block_w = max(block_w, lb[2] - lb[0])
        left_x = (canvas_width - block_w) // 2
        y = top_y
        for line in lines:
            draw.text((left_x, y), line, fill=fill, font=font)
            y += line_h
        return y
    y = top_y
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        draw.text(((canvas_width - line_w) / 2, y), line, fill=fill, font=font)
        y += line_h
    return y


def render_caption_slide(
    primary: str,
    secondary: str | None,
    footer: str | None,
    output: Path,
    width: int = 1920,
    height: int = 1080,
    *,
    primary_pt: int = 84,
    secondary_pt: int = 52,
    footer_pt: int = 32,
    show_accent_bar: bool = True,
    secondary_align: str = "center",
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    primary_font = _load_font(primary_pt, bold=True)
    secondary_font = _load_font(secondary_pt, bold=False)
    footer_font = _load_font(footer_pt, bold=False)

    text_max_w = int(width * 0.78)

    primary_lines = _wrap_to_width(primary, primary_font, text_max_w, draw)
    # Honor explicit newlines in `secondary` (used for bullet lists on the
    # close slide). Each pre-split line is independently word-wrapped.
    secondary_lines: list[str] = []
    if secondary:
        for raw_line in secondary.split("\n"):
            secondary_lines.extend(
                _wrap_to_width(raw_line, secondary_font, text_max_w, draw)
            )

    # Estimate total block height to vertically centre.
    p_bbox = draw.textbbox((0, 0), "Hg", font=primary_font)
    p_line_h = int((p_bbox[3] - p_bbox[1]) * 1.25)
    s_bbox = draw.textbbox((0, 0), "Hg", font=secondary_font)
    s_line_h = int((s_bbox[3] - s_bbox[1]) * 1.25)
    accent_block = 60 if (show_accent_bar and secondary_lines) else 0

    block_h = (
        len(primary_lines) * p_line_h
        + accent_block
        + len(secondary_lines) * s_line_h
    )
    top_y = (height - block_h) // 2

    after_primary_y = _draw_block_centered(
        draw, primary_lines, primary_font, FG, width, top_y
    )

    if secondary_lines and show_accent_bar:
        bar_y = after_primary_y + 18
        draw.rectangle(
            [(width // 2 - 60, bar_y), (width // 2 + 60, bar_y + 4)],
            fill=ACCENT,
        )
        after_primary_y = bar_y + 38

    if secondary_lines:
        _draw_block_centered(
            draw,
            secondary_lines,
            secondary_font,
            MUTED,
            width,
            after_primary_y,
            align=secondary_align,
        )

    if footer:
        footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
        footer_h = footer_bbox[3] - footer_bbox[1]
        footer_w = footer_bbox[2] - footer_bbox[0]
        draw.text(
            ((width - footer_w) / 2, height - 70 - footer_h),
            footer,
            fill=MUTED,
            font=footer_font,
        )

    img.save(str(output), "PNG")
    print(f"wrote {output} ({width}x{height})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--primary", required=True)
    p.add_argument("--secondary", default=None)
    p.add_argument("--footer", default=None)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--primary-pt", type=int, default=84)
    p.add_argument("--secondary-pt", type=int, default=52)
    args = p.parse_args()
    render_caption_slide(
        args.primary,
        args.secondary,
        args.footer,
        args.output,
        primary_pt=args.primary_pt,
        secondary_pt=args.secondary_pt,
    )


if __name__ == "__main__":
    main()
