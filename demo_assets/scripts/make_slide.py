"""Render a 1920×1080 PNG title or caption slide.

Used for project-name slides, act dividers, and the closing card. Avoids
needing Keynote/PowerPoint for one-off cards. Style matches the dark theme
used in the architecture diagram so the deck reads as one piece.

Example:
    python demo_assets/scripts/make_slide.py \\
        --title "Rytmi" \\
        --subtitle "DSP + Gemma 4 for rhythm learning" \\
        --footer "Kaggle Gemma 4 Good Hackathon" \\
        --output demo_assets/output/title.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# Project palette — matches diagrams/architecture.mmd.
BG = (15, 23, 42)              # slate-900
FG = (248, 250, 252)           # slate-50
ACCENT = (167, 139, 250)       # violet-400
MUTED = (148, 163, 184)        # slate-400


# Font fallbacks — try common Linux/macOS sans serifs.
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = _FONT_CANDIDATES if bold else _FONT_CANDIDATES[1:]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    width: int,
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(((width - text_w) / 2, y), text, fill=fill, font=font)
    return text_h


def render_slide(
    title: str,
    subtitle: str | None,
    footer: str | None,
    output: Path,
    width: int = 1920,
    height: int = 1080,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Accent bar for visual anchor.
    bar_y = height // 2 - 8
    draw.rectangle([(width // 2 - 80, bar_y), (width // 2 + 80, bar_y + 6)], fill=ACCENT)

    title_font = _load_font(160, bold=True)
    subtitle_font = _load_font(56)
    footer_font = _load_font(34)

    # Title sits above the accent bar.
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_h = title_bbox[3] - title_bbox[1]
    title_y = bar_y - title_h - 60
    _draw_centered(draw, title, title_y, title_font, FG, width)

    if subtitle:
        # Word-wrap the subtitle to ~80% of slide width so longer
        # taglines (e.g. the post clarity-pass-2 hook subtitle) don't
        # bleed off the edges. Single-line subtitles render unchanged.
        max_w = int(width * 0.80)
        words = subtitle.split()
        lines: list[str] = []
        current = ""
        for w in words:
            candidate = w if not current else f"{current} {w}"
            bbox = draw.textbbox((0, 0), candidate, font=subtitle_font)
            if bbox[2] - bbox[0] <= max_w:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        line_h = subtitle_font.size + 12  # modest leading
        for i, line in enumerate(lines):
            _draw_centered(
                draw, line, bar_y + 50 + i * line_h,
                subtitle_font, MUTED, width,
            )

    if footer:
        footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
        footer_h = footer_bbox[3] - footer_bbox[1]
        _draw_centered(draw, footer, height - 80 - footer_h, footer_font, MUTED, width)

    img.save(str(output), "PNG")
    print(f"wrote {output} ({width}x{height})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--title", required=True)
    p.add_argument("--subtitle", default=None)
    p.add_argument("--footer", default=None)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    args = p.parse_args()
    render_slide(
        args.title, args.subtitle, args.footer, args.output, args.width, args.height
    )


if __name__ == "__main__":
    main()
