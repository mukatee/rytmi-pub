# 2026-04-12 — Phase 1 & 2: style input pivot, segmentation DSP

## Goal
Phase 1: Stop guessing dance style — accept it as user input, provide style-aware coaching.
Phase 2: Add song segmentation DSP — detect rhythmically distinct sections (intro/main/break/build/peak/outro) with per-section energy and rhythm features.

## Context / prior state
- Prompt keys were renamed from `style` to `style_fit` in code.
- Notebook `05_batch_analysis.ipynb` still requested `"style"` in `QUESTIONS`.
- Running the notebook produced `KeyError: 'style'` when building:
  `questions = {k: ALL_QUESTIONS[k] for k in QUESTIONS}`.

## Hypothesis
If notebook config and question key handling are aligned to `style_fit` (with a temporary compatibility alias for `style`), notebook runs will be stable while supporting older configs.

## What changed
- `src/rytmi/types.py`
  - Added `StyleProfile` and `SongSection` dataclasses.
  - Added `dance_style` and `sections` fields on `RhythmAnalysis`.
- `src/rytmi/styles.py`
  - Added style profiles (`bachata`, `kizomba`, `semba`) and beat-accent description helpers.
- `src/rytmi/dsp.py`
  - `analyze()` now accepts `dance_style` and stores it in `RhythmAnalysis`.
  - **Phase 2**: Added `detect_sections()` — novelty-based segmentation into dancer-oriented sections.
  - Added `compute_rhythm_features_windowed()` — per-section rhythm features.
  - Added `_compute_novelty_curve()`, `_segment_boundaries()`, `_energy_level()`, `_label_sections()`.
  - `analyze()` now calls `detect_sections()` and populates `sections` field.
  - Added `scipy.signal.find_peaks` dependency for boundary detection.
- `src/rytmi/prompts.py`
  - Replaced `style` question key with `style_fit` in `ALL_QUESTIONS`.
  - Added style-section formatting and `{style}` placeholder filling.
  - **Phase 3**: Added `_format_sections_block()` — formats per-section data with coaching hints into prompt.
  - **Phase 3**: Added `QUESTION_SECTIONS` template for per-section dance coaching.
  - **Phase 3**: Updated `format_analysis_prompt()` with `sections` and `style_profile` parameters.
  - **Phase 3**: Updated `RHYTHM_ANALYSIS_TEMPLATE` with `{sections_block}` placeholder.
- `src/rytmi/llm.py`
  - `explain_rhythm()` now forwards `dance_style` + style context from profile.
  - **Phase 3**: `explain_rhythm()` now passes `sections` and `style_profile` to prompt formatter.
  - `explain_all()` now iterates `ALL_QUESTIONS` directly (no STYLE->DANCER chaining).
- `notebooks/05_batch_analysis.ipynb`
  - Updated default `QUESTIONS` to use `"style_fit"`.
  - Added `STYLE_TAG_MODE = "folder"` — infer style from subfolder name per track.
  - Added `DANCE_STYLE` → `FIXED_DANCE_STYLE` (optional fixed mode).
  - Summary table now shows Style and Sections columns.
  - **Phase 3**: Added `"sections"` to default QUESTIONS list.
  - **Phase 3**: LLM cell shows section summary in per-track header and uses higher token budget for sections question.
- `pyproject.toml`
  - Added explicit `scipy>=1.14` dependency.
- Tests
  - Added `tests/test_styles.py`.
  - Updated `tests/test_llm.py` for new key names and style-aware prompt behavior.
  - Added segmentation tests to `tests/test_dsp.py`.
  - **Phase 3**: Added 8 section-prompt tests to `tests/test_llm.py`.

## Evidence / test results
Commands run:

```bash
.venv/bin/python -m pytest -v
```

Result:
- `148 passed, 1 skipped`.

## What worked
- The `KeyError: 'style'` mismatch is resolved.
- Notebook now supports both current (`style_fit`) and legacy (`style`) key names.
- Style-aware prompt plumbing is active end-to-end through analysis and explanation.
- Segmentation produces dancer-oriented sections (intro/main/break/build/peak/outro) with energy labels and per-section rhythm features.
- Novelty-curve boundary detection works on real-world-like synthetic audio with energy contrast.

## What did not work / limitations
- Phase 2 segmentation boundaries depend on `_MIN_SECTION_S = 6.0` and `smooth_window = 21` — these heuristics may need per-style tuning later.
- Uniform-energy tracks (like a pure click track) produce a single section, which is correct but means sections are most useful on real music.
- `STYLE_TAG_MODE = "folder"` in the notebook is a single run-level setting, not per-track — but the folder inference gives per-track style.
- Section coaching hints from `StyleProfile` are not yet injected into prompts (Phase 3).
- Sections are not yet shown in the timeline visualization (Phase 4).

## Decision / takeaway
Phases 1–3 are complete. Style-as-input, segmentation DSP, and section-aware prompting are all stable and wired end-to-end. The LLM now receives per-section coaching hints grounded in both DSP data and style profiles.

## Next step
- Phase 4: section-aware visualization — add section overlay bands to `viz.py` timeline.
