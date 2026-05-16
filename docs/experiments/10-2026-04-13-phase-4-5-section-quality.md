# 2026-04-13 — Phase 4.5: section quality (diagnostic + phrase-snap + energy encoding)

## Goal
Start closing the gap between DSP section boundaries and what a dancer actually hears, by (1) making the underlying signals visible, (2) aligning boundaries to the 8-count phrase grid the learner already thinks in, and (3) showing per-phase energy on the timeline.

## Context / prior state
Phase 4 (experiment note 09) shipped colored section bands, S1/S2/S3 labels with time ranges, a reset button, a seek slider, and the cursor-alignment fix. Every band was drawn at a single `alpha=0.25`, and DSP boundaries were whatever `detect_sections()` produced — no grid alignment, no diagnostic output.

After Phase 4 was merged, the user listened to the 7-track kizomba/bachata set again while watching the timeline and flagged concrete boundary-quality issues. Two kizomba tracks in particular:

- **`Teu_Toque`** — intro marked ending at P5/M9 while vocals actually begin at P4/M7 (really on the "8" of P3). Clear structural shifts at P9, P14, ~M38, P22/M43. Break and outro were clean.
- **`E_Magia_Ben_Ana`** — intro marked ending at M6 while vocals start at M8 (beat 4 of M7). Regular energy shifts on an 8-measure (4×8-count) grid: M16, M24, M32, M40, M48. A clear break starts ~M56 and runs to ~M72 — *entirely missed* by the DSP, which instead triggered "outro" around M66.5.

The learner's explicit asks:
1. "how and what is this section identification actually based on?"
2. "could we run this with some extra info output so the signal can be analyzed?"
3. Sections should snap to phrase-grid boundaries — mid-phrase boundaries feel wrong.
4. Long homogeneous `main` runs hide real sub-structure.

The original post-Phase-4 plan had been to add energy encoding to the timeline as a cosmetic polish. The feedback refocused the iteration on *section quality* instead.

## Hypothesis
A **measure-then-fix** bundle is the right first move. Each part is small and safe, and together they address the feedback while keeping follow-up work unblocked:

- **A1 — diagnostic helper** directly answers the learner's "based on what?" question and gives future iterations a baseline to A/B against.
- **A2 — phrase-grid snapping** is the single lowest-risk structural fix: it does not invent new boundaries, it only aligns existing ones to the grid the learner already thinks in. 8-beat snap only; 32-beat structural snap is too aggressive as a default.
- **A3 — energy encoding** is the visual complement — once boundaries are snapped, showing *why* a phase is labeled "main" is a small next step.

Explicitly **not** in scope for this pass: splitting long `main` runs into sub-phases on an energy grid (Option B), refining intro boundaries from transcription vocal-onset timing (Option C). Both depend on having A1 in place first so their effect is measurable.

## What changed
**`src/rytmi/types.py`:**
- Added optional `raw_start_s: float | None` and `raw_end_s: float | None` to `SongSection` to preserve pre-snap boundaries when phrase-grid snapping moves them. Documented in the dataclass docstring.

**`src/rytmi/dsp.py`:**
- New module constants: `_PHRASE_LENGTH_DEFAULT = 8` and `_SNAP_MAX_DRIFT_BEATS = 8.0`.
- New helper `_snap_boundaries_to_phrases(sections, beats, phrase_length=8, max_drift_beats=8.0)`. Snaps each **interior** section boundary (not the track's first start or last end) to the nearest phrase boundary on `beats.times[::phrase_length]`. Enforces a drift threshold (boundaries more than 8 beats from the grid stay put) and monotonicity (a snap that would cross the previous boundary or the fixed last-end is reverted). Preserves the original value on `raw_start_s` / `raw_end_s` when it actually moves a boundary.
- New public helper `describe_sections(analysis) -> str`. Returns a formatted text table — one row per `SongSection` — with: index, label, energy, start/end in seconds, start/end in P#/M# coordinates, drift in beats from the nearest phrase boundary (marked with `*` when snapping moved the boundary), duration in seconds and phrases, RMS ratio vs global mean, and onset density (onsets per beat) over the section.
- Modified `analyze()` to accept `snap_to_phrase_grid: bool = True`. When true, `_snap_boundaries_to_phrases()` runs on the raw sections before `merge_adjacent_sections()`.

**`src/rytmi/viz.py`:**
- Added module-level dicts: `_ENERGY_ALPHA = {"low": 0.15, "medium": 0.30, "high": 0.50}`, `_ENERGY_CHIP = {"low": "▁", "medium": "▄", "high": "█"}`, plus rank tables for the dominant-energy calculation.
- New helper `_dominant_energy(energy_levels)`: mean of section energy ranks, rounded half-up (tie `[medium, high]` → `high`, `[low, low, medium]` → `low`, empty → `medium`).
- `plot_timeline()` band rendering now uses `_ENERGY_ALPHA[_dominant_energy(ph.energy_levels)]` instead of a hard-coded `alpha=0.25`. The energy chip is appended to each S# label (`S2: main ×3 ▄`). The legend adds one grey `Patch` per energy level actually present in the phases — no spurious entries for unused energies.

**`tests/test_dsp.py`:** Added 8 tests under `# --- phrase-grid snapping tests ---` and `# --- describe_sections tests ---` covering:
- boundary at 8.7 s snaps to 8.0 s when the phrase grid is regular;
- drift above the safety threshold is preserved (`max_drift_beats=1.0` on a 2-beat drift → no snap);
- the first section start and the last section end are never moved;
- snapping is a no-op for fewer than 2 sections;
- `analyze(snap_to_phrase_grid=True)` populates `raw_start_s` / `raw_end_s` while `snap_to_phrase_grid=False` leaves them `None`;
- `describe_sections()` returns a non-empty table that names every section index and label, and handles the empty-sections case.

**`tests/test_viz.py`:** Added 4 tests under `# --- Phase 4.5: energy-level encoding on timeline ---`:
- alpha scales with dominant energy (`low` < `high` on the same figure);
- legend contains swatches for energies actually present;
- `_dominant_energy` rounds ties up;
- tracks without phases produce no energy legend entries.

**`notebooks/05_batch_analysis.ipynb`:** New cell `## 2c. Section diagnostic table` that iterates over the per-track results and prints `describe_sections(result)` for each, so the learner can read the same signals the DSP used.

**`docs/how-it-works.md`:** New "Section-aware timeline visualization" block at the end, documenting the energy-alpha / energy-chip / legend behavior, the `snap_to_phrase_grid` flag and the `raw_start_s` / `raw_end_s` preservation, and the `describe_sections()` helper.

## Evidence / test results
**Tests:** 179 pytest tests pass (up from 167 at Phase 4), including the 12 new Phase 4.5 tests. Every existing Phase 4 visualization test still passes unchanged.

**Manual eval:** Ran the updated `05_batch_analysis.ipynb` over the 7-track kizomba/bachata set. The new diagnostic table prints per-track for inspection. The energy chips and graduated band alphas are visible on every track with non-uniform energies. Phrase-grid snapping moved a subset of interior boundaries — visible as `*` markers in the drift column of the diagnostic table — without breaking band rendering or the interactive player's cursor alignment.

## What worked
1. **`describe_sections()` directly answers the learner's question.** Having the RMS ratio, onsets-per-beat, and phrase-drift for every section in one table makes it possible to look at a section the ear disagrees with and see *which* signal (energy shift vs onset density vs snap drift) produced it. This was the single change that most changed "I have no idea why" into "I can see it."
2. **Phrase-grid snapping is safe.** The drift threshold and monotonicity check mean the helper never produces degenerate or overlapping sections, and the `raw_start_s` / `raw_end_s` fields let the diagnostic show exactly which boundaries moved and by how much. Existing Phase 4 visualization tests passing unchanged confirms backward compatibility.
3. **Energy-alpha gradient works.** Even on tracks where the phase label stays `main`, the visual density of the band now carries the sub-phrase energy trend at a glance. The legend-filtering logic keeps it honest — no `high` swatch appears on a track that has no high-energy phases.
4. **The bundle stayed out of DSP novelty/RMS extraction entirely.** No prompt changes, no `llm.py` changes, no `detect_sections()` internals changed. Pure add-ons around the existing pipeline.

## What did not work / limitations
1. **Phrase-grid snapping does not fix the specific learner observations on `Teu_Toque` and `E_Magia_Ben_Ana`.** On `Teu_Toque` the intro boundary at P5/M9 is *already* on a phrase boundary; it's just the wrong phrase boundary. On `E_Magia_Ben_Ana` the M6 intro end and the missed M56 break are structural misses, not drift. The 8-beat snap is correct as a general cleanup but cannot move a boundary by a full 8 measures or invent a missing one. This is the core reason the plan explicitly flagged Options B (sub-main splitting) and C (vocals-onset refinement) as the next iterations.
2. **`rhythm_features` are still computed from the raw, pre-snap section window.** Because snapping typically moves a boundary by less than one phrase and rhythm features are aggregate stats, this is acceptable for now, but a future pass could recompute per-section features after snapping.
3. **The diagnostic table is notebook-only text output.** It does not yet render inside the matplotlib timeline or the interactive HTML player; a learner has to scroll to the diagnostic cell to correlate a visible band with its underlying numbers.
4. **32-beat (4×8) structural snapping is out of scope.** The learner's observations show that kizomba structure often lands on 32-beat phrases, but snapping at 32 beats is too aggressive as a default — revisit after A2's 8-beat snap is validated on more tracks.
5. **No before/after quantitative metric.** "Did snapping improve things?" is currently a qualitative judgement from reading the diagnostic table; we do not yet have a regression suite of annotated section boundaries to score against.

## Decision / takeaway
**Phase 4.5 is the right size for one pass and earns its keep even though it does not close the two specific gaps the learner flagged.** The diagnostic helper is the durable win — it is the foundation every subsequent section-quality iteration will iterate against. Phrase-grid snapping is a low-cost general tidy-up; energy encoding is a cheap visualization polish that removes a real information gap in the Phase 4 chart. Together they cost no risk to existing functionality and unblock the real fixes (Options B and C).

The two specific learner observations (intro snapping to vocal onset, missed breaks inside long `main` runs) are **not** fixed by this pass and are now explicitly queued as Options C and B respectively.

## Next step
1. **Option B — sub-main splitting.** Use the diagnostic table to eyeball where the real energy shifts sit inside a long `main` phase, then extend `detect_sections()` (or add a post-pass) to split the run when RMS/novelty crosses a threshold on an 8- or 16-measure grid. This is what would surface the M16/M24/M32/M40/M48 shifts on `E_Magia_Ben_Ana` and — by forcing a new boundary at the right place — should also catch the missed M56 break.
2. **Option C — vocals-onset → intro boundary refinement.** The transcription pass already selects a vocal clip and has a notion of when vocals start. Surface that timestamp and snap the intro end to the nearest phrase at or before it. This directly addresses the `Teu_Toque` P5→P4 and `E_Magia_Ben_Ana` M6→M8 observations.
3. **Option D — compare-two-songs notebook flow.** Still in the demo-story backlog for the Kaggle pitch.
4. **Regression suite.** Pick 3–5 annotated boundaries from the current eval set (e.g. "intro ends at M7 on `Teu_Toque`") and turn them into a `tests/test_eval_section_quality.py` fixture so future boundary changes can be scored, not eyeballed.
