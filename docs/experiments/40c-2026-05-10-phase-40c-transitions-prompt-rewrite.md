# 2026-05-10 — Phase 40c: Transitions prompt rewrite (re-entry primary, audible-cue anticipation)

## Goal

Fix a structural error in the first-draft `QUESTION_KIZOMBA_TRANSITIONS` (Phase 40, commit `d77d795`): the prompt anchored anticipation cues on counting beats ("in the last 8-count of the main, soften the basic…"), which inverted the project's premise. The target user is a learner who CANNOT yet reliably count to 8 — that's why they need this tool. Asking them to use the count to predict transitions is asking them to use the thing they can't do to plan for the thing they need help with.

Phase 40c makes the prompt match the project's actual user model:
- **Re-entry primary, anticipation secondary.** The learner most often *notices* a transition has happened and reacts on the fly. Coaching must lead with what to do AFTER the boundary, not before.
- **Anticipation only when audibly grounded.** When an audible cue can be composed from the section properties (energy fading, percussion thinning, bass entering, vocals dropping), name it. When it can't, omit anticipation — don't invent generic count-based anticipation.
- **Forbid count-based anticipation explicitly.** "In the last 8-count of <from>", "in the final 8-count", "after N beats" all banned by name in the rules block, with the reasoning ("learner has no reliable internal clock yet") on-page so future iterators understand why.

## Context / prior state

Phase 40 shipped the structural surface (algorithmic extraction, prompt, verifier, notebook 00 integration, tests) with a clean live run on Filomena Maricoa _Teu Toque_. Verifier stats were perfect: `parsed=4 boundaries_matched=4 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=4`. The architecture worked.

But the user feedback on the actual T# coaching surfaced the count-anticipation issue:

> "the part where it is a bit off for me is the assumption that the user can do the 8 count and thus predict the transition phase. the whole project premise was to help find the beat for someone who is not so good at counting to 8. so personally i tend to end up noting that transition seems to have happened and i need to figure out a reasonable transition on the fly to the new phase / energy etc."

Three of four lines in the Filomena live run leaned on the count for anticipation:
- T1: "In the last 8-count of the intro, settle into the pulse…"
- T2: "In the last 8-count of the main, soften the basic and reduce travel…"
- T4: "As the song winds down in the final 8-count…"

Only T3 ("After the stillness of the break, re-enter the main with a walk-step on the first clear bass hit…") was honestly framed — sensorially anchored, after-the-fact, gives the learner something to do at the moment they can act. T3 is the model the rewrite uses.

The user also surfaced a richer follow-up idea ("describe how the transition could be seen in this specific song"), which Phase 40c partially addresses via the audible-cue framing. A more sophisticated implementation (per-boundary "approach window" DSP signals) is Phase 41+ scope.

## Hypothesis

Reframing the prompt around re-entry-primary + audible-cue-secondary will produce substantially more useful coaching for the target user without requiring any structural changes (extraction, verifier, notebook integration all unchanged). The 26B model is robust to vocabulary changes (Phase 38 lesson: model picked up `instrumental` label without prompt-side enumeration); flipping the framing of "what to say first" should land cleanly with the same verifier guardrails.

## What changed

All changes in [src/rytmi/prompts.py](../../src/rytmi/prompts.py) and [tests/test_prompts.py](../../tests/test_prompts.py). No structural code changes; no notebook changes; no other doc changes.

### Prompt rewrite (`QUESTION_KIZOMBA_TRANSITIONS`)

- **New "Critical assumption" paragraph** at the top: names the user model explicitly ("learner CANNOT reliably count to 8 yet — that's why they need this tool"), describes what they actually do ("notice that a transition has happened and need to react on the fly"), and forbids count-based anticipation by name.
- **Coaching-shape rules restructured**: re-entry is now the primary content (every T# line MUST include a re-entry cue); anticipation is conditional on a composable audible cue.
- **Audible-cue rule added** with examples per contrast direction:
  - High → low energy (main → break, main → outro): "as the energy fades and the percussion thins"
  - Low → medium/high energy (intro → main, break → main): "when the bass kicks in", "as the percussion returns"
  - Vocal → instrumental: "when the vocals drop out"
  - Instrumental → vocal: "when the vocals come back in"
- **Per-boundary-type re-entry rules** retained from Phase 40 (break entry/exit, peak/build, intro→main, outro, instrumental, clarity-drop) but stripped of count-anticipation framing.
- **Module docstring updated** to explain the Phase 40c rewrite reasoning so future iterators don't accidentally regress.

### Test changes ([tests/test_prompts.py](../../tests/test_prompts.py))

- **`test_question_kizomba_transitions_break_vocabulary`** — updated to match the new re-entry-primary framing. Drops "soften the basic / reduce travel" assertions (those were anticipation phrases removed in the rewrite); adds "first clear bass hit" / "keep a small pulse" / "do not default to 'pause and hold'" as the canonical re-entry vocabulary.
- **New `test_question_kizomba_transitions_forbids_count_based_anticipation`** — explicit assertion that the prompt names "never anchor anticipation on counting beats" and lists the specific forbidden phrasings ("in the last 8-count of <from>", "in the final 8-count"). The reasoning ("cannot reliably count" / "no reliable internal clock") is also tested so future regressions surface clearly.
- **New `test_question_kizomba_transitions_audible_cue_vocabulary`** — asserts the audible-cue rule appears with examples (energy fading, percussion thinning, bass entering, vocals dropping) and the explicit "omit anticipation" instruction when no specific cue can be composed.
- **New `test_question_kizomba_transitions_re_entry_primary_framing`** — asserts re-entry is named as the "primary content" and "every T# line must include a re-entry cue", plus the after-the-fact framing ("after they notice the new section has arrived").

## Evidence / test results

**Tests (clean run after rewrite):**
```
$ python -m pytest
================= 448 passed, 1 skipped, 64 warnings in 45.98s =================
```

445 (Phase 40 baseline) → 448 (3 new tests, 1 rewritten test). No regressions.

**Live run on Filomena Maricoa — _Teu Toque_:** _filled in after the user runs notebook 00 with the rewritten prompt._ Watch for:

- **Every T# line leads with a re-entry cue** — what the dancer does after they notice the new section has arrived.
- **Anticipation is present only when audibly grounded** — references energy fade, percussion thinning, bass entering, vocals dropping. NEVER "in the last 8-count of <from>" or any count-based prediction.
- **T3 (break → main) preserves its honest framing** — "after the stillness of the break, walk-step on the first clear bass hit, don't chase the loudest percussion that comes back". This was the model line; the rewrite should produce more lines like it.
- **Audible cue specificity matches Filomena's structural deltas**:
  - intro (low) → main (medium): bass kicking in, percussion returning
  - main (medium/high) → break (low): energy fading, percussion thinning
  - main → outro (low): energy contracting (Filomena's outro has BC=0.42 / RMS×0.82 — present but reduced)

## What worked / didn't / decision

_Filled in after the live run._

## Next step

1. **Live-run validation on Filomena.** If T# lines still slip back to count-anticipation (model momentum from training data), tighten the rule — possibly with a worked-example block showing one acceptable line and one forbidden line.
2. **Phase 40d — notebook 09 (extended kizomba set) integration.** Mirror the notebook 00 wiring; capture transitions evidence across more songs (Charbel _E Magic_ for instrumentals + breaks, Daniel Santacruz _Lento_ for main-rich structure, etc.). Tells us whether the audible-cue rule generalizes or needs more specifics.
3. **Phase 40b — bachata transitions mirror.** Defer until kizomba transitions land cleanly across the broader set.
4. **Phase 41 candidate — per-boundary approach-window DSP.** If learners want sharper per-song cues (the user's "describe what to listen for in this specific song" idea), add a DSP feature that scans the last 4–8 beats before each boundary and reports the trend (energy decay, percussion drop-out, vocal pause). Gives Gemma per-boundary cues at seconds resolution rather than section-level deltas. Out of scope for Phase 40c.
