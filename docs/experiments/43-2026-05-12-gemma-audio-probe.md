# Phase 43 — Gemma 4 audio probe (E4B) on kizomba excerpts

**Date:** 2026-05-12
**Status:** Negative result — shelved
**Branch:** main

## Goal

Sanity-check whether Gemma 4 multimodal (`E4B`, audio-capable) can describe
**song-specific musicality** of short kizomba excerpts in a way the existing
DSP→text pipeline cannot. If yes, audio could either (a) supplement the
prompt with novel observations, or (b) replace some of the DSP-derived
descriptors with richer language.

This is the third time we've checked this assumption, but the first time
with a runnable, repeatable script and stored output:

- [`kaggle_writeup.md`](../kaggle_writeup.md): "raw-audio prompting against
  E2B/E4B was unreliable on instrumentation, missed percussion entries…"
  — narrative claim from earlier iterations.
- [`17-2026-04-18-phase-11-validated-upgrades.md`](./17-2026-04-18-phase-11-validated-upgrades.md):
  used Gemma E4B audio for the *speech-vs-singing* yes/no, which works
  because it lines up with the model's documented speech-shaped capability.
- This phase: rhythmic / dancer-coaching prompts on short music clips
  (the original "can it short-cut DSP" theory).

## Hypothesis

Gemma 4 audio, when prompted with structured kizomba teacher framing on a
12-second clip, will name something **clip-specific** (intermittent vocal,
band thinning, kick-pattern change, etc.) that the DSP categories
(`main` / `break` / `peak` + energy bucket) don't already encode.

## What changed

- Fixed [`demo_assets/scripts/probe_gemma_audio.py`](../../demo_assets/scripts/probe_gemma_audio.py)
  glob handling so YouTube-ID brackets in filenames resolve correctly.
- Repaired the venv: `torchvision 0.26.0+rocm7.2` was ABI-incompatible with
  CPU `torch 2.11.0`, which silently broke `torchvision::nms` registration
  and propagated to `transformers.Gemma4ForConditionalGeneration` import.
  Reinstalled CPU `torchvision==0.26.0` (`pip install --no-deps`).
- Ran the probe end-to-end on three excerpts (12 s each) × two prompts:
  Filomena steady main, E_Magia Ben_Ana break (thinned percussion),
  Tony_Pirata pre-break build. Output stored in
  [`demo_assets/output/gemma_audio_probe.md`](../../demo_assets/output/gemma_audio_probe.md).

## Evidence

Verbatim model output (full file in
[`gemma_audio_probe.md`](../../demo_assets/output/gemma_audio_probe.md)):

| Clip                     | What's actually there        | Gemma "musicality" answer (summary)                |
| ------------------------ | ---------------------------- | -------------------------------------------------- |
| Filomena main, ~92 BPM   | full vocal + bass, steady    | "driving rhythmic pulse… infectious groove"        |
| E_Magia Ben_Ana 145 s    | break, percussion thinned    | "smooth rhythmic pulse… warm, inviting flow"       |
| Tony_Pirata 125 s build  | pre-break build, vocals      | "driving syncopated pulse… deep, swaying bassline" |

Three observations:

1. **No clip differentiation.** The break excerpt is described as a "smooth
   inviting flow" — the opposite of what's happening musically (sparsest of
   the three). The other two are interchangeable kizomba boilerplate.
2. **No structural awareness.** The "pre-break build" gets no mention of
   building tension or impending change.
3. **Dancer cues collapse to a template.** All three answers reduce to
   "shift your weight to your left foot" — generic intro-to-kizomba advice
   that has nothing to do with the specific audio.

This matches the pattern earlier work hinted at: the model produces
plausible *kizomba-shaped* prose regardless of input, suggesting it's
leaning on the textual prompt framing more than the actual audio content.

## What worked

- The probe ran end-to-end on CPU in a few minutes per clip — reproducible
  if anyone wants to recheck against a future Gemma release.
- The negative result is now **stored, dated, and pointed at concrete
  filenames**, not just narrated.

## What did not / limitations

- Single model (`E4B`); no `E2B` comparison, no future-Gemma comparison.
- Single language framing (English teacher persona); a Portuguese-prompted
  version might do marginally better on lyric content but wouldn't change
  the rhythmic-content conclusion.
- Two prompts per clip; richer chain-of-thought or "list three things you
  hear, then answer" prompting was not attempted. We have low confidence
  this would change the verdict given how generic the failure mode is, but
  it's the obvious next escalation if the assumption is ever revisited.
- 12 s window; the 30 s ceiling was not used.
- The dancer_cue answers may also be biased by safety-style hedging
  toward generic foundational advice, separate from the audio-understanding
  question.

## Decision / takeaway

**Shelve raw-audio music-content prompting for the demo.** Reaffirm the
DSP-as-grounding architecture documented in
[`kaggle_writeup.md`](../kaggle_writeup.md): Gemma is excellent at *talking
about* music when given structured DSP descriptions, and DSP earns its
keep by being the part that listens.

Keep the probe script committed as evidence the assumption was tested,
not assumed away.

The earlier conclusion stands: the only audio-domain task where the
documented speech-shaped capability has paid off in this project is the
**speech-vs-singing yes/no** (Phase 11), which is structurally aligned
with the model's training. Music-structure understanding from raw audio
is not.

## Next step

- None on the audio-input axis — closing the loop on "should we use Gemma
  audio for music?" with a stored, reproducible no.
- If future Gemma releases ship music-trained audio encoders, re-run this
  same probe (`python demo_assets/scripts/probe_gemma_audio.py`) and diff
  against [`gemma_audio_probe.md`](../../demo_assets/output/gemma_audio_probe.md)
  to see whether the failure mode has moved.

## Files touched

- [`demo_assets/scripts/probe_gemma_audio.py`](../../demo_assets/scripts/probe_gemma_audio.py)
  — glob-escape fix for bracketed filenames.
- [`demo_assets/output/gemma_audio_probe.md`](../../demo_assets/output/gemma_audio_probe.md)
  — generated, the actual evidence.
- [`docs/project-vision.md`](../project-vision.md) — added pointer to this
  note from the "Note on vocals and song structure" section.
- [`docs/experiments/README.md`](./README.md) — index entry.
