# 2026-04-11 — Surfacing downbeat confidence in the learner flow

## Goal
Make the new `downbeat_confidence` value (added in the DSP review pass) actually
visible and useful: in the batch notebook summary, in the Gemma prompt context, and
in the test coverage that verifies the full path from DSP result to prompt text.

## Context / prior state
After the DSP review pass, `RhythmAnalysis.downbeat_confidence` existed as a float
in `[0, 1]` but was not surfaced anywhere:

- `format_analysis_prompt()` did not include downbeat times or confidence in the text
  sent to Gemma.
- `explain_rhythm()` did not forward any downbeat fields.
- The batch notebook showed tempo, beats, onsets, duration — but no "1" estimate or
  confidence indicator.
- Gemma received no signal to adjust its certainty about the phrase start.

## Hypothesis
Surfacing the confidence through the full path (DSP → prompt → Gemma → notebook)
will make Gemma's explanations more honest and help the learner understand when the
"1" estimate is reliable vs. ambiguous — without changing any DSP logic.

## What changed

### `src/rytmi/prompts.py`
- Added `downbeat_confidence_label(confidence: float) -> str` — public helper that
  maps the numeric score to a learner-friendly band:
  - `>= 0.35`  → `"high confidence"`
  - `0.15–0.35` → `"plausible guess"`
  - `< 0.15`  → `"ambiguous — treat as a weak guess"`
- Added private `_format_downbeat_section()` that builds the downbeat block
  inserted into the prompt, including:
  - the first 4 likely "1" timestamps
  - the confidence label and numeric value
  - an explicit uncertainty note when confidence is below `0.15`, instructing
    Gemma to use hedged language ("the 1 is likely around…")
- Updated `RHYTHM_ANALYSIS_TEMPLATE` to include `{downbeat_section}` after the IOI
  line.
- Updated `format_analysis_prompt()` with two optional keyword arguments:
  `downbeat_times` and `downbeat_confidence`.  Callers that omit them get the
  original prompt unchanged — fully backwards-compatible.

### `src/rytmi/llm.py`
- `explain_rhythm()` now forwards `analysis.downbeats` and
  `analysis.downbeat_confidence` to `format_analysis_prompt()`.
- Imported `downbeat_confidence_label` (available for future use or re-export).

### `notebooks/05_batch_analysis.ipynb`
- **Cell 2**: added `downbeat_confidence_label` to the `from rytmi.prompts import …`
  line.
- **Cell 9** (per-track LLM display): added a `Downbeat "1":` line to the metadata
  row shown above each track's Gemma responses, e.g.:
  ```
  Tempo: 124 BPM   Beats: 62   Onsets: 80   Duration: 30.0s
  Downbeat "1": plausible guess (0.20)
  ```
- **Cell 11** (summary table): added a `Downbeat "1"` column showing label + score
  for every analyzed track.

### `tests/test_llm.py`
Added 8 new tests:
- `test_confidence_label_high/plausible/ambiguous` — all three bands
- `test_confidence_label_boundary_between_plausible_and_high` — exact boundary
- `test_format_analysis_prompt_with_downbeat_data_no_placeholders` — no
  unfilled `{…}` when downbeat data is supplied
- `test_format_analysis_prompt_includes_downbeat_times_and_label` — times and
  label text appear in prompt
- `test_format_analysis_prompt_low_confidence_adds_uncertainty_note` — "uncertain"
  and "ambiguous" appear when confidence < 0.15
- `test_format_analysis_prompt_high_confidence_no_uncertainty_note` — no
  "uncertain" text when confidence is high
- `test_format_analysis_prompt_no_downbeat_args_still_clean` — omitting the new
  args gives a clean prompt with no downbeat section
- `test_explain_rhythm_prompt_contains_downbeat_data` — end-to-end integration
  check: `explain_rhythm()` on a real `analyze()` result includes "downbeat" and
  "confidence" in the captured prompt

## Evidence / test results

```
$ .venv/bin/python -m pytest tests/test_llm.py tests/test_dsp.py -v
48 passed in 5.03s
```

Sample of the actual prompt text now sent to Gemma for a high-confidence track:

```
- Inter-onset intervals (first 8, ms): 595, 485, 490, 480, ...
- Likely downbeat / "1" times (first 4, seconds): 0.50, 2.40, 4.35, 6.30 ... (5 total)
- Downbeat estimate confidence: high confidence (0.41)

Small differences in timing (under ~25 ms) are measurement noise...
```

For a low-confidence (ambiguous) track:

```
- Likely downbeat / "1" times (first 4, seconds): 0.50, 2.40, 4.35, 6.30 ... (5 total)
- Downbeat estimate confidence: ambiguous — treat as a weak guess (0.04)

Note: the downbeat position is uncertain for this track. The analysis could not
clearly identify which beat is the "1". When discussing where the phrase starts or
where to step on "1", use hedged language (e.g. "the 1 is likely around...", "you
may need to listen for the downbeat rather than relying on this estimate").
```

## What worked
- The full DSP → prompt → Gemma path now carries uncertainty context from end to end
  without any change to the DSP logic.
- Backwards compatibility is complete: callers that don't supply downbeat args get
  the original prompt.
- The explicit uncertainty note is phrased as an instruction to Gemma, not as a
  disclaimer to the user — this is more likely to produce hedged language in the
  actual Gemma output.
- The confidence label (`downbeat_confidence_label`) is importable for use in
  notebooks and future visualization code.

## What did not work / limitations
- **Threshold calibration is still provisional.** The `0.15` / `0.35` boundaries
  were set based on synthetic click-track experiments, not real bachata, kizomba, or
  salsa tracks.  After real-music evaluation, these may need to shift.
- **Gemma's response to the uncertainty note has not been verified.** The note
  steers the model correctly in principle, but actual Gemma outputs have not been
  collected with the new prompt — that requires a live model run.
- **The visualization layer (`viz.py`) still does not show the confidence label.**
  The interactive timeline marks downbeats visually but does not annotate them with
  the confidence score.  That is the next natural extension.
- **Only one `beats_per_measure` is tried.**  The prompt still says `4/4 (assumed)`;
  there is no 3/4 vs 4/4 disambiguation yet.

## Decision / takeaway
The confidence signal is now end-to-end connected.  The design pattern — DSP
computes a score, a small helper maps it to a learner label, the prompt carries the
label and optionally an uncertainty instruction — is clean enough to reuse for other
uncertainty sources (e.g., tempo stability, onset density variance).

## Next step
1. Run a live Gemma inference session with the new prompt on a few bachata and
   kizomba tracks to observe whether the hedged vs. confident wording actually
   appears in the model output.
2. Calibrate the `0.15` / `0.35` thresholds against real-music confidence values
   once an eval set is in place.
3. Extend `viz.py` to annotate the downbeat markers with the confidence label.
