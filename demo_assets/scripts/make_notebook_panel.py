"""Render a 1920×1080 PNG that mimics a Jupyter notebook output cell.

Used for the Act 3a pre-roll panels — each panel shows real Gemma output
verbatim from `notebooks/00_demo_outputs.md`, framed as if peeled from
the live notebook so the audience sees "this is the actual model output,
not a paraphrase" rather than a stylized caption.

Layout:

- Dark slate background matching the rest of the deck.
- Top label strip: a small monospace cell-tag (e.g.
  ``In [12]:  explain_all('kizomba', 'Filomena – Teu Toque')``) and a
  larger muted heading from the notebook's Markdown row.
- Main body: the Gemma output in monospace (DejaVu Sans Mono), word-wrapped
  to fit the canvas width. Optionally shows a leading single-line tag
  (e.g. ``[song_arc]``) above the body in the accent colour.
- Footer: tiny attribution (``notebooks/00_demo.ipynb · verbatim Gemma 4
  output``) so the source is unambiguous on screen.

Re-rendered idempotently from caller scripts. Each panel is a single
PNG; animation/staging happens at the ffmpeg-stitch step in the act
scripts.

Example::

    python demo_assets/scripts/make_notebook_panel.py \\
        --heading "Filomena Maricoa — Teu Toque (song_arc)" \\
        --tag "song_arc" \\
        --body "The track begins with a low-energy intro …" \\
        --output demo_assets/output/_act3a_song_arc.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# Project palette — mirrors make_caption_slide.py.
BG = (15, 23, 42)              # slate-900
PANEL_BG = (30, 41, 59)        # slate-800 — body background, slightly lifted
FG = (248, 250, 252)           # slate-50
ACCENT = (167, 139, 250)       # violet-400
MUTED = (148, 163, 184)        # slate-400
TAG_FG = (94, 234, 212)        # teal-300 — for the cell-tag prefix


_FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
_FONT_REGULAR_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
_FONT_MONO_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def _load_font(size: int, kind: str = "regular") -> ImageFont.FreeTypeFont:
    paths = {
        "regular": _FONT_REGULAR_CANDIDATES,
        "bold": _FONT_BOLD_CANDIDATES,
        "mono": _FONT_MONO_CANDIDATES,
    }[kind]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _wrap_mono(text: str, font: ImageFont.FreeTypeFont, max_w_px: int,
               draw: ImageDraw.ImageDraw) -> list[str]:
    """Word-wrap each paragraph (split on \n) to fit within max_w_px.

    Lines that already fit within max_w_px are emitted *verbatim* —
    runs of spaces are preserved so monospace tables keep their column
    alignment. Only lines that overflow get re-wrapped on whitespace
    boundaries (which inevitably collapses internal spacing for that
    line).
    """
    out: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            out.append("")  # preserve blank lines as paragraph breaks
            continue
        bbox = draw.textbbox((0, 0), paragraph, font=font)
        if bbox[2] - bbox[0] <= max_w_px:
            # Already fits — keep verbatim (preserves table column spacing).
            out.append(paragraph)
            continue
        # Overflow: re-wrap on whitespace.
        words = paragraph.split()
        if not words:
            out.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            cb = draw.textbbox((0, 0), candidate, font=font)
            if cb[2] - cb[0] <= max_w_px:
                current = candidate
            else:
                out.append(current)
                current = word
        out.append(current)
    return out


def render_notebook_panel(
    heading: str,
    body: str,
    output: Path,
    *,
    tag: str | None = None,
    cell_prompt: str | None = None,
    footer: str = "notebooks/00_demo.ipynb · verbatim Gemma 4 output",
    width: int = 1920,
    height: int = 1080,
    body_pt: int = 32,
    heading_pt: int = 44,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    margin_x = 120
    margin_top = 90
    margin_bottom = 80

    heading_font = _load_font(heading_pt, "bold")
    cell_font = _load_font(22, "mono")
    tag_font = _load_font(28, "bold")
    body_font = _load_font(body_pt, "mono")
    footer_font = _load_font(22, "regular")

    y = margin_top

    # Cell prompt strip (e.g. `In [12]:  explain_all(...)`).
    if cell_prompt:
        draw.text((margin_x, y), cell_prompt, fill=MUTED, font=cell_font)
        y += 36

    # Heading.
    draw.text((margin_x, y), heading, fill=FG, font=heading_font)
    y += heading_pt + 18

    # Accent rule under heading.
    draw.rectangle(
        [(margin_x, y), (margin_x + 120, y + 4)],
        fill=ACCENT,
    )
    y += 28

    # Optional tag (e.g. `[song_arc]`).
    if tag:
        draw.text((margin_x, y), tag, fill=TAG_FG, font=tag_font)
        y += 64

    # Body panel (monospace, on a lifted slate background).
    body_max_w = width - 2 * margin_x - 40  # 20 px inner padding each side
    wrapped = _wrap_mono(body, body_font, body_max_w, draw)
    bbox = draw.textbbox((0, 0), "Hg", font=body_font)
    line_h = int((bbox[3] - bbox[1]) * 1.55)

    body_top = y
    body_bottom = body_top + len(wrapped) * line_h + 40

    draw.rounded_rectangle(
        [(margin_x - 20, body_top - 16),
         (width - margin_x + 20, body_bottom)],
        radius=14,
        fill=PANEL_BG,
        outline=(51, 65, 85),  # slate-700
        width=2,
    )

    text_y = body_top + 8
    for line in wrapped:
        draw.text((margin_x, text_y), line, fill=FG, font=body_font)
        text_y += line_h

    # Footer.
    footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    draw.text(
        ((width - footer_w) / 2, height - margin_bottom),
        footer,
        fill=MUTED,
        font=footer_font,
    )

    img.save(str(output), "PNG")
    print(f"wrote {output} ({width}x{height})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--heading", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--tag", default=None)
    p.add_argument("--cell-prompt", default=None)
    p.add_argument("--footer", default="notebooks/00_demo.ipynb · verbatim Gemma 4 output")
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--body-pt", type=int, default=32)
    p.add_argument("--heading-pt", type=int, default=44)
    args = p.parse_args()
    render_notebook_panel(
        heading=args.heading,
        body=args.body,
        output=args.output,
        tag=args.tag,
        cell_prompt=args.cell_prompt,
        footer=args.footer,
        body_pt=args.body_pt,
        heading_pt=args.heading_pt,
    )


if __name__ == "__main__":
    main()
