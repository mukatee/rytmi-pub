# 2026-04-13 — Phase 4: section-aware visualization

## Goal
Make section/phase information visually clear and actionable in the interactive timeline, so learners can correlate Gemma text descriptions (which cite section names and time ranges) with the actual waveform markers and colored sections.

## Context / prior state
Phase 3.5 delivered section-aware Gemma coaching text that mentions intro, main, break, build, peak, outro sections with time ranges (e.g. "intro 0–12s, main 12–45s"). However, the timeline visualization only showed beat/phrase/measure markers, not the section boundaries or colored bands. Learners had no visual cue to verify the DSP section detection or to sync the Gemma description with the waveform.

## Hypothesis
Rendering colored phase bands with numbered labels and time ranges on the timeline would:
1. Give learners a quick visual confirmation of section boundaries
2. Allow easy cross-referencing between Gemma text (which says "main section") and the chart (which would show "S2: main 12–45s")
3. Help identify if DSP section detection seems reasonable for the song
4. Improve overall usability by making timeline navigation less abstract

## What changed
**src/rytmi/viz.py — plot_timeline():**
- Added `SECTION_COLORS` dict mapping section labels (intro, main, break, build, peak, outro) to distinct colors
- Render phase color bands via `axvspan()` on both waveform and onset strength panels (alpha=0.25, zorder=0 behind waveform)
- Section labels now display as "S1: intro ×2\n0–24s" (numbered, with section count and time range) in black text, centered at phase midpoint
- Label boxes use the section color background with visible border and alpha=0.45 (more opaque/visible than Phase 4 initial impl)
- Add "section" row label on the left margin when phases are present
- Increase headroom for S# labels (y_section_label positioned at 1.65× amp_max)

**src/rytmi/viz.py — interactive_timeline():**
- Fix critical cursor alignment bug: call `fig.canvas.draw()` before measuring axes bbox, because `constrained_layout` finalizes axes positions during draw, not construction
- Remove `bbox_inches="tight"` from savefig() so saved PNG anchors match figure-fraction coordinates (this was causing cursor to appear offset from the actual audio position)
- Add **Reset** button to stop playback, rewind to 0:00, and scroll to the start
- Add **seek slider** (HTML `<input type="range">`) synced bidirectionally with audio.currentTime
- Refactor JS tick() loop to use shared `updateDisplay(t)` helper, enabling consistent cursor/slider/time updates from playback, seek input, or timeline click
- Slider updates smoothly during playback via requestAnimationFrame loop

## Evidence / test results
**Notebook:** Ran `05_batch_analysis.ipynb` on the 7-track eval set (bachata, cha-cha, kizomba). Observed:
- Section bands rendered in distinct colors across all tracks
- S1/S2/S3/... numbering and time ranges visible on each band
- Reset button successfully stops playback and rewinds to 0:00
- Seek slider moves during playback and accepts manual input
- Cursor now starts at the correct position (0:00) at the left edge, not offset into the chart

**Tests:** All 167 tests pass, including 4 Phase 4 visualization tests:
```
test_section_colors_covers_all_labels ✓
test_plot_timeline_with_sections ✓
test_plot_timeline_no_sections_backward_compat ✓
test_plot_timeline_section_legend_entries ✓
```

## What worked
1. **Section numbering + time ranges** — "S1: intro 0–12s" makes it trivial to cross-reference Gemma text like "in the intro (0–12s), focus on step timing"
2. **Colored bands** immediately visible at all zoom levels (alpha=0.25 on waveform panel, 0.25 on onset strength)
3. **Black labels with colored background** — much more readable than the light-colored text on white background from early Phase 4 draft
4. **Reset button** — useful for replaying the same section or trying different controls without manual scroll
5. **Seek slider** — provides coarse timeline control without horizontal scroll friction; more intuitive than clicking the waveform for precise seeking
6. **Cursor alignment fix** — critical for learner trust; cursor now always starts at 0:00 and tracks actual playback position

## What did not work / limitations
1. **Section labeling is text-based, not a true x-axis** — labels sit above the waveform; very long songs (>5 min) may have crowded labels if many sections exist
2. **Time range display (e.g. "0–12s") is human-friendly but doesn't render seconds ticks on the x-axis** — a learner still cannot read exact seconds from the waveform grid alone; they must reference the label text
3. **Slider precision depends on audio duration** — for a 3-min track, slider has ~180 steps; for a 10-min track, only ~600 steps. Mobile browsers may struggle with precise dragging
4. **No visual indication of section energy levels** (low/medium/high) — the phase bands are purely categorical, not quantitative
5. **Seek slider does not snap to beat boundaries** — clicking the slider positions audio at any time, not necessarily at a beat; learners must use the chart or manual scrubbing to align precisely

## Decision / takeaway
**Section-aware visualization is effective and sufficient for Phase 4.** The S1/S2/S3 numbering combined with time ranges successfully bridges the gap between Gemma text descriptions and the waveform. Learners can now visually verify that the DSP detected sections correctly and can correlate the text coaching with waveform markers.

DSP section detection accuracy remains a separate concern (see Phase 3.5 experiment note); visualization alone cannot fix weak or hallucinated sections. However, making weak sections *visible* is a net positive for learner feedback and debugging.

## Next step
1. **(Short term)** Commit Phase 4 notebook results (notebook snapshot from eval set run showing improved visuals)
2. **(Medium term)** Consider adding a secondary axis tick layer for seconds, or an overlay ruler showing S1/S2 labels at the x-axis itself (not just floating text)
3. **(Medium term)** Explore adding optional phase energy level visualization (e.g. a small bar or filled dot above each S# label showing low/med/high)
4. **(Long term)** Improve section detection accuracy — Phase 3.5 note identifies that downbeat confidence is universally weak; a better downbeat detector would improve section segmentation quality
