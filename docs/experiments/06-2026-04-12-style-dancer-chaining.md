# 2026-04-12 — STYLE→DANCER chaining, half-time signal, clip retry, empty response retry

## Goal

Fix four issues observed on the 7-track eval set after the rhythm-features
and audio-transcription experiments:

1. **STYLE/DANCER disagreement** on 2 tracks (Me Emborrachare: STYLE=Bachata,
   DANCER=Cha-cha; Canalla: STYLE=Bachata, DANCER=Zouk).
2. **Baila Kizomba Amor** (144 BPM, Portuguese): both STYLE and DANCER pick
   Merengue, ignoring the half-time note and Portuguese language.
3. **Teu Toque** (123 BPM, Portuguese): STYLE response is completely empty.
4. **Canalla**: language detected as Kriol instead of Spanish because the clip
   at 89s landed on an instrumental section.

## Changes made

### Phase 1 — Chain STYLE→DANCER (highest impact)

- `explain_all()` in `src/rytmi/llm.py` now explicitly orders questions so
  STYLE runs before DANCER.  The STYLE answer text is prepended to the DANCER
  question as: `"Context: this track was identified as {style_answer}.\n\n"`.
- `prepend_style_context()` helper added to `src/rytmi/prompts.py`.
- `explain_rhythm()` single-question API is unchanged.

### Phase 2 — Strengthen half-time signal

- `_format_rhythm_features_section()` in `src/rytmi/prompts.py`: the half-time
  note moved from the end of the features block to the **first bullet**, with
  explicit wording: "Estimated half-time tempo: {N} BPM (the detected tempo may
  be double-time; some styles like kizomba/semba play at ~70-80 BPM but are
  detected at ~140-160 BPM)".
- `QUESTION_STYLE` now instructs: "If a half-time tempo is shown, compare dance
  styles at BOTH the measured tempo and the half-time tempo."
- `QUESTION_DANCER` section 1 has the same half-time comparison instruction.
- **Semba** added to the style vocabulary in both STYLE and DANCER:
  "semba (130-160 BPM, Angolan/Portuguese, similar to kizomba but faster)".

### Phase 3 — Clip selection retry

- `transcribe_vocals()` in `src/rytmi/transcribe.py` now accepts
  `max_retries: int = 3`.  On each retry, a different `skip_intro_frac` is
  used: 0.15 (default), 0.40, 0.60.
- The first result with a recognized language (not "instrumental" or "unknown")
  is returned.  If all retries fail, the last result is returned (status quo).
- Internal generation logic extracted to `_transcribe_clip()` private helper.

### Phase 4 — Empty response retry

- `_generate_cloud()` and `_generate_local()` in `src/rytmi/llm.py` now retry
  once with `temperature=0.5` if the initial response is empty or
  whitespace-only.  Logged as `"  empty response, retrying with temperature=0.5"`.

## Evidence

### Tests — PASS (102 passed, 1 skipped)

```
.venv/bin/python -m pytest -q
102 passed, 1 skipped in 8.51s
```

New tests added:
- `test_explain_all_chains_style_to_dancer` — mock generate, verify DANCER
  prompt contains STYLE context
- `test_explain_all_style_runs_before_dancer` — verify ordering
- `test_prepend_style_context` — helper formats correctly
- `test_empty_response_retry_cloud` — mock empty→valid, verify retry with temp=0.5
- `test_no_retry_when_response_not_empty` — no unnecessary retry
- `test_format_rhythm_features_half_time_prominent` — half-time is first bullet
- `test_question_style_contains_semba` / `test_question_dancer_contains_semba`
- `test_transcribe_retries_on_instrumental` — mock instrumental→spanish, verify retry
- `test_transcribe_returns_last_result_when_all_retries_fail` — all retries fail
- `test_transcribe_no_retry_when_language_detected` — no unnecessary retry

Existing tests updated:
- `test_format_rhythm_features_section_with_half_time` — updated to match new wording

## Expected impact on eval set

Not yet verified on live inference (requires notebook rerun with Ollama).
Expected effects:

1. **STYLE/DANCER disagreement** → DANCER now sees STYLE's answer as context,
   should agree on most tracks.
2. **Baila Kizomba Amor** (144 BPM) → half-time note is now prominent and
   instructs comparison at both 144 and 72 BPM; semba is a valid pick;
   Portuguese language biases toward kizomba/semba/zouk.
3. **Teu Toque empty STYLE** → empty-response retry should produce output on
   the second attempt with temperature=0.5.
4. **Canalla Kriol misdetection** → clip retry at 40% and 60% into the track
   should find a section with Spanish vocals instead of instrumental.

## Limitations

1. Chaining is one-directional (STYLE→DANCER only).  If STYLE is wrong, DANCER
   inherits the error.
2. Clip retry positions (0.15, 0.40, 0.60) are heuristic, not onset-density
   guided per position.
3. Empty-response retry uses a fixed temperature=0.5; not tuned.
4. No eval-set rerun yet to measure actual impact.

## Next steps

1. Rerun the 7-track eval set and compare to the 2026-04-12 baseline.
2. If STYLE errors propagate to DANCER, consider adding a "disagree" check.
3. Consider onset-density-guided clip selection for retries.
