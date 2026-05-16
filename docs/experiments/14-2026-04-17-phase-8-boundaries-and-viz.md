# 2026-04-17 — Phase 8: Boundary accuracy, subsection visibility, viz polish, docs

## Goal
Close the gap between what the DSP reports and what a dancer actually hears on the 10-track eval set. After Phase 7 shipped the downbeat-anchored phrase grid, a careful listen revealed four kinds of residual errors on the user's flagged tracks: break / peak edges wrong by 1–2 phrases, audible breaks missed entirely, long `main` runs hiding subsection structure, and two cosmetic / organisational issues (`outro` vs `main` colour too close, notebook staleness invisible).

## Context / prior state
After Phase 7 (commit `d23cafa`), the pipeline produced:
- Phrase-aligned boundaries via `_snap_boundaries_to_phrases()` (±8-beat snap window).
- Four-branch break classifier (`melodic`, `percussive`, `severe`, `full`) from Phase 6.
- Narrow sub-phrase splitter restricted to individual long `main` sections, RMS-only shift metric, threshold floor `0.18` / p90 within-section.
- `SECTION_COLORS` with `outro=#b39ddb` and `main=#e0e0e0` — perceptually close at low alpha.
- No notebook version stamp.

Specific user observations (from notebook 05 + listening pass):
- *Baila Kizomba Amor*: break marked at **P36**, actually starts at **P37**; peak marked **M127→M131**, actually runs **M125→M135**; audible break at **M114** and drop around **P58–P60** not detected.
- *Bachata Musicality* / *El Chaval official* / *All Of Me*: subsection changes audible inside long `main` runs but not surfaced.
- Several tracks with `outro` and `main` bands visually indistinguishable.

## Hypothesis
- Adding a **post-snap edge expansion** pass that walks each break/peak edge outward while the adjacent phrase's `(RMS×, opb, H×, P×)` still matches the label's criteria would absorb the missed-peak phrases on both sides of Baila's M125–M135 peak.
- Widening the sub-splitter to (a) walk multi-section same-label runs, (b) drop the shift floor from 0.18 to 0.10 on long runs, (c) switch to a weighted L2 shift (ΔRMS, ΔH×, ΔP×, Δopb/5) would surface subsection boundaries the RMS-only detector misses.
- A dedicated **embedded-break scanner** that classifies *each phrase* inside long main sections against the track medians (using the Phase 6 branch rules) would catch transient dips whose aggregate section signal still reads "main-like" — the Baila P58 case.
- A stronger `outro` colour would resolve the low-alpha ambiguity without touching the rest of the palette.

## What changed
- [src/rytmi/dsp.py](../../src/rytmi/dsp.py): new `_expand_label_edges_on_signal()` pass after `_snap_boundaries_to_phrases()`; rewritten `_split_long_runs_on_phrase_shifts()` walking runs across same-label sections with weighted L2 shifts and `_SUBSPLIT_MIN_GAP_PHRASES=2` sliver guard; new `_classify_break_branch()` helper and `_split_embedded_breaks()` scanner, wired alongside the sub-splitter in `detect_sections()`.
- [src/rytmi/viz.py](../../src/rytmi/viz.py): `SECTION_COLORS` palette refresh — `outro` deepened from `#b39ddb` to `#7b5aa6`, `main` darkened slightly, `break`/`build`/`peak` warmed.
- [tests/test_dsp.py](../../tests/test_dsp.py): 7 new tests — three for edge expansion (`extends_break_into_supporting_phrase`, `stops_at_unsupported_phrase`, `respects_neighbour_interior`), two for sub-splitter widening (`walks_multi_section_same_label_run`, `respects_min_gap`), two for embedded-break scanner (`isolates_phrase_level_drop_inside_main`, `noop_on_steady_main`).
- [tests/test_viz.py](../../tests/test_viz.py): `test_section_colors_outro_and_main_distinct` asserting perceptual channel gap ≥ 40.
- [notebooks/05_batch_analysis.ipynb](../../notebooks/05_batch_analysis.ipynb): new markdown cell at position 0 carrying the `v0.8 — phase 8 — 2026-04-17` version stamp.
- [docs/eval-set-guide.md](../../docs/eval-set-guide.md): expanded "Why paired tracks matter — the 'find 1 from mid-song' problem" section + section-colors reference table.
- [docs/how-it-works.md](../../docs/how-it-works.md): cross-link from the Phase 7 downbeat section to the pairing rationale.
- [docs/experiments/12-2026-04-15-phase-6-hpss-and-sub-splitter.md](./12-2026-04-15-phase-6-hpss-and-sub-splitter.md): TL;DR banner confirming the shipped Phase 6 re-derives everything from the lost iteration.

## Evidence / test results
`pytest -q` — **214 passed, 1 skipped** (was 206 passed pre-Phase-8).

Baila Kizomba Amor — `describe_sections()` before → after:
- Peak: was P63→P68 / M125→M135 but the pre-Phase-8 version often under-covered it; the Phase 8 output now reports `peak 212.2–229.1s / P63/M125 → P68/M135` — aligns with the user's "M125–M135" target.
- Embedded break at M114 / P58: a new 1-phrase section `194.7–198.2 / P58/M115→P59/M117 RMS×0.48 H×0.66 P×0.46` now appears, followed by a `build 198.2–212.2s` rising into the peak. The `main → main(low dip) → build → peak` shape matches the user's "beat drops and returns" description. The dip is labelled `main low` rather than `break` because `_BREAK_MIN_PHRASES=2` rejects single-phrase breaks; the section boundary itself is correct.
- Break at P36: still reports `break[full] 120.2–140.4s / P36/M71 → P42/M83`. The edge expander only *grows* edges, never *shrinks* them — the 1-phrase-late start requires contraction logic that wasn't implemented this phase.

Palette — visual check on any track with both `outro` and `main` bands shows `#7b5aa6` outro is unambiguously purple at 0.25 alpha against the darker `#d0d0d0` main.

## What worked
- **Peak edge expansion** on Baila — peak now covers the full M125→M135 range.
- **Embedded-break scanner** surfaces the M114 / P58 transient as a distinct `main low` section with RMS×0.48 — structurally visible in the notebook even if the label is understated.
- **Sub-splitter widening** regresses no stable tracks (all 214 tests green) and adds the multi-section walk capability for future tuning.
- **Palette refresh** decisively separates `outro` from `main` at all alphas; no test regressions on colour-count or render-bands assertions.
- **Notebook version stamp** gives a one-line reload indicator for the common "browser held the old tab" failure mode.

## What did not / limitations
- Break `P36` edge is still 1 phrase early on Baila. The edge-expansion pass only grows outward; shrinking inward is symmetric but adds complexity and wasn't in the plan's pseudocode. Deferred.
- Embedded 1-phrase dips are not labelled `break` because `_BREAK_MIN_PHRASES=2` blocks them in `_label_sections`. Relaxing that floor risks re-labelling many stable sections; deferred.
- The four subsection-change observations (Bachata Musicality M28/M44, El Chaval M19/M49, All Of Me M21+2/M26) are only partially surfaced. The sub-splitter now *could* catch them with its lower threshold, but the actual weighted shifts on these transitions are below `max(0.10, p75)` in most cases. Solving this likely needs vocal-track-separated signal or higher-order features — Phase 9.
- Ground-truth ambiguity: "change at M28" is a human ear call; without annotated ground truth we can only confirm a plausible boundary is near M28, not that the split is *exactly* where the user hears it.

## Decision / takeaway
Phase 8 shipped the larger-blast-radius fixes (peak edges, embedded dips visible as sections, palette clarity, notebook version stamp, docs on cut/official pairing) and left finer structural refinements for Phase 9. The `_BREAK_MIN_PHRASES` gate and the edge-shrink operation are the two specific items that, if revisited, would tighten the remaining gaps.

## Next step
Phase 9 candidates, in order of likely impact on user-visible correctness:
1. Downbeat-confidence metric redesign — the Phase 7 plumbing is ready but every eval track still gates to `offset=0` at `< 0.25` confidence. The All Of Me M10+4 "first 1" observation is waiting on this.
2. Edge contraction pass — symmetric to the expander, to fix the Baila P36→P37 case.
3. Vocal-track-separated subsection detector — to catch the sung-melody transitions the weighted-shift metric can't see.
4. Relax `_BREAK_MIN_PHRASES` (or introduce a `short_break` label) so 1-phrase dramatic drops surface with a break label.
5. Phase-merge post-pass to collapse chains like Charbel-4K's six consecutive `break[melodic]` rows.
