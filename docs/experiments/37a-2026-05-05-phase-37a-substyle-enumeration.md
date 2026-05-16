# 2026-05-05 — Phase 37a: Sub-style enumeration in rhythm_anatomy

## Goal

Expand `QUESTION_RHYTHM_ANATOMY` from a single-paragraph genre intro to a two-paragraph intro that **also enumerates 2-4 major sub-styles** of the genre with rhythmic distinguishers. Genre-literacy framing — the learner uses the hints to *place* a track they'll hear, not to have the system classify the song. Honest uncertainty: sub-style identification from a `RhythmAnalysis` alone is unreliable, so the system never claims a song belongs to a specific sub-style.

## Context / prior state

Phase 36 (`402b02a`) shipped the genre intro as one paragraph per style. The user flagged a real gap during planning: kizomba in particular splits into multiple sub-styles (Angolan kizomba, kizomba fusion, urbankiz, tarraxinha, semba, ghetto zouk) and the rhythmic feel — and what coaching makes sense — varies meaningfully across them. A learner who picks up a tarraxinha track without knowing the genre's sub-style territory will get a tutor that's technically correct but tonally off.

The conversation explored two follow-up shapes:

- **Phase 37a (this phase)** — sub-style *enumeration* in the genre intro. Cheap, additive. The user reads the hints and picks themselves.
- **Phase 37b** — per-track sub-style *hint with explicit uncertainty*. Architecturally heavier. Sub-style distinctions often need vocal-style and production cues that DSP can't see. **Deferred** because honest sub-style identification from a `RhythmAnalysis` alone is unreliable — the user's note: _"the user can try to pick some hints from the general intro themselves, and not be left completely in the dark about it."_

Phase 37a is the smaller, more honest fix.

## Hypothesis

Expanding `QUESTION_RHYTHM_ANATOMY` to two paragraphs (anatomy + sub-style hints) will:

1. Give the learner enough sub-style awareness to *place* a track they hear afterward, without committing the system to per-track classification.
2. Inherit the Phase 35 hardened helpers (`_METRIC_GUARD_RULE`, `_KIZOMBA_DOWNBEAT_GUARD_RULE`) day-zero — same architectural compounding that made Phase 36 land in zero iterations.
3. Naming common sub-styles in the prompt (Angolan / kizomba fusion / urbankiz / tarraxinha / ghetto zouk / semba for kizomba; Dominican / sensual / urban / bachatango for bachata) gives the model a stable reference set so cross-run output is consistent. Phase 35 lesson about example-echoing applies but here the sub-style enumeration is the **desired output**, not a forbidden construction — examples in the prompt are intentional templates, not anti-patterns.

## What changed

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — `QUESTION_RHYTHM_ANATOMY` rewritten:
  - Was: ONE paragraph (~120 words, capped at 150).
  - Now: TWO paragraphs. **Paragraph 1 — rhythmic anatomy** (~100 words, same content as Phase 36). **Paragraph 2 — sub-style hints** (~80 words, 2-4 sub-styles per genre with rhythmic distinguishers).
  - Word cap raised from 150 to 220 across both paragraphs.
  - New hard rule: _"Do NOT claim that any specific track belongs to a specific sub-style. Sub-style identification from a `RhythmAnalysis` alone is unreliable; the sub-style hints are framing for the learner, not a classification of any song they will hear."_
  - Sub-style reference set baked into the prompt: kizomba candidates (Angolan, kizomba fusion, urbankiz, tarraxinha, ghetto zouk, semba); bachata candidates (Dominican / traditional, sensual / modern, urban, bachatango). The model picks the 2-4 most relevant for the `{style}` parameter.
- **[tests/test_prompts.py](../../tests/test_prompts.py)** — one new test, plus a small update to an existing test:
  - `test_question_rhythm_anatomy_includes_substyle_hints` (NEW) — asserts the new paragraph-2 framing wording (`sub-style`, `2 to 4 major sub-styles`), the major sub-style examples for both genres (`angolan kizomba`, `urbankiz`, `tarraxinha`; `dominican`, `sensual`, `bachatango`), and the architectural-honesty rule (`do not claim that any specific track belongs to a specific` + `sub-style identification ... unreliable`).
  - `test_question_rhythm_anatomy_registered_and_grounded` (UPDATED) — asserts the new "two-paragraph genre intro" + "two prose paragraphs" wording instead of the old "one short paragraph".
- **No notebook changes.** The prompt is registered through the same path; notebooks 00 and 09 pick up the expanded output automatically through `explain_rhythm`.

## Phase 37a-bis guard hardening

The first live run showed the 37a sub-style change worked, but it also exposed an inherited listening-guide guard weakness: the Filomena kizomba listening guide wrote _"Because the downbeat position is ambiguous..."_ in learner-facing prose. The advice itself was useful, but the wording violated the Phase 35/36 kizomba rule.

Root cause: the output guard forbade the word, but `format_analysis_prompt(...)` could still inject a low-confidence downbeat-analysis block into kizomba prompts before the question. The model copied that field language despite the guard.

Follow-up changes:

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — `format_analysis_prompt(...)` now omits the downbeat-analysis block when `dance_style="kizomba"`; beat-position anchoring remains available for non-kizomba styles such as bachata.
- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — `_KIZOMBA_DOWNBEAT_GUARD_RULE` now includes a positive replacement for uncertain beat-position anchoring: do not name that field; say the pulse is subtle, trust the bass line, or avoid relying on a specific count.
- **[tests/test_llm.py](../../tests/test_llm.py)** — `test_format_analysis_prompt_omits_downbeat_block_for_kizomba` asserts that even if downbeat times/confidence are provided, a kizomba prompt does not receive the conflicting downbeat block.
- **[tests/test_prompts.py](../../tests/test_prompts.py)** — existing guard tests now assert the new positive replacement wording and that the helper still contains the forbidden word only in the explicit forbidden-token instruction.

## Evidence / test results

**Tests (clean run after Phase 37a changes):**
```
$ python -m pytest
================= 413 passed, 1 skipped, 64 warnings in 46.00s =================
```
412 baseline → 413 (1 new sub-style test). Existing rhythm_anatomy tests pass after the small wording update for the two-paragraph structure.

**Focused tests after Phase 37a-bis guard hardening:**
```
$ python -m pytest tests/test_prompts.py::test_question_listening_guide_kizomba_downbeat_guard tests/test_prompts.py::test_kizomba_downbeat_guard_rule_canonical_wording tests/test_prompts.py::test_question_rhythm_anatomy_includes_substyle_hints tests/test_llm.py::test_format_analysis_prompt_omits_downbeat_block_for_kizomba -v
============================== 4 passed in 0.24s ===============================
```

**Full tests after Phase 37a-bis guard hardening:**
```
$ python -m pytest
================= 414 passed, 1 skipped, 64 warnings in 48.13s =================
```

**Live run output before 37a-bis:**

- `notebooks/00_demo_outputs.md` / kizomba `rhythm_anatomy`: two paragraphs. The second paragraph names Angolan kizomba, urbankiz, Tarraxinha, and ghetto zouk, with learner-facing rhythmic/texture/energy distinguishers.
- `notebooks/00_demo_outputs.md` / bachata `rhythm_anatomy`: two paragraphs. The second paragraph names traditional Dominican bachata, modern/sensual bachata, Urban bachata, and bachatango, with percussion/texture/phrasing distinguishers.
- `notebooks/09_kizomba_extended_outputs.md` / kizomba `rhythm_anatomy`: two paragraphs. The second paragraph names traditional Angolan kizomba, urbankiz, and Tarraxinha.
- No per-track output claimed a specific sub-style for a specific song.
- No `continues.` filler appeared in the fresh markdown dumps.
- Raw decimal-looking matches were confined to DSP tables/metadata, not learner-facing Gemma prose.

**Post-37a-bis live run:**

- `notebooks/00_demo_outputs.md` / Filomena `listening_guide`: the forbidden beat-position wording is gone. The advice now frames the hard moment as a subtle pulse and ends with the intended replacement language: trust the bass line to maintain connection to the pulse.
- `notebooks/09_kizomba_extended_outputs.md`: no learner-facing matches for the kizomba guard patterns (`downbeat`, `the 1`, step/count-position anchors, or beat-position wording) in the generated listening-guide or tutor prose.
- Remaining `downbeat` matches in `notebooks/00_demo_outputs.md` are confined to DSP/debug table lines and bachata metadata, not kizomba Gemma prose.
- The two-paragraph genre intro still lands in both notebooks. The fresh kizomba intro names Angolan kizomba, urbankiz, and tarraxinha; the fresh bachata intro names traditional/Dominican, modern/sensual, urban, and bachatango. No per-track output claims a specific song belongs to a specific sub-style.

## What worked

- **Kizomba intro covers anatomy AND sub-styles.** Both notebook 00 and notebook 09 produced the intended two-paragraph shape. The sub-style paragraph named likely dance-floor variants and gave enough rhythmic texture for a learner to start placing what they hear.
- **Bachata intro covers anatomy AND sub-styles.** Notebook 00 produced the intended second paragraph with Dominican/traditional, modern/sensual, urban, and bachatango framing.
- **Sub-style identification rule held.** No language like "this track is a tarraxinha" or "this song belongs to urbankiz" appeared in per-track outputs. The sub-style vocabulary stayed in the genre intro, not the track-specific listening guide or tutor.
- **Post-fix kizomba guard held.** The Filomena listening guide no longer echoes the analysis field language. The model used the desired learner-facing replacement: subtle pulse / bass-line trust.
- **Length stayed workable.** The outputs stayed compact enough for the demo flow; the 220-word cap is comfortable for the two-paragraph shape.
- **Shared-helper architecture paid off again.** The 37a-bis fix hardened both the shared guard and the formatter path, so listening guide / tutor / drills inherit the safer wording without repeating local rules.

## What did not work / limitations

- **Inherited listening-guide guard leak.** The first live run produced one kizomba prose sentence with forbidden beat-position wording in the Filomena listening guide. This was not caused by the new sub-style paragraph, but Phase 37a made us re-run the demo and catch it. Fixed in 37a-bis by removing the conflicting analysis block for kizomba and strengthening the positive replacement wording.
- **Kizomba drills grouping needed deterministic cleanup.** The fresh 00 run again crossed the final `main`/`outro` boundary in `kizomba_drills` by emitting `P7-P8: main (159s-195s...)` and then a separate `P8: outro (195s-209s...)`. The prompt already contained the correct rule and worked example, so more prompt prose was unlikely to be the best next fix. Phase 37c implements a post-generation verifier/normalizer for drill phase ranges.
- **Sub-style enumeration is still framing, not classification.** Phase 37a intentionally does not classify individual songs into sub-styles. That remains the honest tradeoff because a `RhythmAnalysis` alone is not enough evidence for reliable sub-style identification.
- **Notebook outputs need commit hygiene.** The reruns made notebooks dirty with large outputs. Before commit, clear all tracked notebooks with `nbconvert` and stage only output-cleared notebook diffs or intentional source-cell fixes.

## Decision / takeaway

Phase 37a's design is validated: keep sub-style enumeration in the genre intro and keep per-track sub-style classification deferred. The first live run did not show sub-style leakage; it showed an inherited kizomba beat-position wording leak, which Phase 37a-bis now fixes in both tests and fresh live output.

Ship the Phase 37a / 37a-bis prompt changes after notebook-output clearing. The genre intro becomes the demo's stronger opening: it explains what the style sounds like and gives the learner a small map of variants they may encounter, while staying honest about what the system can and cannot classify. The drill range duplication is now captured as Phase 37c: a deterministic verifier that preserves Gemma's coaching language while enforcing phase structure.

## Next step

1. **Clear notebook outputs before commit.** Use `python -m jupyter nbconvert --clear-output --inplace notebooks/*.ipynb` (or the long-form ClearOutputPreprocessor command if needed). Include notebook 08 in this hygiene pass because it has previously become large.
2. **Final diff review.** Stage prompt/test/doc changes plus output-cleared notebook diffs. Do not stage ignored markdown evidence dumps unless explicitly needed for the experiment archive.
3. **Phase 37c follow-through.** Run a post-verifier notebook 00 check so the visible `kizomba_drills` output shows the normalized non-overlapping phase ranges, then record the result in `docs/experiments/37c-2026-05-06-kizomba-drill-verifier.md`.
4. **Writeup editorial pass — promote the demo flow to the central frame.** Once Phase 37a lands, the writeup can describe the seven-mode flow in detail (rhythm_anatomy with sub-styles → describe_sections → listening_guide → song_arc → kizomba_tutor → polish → kizomba_drills). ~30 minutes of editorial work.
5. **Phase 37b candidate remains deferred.** Per-track sub-style hints with explicit uncertainty are not needed unless later evidence shows a clear demo benefit.
6. **Demo recording prep.** Storyboard against the new opening flow.
