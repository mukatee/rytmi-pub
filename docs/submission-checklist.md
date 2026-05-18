# Kaggle submission checklist — Gemma 4 Good Hackathon

Internal pre-submit gate. Walk top-to-bottom and check off.

## Deliverables to upload to Kaggle

- [ ] **Writeup** — `docs/kaggle_writeup.md` (currently ~1530 words incl. code/links; prose body ≤1500). Paste into Kaggle Discussion post or attach as PDF.
- [ ] **Cover image** — `demo_assets/cover.png` (cover_B: backlit kizomba silhouette + the real E Magia 165s transition waveform + the two-tone Rytmi-DSP→Gemma-4 coaching caption, 1400×1400 square). Rebuild: `.venv/bin/python demo_assets/scripts/make_cover.py`; A/B/C candidates in `demo_assets/cover_candidates/`. Architecture diagram retained at `demo_assets/output/architecture.png` for in-writeup / Act-2 use.
- [ ] **Card / thumbnail image (Kaggle form, exactly 560×280)** — upload `demo_assets/cover_candidates/cover_card_story_short_airy_560x280.png`. Crop-safe by design: left 280×280 = title lockup (_Rytmi_ / _Hear the Beat, Feel the Song_); right 280×280 = the **story** square — couple + halo + glowing pulse, with the verbatim short Gemma coaching line (_"keep a small pulse in the body, and listen."_) over a teal `DSP · 165s main → break` line. Nothing crosses the midline. **Pick the right square** for the thumbnail (the chosen one — couple + Gemma/DSP story, not tool names); left square also clean if a text-legible tile is ever wanted; **avoid dead-center** (seam). "Airy" treatment: light scrim + semi-transparent text so the pulse/couple read through. Exact-pixel crop previews: `cover_card_story_short_airy_crop_{right,left}.png`. Other explored cuts kept in `cover_candidates/` (`cover_card_dual_*`, `cover_card_story_{full,short}_*`, `cover_card_560x280.png`). Same `make_cover.py` rebuild; airy/scrim knobs in `candidate_card_story`.
- [ ] **Demo video** — `demo_assets/output/rytmi_demo_master.mp4` (**2:28.8** after the 2026-05-18 sparkler re-cut + pass #2: poster-cover open; trimmed Act 1; Act 2 deduped (caption2/3 dropped, real `describe_sections` DSP table now the post-diagram bridge); pre-roll 4→2 Gemma panels; one-line structure→dance framing before the unified timeline; close **bookends on the opening poster + verbatim Gemma feeling line** instead of the tech tagline; live reel lands ~1:24 vs ~1:57). Re-render path: `make_cover_intro.py` → `make_act1_video.py` → `make_act2_video.py` → `make_act3a_preroll_video.py` → `make_structure_framing_video.py` → `make_close_video.py` → `compose_master_reel.py`. **Re-upload note:** YouTube has no in-place replace; re-uploading creates a new video ID — update the URL in `docs/kaggle_writeup.md` (links table) + `README.md` + this checklist + the Kaggle form/media gallery if the ID changes. YouTube thumbnail: `demo_assets/cover_candidates/cover_video_help_me_hear.png` (16:9, video title).
- [ ] **Project Media gallery** — `demo_assets/gallery/` (7 items, story order): 01 poster cover → 02 architecture → 03–06 four real coaching-moment stills (kizomba Filomena/E Magia, bachata Royce/Romeo — each = real waveform + section bands + playhead + verbatim two-tone DSP/Gemma caption, frame-pulled from the captioned clips) → 07 unified-timeline signature panel. Optionally also upload 2–3 `demo_assets/output/timeline_*_captioned.mp4` clips for motion+audio. Regenerate stills: re-run the ffmpeg frame-pull (see git history) against the `timeline_*_captioned.mp4` set.
- [ ] **GitHub repo** — public; latest commit pushed; LICENSE present.
- [ ] **Demo notebook** — `notebooks/00_demo.ipynb` runnable from a clean clone via `requirements-demo.txt`; optionally also uploaded as a Kaggle Notebook for one-click review.
- [ ] **Declared track** — _Future of Education_ (primary); _Ollama Special Technology_ (secondary) noted in writeup header.

## Things to fill in before submitting

In `docs/kaggle_writeup.md`:

- [x] GitHub repo URL: https://github.com/mukatee/rytmi-pub ✓
- [x] YouTube URL in writeup: https://youtu.be/S3yNA6M_CFs ✓
- [x] Kaggle Notebook URL: https://www.kaggle.com/code/donkeys/gemma-dancing ✓

In `README.md`:

- [x] YouTube URL: https://youtu.be/S3yNA6M_CFs ✓
- [x] Kaggle Notebook URL: https://www.kaggle.com/code/donkeys/gemma-dancing ✓

## Music attribution / risk

- [ ] YouTube upload includes a description noting the educational/demo basis for the brief excerpts and links to the writeup's "A note on the demo video's audio" section.
- [ ] `docs/audio-sources.md` covers all 5 reel tracks with artist and title.
- [ ] Acknowledge: a ContentID match is possible. Acceptable fallback: take video down and re-upload reel with CC-licensed substitutes.

## Reproducibility smoke test

Fresh clone reviewer path (validates `requirements-demo.txt`):

```bash
git clone <repo> && cd kaggle-gemma4-rytmi
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-demo.txt && pip install -e .
ollama pull gemma4:e4b && ollama serve
jupyter lab notebooks/00_demo.ipynb
# run first cell on data/songs/eval_set/ track; verify Gemma output appears.
```

- [ ] Ran on a clean venv.
- [ ] `00_demo.ipynb` cell 1 produces a valid `RhythmAnalysis`.
- [ ] At least one Gemma prompt completes against the running Ollama endpoint.

## Deferred (post-submission OK)

- CC-BY sample pack so `00_demo.ipynb` doesn't depend on user-supplied audio (user will package separately).
- Kaggle Notebook upload + badge URL in README (after the above).
