# 2026-04-11 — Downbeat confidence heuristic review

> Source: summary from the Claude Code second-pass DSP review and implementation run.

## Goal
Improve the honesty and usefulness of the likely downbeat / `1` detection by adding a more meaningful confidence signal and reducing known biases in the first-pass heuristic.

## Context / prior state
The first-pass `detect_downbeats()` approach had the right high-level idea — choose the beat offset with the strongest evidence and normalize a confidence score — but it had two important weaknesses:

1. **Offset-count bias from sum-based scoring**
   - With beat counts that do not divide evenly into the measure length, some offsets include more beats than others.
   - A raw sum therefore favored earlier offsets for structural reasons rather than musical evidence.

2. **Ambiguity blindness in the confidence score**
   - The original dominance-only score could not distinguish a true strong winner from a tied or nearly tied top two offsets.
   - This made structurally ambiguous cases look more confident than they should.

## What changed
### `src/rytmi/dsp.py`
- changed offset scoring from **sum** to **mean per offset** to remove offset-count bias
- added a **margin** term: `(best - runner_up) / best`
- retained a **dominance** term relative to the uniform-chance baseline
- combined the two via geometric mean: `sqrt(margin * dominance)`
- added guard cases for:
  - `beats_per_measure < 2`
  - effectively silent/degenerate scores (`best <= 1e-9`)
- kept the implementation DSP-grounded and readable

### `src/rytmi/types.py`
- added `downbeat_confidence: float | None = None` to `RhythmAnalysis`

### `tests/test_dsp.py`
- tightened expectations for confidence on uniform beats
- added a tied-top ambiguity regression test
- added a small edge-case test for `beats_per_measure < 2`

## Why this change matters
The project should not present a guessed `1` as if it were certain. The new approach is better aligned with the product goal of being **helpful but honest**, especially for rhythm learners.

### Interpretation of the new confidence design
- **dominance** asks whether the winner beats the chance baseline
- **margin** asks whether the winner clearly beats the runner-up
- the geometric mean forces both signals to be present for a confident result

This makes the system better at saying:
- “this is a plausible `1` candidate” when the evidence is real, and
- “this is ambiguous” when the structure is weak or tied.

## Evidence / test results
Reported empirical behavior from the run:

| Signal | Old confidence | New confidence |
|---|---:|---:|
| uniform 1 kHz click | 0.027 | 0.011 |
| uniform 100 Hz click | 0.062 | 0.034 |
| 1 kHz, 3× accent every 4 | 0.037 | 0.132 |
| 80 Hz, 5× accent every 4 | 0.460 | 0.426 |
| 80 Hz, 5× accent every 2 (tied tops) | 0.170 | 0.028 |
| 100 Hz, 5× accent every 4 | 0.392 | 0.382 |

### Verified test summary from the run
- `16 passed in 2.62s`

## What worked
- strong accent-every-4 cases remain clearly stronger than uniform cases
- tied-top ambiguity is now pushed down much more aggressively
- uniform signals produce lower confidence than before
- the change stays compact, explainable, and easy to defend in a writeup

## What did not work / limitations
- real-song calibration has not yet been done on bachata, kizomba, salsa, or other actual music
- tempo octave errors are still outside the scope of this pass
- only one `beats_per_measure` value is tried at a time
- the new `downbeat_confidence` value is not yet fully surfaced in notebooks, visualizations, or Gemma explanations

## Decision / takeaway
This heuristic is a better default than the earlier version and is worth keeping as the current baseline.

However, the **next meaningful experiment should be consumer integration + real-song evaluation**, not more synthetic-only DSP tuning.

## Recommended next step
1. Surface `downbeat_confidence` in the notebook and visualization outputs
2. Pass that uncertainty through to the Gemma explanation layer
3. Create a small curated song set for manual evaluation across styles
