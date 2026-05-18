# Rytmi — DSP + Gemma 4 rhythm-learning prototype

> **▶ 3-minute demo video:** [YouTube](https://youtu.be/ISkf6fZbG-Y)  ·  **Kaggle Notebook:** [gemma-dancing](https://www.kaggle.com/code/donkeys/gemma-dancing)  ·  **Kaggle writeup:** [docs/kaggle_writeup.md](docs/kaggle_writeup.md)  ·  **Public repo:** <https://github.com/mukatee/rytmi-pub>

![Rytmi architecture — DSP listens, Gemma 4 talks](demo_assets/cover.png)

A rhythm-learning assistant for dance music. **librosa-based DSP** detects what the audio actually contains (tempo, beats, sections, downbeat confidence, per-section beat clarity); **Gemma 4** turns that grounded analysis into practical movement coaching for a learner. The split is deliberate: Gemma is never the primary beat detector and is forbidden from inventing musical facts the analysis can't support.

Built for the **Gemma 4 Good Hackathon** (deadline 2026-05-18). Submitted track: **Future of Education** (also eligible for the *Ollama Special Technology Track*).

## Reviewers — fastest path

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-demo.txt && pip install -e .
ollama pull gemma3:4b && ollama serve   # or point at any OpenAI-compatible Gemma endpoint
jupyter lab notebooks/00_demo.ipynb
```

`requirements-demo.txt` covers only the cloud-endpoint + notebook path; heavy optional extras (local HuggingFace, Demucs, BeatNet/madmom) live in `pyproject.toml` extras and are not needed to see the Gemma coaching output.

## The problem

Dancers struggle to *hear* the beat in some music. Bachata's "1" is usually clear; **kizomba has no acoustic downbeat at all** and its pulse is often subtle. Generic counting apps don't know the difference, and a naive beat tracker locks onto whatever percussion is loudest — confidently wrong on the sections that matter most for a learner.

Rytmi addresses this two ways:

1. A **style-aware DSP path** that uses different beat-tracking strategies per dance style and reports per-section beat clarity (subtle / moderate / clear) so downstream tools can express uncertainty.
2. A **Gemma 4 coaching layer** that translates the analysis into movement strategy — and refuses to fabricate a downbeat for kizomba or narrate raw metrics at the learner.

## Quickstart (full install)

Requires Python ≥ 3.12.

```bash
pip install -e ".[cloud,notebook]"
ollama pull gemma3:4b
ollama serve
jupyter lab notebooks/00_demo.ipynb
```

For the local HuggingFace backend (instead of Ollama) install `[llm]` instead of `[cloud]`. Optional extras: `[vocals]` for demucs vocal separation, `[downbeat]` for BeatNet downbeat fusion, `[app]` for the Gradio interface in `app/`.

## Where to look

- **`notebooks/00_demo.ipynb`** — end-to-end story: one kizomba and one bachata track, full pipeline, side-by-side coaching output. Start here.
- `notebooks/07_kizomba_tutor.ipynb` — kizomba tutor over all 5 tap-reference tracks (incl. honest `beat: subtle` behavior on Charbel).
- `notebooks/06_kizomba_batida_check.ipynb` — visual diagnostic for the kizomba beat tracker.
- `notebooks/05_batch_analysis.ipynb` — every prompt in `ALL_QUESTIONS` over the eval set.
- `notebooks/01–04` — component notebooks (audio loading, onset/beat detection, visualization, Gemma basics).

## Architecture

```
audio file ─► librosa DSP ─► RhythmAnalysis ─► Gemma 4 prompt ─► coaching
             (beats,         (tempo, sections,   (style-aware,
              onsets,          downbeats,          grounded in
              HPSS,            beat-clarity,       analysis only)
              sections)        phases)
```

- `src/rytmi/audio.py` — loading and normalization.
- `src/rytmi/dsp.py` — beat tracking, onset detection, HPSS, section labeling, downbeat detection. The kizomba-specific batida path (`_track_kizomba_batida`) uses an explicit low-frequency mel filterbank — see Phase 28 notes for why.
- `src/rytmi/prompts.py` — `ALL_QUESTIONS` registry of style-aware prompts including `QUESTION_KIZOMBA_TUTOR` and the polish-pass scaffolding.
- `src/rytmi/llm.py` — Gemma 4 backends (local HF or any OpenAI-compatible cloud endpoint), `explain_rhythm`, `polish_kizomba_tutor_output`.
- `src/rytmi/viz.py` — interactive timelines with synced audio playback.

## Key design choices

- **Local-first.** Default backend is Ollama-served Gemma 4 (E2B / E4B). Cloud-compatible API works the same.
- **Smaller models first.** E2B and E4B handle the coaching prompts well; larger models only if extra reasoning quality clearly matters.
- **Honest about kizomba downbeats.** Kizomba doesn't have an acoustic "1"; the tutor prompt explicitly forbids naming one. This is a musical fact, not a detection failure — see `docs/experiments/24-...md`.
- **Beat-clarity per section, not per song.** A single "is this song danceable" score hides the parts of a song where movement *should* shrink. Per-section labels let the tutor say "trust the pulse here, mark in place there."
- **Optional polish pass.** A second Gemma call can rewrite tutor output against a stricter coaching rubric while preserving every analysis fact from the draft. Off by default — doubles LLM cost and can preserve ungrounded language already in the draft.

## Documentation

- `docs/project-vision.md` — what we are and aren't trying to build, roadmap.
- `docs/how-it-works.md` — DSP architecture, prompt design, evaluation strategy.
- `docs/gemma-kaggle-compo.md` — competition framing.
- `docs/audio-sources.md` — track sources and licensing.
- `docs/eval-set-guide.md` — eval set structure, paired tracks, attribute taxonomy.
- `docs/kaggle_writeup.md` — Kaggle submission writeup (work in progress).
- `docs/experiments/` — dated phase notes (Phase 28 mel-filterbank gotcha, Phase 29 / 29b tutor refresh, etc.).

## Tests

```bash
pytest                  # full suite
pytest tests/test_prompts.py   # focused
```

384 passed, 1 skipped at last commit.

## License

Code: MIT (see [LICENSE](LICENSE)). Music files referenced under `data/songs/` and used as input audio in the demo video remain the property of their respective rights holders and are used for educational and evaluation purposes only — see [docs/audio-sources.md](docs/audio-sources.md) for per-track attribution.
