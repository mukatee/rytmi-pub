# Rytmi Demo Assets

Self-contained tools and rendered files for the Kaggle demo video. Everything
in this folder is optional: the project itself runs without it. Outputs go in
`output/` so they are easy to delete and regenerate.

## What's here

```
demo_assets/
├── README.md                 ← this file
├── diagrams/
│   └── architecture.mmd      ← Mermaid source for the audio→DSP→Gemma flow
├── scripts/
│   ├── make_click_overlay.py ← run librosa beat_track on a clip and overlay clicks
│   ├── cut_excerpt.py        ← clean audio cuts with optional fade in/out
│   ├── make_slide.py         ← PNG title/caption cards (PIL, no design tool needed)
│   ├── render_diagram.sh     ← convert architecture.mmd to PNG via mermaid-cli
│   └── make_all_demo_clips.py ← one-shot: cut Filomena hook + click-overlay + title card
└── output/                   ← all rendered files land here (gitignored if you want)
```

## Quick start (one-shot)

Renders the three core Act 1 assets in one go:

```bash
.venv/bin/python demo_assets/scripts/make_all_demo_clips.py
```

Produces in `demo_assets/output/`:
- `act1_filomena_hook.wav` — 10s cut of Filomena starting near a beat
- `act1_filomena_hook_clicks.wav` — same clip with librosa-detected beat clicks at 35% volume
- `act1_title_slide.png` — 1920×1080 title card

## Per-tool usage

### Click overlay
```bash
.venv/bin/python demo_assets/scripts/make_click_overlay.py \
    --input "data/songs/eval_set/kizomba/Filomena_Maricoa_-_Teu_Toque_Official_Video [sKbWzD0mt6I].mp3" \
    --start 32 --duration 10 \
    --output demo_assets/output/filomena_clicks.wav \
    --click-volume 0.35
```

### Audio excerpt
```bash
.venv/bin/python demo_assets/scripts/cut_excerpt.py \
    --input <song.mp3> --start 32 --duration 10 \
    --output demo_assets/output/clip.wav \
    --fade-in 0.05 --fade-out 0.3
```

### Slide
```bash
.venv/bin/python demo_assets/scripts/make_slide.py \
    --title "Rytmi" \
    --subtitle "DSP + Gemma 4 for rhythm learning" \
    --output demo_assets/output/title.png
```

### Architecture diagram
Mermaid source is `diagrams/architecture.mmd`. Render to PNG with the official
CLI (one-time install: `npm i -g @mermaid-js/mermaid-cli`):

```bash
demo_assets/scripts/render_diagram.sh
```

This writes `output/architecture.png` at 1920×1080. Or paste the source into
<https://mermaid.live> for a quick view without installing anything.

## What's intentionally NOT here

- No video editor automation. Compose the final cut in kdenlive / Resolve / OBS.
- No background music. Caption-first per the storyboard.
- No voice-over. Captions only.
- No live notebook execution during recording. Pre-render once, screen-grab.

See `docs/demo_storyboard.md` for the full per-act plan.
