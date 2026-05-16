# 2026-04-18 — Phase 12 (Commit A): tighten short-break HPSS gate

## Goal

Phase 11 left three per-track section-boundary issues in its "out of scope" list (Baila P58→P59, Charbel-Ana P17 ending, Teu Toque S6/M74). Fix these **as generalizable heuristic improvements**, not per-track hacks — any constant we touch has to hold up across the whole eval set and plausibly across new tracks.

## Context / prior state

After Phase 11, `_label_sections` in [src/rytmi/dsp.py](../../src/rytmi/dsp.py) emits `short_break[branch]` whenever the four-branch classifier fires on a section that is below the 2-phrase `break` floor but at least 1 phrase long. Inspecting the 10-track archive at [tmp/05_batch_analysis.phase11-main.txt](../../tmp/05_batch_analysis.phase11-main.txt) there are four `short_break` rows:

| Track | Row | Duration | Branch | RMS× | H× | P× | Label correct? |
|---|---|---|---|---|---|---|---|
| Baila Kizomba Amor | 17 | 3.5 s / 1.0 ph | `full` | 0.48 | 0.66 | 0.46 | **yes** — real energy drop |
| Charbel-Ana (cut) | 1 | 20.4 s / 4.1 ph | `melodic` | 0.95 | 0.71 | 1.39 | graze — no energy drop |
| Charbel-Ana (cut) | 6 | 5.1 s / 1.0 ph | `melodic` | 0.94 | 0.70 | 1.37 | graze — the user-flagged P17 issue |
| Charbel-Ana (cut) | 7 | 10.2 s / 2.0 ph | `melodic` | 0.98 | 0.74 | 1.39 | graze — adjacent to row 6 |

The `melodic` branch fires on `harm < 0.70 × median_harm AND perc > 0.85 × median_perc`. On Charbel-Ana, three sections graze those thresholds (H× in the 0.70–0.74 band, P× ≈ 1.37) with RMS essentially untouched (0.94–0.98). Audibly, the main vocal / instrument is *changing character* but the energy isn't dropping — so labelling these as breaks mis-represents the song structure to the dancer.

## Hypothesis

Tightening the gate only for `short_break` — i.e. requiring a 1-phrase section to have either a substantial RMS drop OR a severe HPSS component collapse — will retract the three Charbel-Ana false positives without regressing the one genuine `short_break[full]` on Baila, and without touching any multi-phrase `break[*]` label (which remains anchored to the looser thresholds that Phase 6 tuned).

## What changed

[src/rytmi/dsp.py](../../src/rytmi/dsp.py):
- Added two constants: `_SHORT_BREAK_STRONG_RMS_RATIO = 0.70` and `_SHORT_BREAK_STRONG_HPSS_RATIO = 0.60`.
- Added a second gate inside `_label_sections` after the four-branch classifier: when the firing branch is `melodic` or `percussive` AND the section is `is_short`, retract `fired` to `None` unless `rms_ratio < 0.70 × median_rms` OR one of `harm`/`perc` falls below `0.60 × median`.
- The `full` and `severe` branches are intentionally untouched — `full` already requires both RMS and OPB to drop, and `severe` already demands both HPSS components to collapse. The regression risk is concentrated in `melodic` / `percussive`, which each look at only one of the two HPSS components and can fire when the other component is merely within the normal band.

[tests/test_dsp.py](../../tests/test_dsp.py) — four new cases:
- `test_short_break_rejects_melodic_graze_without_strong_rms_or_hpss` — Charbel-Ana row-6 pattern → `main` (new gate fires).
- `test_short_break_keeps_melodic_when_hpss_drop_is_severe` — 1-phrase H×0.50 → `short_break[melodic]` preserved.
- `test_short_break_keeps_melodic_when_rms_drop_is_strong` — 1-phrase RMS×0.65 + H×0.68 → `short_break[melodic]` preserved.
- `test_regular_break_melodic_not_affected_by_short_break_gate` — 2-phrase melodic graze → `break[melodic]` preserved (the gate is `is_short`-scoped).
- `test_short_break_full_branch_not_affected_by_short_break_gate` — 1-phrase `full`-branch short break (RMS×0.80 + opb drop) → `short_break[full]` preserved.

## Evidence / test results

```
$ python -m pytest -q
288 passed, 1 skipped in 30.51s
```

All existing tests pass. New cases cover both retraction (graze) and preservation (strong HPSS, strong RMS, regular-break pathway, `full` branch).

Logical trace on the four archive rows listed above:

| Row | `is_short` | `rms_strong`<br/>(< 0.70 × med) | `hpss_strong`<br/>(H or P < 0.60 × med) | New label |
|---|---|---|---|---|
| Baila 17 | True | **True** (0.48) | — | `short_break[full]` (unchanged — `full` branch bypasses the new gate) |
| Charbel-Ana 1 | True (per archive) | False (0.95) | False (0.71 / 1.39) | retracted → `main` |
| Charbel-Ana 6 | True | False (0.94) | False (0.70 / 1.37) | retracted → `main` (fixes the flagged P17 ending) |
| Charbel-Ana 7 | True (2 ph, at edge) | False (0.98) | False (0.74 / 1.39) | retracted → `main` |

A full notebook re-run on the eval set will be needed to confirm the ratios as written above still hold under the new snap/label passes in combination — the archive gives pre-change numbers, and running the pipeline is not reproducible from unit tests alone.

## What worked

- The false-positive pattern is structurally obvious once laid out in table form: three rows on the same track with H× in the 0.70–0.74 band and RMS essentially normal, triggered by a single-component threshold.
- Scoping the gate to `is_short` contains the blast radius — multi-phrase breaks are untouched, so the 10 `break[*]` rows on other eval tracks stay exactly as Phase 11 left them.

## What did not / limitations

- **Baila P58 → P59 is not addressed here.** The user originally flagged the short_break label as landing one phrase early. After staring at the data, that section is labeled correctly at the *signal* level (RMS × 0.48 is a real drop at 194.7 s); the off-by-one is inherited from a downbeat-offset grid anchored to beat 0 at confidence 0.02. The P-numbering is a naming consequence of the weak downbeat, not a section-boundary bug. Any fix belongs in the downbeat-detection layer, not here.
- **Teu Toque (cut) S6 / M74 is not addressed here.** Same root cause — `low downbeat confidence 0.00, grid anchored to beat 0`. The section boundary at 71.7 s is where the novelty curve placed it; calling it "M74" vs "M47" is downbeat-numbering drift, not a label error.
- **Charbel-Ana rows 1 and 7 flip to `main` as collateral.** Row 1 is a long (4-phrase) section whose `short_break` label is already arguably wrong (the `is_short` flag got set due to phrase_s accounting, not because it's audibly a short break); row 7 is a 2-phrase melodic graze. Neither was user-flagged as a regression, and both are retracted cleanly by the gate. If a subsequent listen-pass says row 7 *should* have stayed `short_break[melodic]`, we'd need to soften the gate (e.g. require only `rms_strong` OR the perc side of `hpss_strong`).
- The short_break gate does not look at the *neighbour* sections' signals — a real break should generally have significantly different signals than its surroundings, not just be below a global threshold. A future refinement could compare to the local-mean instead of the track-median, which would be more robust on tracks with high variance across sections.
- Production verification (notebook re-run on 10-track eval) is deferred — unit tests cover the mechanism but not the interaction with snap / relabel passes downstream.

## Decision / takeaway

Short-break HPSS-branch firings need a stronger signal than regular breaks do. Add the gate; leave the regular-break thresholds alone; don't attempt to fix downbeat-anchor drift from this layer.

## Next step

- **Phase 12 Commit B** (per the plan in [.claude/plans/validated-tumbling-toast.md](../../.claude/plans/validated-tumbling-toast.md)): Gemma-vocal vs Demucs A/B resolution using the three [tmp/05_batch_analysis.phase11-*.txt](../../tmp/) archives as evidence. Decide whether `VOCAL_SOURCE = "gemma"` should become default, stay experimental, or get removed.
- **Phase 13 candidate:** address the downbeat-confidence floor that leaves Baila (0.02) and Teu Toque (0.00) with essentially-random P-numbering. This is where the real "off-by-one phrase" perception comes from. Options include: per-genre accent templates (Q1 FU-1b), a second-chance grid search at higher confidence granularity, or asking Gemma E4B "which of these four candidate downbeats sounds like the `1`?" on low-confidence tracks.
- **Phase 13 candidate:** re-run the eval set notebook after Commit B lands, check whether Charbel-Ana row 7 should be restored to `short_break[melodic]` via a softened gate.
