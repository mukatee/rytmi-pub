# 2026-04-14 — Phase 5: percentile-based section labels + signal-aware break/peak detection

## Goal
Close the gap the Phase 4.5 diagnostic table exposed: the DSP was producing varied RMS and onset-density signals per section, but the classifier was collapsing almost every section to `main medium` on real dance tracks. Fix the classifier so the labels reflect what the signals already say — *without* touching the segmenter or inventing new boundaries.

## Context / prior state
Phase 4.5 shipped `describe_sections()`, phrase-grid snapping, and energy encoding. The learner ran the new diagnostic (cell 2c in `05_batch_analysis.ipynb`) on the 7-track kizomba/bachata eval set and the output made the failure mode immediately visible:

| Track | Sections | break/build/peak count | RMS range | Notable |
|---|---|---|---|---|
| 1. `Bachata_Musicality_12` (129 BPM) | 14 | 0 | 0.78 – 1.10 | Every mid section → `main medium` |
| 2. `Grupo_Extra_Me_Emborrachare` (123 BPM) | 17 | 0 | 0.52 – 1.27 | Sec 12 at RMS×1.27 labeled `main`; near-silent sec 1 also `main` |
| 3. `Romeo_Santos_Propuesta_Indecente` (123 BPM) | 23 | build/peak/main-high present | 0.31 – 1.32 | Only track where the classifier fired |
| 4. `All_Of_Me` (112 BPM) | 20 | 0 | 0.81 – 1.22 | All mid sections `main medium` |
| 5. `Baila_Kizomba_Amor` (144 BPM) | 25 | 1 break | 0.53 – 1.20 | Break correctly caught at RMS×0.53 |
| 6. `Charbel_E_Magia_Ben_Ana` (96 BPM) | 16 | 0 | 0.72 – 1.18 | **Sec 14 at RMS×0.72 opb=1.1, 30.6 s — clearly break-like, labeled `main`** |
| 7. `Tony_Pirata_Filomena` / Teu_Toque (123 BPM) | 18 | 1 break | 0.46 – 1.20 | Break at RMS×0.46 correctly caught |

The core defect sat in two places in [`src/rytmi/dsp.py`](../../src/rytmi/dsp.py):

- **`_energy_level()`** used fixed ratios `< 0.6×` / `> 1.3×` to decide low/high. Dance music's compressed dynamic range rarely reaches those thresholds → everything becomes `medium`.
- **`_label_sections()`** decided break/peak/build by mapping the already-collapsed 3-bucket energy *back* to ranks, so the raw per-section RMS and onset density — the informative signals — were discarded before the label decision ever saw them.

## Hypothesis
Replace the classifier, not the segmenter. A **per-track percentile** energy classifier + a **signal-aware labeller** that reads raw RMS ratio and onsets-per-beat against track medians should:

1. Give tracks with compressed dynamic range actual low/medium/high distribution.
2. Catch the missed Track 6 break at 30.6 s.
3. Not regress the already-correct Track 3 / Track 5 / Track 7 breaks.
4. Produce richer middle-track structure (`build → peak` arcs) on tracks that currently collapse to one long `main` run.

Not in scope: inventing new boundaries (still Option B), vocals-onset intro refinement (Option C), compare-two-songs flow (Option D).

## What changed

**`src/rytmi/dsp.py`:**
- New constants and helper `_classify_section_energies(seg_rms_ratios, *, low_pct=30.0, high_pct=75.0, low_ceiling=0.85, high_floor=1.10, min_sections=4)`. Computes per-track percentiles and assigns `low` / `medium` / `high`, with absolute floor/ceiling guardrails so flat tracks don't get a spurious split from percentile noise. Falls back to `_energy_level()` when `len(ratios) < 4` so synthetic click fixtures stay stable.
- New helper `_segment_opb(start_s, end_s, onset_times, beat_times)` factoring out the onsets-per-beat calculation so both the classifier path and `describe_sections()` share it.
- Rewrote `_label_sections()` with a new 5-tuple input signature `(start, end, energy_category, rms_ratio, opb)` and three-pass decision logic. Decision thresholds are **track-relative**:
  - **break** — duration ≥ 2 phrases AND *either* (a) severe RMS drop alone (`rms_ratio < 0.60 × median_rms`) — catches kizomba melodic drops where percussion stays up — *or* (b) moderate drop (`< 0.85×`) combined with low onset density (`opb < 0.70 × median_opb`).
  - **peak** — `rms_ratio > 1.05 × median_rms` AND `opb > 1.00 × median_opb` AND highest-RMS section in the middle half of the track.
  - **build** — a `main` immediately before a `peak` with strictly rising RMS.
- `detect_sections()` now computes per-segment `rms_ratio` and `opb` directly from `beats` / onsets and passes the 5-tuple into the new classifier and labeller. The median inter-beat-interval is used to compute `min_break_s` tempo-adaptively.
- `merge_adjacent_sections()` extended: a run of same-label sections also splits when the per-section energy category changes, guarded by a "both sides of the split must be ≥ 2 sections" rule so a single high-energy blip does not fragment a phase.

**`tests/test_dsp.py`:** 10 new tests under `# --- Phase 5: percentile energies & signal-aware labels ---` covering:
- percentile classifier assigns low/medium/high distribution on varied ratios;
- flat-track input collapses to all-medium via the ceiling/floor guardrails;
- `< 4` sections routes to the legacy `_energy_level()` fallback;
- break fires on low-RMS + low-OPB center section;
- break fires on severe RMS drop alone (high-OPB kizomba case);
- break respects the 2-phrase minimum duration;
- peak fires on high-RMS + high-OPB center section;
- build fires on a `main` immediately before a peak with rising RMS;
- intro and outro are always positional regardless of signal levels;
- `merge_adjacent_sections()` splits a same-label run on an energy-category change when both sides are ≥ 2 sections.

**`docs/how-it-works.md`:** Two new subsections under "Section-aware timeline visualization" documenting the percentile classifier and the signal-aware labeller.

## Evidence / test results

**Tests:** 189 pytest tests pass (up from 179 at Phase 4.5), with 10 new Phase 5 tests added. Every existing test continues to pass unchanged — the `_energy_level()` fallback for `< 4` sections is what keeps the synthetic click-track fixtures stable.

**Manual eval on the 7-track set** (re-run of the same 2c diagnostic after Phase 5 landed):

| Track | Before (Phase 4.5) | After (Phase 5) | Target |
|---|---|---|---|
| 1. 129 BPM `Bachata_Musicality_12` | 14 sections, all `main medium` | One `main high` at sec 7; still no break/peak (uniform track) | varied energies |
| 2. 123 BPM `Grupo_Extra` | 17 sections, all `main medium` | `main high` at sec 4, 12, 13; outro `low` | varied energies |
| 3. 123 BPM `Romeo_Santos` | `break low` at 1, `main high` cluster, `build high → peak high` at 11→12 | **Identical** — no regression | preserved |
| 4. 112 BPM `All_Of_Me` | 20 sections, all `main medium` | `main high` at 3, 11, 15, 16; `build medium → peak high` at 7→8; `main low` at 13 | varied + build/peak arc |
| 5. 144 BPM `Baila_Kizomba` | `break low` at 10 (20.2 s) | `break low` at 10 preserved, **plus** `peak high` at 17 and `main high` 18–20 | break preserved, peak added |
| 6. 96 BPM `Charbel_E_Magia_Ben_Ana` | 16 sections, all `main medium` | **`break low` at sec 14 (30.6 s, RMS×0.72, opb=1.1)** + `main high` at 5, `build high → peak high` at 11→12, `main high` at 13 | **target break caught** |
| 7. 123 BPM `Tony_Pirata` / Teu_Toque | `break low` at 12 (RMS×0.46) | **`break low` at 12 preserved**, plus `main high` at 4, 5, 10, 11, 14 | break preserved, varied energies |

Full before/after diagnostic tables for all 7 tracks are reproducible by running `python tmp/run_phase5_eval.py`.

## What worked

1. **The learner's target break is now caught.** Track 6 section 14 — RMS×0.72, opb=1.1, 30.6 s duration — was the single clearest "missed break" in the Phase 4.5 diagnostic. It now fires correctly via the moderate-drop branch (RMS < 0.85× median AND opb < 0.70× median opb). This is the headline result.
2. **The severe-drop branch rescued the Track 7 regression.** The first version of `_label_sections()` required BOTH low RMS AND low OPB, which killed the pre-existing Track 7 `break` at section 12 (RMS×0.46, but opb=2.7 because tumba and congas keep playing through the melodic drop). Adding a "severe RMS drop alone → break" branch fixes this class cleanly: kizomba melodic breaks often have percussion still going, and the < 0.60× RMS threshold is a strong enough signal on its own.
3. **Percentile classifier solved the medium monoculture.** Tracks 1, 2, 4 that previously collapsed to all-medium now show a legitimate distribution of high/medium/low. The absolute floor/ceiling guardrails (`0.85×` / `1.10×`) keep the flat-track test from producing false low/high entries.
4. **Track-relative medians were the right move for break/peak thresholds.** A kizomba break at RMS×0.72 would never cross a global threshold of `0.60×`, but it crosses `0.85× × median = 0.85 × 0.97 ≈ 0.82`, which is exactly where the moderate-drop branch fires. The same relative-threshold logic is why the bachata breaks at RMS×0.46 / RMS×0.55 still catch on their tracks.
5. **No prompt changes, no segmenter changes, no `llm.py` changes.** The entire Phase 5 bundle is a classifier rewrite behind the existing `detect_sections()` → `merge_adjacent_sections()` pipeline. Backward compatibility is a non-issue because the 5-tuple signature is purely internal.

## What did not work / limitations

1. **Long genuinely-uniform `main` runs still look flat.** Track 1 has 12 mid sections that really *are* all close to `main medium` — no percentile trick can invent structure that is not in the signal. The new energy-split merge does not fire because the same-label run lacks sustained energy transitions on both sides. The real next step for this class of track is **Option B (sub-main splitting)**, which inserts new boundaries on RMS/novelty shifts inside long same-label runs.
2. **Phrase-grid and novelty misses are unchanged.** The `E_Magia_Ben_Ana` M56 break that the novelty curve never triggered on is still missed — Phase 5 can only relabel existing sections, not invent them. Same for `Teu_Toque`'s intro boundary at the wrong phrase. Those are Options B and C.
3. **Energy labels are unstable across segmenter changes.** A percentile classifier by definition depends on the full section list — if a future change adds or removes a section, the percentiles shift and some labels could flip. The absolute floor/ceiling guardrails keep the extremes stable, but any track that sits close to the 30th / 75th percentile is on the boundary. This is the cost of the track-relative design; the floor/ceiling rule is the main mitigation.
4. **Peak detection is single-shot.** `_label_sections()` picks the one best peak in the middle half; tracks that genuinely have two climaxes (verse-chorus / chorus-chorus') can only label one of them. Acceptable for now — the learner feedback has not asked for multi-peak yet.
5. **`rhythm_features` are still computed on the raw, pre-snap section window** — unchanged from Phase 4.5. Phase 5 did not touch this.
6. **No annotated-boundary regression suite.** Current verification is still "run the eval, read the diagnostic, compare rows." A proper `tests/test_eval_section_quality.py` with 3–5 hand-annotated expectations from the 7-track set would turn this into a scored check instead of an eyeball check.

## Decision / takeaway

**Phase 5 is the right classifier fix for Phase 4.5's diagnostic to land against.** It closes the headline gap (Track 6 missed break), preserves every correct label from the earlier system, and surfaces genuine middle-track structure on tracks where it existed but was being hidden by the old collapsed-energy pipeline. Every other structural gap the learner flagged is now explicitly attributable to missing boundaries, not missing labels — which is exactly the cleaner baseline Option B needs to build on.

The severe-drop-alone break branch is a notable lesson: real-world break detection needs a *disjunction*, not a *conjunction*, of low-RMS and low-OPB, because kizomba and bachata handle breaks very differently. Kizomba often drops the melody while the tumba keeps playing; bachata often drops everything. A single conjunctive rule would always bias toward one or the other.

## Next step

1. **Option B — sub-main splitting.** Now that Phase 5 has established a percentile baseline, the next iteration should split long same-label runs on RMS/novelty transitions on an 8- or 16-measure grid inside the run. This is the only thing that can surface the `E_Magia_Ben_Ana` M16/M24/M32/M40/M48 sub-structure and the missed M56 break.
2. **Option C — vocals-onset intro refinement.** Surface the transcription pass's vocal-start timestamp and snap the intro end to the nearest phrase at or before it. Directly addresses the `Teu_Toque` P5→P4 and `E_Magia_Ben_Ana` M6→M8 observations.
3. **Regression suite.** Pick 3–5 annotated boundaries from the current eval set (e.g. "Track 6 has a `break` at M28 lasting ~6 phrases"; "Track 3 intro ends on P5") and turn them into a pytest fixture so future iterations can be scored, not eyeballed.
4. **Gemma sanity check.** Run STYLE and DANCER on at least one of the newly-labeled tracks (e.g. Track 4's build/peak arc) and confirm the coaching reads coherently. The prompt formatter already handles all six labels, so no `llm.py` change is expected — but this is cheap insurance against tone drift from the richer label distribution.
