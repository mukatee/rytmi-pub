# Kaggle submission checklist — Gemma 4 Good Hackathon

Internal pre-submit gate. Walk top-to-bottom and check off.

## Deliverables to upload to Kaggle

- [ ] **Writeup** — `docs/kaggle_writeup.md` (currently ~1530 words incl. code/links; prose body ≤1500). Paste into Kaggle Discussion post or attach as PDF.
- [ ] **Cover image** — `demo_assets/cover.png` (architecture diagram, 1920×1080).
- [ ] **Demo video** — `demo_assets/output/rytmi_demo_master.mp4` (2:55.5, under 3:00 cap). Uploaded to YouTube as unlisted or public.
- [ ] **GitHub repo** — public; latest commit pushed; LICENSE present.
- [ ] **Demo notebook** — `notebooks/00_demo.ipynb` runnable from a clean clone via `requirements-demo.txt`; optionally also uploaded as a Kaggle Notebook for one-click review.
- [ ] **Declared track** — _Future of Education_ (primary); _Ollama Special Technology_ (secondary) noted in writeup header.

## Things to fill in before submitting

In `docs/kaggle_writeup.md`:

- [x] GitHub repo URL: https://github.com/mukatee/rytmi-pub ✓
- [x] YouTube URL in writeup: https://youtu.be/ISkf6fZbG-Y ✓

In `README.md`:

- [x] YouTube URL: https://youtu.be/ISkf6fZbG-Y ✓

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
ollama pull gemma3:4b && ollama serve
jupyter lab notebooks/00_demo.ipynb
# run first cell on data/songs/eval_set/ track; verify Gemma output appears.
```

- [ ] Ran on a clean venv.
- [ ] `00_demo.ipynb` cell 1 produces a valid `RhythmAnalysis`.
- [ ] At least one Gemma prompt completes against the running Ollama endpoint.

## Deferred (post-submission OK)

- CC-BY sample pack so `00_demo.ipynb` doesn't depend on user-supplied audio (user will package separately).
- Kaggle Notebook upload + badge URL in README (after the above).
