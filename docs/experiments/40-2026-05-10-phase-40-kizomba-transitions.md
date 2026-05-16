# 2026-05-10 — Phase 40: Kizomba transitions coaching (algorithmic + prompt + verifier)

## Goal

Ship a transitions coaching surface as the seventh kizomba mode in [notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb). The kizomba_tutor and kizomba_drills cover steady-state movement *during* each section; transitions cover the moments *between* — the anticipation cue (last 8-count of the incoming section), the boundary itself, and the re-entry cue (first 8-count of the outgoing section).

Closes a real coaching gap the user named: when a `break` arrives mid-song without rehearsal, festival/YouTube dancers can plan transitions because they know the song; a regular learner hitting a song they don't fully know cannot. The new mode gives them a way to handle transitions on first listen.

## Context / prior state

Through Phase 39b the kizomba surface was: rhythm_anatomy → describe_sections + timeline → listening_guide → song_arc → kizomba_tutor (one-pass + polished) → kizomba_drills (verified). Six modes, all per-section. Nothing for the *boundaries* between sections.

The user identified the gap explicitly: "the basic approach for a break in kizomba is to stop and do basic 1. but you cannot really just magically teleport there when the break comes." Phase 40's design choice was the most ambitious of three offered scopes:

- **Algorithmic transition extraction** in code (deterministic, inspectable)
- **New prompt** for the coaching language
- **Structural verifier** for output integrity

Target was under 2 days. Bachata transitions deferred to Phase 40b.

## Hypothesis

A code-side extraction of label-change boundaries, fed to Gemma as a structured "Transitions" block in the analysis dump, plus a prompt that requires every T# in the output to map to a real boundary, plus a structural verifier that drops invented transitions and fills missing ones, will produce clean per-transition coaching without fabrication. The hypothesis matches the project's existing **code identifies, Gemma writes, code verifies** pattern (drills verifier from Phase 37c, bachata verifier reuse from Phase 39).

## What changed

### Code surface

- **[src/rytmi/types.py](../../src/rytmi/types.py)** — added `Transition` dataclass: `boundary_time_s`, `from_label`, `to_label`, `from_clarity`, `to_clarity`, `from_phase_idx`, `to_phase_idx`, optional `from_energy`, `to_energy`.

- **[src/rytmi/dsp.py](../../src/rytmi/dsp.py)** — added `extract_transitions(phases) -> list[Transition]` and `describe_transitions(analysis) -> str`. Extraction iterates the phase list and emits a transition only when consecutive phase labels differ — same-label phase pairs (energy-only changes within a `main` run) are skipped because the section-role vocabulary in `kizomba_tutor` already covers those. Helpers `_phase_clarity_tag` (mirror of `prompts._beat_clarity_tag`, intentionally duplicated to avoid a `dsp → prompts` import dependency) and `_phase_energy_tag`.

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — three additions:
  - `_format_transitions_block(phases)` — builds the analysis-dump sub-section listing every label-change boundary with time and beat-clarity context. Lazy-imports `extract_transitions` to avoid a top-level dsp dependency. Wired into `RHYTHM_ANALYSIS_TEMPLATE` (interpolated as `{transitions_section}` between `sections_block` and `style_section`) and into `format_analysis_prompt`.
  - `QUESTION_KIZOMBA_TRANSITIONS` — new prompt constant. Output format `T#: <boundary_time>s [<from_label> → <to_label>, beat: <from_clarity> → <to_clarity>] — <coaching>`. Inherits `_METRIC_GUARD_RULE` and `_KIZOMBA_DOWNBEAT_GUARD_RULE`. Rules cover break / peak / build / outro / intro / instrumental boundary types with anticipation + re-entry vocabulary (no "pause and hold" default; "first clear bass hit" for break re-entry). Length cap ~200 words. Registered in `ALL_QUESTIONS` as `"kizomba_transitions"`.
  - `verify_kizomba_transitions_output` + `VerifiedKizombaTransitionsOutput` dataclass + `_KIZOMBA_TRANSITION_LINE_RE` regex + `_fallback_transition_tail` template + `_format_transition_line` helper. Parses T# lines, matches each against the extracted transitions list (±2.0s tolerance for rounding), drops invented boundaries, fills missing ones with deterministic template text, renumbers chronologically. Stats: `parsed`, `boundaries_matched`, `boundaries_invented`, `boundaries_missing_filled`, `skipped_lines`, `output_lines`.

- **[src/rytmi/llm.py](../../src/rytmi/llm.py)** — `explain_all` dispatch extended: when the prompt key is `"kizomba_transitions"` and `dance_style == "kizomba"`, run `verify_kizomba_transitions_output(raw, extract_transitions(phases))`. Returns `kizomba_transitions`, `kizomba_transitions_raw`, `kizomba_transitions_verified_stats` keys mirroring the drills pattern.

### Tests

- **[tests/test_dsp.py](../../tests/test_dsp.py)** — 6 new tests for extraction + describe (simple arc, same-label runs skipped, empty/single-phase no phantom, clarity/energy tags carried, describe_transitions format, describe_transitions empty case).

- **[tests/test_prompts.py](../../tests/test_prompts.py)** — 14 new tests:
  - 3 for `_format_transitions_block` (lists label boundaries, skips same-label runs, empty for single-label song)
  - 5 for `QUESTION_KIZOMBA_TRANSITIONS` (registered + grounded, inherits metric guard, inherits downbeat guard, no-invent / no-skip rule, break vocabulary)
  - 6 for `verify_kizomba_transitions_output` (passes clean output, drops invented, fills missing with template, tolerates ±2s rounding, no transitions returns raw, preserves chronological order)

- **[tests/test_llm.py](../../tests/test_llm.py)** — 1 new test (`test_explain_all_verifies_kizomba_transitions` — confirms dispatch fires, drops invented boundaries, fills missing, renumbers chronologically, stats line correct). `test_all_questions_keys` updated to include `"kizomba_transitions"`.

### Notebook

- **[notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb)** — three changes:
  - `demo-imports`: add `describe_transitions`, `extract_transitions` from `rytmi.dsp`; add `QUESTION_KIZOMBA_TRANSITIONS`, `verify_kizomba_transitions_output` from `rytmi.prompts`.
  - New markdown + code cell pair (`d128b3d8` + `28ab7b58`) inserted after the kizomba_drills code cell (`6c963f56`). Markdown explains the code-identifies / Gemma-writes / code-verifies pattern. Code prints `describe_transitions(kiz)`, runs the prompt, runs the verifier, prints the verified output and stats line.
  - Output dump cell `1447fabb`: four new entries in the kizomba section (describe_transitions, kizomba_transitions verified, kizomba_transitions verifier stats, kizomba_transitions raw).

## Evidence / test results

**Tests (clean run after all changes):**
```
$ python -m pytest
================= 445 passed, 1 skipped, 64 warnings in 46.54s =================
```

424 (Phase 39b baseline) → 445 (21 new Phase 40 tests). No regressions.

The new tests cover extraction (6), the analysis-dump block (3), the prompt structure (5), the verifier (6), and the explain_all dispatch (1).

**Live run on Filomena Maricoa — _Teu Toque_:** _filled in after the user runs the notebook._ Watch for:

- **describe_transitions output**: 4 transitions on Filomena (intro→main at ~12s, main→break at ~148s, break→main at ~159s, main→outro at ~195s). Each with from/to labels and from/to clarity tags from the phase list.
- **kizomba_transitions output**: 4 substantive T# lines, one per real boundary. Each with anticipation + re-entry vocabulary tied to the boundary type. No naming the "1". No metric leaks.
- **Verifier stats**: `parsed=4 boundaries_matched=4 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=4` on a clean run. Non-zero `boundaries_invented` would mean Gemma quoted a boundary time off by >2s. Non-zero `boundaries_missing_filled` would mean Gemma skipped one of the four real boundaries.
- **Optional secondary live run on Charbel — _E Magic_** (richer case: instrumentals + two real breaks). Expected 6–8 transitions. Confirms the prompt + verifier handle a richer set without fabrication.

## What worked / didn't / decision

_Filled in after the live run._

## Next step

1. **Phase 40b — bachata transitions.** Mirror the kizomba surface for bachata. Bachata anchors on the count when `downbeat_confidence` supports it (inverted-honesty stance — the bachata equivalent of "first clear bass hit" is "land the basic on 1" when confidence is high or moderate, "trust the steady pulse" otherwise). Reuse the structural verifier — extraction is style-agnostic.

2. **Storyboard update incorporating transitions.** Add a Phase-40 transitions beat to Act 3 (likely as a new §7 between drills and the multi-clip B-roll). The Close currently names transitions as "what's next" — that line gets dropped or repurposed since we now ship them. Decide multi-track question at the same time (Charbel — _E Magic_ as Act 3 secondary moment to showcase richer transition set).

3. **Phase 41 candidates** (conditional on live evidence):
   - **Beat-clarity-only transitions** (within-label clarity changes — e.g. main `clear` → main `subtle`). Skipped in Phase 40 by design. If live runs on `beat: subtle` tracks (Charbel set) show learners need coaching on clarity shifts within a `main` run, this becomes a candidate.
   - **Top-N transition selection** if Charbel or other rich tracks blow the 200-word cap.

4. **Recording prep.** Pre-render outputs end-to-end with the new transitions mode, finalize storyboard, capture.
