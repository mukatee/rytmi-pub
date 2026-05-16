# 2026-04-20 — Beat clarity scoring per section

## Goal
Add a per-section "beat clarity" score so the system can tell learners where the beat is easy vs. hard to hear — the key feature for kizomba-mode analysis (see direction change in experiment 23).

## Context / prior state
- `RhythmFeatures` already had per-section `beat_strength_pattern`, `percussiveness`, and `tempo_stability` — all relevant signals for beat clarity, but no combined score.
- `describe_sections()` showed RMS, opb, H×, P× but no clarity indicator.
- Phase 15b concluded that kizomba downbeat detection is the wrong problem; beat clarity is the right one.

## What changed
- Added `beat_clarity: float` (0–1) to `RhythmFeatures` in `src/rytmi/types.py`
- Added `_beat_clarity()` helper in `src/rytmi/dsp.py` — geometric mean of three signals:
  - Beat-strength contrast: `1 - 1/(max/mean)` of the beat-position pattern (0 when flat)
  - Percussiveness: HPSS percussive fraction (already 0–1)
  - Tempo regularity: `1/(1 + tempo_stability_CV)`
- Wired into both `compute_rhythm_features()` and `compute_rhythm_features_windowed()`
- Surfaced as `BC=` column in `describe_sections()` output
- Added 7 tests in `TestBeatClarity` class in `tests/test_dsp.py`

## Evidence / test results
- 323 tests pass, 0 failures (full suite excluding test_gemma_downbeat)
- Unit tests cover: clear signal (>0.4), flat pattern (==0), no percussion (==0), unstable tempo comparison, both feature functions, empty pattern edge case

### Eval set validation (16 tracks)
BC scores across the eval set show meaningful variation:
- **Lowest**: Bonga (semba roots, user "can't find beat") — BC_mean=0.251, min=0.145
- **Highest**: Don Kikas (sensual, clear percussion) — BC_mean=0.421, max=0.530
- **Break sections**: E Magia Official has a 38s break section with BC=0.00 (no beats detected)
- **Teu Toque**: the severe break section drops to BC=0.18
- Bachata tracks cluster 0.27–0.34 mean; kizomba 0.25–0.42 (wider spread, as expected)
- Per-section variation within tracks: typically 0.15–0.20 range, which should give Gemma enough signal to coach "this section is harder to hear"

## What worked
- The geometric mean naturally handles the "all signals must contribute" requirement — any zero input collapses the score to 0.
- No new DSP computation needed; purely derived from existing per-section features.
- Bonga scoring lowest validates the score against the user's listening experience.
- E Magia Official's 0.00 section correctly catches a no-beat passage.

## Limitations
- BC scores are compressed in the 0.2–0.5 range for most music — the full 0–1 range isn't well utilized.
- The three sub-scores are weighted equally (geometric mean); may need tuning.
- No per-style normalization — what counts as "clear" may differ between bachata and kizomba.

## Wiring into prompts and visualization
- **Prompts**: Added `beat_clarity` to both whole-song `_format_rhythm_features_section()` (with learner-friendly label: "very subtle"/<0.2, "moderate"/<0.35, "clear"/≥0.35) and per-section detail lines in `_format_sections_block()`.
- **Viz**: Added a red→yellow→green color strip along the bottom of the onset-strength panel in `plot_timeline()`, with BC legend entries.

## Next step
- Test with Gemma to see if the BC score in the prompt actually changes the coaching output.
- Consider per-style BC normalization if the compressed range becomes a problem.
- Consider adding BC to the phase-level summary (currently only per-section).
