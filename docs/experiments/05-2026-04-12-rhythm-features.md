# 2026-04-12 — DSP rhythm features for style disambiguation

## Goal

Give Gemma concrete numerical signals (onset density, percussiveness, beat
accent pattern, spectral brightness, tempo stability) instead of vague
instructions like "use onset density as a tiebreaker".  This targets the
BPM-overlap confusion between bachata/cha-cha (120–130 BPM) and kizomba/zouk
(85–110 BPM) that persisted even after language detection was added.

## Changes made

### Phase 1 — DSP features
- `RhythmFeatures` dataclass in `src/rytmi/types.py` with 7 fields:
  `onsets_per_beat`, `beat_strength_pattern`, `percussiveness`,
  `spectral_centroid_mean`, `tempo_stability`, `ioi_median_ms`, `ioi_std_ms`.
- `_beat_position_strengths()` extracted from `detect_downbeats()` in
  `src/rytmi/dsp.py` — shared helper for mean onset strength per beat position.
- `compute_rhythm_features()` in `src/rytmi/dsp.py` — uses librosa's HPSS for
  percussiveness, spectral_centroid for brightness, and numpy for the rest.
- `rhythm_features` and `tempo_half` fields added to `RhythmAnalysis`.
- `analyze()` now calls `compute_rhythm_features()` and sets `tempo_half`
  when `tempo > 140`.

### Phase 2 — Prompt integration
- `_format_rhythm_features_section()` in `src/rytmi/prompts.py` with
  interpretive labels (sparse/moderate/dense, low/moderate/high, etc.).
- `{rhythm_features_section}` added to `RHYTHM_ANALYSIS_TEMPLATE`.
- `format_analysis_prompt()` accepts `rhythm_features` and `tempo_half` kwargs
  (None → empty section, backwards compatible).
- `QUESTION_STYLE` and `QUESTION_DANCER` section 1 updated to reference
  concrete features instead of vague "onset density" instruction.
- Language → style hint phrasing unified between STYLE and DANCER prompts.

### Phase 3 — Half-time check
- `tempo_half` field on `RhythmAnalysis`, set when `tempo > 140`.
- Surfaced in prompt as "Note: tempo may be double-time; half-time would be
  {tempo/2:.0f} BPM".

## Evidence

### Tests — PASS (72 passed, 1 skipped)
```
.venv/bin/python -m pytest tests/test_dsp.py tests/test_llm.py tests/test_transcribe.py -q
72 passed, 1 skipped in 7.51s
```

New tests added:
- `test_compute_rhythm_features_basic` — click track: onsets_per_beat in range,
  low tempo stability
- `test_rhythm_features_percussiveness` — click > sine sweep
- `test_beat_strength_pattern_length` — equals beats_per_measure
- `test_rhythm_features_handles_short_audio` — <1s audio doesn't crash
- `test_analyze_has_rhythm_features` — analyze() populates the field
- `test_analyze_tempo_half_below_140` — 120 BPM → None
- `test_format_rhythm_features_section_none` — None → empty string
- `test_format_rhythm_features_section_renders` — key labels present
- `test_format_rhythm_features_section_with_half_time` — half-time note
- `test_format_analysis_prompt_with_features` — no unfilled placeholders
- `test_format_analysis_prompt_no_features_backwards_compatible` — regression
- `test_explain_rhythm_forwards_rhythm_features` — features in prompt

### Backwards compatibility — PASS
- `format_analysis_prompt()` with `rhythm_features=None` produces byte-identical
  output to omitting the parameter entirely (regression test).
- All pre-existing tests continue to pass unchanged.

## Expected impact on eval set

Not yet verified on live inference (requires notebook rerun). Expected effects:

1. **Bachata vs cha-cha (120–130 BPM)**: onset density and percussiveness
   provide concrete tiebreaker values. Bachata tracks should show higher
   onsets_per_beat and percussiveness than cha-cha.
2. **Kizomba at 144 BPM (Baila Kizomba Amor)**: half-time note tells Gemma
   to consider 72 BPM kizomba, which was previously impossible.
3. **Consistent STYLE ↔ DANCER answers**: both prompts now use identical
   language-override phrasing and reference the same concrete features.

## Limitations

1. Feature thresholds (sparse <1.5, dense >2.5, etc.) are set by intuition,
   not calibrated against a labeled dataset.
2. `percussiveness` via HPSS is a rough proxy — works well for percussive vs
   smooth but may not distinguish sub-styles.
3. `tempo_half` is a simple `tempo > 140` check — doesn't verify whether
   half-time actually fits the rhythmic pattern.
4. No eval-set rerun yet to measure actual impact on style accuracy.

## Next steps

1. Rerun the 7-track eval set with these features enabled and compare to the
   2026-04-12 audio-transcription baseline.
2. Calibrate density/percussiveness labels against real tracks if the eval
   shows they mislead Gemma.
3. Consider adding swing ratio (IOI pair ratio) as an additional feature for
   swing-feel styles.
