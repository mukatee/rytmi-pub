# 2026-05-09 — Phase 39: Bachata coaching surface (tutor + drills, verifier reuse)

## Goal

Bring bachata up to parity with kizomba on the coaching side: add `QUESTION_BACHATA_TUTOR` and `QUESTION_BACHATA_DRILLS` prompts, register them in `ALL_QUESTIONS`, and reuse the structural drill verifier (`verify_kizomba_drills_output`, name unchanged for now) so generated bachata practice plans cannot cross section boundaries or duplicate phase coverage. Same shape as the kizomba coaching surface, with bachata-specific honesty about the acoustic "1".

## Context / prior state

Through Phase 38 the bachata path was thinner than the kizomba path:

- **Kizomba**: rhythm_anatomy → listening_guide → song_arc → kizomba_tutor (one-pass + polished) → kizomba_drills (verified). Six modes.
- **Bachata**: rhythm_anatomy → listening_guide → song_arc → dancer (the generic 4-section narrative). Four modes; no per-phase tutor, no practice plan.

The asymmetry was an artefact of the project starting from kizomba's harder DSP problem (subtle pulse, no acoustic downbeat). Bachata is the "easier case" but it still has real coaching surface area — phrasing, count anchoring, breaks, phrase recovery. A learner picking up Propuesta Indecente should get the same kind of per-phase coaching and practice-plan output a kizomba learner gets.

The Phase 37c drill verifier is structural — it parses the P# format and validates ranges against `analysis.phases`. Nothing in it is kizomba-specific. So the verifier reuses cleanly for bachata; the only generalisation needed is `explain_all`'s dispatch logic (was hard-coded to `dance_style == "kizomba"`).

## Hypothesis

Two new prompts plus one small `explain_all` generalisation will give bachata the same coaching depth as kizomba:

1. **`QUESTION_BACHATA_TUTOR`** — per-phase movement coaching, same P# format and beat-clarity-tag grounding as `QUESTION_KIZOMBA_TUTOR`. Differs in being **honest about the 1**: where the kizomba tutor explicitly forbids naming a downbeat (because detection is unreliable), the bachata tutor anchors the learner on the 1 *when downbeat confidence supports it*. Vocabulary is bachata-specific ("the 1-2-3-tap, 5-6-7-tap basic", "land the basic on 1", "8-count").
2. **`QUESTION_BACHATA_DRILLS`** — practice plan that mirrors `QUESTION_KIZOMBA_DRILLS` (whole-song coverage, same-label same-beat grouping, contrasting-section boundaries, P# range syntax) with bachata vocabulary and 1-2-3 / 5-6-7 anchoring.
3. **`explain_all` dispatch generalisation** — a small dict that maps `dance_style` to the matching `*_drills` registry key, so the structural verifier runs for bachata the same way it does for kizomba. Verifier itself unchanged; reused via the existing `verify_kizomba_drills_output` symbol (renaming to `verify_drills_output` is deferred — would be a pure refactor, scope creep here).

The bachata tutor must NOT inherit `_KIZOMBA_DOWNBEAT_GUARD_RULE` — bachata is the genre where naming the 1 is honest, and dropping the kizomba guard verbatim into the bachata tutor would make the model refuse to anchor the learner on the count, defeating the entire point.

## What changed

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — added `QUESTION_BACHATA_TUTOR` and `QUESTION_BACHATA_DRILLS` constants. Both interpolate `_METRIC_GUARD_RULE` (Phase 35); neither interpolates `_KIZOMBA_DOWNBEAT_GUARD_RULE` (would conflict with bachata's honest-1 framing). Both registered in `ALL_QUESTIONS` as `bachata_tutor` and `bachata_drills`.
- **[src/rytmi/llm.py](../../src/rytmi/llm.py)** — `explain_all` now dispatches to the structural drill verifier based on `dance_style` (kizomba → `kizomba_drills`, bachata → `bachata_drills`). The verifier is the existing `verify_kizomba_drills_output`; the result keys (`{key}`, `{key}_raw`, `{key}_verified_stats`) are computed from the active drills key so the per-track output structure is consistent across styles.
- **[tests/test_prompts.py](../../tests/test_prompts.py)** — five new tests:
  - `test_question_bachata_tutor_registered_and_grounded` — registered, beat-clarity-tag grounded, references downbeat-confidence labels (high confidence / plausible guess / ambiguous), uses P# format.
  - `test_question_bachata_tutor_does_not_inherit_kizomba_downbeat_guard` — explicit assertion that the kizomba downbeat guard is NOT in the bachata tutor; bachata-specific vocabulary (`8-count`, `1-2-3`, `5-6-7`) IS present.
  - `test_question_bachata_tutor_break_handling_uses_recovery_vocabulary` — same Phase 29b break-handling pattern (don't default to "pause and hold").
  - `test_question_bachata_drills_registered_and_groupable` — registered, same drill format the structural verifier parses, 1-2-3 / 5-6-7 anchoring, no kizomba downbeat guard.
  - `test_verify_kizomba_drills_reuses_for_bachata_shaped_input` — the structural verifier is style-agnostic; a bachata-shaped raw draft that crosses a `main`/`outro` boundary is repaired the same way as the kizomba case.
- **[tests/test_llm.py](../../tests/test_llm.py)** — one new test:
  - `test_explain_all_verifies_bachata_drills` — `explain_all` cleans invalid bachata drill ranges via the same structural verifier used for kizomba.
  - `test_all_questions_keys` updated to include `bachata_tutor` and `bachata_drills`.
- **[notebooks/05_batch_analysis.ipynb](../../notebooks/05_batch_analysis.ipynb)** — outputs from a recent batch run; cleared before commit.

No notebook 00 / 09 changes in this phase — those notebooks already use the existing `QUESTION_DANCER` for bachata, which still works. Wiring `bachata_tutor` and `bachata_drills` into notebook 00 is a follow-up if the demo flow wants per-phase bachata coaching.

## Evidence / test results

**Tests (clean run):**
```
$ python -m pytest
================= 430 passed, 1 skipped, 64 warnings in 47.65s =================
```
424 (Phase 38 baseline) → 430 (6 new Phase 39 tests). No regressions.

The new tests cover both prompts (registered, structural rules, no-kizomba-guard, break-handling) and the verifier reuse (the structural verifier handles bachata-shaped input the same way as kizomba-shaped input).

## What worked

- **Drill verifier reuses cleanly without modification.** `verify_kizomba_drills_output` is genuinely structural — nothing in it depends on kizomba-specific section labels or rules. The `explain_all` dispatch generalisation was four lines of code.
- **No-kizomba-guard rule is testable.** `test_question_bachata_tutor_does_not_inherit_kizomba_downbeat_guard` asserts the helper is NOT in the prompt, with a clear comment about why (bachata is the genre where naming the 1 is honest).
- **Bachata tutor structure mirrors kizomba tutor.** P# format, beat-clarity branches, break-handling pattern, section-role vocabulary all transferred. Phase 34's *establishing / sustaining / building / returning / closing* role-naming applies to bachata as well, since it's grounded on phase position not label semantics.
- **No leak surface increase.** Both new prompts use the Phase 35 shared `_METRIC_GUARD_RULE` from day one. The architectural compounding from Phase 36 / 37a held: the new prompts inherited the hardened metric guard without iteration.

## What did not work / limitations

- **Notebook 00 / 09 not yet wired to use the new prompts.** Bachata side of notebook 00 still calls `QUESTION_DANCER` (the generic 4-section narrative). Adding bachata_tutor + bachata_drills to the demo notebook is a follow-up. It's not required for Phase 39 to ship — `explain_all` and direct `explain_rhythm` calls work — but the demo recording would benefit from showing the parallel bachata coaching flow.
- **Verifier symbol name stays `verify_kizomba_drills_output`** despite serving both styles. Renaming to `verify_drills_output` would be a pure refactor; deferred to keep this phase tight. The docstring updates in `explain_all` reflect the dual-purpose nature, so the surface is honest even if the symbol name is historical.
- **No live-run evidence in this doc.** The bachata coaching surface was implemented in working tree across earlier sessions but never committed; this doc commits the code with passing tests but the live-run pass for actually exercising `bachata_tutor` and `bachata_drills` against `gemma-4-26b-a4b-it` on Propuesta Indecente (or an extended bachata set) is a follow-up.

## Decision / takeaway

Ship Phase 39. The bachata coaching surface is structurally complete (prompts, dispatcher, verifier reuse, tests). Follow-up to wire into the demo notebook(s) is small (mirror notebook 00's kizomba section structure for bachata) and can be a Phase 39b if it lands as part of the demo recording prep.

## Next step

1. **Phase 39b candidate — wire `bachata_tutor` + `bachata_drills` into notebook 00's bachata flow.** Mirror the kizomba section structure (analyze → describe_sections → listening_guide → song_arc → bachata_tutor → bachata_drills, with the `dancer` prompt either kept alongside or retired). Live-run on Propuesta Indecente, capture evidence in a Phase 39b doc.
2. **Writeup editorial pass.** Now that bachata has parity, the writeup can describe the *seven-mode flow* per style (rhythm_anatomy → describe_sections → listening_guide → song_arc → tutor → drills, with the kizomba flow adding the polish pass). The seventh mode being the rhythm_anatomy intro that runs once at the top.
3. **Demo recording prep.** With both styles at parity and the vocal-aware section labelling from Phase 38 surfacing instrumental sub-sections, the demo flow has a clean, symmetric story: same architecture for both styles, style-specific honesty about the downbeat (kizomba forbids it, bachata anchors on it).
