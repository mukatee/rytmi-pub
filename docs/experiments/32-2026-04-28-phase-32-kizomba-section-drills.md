# 2026-04-28 — Phase 32: kizomba section-drills

## Goal

Give the kizomba demo a stronger closing beat: pitch → song arc → tutor → polished tutor → **drills**. The bachata `dancer` drill that landed in Phase 31 ("During the main section starting at 38.2s, loop counts 1–8 of the bachata basic and focus on hips landing on count 4") came out genuinely useful in the live run — concrete, anchored to a real section, no fluff. Translate that drill structure to kizomba via a per-section drill prompt, so a learner gets actionable practice cues rather than just per-phase coaching.

## Context / prior state

Phase 31 (`2f2097a`) shipped the bachata dancer rewrite, song-arc tightening, and the kizomba song-arc cell in notebook 00. Live run evidence in `docs/experiments/31-...md` confirms both song arcs read as narrative, the dancer drill is anchored to a real section, and the kizomba per-phase tutor handles `break` correctly.

The Phase 31 doc registered Phase 32 with rough shape and 5 open design questions. This phase resolves them: standalone prompt (not embedded in `kizomba_tutor`), selective 3–5 drills per song, kizomba-only.

## What changed

1. **New prompt `QUESTION_KIZOMBA_DRILLS`** in `src/rytmi/prompts.py`:
   - Standalone (separate LLM call), registered in `ALL_QUESTIONS["kizomba_drills"]` so callers reach it via the existing `explain_rhythm(...)` flow. No new helper in `llm.py` — mirrors how `kizomba_tutor` is registered.
   - Output format: `P#: <start>s-<end>s, <section> [beat: ...] — Drill: <action>. <duration>.`
   - **Selectivity rule:** pick 3 to 5 phases (not one per phase). Cover variety where the analysis allows: at least one `beat: clear` main, the `break` (or `short_break`) if there is one, and a `subtle`/`moderate` recovery drill if any phase has that beat tag. Skip adjacent same-label phases ("main ×4" gets ONE drill, not four).
   - **Section slot** enumeration lifted verbatim from the Phase 29b `kizomba_tutor` fix (intro / main / break / short_break / build / peak / outro), with explicit forbid on energy descriptors in the slot.
   - **Drill content rules:** one concrete focus per drill (body part, weight transfer, recovery action, internal count); always state a duration; default ~30s, scaled to section length.
   - **Same metric guards as `kizomba_tutor`:** no downbeat / "1" claim, no raw decimals, no invented instruments. This is the **fourth application** of the metric-guard pattern (after `kizomba_tutor` Phase 29, `dancer` Phase 31, `song_arc` Phase 31). Phase 31 doc flagged the pattern as a candidate for refactor into a shared helper string; deferred again here, but the case is stronger.

2. **Tests** in `tests/test_prompts.py`:
   - `test_question_kizomba_drills_registered_and_grounded` — registered, uses beat-clarity labels, has `Drill:` format and P# format.
   - `test_question_kizomba_drills_is_selective` — 3 to 5, "not one per phase", "main ×4" mentioned as example of same-label collapse.
   - `test_question_kizomba_drills_section_slot_excludes_energy` — same Phase 29b label-slot fix.
   - `test_question_kizomba_drills_hides_raw_metrics` — same metric guards.
   - `test_question_kizomba_drills_forbids_downbeat_and_requires_duration` — no downbeat, "always state a duration".
   - `tests/test_llm.py::test_all_questions_keys` updated to include `"kizomba_drills"` in the expected set.

3. **Demo notebook** (`notebooks/00_demo.ipynb`):
   - New markdown header + code cell inserted between `demo-kizomba-tutor-polish` and `demo-bachata-header`. Markdown frames drills as the closing beat ("now go practice"). Code: `print(explain_rhythm(kiz, QUESTION_KIZOMBA_DRILLS, processor, model))`.
   - `QUESTION_KIZOMBA_DRILLS` added to the import block.

Tests after Phase 32: 393 passed, 1 skipped (was 388 + 5 new drills tests = 393).

## What worked

- The Phase 29 metric-guard pattern lifts cleanly to a fourth use case. No structural surprises.
- The `explain_rhythm(analysis, QUESTION_*)` registration pattern means no new code in `llm.py` — drills slot in as just another `ALL_QUESTIONS` entry.
- Live run on Filomena (kizomba) confirmed the structural rules:
  - 4 drills emitted (within 3–5 range), adjacent same-label phases collapsed (P3/P4/P5 all `main` → no separate drill, P2 covers them).
  - P# format with `Drill:` prefix and beat-clarity tag — no format drift.
  - Concrete durations matched section length: 12s on a 12s intro, 30s on a long main, 11s on the 11s break, 14s on the outro.
  - No raw decimals, no downbeat / "1" claims.

  Sample lines (post break-rule fix below):
  ```
  P1: 0s-12s, intro [beat: clear] — Drill: Maintain a close embrace and focus
      on a tiny shoulder bounce to feel the pulse. 12s.
  P2: 12s-59s, main ×4 [beat: clear] — Drill: Practice a steady walk-step
      focusing on smooth weight transfers. 30s.
  ```

## What broke and was fixed in the same phase

The first run's break drill regressed exactly the failure mode Phase 29b had
fixed for `kizomba_tutor`:

> P6: 148s-159s, break [beat: clear] — Drill: **Stop your steps and hold
> stillness** to listen to the music. 11s.

The break has `beat: clear`. The drills prompt had the rule "Only suggest
stillness when the beat tag is genuinely `subtle`" — but the model produced
stillness anyway, just rephrased ("hold stillness" instead of "pause and
hold"). The Phase 29b lesson on `kizomba_tutor` was that **soft rules don't
work — the failure phrases must be named explicitly as forbidden**.

**Fix (in this phase):**
- Tightened the break rule to explicitly forbid the failure phrases: "do
  NOT default to 'pause and hold', 'stop your steps', or 'hold stillness'".
- Restated the recovery vocabulary positively for `beat: clear` /
  `beat: moderate` breaks: "the learner should keep the pulse in their body
  and shrink the dance, not freeze".
- Added `test_question_kizomba_drills_break_handling_uses_recovery_vocabulary`
  to lock in the failure-phrase forbid + recovery vocabulary.

This is the same surgical move as the `kizomba_tutor` Phase 29b fix. The
metric-guard pattern is now four uses; the break-rule pattern (forbid
failure phrases by name + require recovery vocabulary) is now two uses.
Worth keeping the second pattern in mind if a third use appears.

## Risks / what to watch

- **Selectivity might collapse.** Filomena has 18 sections but only one `break` and otherwise mostly `main` phases at `beat: clear`. The first run handled this well — adjacent same-label phases collapsed. Watch on tracks with even less variety (e.g. uniform-energy bachata) if Phase 33 happens.
- **Drill format drift.** No drift seen on Filomena. Watch on different tracks.
- **Metric leaks.** None seen on Filomena. Fourth metric-guard application held.
- **Duration realism.** Worked perfectly on Filomena (durations matched section lengths). Watch on tracks with very short sections (sub-10s short_breaks).

## Decision / takeaway

- Ship the standalone drills prompt; one-pass output is the documented baseline.
- Bachata stays untouched (Phase 33 candidate if demo-useful after the video).
- The metric-guard pattern has now been applied four times. Worth a small refactor phase later (lift "Do NOT quote raw decimals…" into a shared helper string) but not in scope here.
- Notebook 07 (kizomba over 5 tap-reference tracks) stays untouched in this phase. If Filomena's drill output reads well, revisit running drills over all 5 tracks; if the output is rough on Filomena, fix it on Filomena first.

## Phase 32b — drills format redesign (full coverage + grouping + variations)

After the break-rule fix landed, the second live run on Filomena produced
metric-clean drills but exposed a **UX problem**: the 3–5 drill cap with
selective phase picks left huge gaps (P2 ends 59s, P6 starts 148s — 90
seconds of song unaccounted for). The format `P#: <span>, <section> —
Drill: ...` implied "do this exact drill at this exact moment" so the
gaps read as "do nothing here", which isn't what a practice plan should
communicate. The drills are meant to be practice patterns tied to
section types, not isolated time windows.

User feedback also flagged that the rule collapsed P7 (post-break `main`)
into the same group as P2-P5 even though the kizomba_tutor caught the
narrative shift ("now add subtle styling once the basic feels automatic").

**Redesign:**

- **Full coverage rule:** every phase from the analysis maps to exactly
  one drill line. Drop the "3-5 drills" cap.
- **Grouping rule:** adjacent phases sharing the SAME section label AND
  the SAME beat tag collapse into ONE drill line with a P# range and
  combined time span (e.g. `P2-P5: main (12s-148s, beat: clear)`).
- **Contrast-ends-group rule:** a contrasting section (`break`, `peak`,
  `build`) ends a group, so a recurring same-label sequence after the
  contrast becomes a NEW group with its own line.
- **Variation rule:** when the same section type recurs after a
  contrast, the second occurrence notes a meaningful variation tied to
  the narrative shift (post-break: add subtle styling; after a peak:
  keep the energy you built).
- **Chronological ordering** (P1 first, last phase last).
- **New format spec:** `P#[-#]: <section> (<start>s-<end>s, beat: ...) — Drill: <action>. <duration>.`
- Word budget bumped from 230 to 250 to accommodate variation notes.

**Updated tests** in `tests/test_prompts.py`:
- Replaced `test_question_kizomba_drills_is_selective` (the "3-5" rule
  test) with four new tests: `_covers_whole_song`,
  `_groups_adjacent_same_label`, `_handles_recurring_groups`,
  `_chronological_ordering`.
- Updated the format-spec assertion in `_registered_and_grounded` to
  match the new `p#[-#]:` token.

**Notebook 00 markdown** updated to describe the new shape (whole-song
coverage, P# ranges, variations after contrasts) instead of the
"picks 3-5 phases" framing.

**Expected output shape** (Filomena projection):

```
P1: intro (0s-12s, beat: clear) — Drill: close embrace, feel the pulse
    through your frame, no stepping yet. 12s.
P2-P5: main (12s-148s, beat: clear) — Drill: steady walk-step, focusing
    on smooth weight transfers. 30s loop, repeated through all four
    main phases.
P6: break (148s-159s, beat: clear) — Drill: shrink to a small pulse in
    the body, reduce travel, reset your connection. Do not stop. 11s.
P7: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5,
    but now add subtle hip styling once the basic feels automatic. 30s
    loop.
P8: outro (195s-209s, beat: clear) — Drill: slow your pace, return to
    minimal movement. 14s.
```

5 drill lines covering all 8 phases. No gaps. Post-break P7 gets its
own line with a variation note.

### First Phase 32b live run

Most of the redesign landed cleanly:

```
P1: intro (0s–12s, beat: clear) — Drill: focus on maintaining a steady
    frame while feeling the pulse together. 12s.
P2-P5: main (12s–148s, beat: clear) — Drill: practice a steady
    walk-step, letting the bass guide your weight transfer. 30s loop,
    repeated through the four main phases.
P6: break (148s–159s, beat: clear) — Drill: reduce travel and keep a
    small, internal pulse in the body to reset. 11s during the break.
P7-P8: main (159s–209s, beat: clear) — Drill: same walk-step as P2-P5,
    but now add subtle hip styling once the basic feels automatic. 50s.
```

✓ Full coverage, P# ranges, post-break variation note, recovery
vocabulary on the break, no metric leaks, no downbeat claim.

✗ **Bug**: `P7-P8: main` — the model merged P7 (`main`) with P8
(`outro`) into one group despite different labels. The grouping rule
already required SAME label, but soft enforcement wasn't enough. The
outro lost its wind-down guidance ("slow the pace, return to minimal
movement") because it got rolled into the post-break re-engagement
drill.

### Phase 32b grouping-rule fix

Tightened the grouping paragraph in `QUESTION_KIZOMBA_DRILLS` with:

- **Positive enumeration**: "DIFFERENT LABELS = DIFFERENT GROUPS, even
  when the beat tag is the same. The valid section-label set is
  `intro`, `main`, `break`, `short_break`, `build`, `peak`, `outro` —
  every change between any of these starts a new group."
- **Worked counter-example**: "if P7 is `main` and P8 is `outro`, you
  MUST emit two separate drill lines (`P7: main (...)` and `P8: outro
  (...)`), NOT a single `P7-P8: main` line. The outro deserves its
  own wind-down drill (slow the pace, return to minimal movement) and
  merging it into the preceding main loses the closing arc."
- **Test updated**: `test_question_kizomba_drills_groups_adjacent_same_label`
  now asserts the new wording, the worked counter-example
  (`P7-P8`, "must emit two separate drill lines"), and that the full
  canonical label set is enumerated in the rule paragraph.

Tests after the grouping-rule fix: 397 passed, 1 skipped (unchanged —
the fix tightened existing wording rather than adding tests).

### Second Phase 32b live run + time-span fix

Re-running the notebook after the grouping-rule fix produced:

```
P1: intro (0s–12s, beat: clear) — Drill: Focus on connection through
    a steady frame without stepping. 12s.
P2-P5: main (12s–121s, beat: clear) — Drill: Practice a steady
    walk-step focusing on weight transfer. 30s loop, repeated through
    the four main phases.
P6: break (148s–159s, beat: clear) — Drill: Shrink your steps and keep
    a small pulse in your body to prepare for the return. 11s during
    the break.
P7: main (159s–195s, beat: clear) — Drill: Same walk-step as P2-P5,
    but now add subtle hip styling once the basic feels automatic. 36s.
P8: outro (195s–209s, beat: clear) — Drill: Return to minimal movement
    and slow your pace to end the dance gently. 14s.
```

✓ Grouping-rule fix worked: P7 (`main`) and P8 (`outro`) are now
separate, P8 gets its own wind-down drill back.

✗ **New bug**: P2-P5 time span shows `12s–121s` but P5 actually ends
at 148s — the model used the end of P4 as the group end, leaving 27s
of song uncovered. Phase counts were correct ("four main phases") and
the start was right, but the end timestamp was off by one phase.

**Time-span rule fix:**

Added an explicit instruction to `QUESTION_KIZOMBA_DRILLS` after the
grouping rule:

> TIME SPAN RULE for grouped lines: the combined time span MUST run
> from the START of the FIRST phase in the group to the END of the
> LAST phase in the group. Do NOT use the end of the second-to-last
> phase. Example: if P2 starts at 12s and P5 ends at 148s, write
> `P2-P5: main (12s-148s, beat: clear)` — NOT `(12s-121s)` even if
> 121s is where P4 ends. Read each phase row carefully and use the
> LAST phase's end timestamp.

Added `test_question_kizomba_drills_time_span_rule` asserting both the
correct example (`12s-148s`) and the worked counter-example
(`12s-121s` named as wrong) appear in the rule paragraph.

Tests after the time-span fix: 398 passed, 1 skipped.

### Third Phase 32b live run + negative-example backfire fix

Re-running the notebook after the time-span fix produced:

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace
    with minimal movement to feel the pulse. 12s.
P2-P5: main (12s-148s, beat: clear) — Drill: perform a steady
    walk-step focusing on weight transfer. 30s loop, repeated through
    the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce travel and keep a
    small pulse in the body to reset. 11s.
P7-P8: main (159s-195s, beat: clear) — Drill: same walk-step as
    P2-P5, but now add subtle hip styling once the basic feels
    automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: return to minimal
    movement to end the dance gently. 14s.
```

✓ Time-span fix worked: `P2-P5: 12s-148s` is now correct.
✓ P8 outro appears as its own line with the correct wind-down drill.

✗ **New bug**: the model emitted `P7-P8: main (159s-195s)` AND a
separate `P8: outro` line. The "P7-P8: main" range is wrong (P7 is
`main` but P8 is `outro`), AND the time span (159s-195s) is just P7's
range — so the range label and the span are inconsistent with each
other. P8 ends up referenced twice.

**Root cause hypothesis**: the prompt's grouping rule contained the
literal string `"P7-P8: main"` as a counter-example showing what NOT
to write. Negative examples can backfire — the model sees the exact
tokens and may emit them anyway. This is a known prompt-design
hazard.

**Negative-example backfire fix:**

- Removed the literal `P7-P8: main` string from the prompt.
- Reformulated the rule with **abstract `Pn-Pm` notation** so there
  are no concrete P# numbers in the wrong example for the model to
  pattern-match.
- Replaced the worked counter-example with a positive rule
  ("A `Pn-Pm` range is ONLY valid when every phase from Pn through
  Pm shares the SAME section label") and concrete label-boundary
  examples that don't include P# literals ("a `main` next to an
  `outro`, an `intro` next to a `main`").
- Added a **SELF-CHECK rule** asking the model to read out the labels
  of every phase in its range before emitting and to split the line
  if any two differ.

Test updated:
- `test_question_kizomba_drills_groups_adjacent_same_label` now
  asserts the abstract `pn-pm` notation, the `same section label`
  rule wording, and the `self-check` instruction. The literal
  `p7-p8` assertion was removed because the prompt no longer
  contains that string.

Tests after the negative-example backfire fix: 398 passed, 1 skipped
(unchanged — the test was rewritten rather than added/removed).

### Lessons captured

1. **The metric-guard pattern is now five uses** (`kizomba_tutor`,
   `dancer`, `song_arc`, `kizomba_drills`, `kizomba_drills` second
   pass). A shared helper string is overdue.
2. **The break-rule recovery vocabulary** is now in two prompts
   (`kizomba_tutor`, `kizomba_drills`). Same case for a shared
   helper.
3. **Negative examples can backfire.** When a prompt says "do NOT
   write `X`", the model can still emit `X` by token-matching the
   literal. Prefer abstract notation (`Pn-Pm`, `<label>`) over
   concrete forbidden literals; pair with a positive rule and a
   self-check.

### Fourth Phase 32b live run + positive-example fix

Re-running the notebook after the negative-example backfire fix
produced this:

```
P7-P8: main (159s-209s, beat: clear) — Drill: same walk-step as
    P2-P5, but now add subtle hip styling once the basic feels
    automatic. 50s.
P8: outro (195s-209s, beat: clear) — Drill: return to minimal
    movement and slow the pace. 14s.
```

The forbidden `P7-P8: main` literal is gone from the prompt, but the
model **still emitted it** — and this time the time span (159s-209s)
even covers both P7 and P8, so the model is internally inconsistent
(it knows P8 is outro because it emits the separate P8 line, but
also grabs P8 into the preceding range).

**Hypothesis**: the rule, the abstract `Pn-Pm` notation, and the
self-check all teach what's *wrong*, but the model is in "range mode"
right after emitting `P2-P5` and reflexively reaches for another
range. There's no positive *shape* in the prompt for "main → outro
on separate lines" to pattern-match against.

**Positive-worked-example fix:**

Added an explicit positive shape after the self-check rule:

> WORKED POSITIVE EXAMPLE — when a song has a `main` group followed
> by an `outro` (a common ending pattern), write them as TWO
> separate lines, not as a range. Schematically:
>     P_a: main (s_1-s_2, beat: clear) — Drill: …
>     P_b: outro (s_2-s_3, beat: clear) — Drill: slow the pace,
>         return to minimal movement. …
> Two lines, two different labels, two distinct drills (the outro
> always gets its own wind-down). Apply this same shape whenever
> the LAST main phase is followed by an outro — do not reach for a
> range across the boundary.

The variables `P_a` / `P_b` and `s_1` / `s_2` / `s_3` are abstract
enough that the model shouldn't substitute them into another track's
real numbers verbatim, but concrete enough as a pattern that the
model can imitate the shape.

Test extended in `_groups_adjacent_same_label` to assert the
"worked positive example" + `p_a: main` / `p_b: outro` strings are
present.

Tests after the positive-example fix: 398 passed, 1 skipped
(unchanged — the existing test was extended, not added/removed).

### Lesson updated

4. **Positive examples beat negative examples.** When a generation
   model is making a structural mistake, adding a worked positive
   example of the right shape is more effective than another rule
   forbidding the wrong shape. The model has "shape priors" — give
   it the right shape to match.

### Fifth Phase 32b live run + ship decision

Re-running the notebook after the positive-example fix produced:

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace
    with minimal movement to feel the pulse. 12s.
P2-P5: main (12s-121s, beat: clear) — Drill: practice a steady
    walk-step focusing on weight transfer. 30s loop, repeated through
    the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce travel and keep a
    small pulse in the body to reset. 11s.
P7-P7: main (159s-195s, beat: clear) — Drill: same walk-step as
    P2-P5, but now add subtle hip styling once the basic feels
    automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: slow the pace and return
    to minimal movement. 14s.
```

✓ Cross-label range fix held: P7 and P8 are on separate lines.
✓ Recovery vocabulary on the break held.
✓ Post-break variation note held.

✗ P2-P5 time span regressed back to `12s-121s` (the bug we already
fixed once before — model used end of P4, not P5).
✗ New cosmetic: `P7-P7: main` instead of just `P7: main`. A
single-phase group should not be written as a range.

### LLM-variance limitation (acknowledged)

Across five Phase 32b live runs, every prompt fix landed
**non-deterministically**: a fix would hold on one run and slip on
another. Diminishing returns with prompt engineering — each new
constraint the model can honor or skip on any given generation. Same
prompt, different output each time:

| Run | Bug fixed | Bug remaining/regressed |
|---|---|---|
| 1 | (selectivity 3–5 cap) | gaps in coverage → redesign to full coverage |
| 2 | (full coverage rule) | `P7-P8: main` cross-label range |
| 3 | (different-labels rule) | `P2-P5: 12s-121s` wrong end span |
| 4 | (time-span rule) | `P7-P8: main` returned despite literal removal |
| 5 | (positive-example fix) | `P2-P5` end-span regressed; `P7-P7` cosmetic |

### Decision: ship Phase 32 as-is

The two remaining issues are minor:

- **`P2-P5: 12s-121s`**: wrong by 27 seconds. The drill content is
  fine; only the displayed end-of-group timestamp is one phase short.
  A learner would still practice the right walk-step on the right
  song.
- **`P7-P7`**: purely cosmetic. Parses as a single phase exactly as
  intended.

The Phase 32 work added real value to the demo (drills, full coverage,
P# ranges, post-break variations, recovery vocabulary on breaks, no
metric leaks, no downbeat claims). Continuing to iterate on prompt
wording would block the demo video sprint with little marginal gain
given LLM variance.

### Future hardening (out of scope, queued for after demo video)

If user testing shows the residual variance confuses learners, the
reliable fix is a small post-processor in `rytmi.llm` (or a sibling
`validate_kizomba_drills(text, analysis)` helper) that:

- Parses each emitted drill line.
- Looks up the actual phase boundaries from the supplied
  `RhythmAnalysis`.
- Replaces `Pn-Pn` with `Pn`.
- Replaces wrong-end time spans (e.g. `12s-121s` → `12s-148s`) by
  recomputing from the underlying phase list.
- Splits any range that crosses a label boundary.

Estimated ~30 lines, deterministic, would catch every shape variance
seen in Phase 32b runs. Defer until after the demo video unless
learner-facing harm is observed.

## Next step

1. User runs `notebooks/00_demo.ipynb` end-to-end to confirm the
   redesigned drills format lands as projected (full coverage, P#
   ranges with `Pn-Pm`, post-break variation note, recovery vocabulary
   on the break).
2. If clean, commit and move to demo video sprint (or Phase 33 bachata
   drills if more demo content is needed first).
3. If the model deviates (e.g. doesn't emit `Pn-Pm` ranges, or skips
   variations), iterate on the prompt — likely the variation rule
   needs sharper examples.

## Future ideas (out of scope)

- **"Give me different drills" iteration.** A learner who has done the
  default plan might want a fresh practice plan with the same coverage
  but different drill picks (e.g. different focus body parts, alternate
  recovery patterns). Could be a `seed` parameter or a "regenerate"
  helper. Worth scoping as a future small phase if user testing flags
  it as useful.

## Phase 33 anchor — bachata section-drills (out of scope)

`QUESTION_DANCER` already has one drill at the end and reads cleanly post-Phase-31. A per-section bachata drill prompt could subsume that — but it would also break the existing dancer-prompt structure. Worth doing **only if** the demo video would benefit from a parallel kizomba/bachata drill story; otherwise defer.

Open design questions (don't decide here):
- Standalone `QUESTION_BACHATA_DRILLS` vs. extension of `QUESTION_DANCER`?
- If bachata gets per-section drills, drop the dancer's single closing drill?
- Style-parameterized `QUESTION_SECTION_DRILLS` (one prompt for both styles) — but kizomba's no-downbeat / `subtle` guards don't apply to bachata, so the prompt would need style-aware branching.
