# Phase 7 — Downbeat-anchored phrase grid + eval set metadata

**Date:** 2026-04-16

## Goal

Expose the `best_offset` from `detect_downbeats()`, confidence-gate it, and thread it through the phrase grid, section diagnostics, and timeline visualization so that cut-video tracks can show musically correct measure/count numbers when the downbeat is confidently detected. Also establish machine-readable eval set metadata and a CLI runner.

## Context / prior state

Phase 6 shipped HPSS break classification (melodic/percussive/severe/full branches) and a narrow-scope sub-phrase splitter. The DSP pipeline was fully functional, but the phrase grid was always anchored to `beats.times[0]` regardless of where the musical "1" actually fell.

The user observed that many eval-set tracks ripped from YouTube dance videos are cut partway through the intro, so the DSP phrase grid was offset from musical reality:
- *Romeo Santos El Chaval (dance-video cut):* vocals should land on M11 count 1; analysis showed count 3.
- *Charbel E Magia (dance-video cut):* beat should start at M16 count 1; analysis showed count 2 or 6.
- *Filomena Maricoa Teu Toque (dance-video cut):* M1 was 2 beats in from mp3 start.

`detect_downbeats()` already computed `best_offset` (beat index within a measure where the strongest evidence for "1" lies) and `downbeat_confidence`, but the offset was discarded at the return site.

## Hypothesis

1. Widening `detect_downbeats()` to return `best_offset` as a 4th tuple element and confidence-gating it at `>= 0.25` will allow the pipeline to anchor the phrase grid at the detected downbeat when confidence is high enough.
2. On tracks where confidence is low (< 0.25), defaulting to offset=0 preserves current behavior without regressing.
3. The timeline viz can render pickup beats (pre-downbeat) as grey/muted, with a dotted marker before the first real downbeat.

## What changed

**[src/rytmi/dsp.py](../../src/rytmi/dsp.py)**

- `detect_downbeats()` return widened from 3-tuple to 4-tuple: `(downbeat_times, beats_per_measure, confidence, best_offset)`. All three return paths updated.
- New constant `_DOWNBEAT_OFFSET_MIN_CONFIDENCE = 0.25`.
- `analyze()` unpacks the 4-tuple, computes `effective_offset` (gated by confidence), stores it on `RhythmAnalysis`, and passes it to `_snap_boundaries_to_phrases()`.
- `_snap_boundaries_to_phrases()` gains `offset: int = 0` kwarg; phrase grid changed from `beats.times[::phrase_length]` to `beats.times[offset::phrase_length]`.
- `describe_sections()` inner functions `phrase_measure_at()` and `drift_beats()` now use `rel = beat_idx - offset` indexing. Header shows downbeat offset/confidence info.

**[src/rytmi/types.py](../../src/rytmi/types.py)**

- `RhythmAnalysis` gains `downbeat_offset: int | None = None`.

**[src/rytmi/viz.py](../../src/rytmi/viz.py)**

- `plot_timeline()` beat loop rewritten from sequential counters to `rel = i - offset` arithmetic. Pickup beats (rel < 0) render as grey with lighter alpha. Dotted purple `&` marker placed half a beat before the first real downbeat when `offset > 0`.

**[tests/test_dsp.py](../../tests/test_dsp.py)**

- Existing 9 downbeat tests updated to unpack 4-tuples.
- `test_detect_downbeats_returns_three_tuple` → `test_detect_downbeats_returns_four_tuple`.
- New tests: `test_detect_downbeats_offset_matches_first_downbeat`, `test_analyze_stores_downbeat_offset`, `test_snap_boundaries_respects_offset`, `test_describe_sections_phrase_measure_respects_offset`, `test_describe_sections_shows_offset_header`.

**[tests/test_viz.py](../../tests/test_viz.py)**

- New tests: `test_plot_timeline_pickup_beats_with_offset`, `test_plot_timeline_zero_offset_unchanged`.

**[data/songs/eval_set/metadata.yaml](../../data/songs/eval_set/metadata.yaml)** — New. Per-track entries with style/source/paired_with/attributes for all 10 eval tracks.

**[tmp/run_eval.py](../../tmp/run_eval.py)** — New. Argparse CLI runner replacing `tmp/run_phase5_eval.py` with `--fast`, `--style`, `--attribute`, `--pair` flags.

**[docs/eval-set-guide.md](../eval-set-guide.md)** — New. Attribute taxonomy, adding-tracks guide.

**[docs/how-it-works.md](../how-it-works.md)** — New subsection "Downbeat-anchored phrase grid (Phase 7)".

## Evidence / test results

`pytest tests/test_dsp.py -q` → **74 passed**. `pytest tests/test_viz.py -q` → **19 passed**. Full suite `pytest -q` → **206 passed, 1 skipped**.

Eval on the full 10-track set (`tmp/run_eval.py`):

| track | downbeat confidence | offset used |
|---|---|---|
| all 10 tracks | 0.00 – 0.09 | 0 (gated) |

All 10 tracks have downbeat confidence below the 0.25 threshold, so the offset is gated to 0 on every track. This means the phrase grid anchoring has zero behavioral change on the current eval set — no regressions, but also no visible improvement yet.

## What worked

- The **infrastructure is fully wired**: offset flows from `detect_downbeats()` through `analyze()` → `_snap_boundaries_to_phrases()` → `describe_sections()` → `plot_timeline()`. When a future track or improved detection algorithm produces confidence >= 0.25, the phrase grid, diagnostics, and timeline will automatically anchor correctly.
- The **confidence gating** correctly prevents false-positive offsets: all 10 eval tracks get `offset=0`, preserving Phase 6 behavior exactly.
- The **`describe_sections()` header** now shows `"low downbeat confidence X.XX, grid anchored to beat 0"` — transparent about why the grid isn't offset.
- The **eval runner** with `--fast`, `--style`, `--attribute`, `--pair` flags works cleanly and replaces the old `run_phase5_eval.py`.
- The **pickup beat rendering** in `plot_timeline()` (grey dots, `&` marker) is wired up and tested — it just doesn't fire on any current eval track because offset=0.

## What did not / limitations

- **No eval track triggers the offset.** The downbeat confidence metric (geometric mean of margin × dominance) is calibrated for synthetic click tracks. On real music with complex arrangements, the metric produces values well below 0.25 even on tracks where a human can clearly hear the downbeat. This is the known "residual ambiguity" from the plan: DSP alone may not be enough — vocals onset or structural boundary detection may be needed to disambiguate.
- **Threshold 0.25 is a guess.** The confidence metric may need to be redesigned rather than just adjusting the threshold. The current metric penalizes tracks where multiple beat positions carry strong evidence (e.g. 2/4 feel in 4/4 grouping), which is common in real music.
- **Pickup beat rendering is untested on real music** — only synthetic test fixtures.

## Decision / takeaway

Ship it. The infrastructure is correct, tested, and has zero behavioral regression. The eval set metadata and runner are immediate quality-of-life wins. The downbeat offset will start producing visible improvements when either:
1. The confidence metric is improved (e.g. using vocals onset or structural cues), or
2. A track with genuinely clear downbeat evidence is added to the eval set.

## Next step

Possible Phase 8 directions:
- Improve the downbeat confidence metric using vocals onset or first structural boundary as a disambiguator.
- Grow the eval set to 16-24 tracks with better attribute coverage.
- Address the Charbel over-firing issue (6 adjacent `break[melodic]` sections) with a consecutive-breaks-collapse post-pass.
