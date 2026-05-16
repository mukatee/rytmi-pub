# 2026-05-04 — Phase 35: Shared metric-guard and kizomba-downbeat-guard helpers

## Goal

Lift the metric-guard and kizomba-downbeat-guard wording — currently duplicated and slightly drifted across six prompts — into two module-level constants in [src/rytmi/prompts.py](../../src/rytmi/prompts.py), and harden each rule with the **positive-replacement clause** the Phase 32 / 33b lessons proved out. Every consuming prompt is refactored to interpolate the shared helper at module-load time, so a future leak gets fixed once and inherited everywhere.

Also: flip the kizomba-tutor polish pass from **opt-in** to **default for the demo** in [notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb). The one-pass output ships occasional leaks under non-determinism; polish reliably catches them. The one-pass cell is kept visible for transparency.

## Context / prior state

After Phase 34 the metric-guard and kizomba-downbeat-guard rules were the **seventh and second-most-applied prompt pattern in the project** respectively, and both had observed leaks despite explicit forbidding:

- **Metric-guard leak:** Phase 31 dancer/song-arc raw-decimal narration ("percussiveness 0.22"), Phase 34 Calo Pascoal listening-guide _"Because the percussiveness is relatively low at 0.34..."_ — clean rule violation on a 1-in-6 track.
- **Kizomba-downbeat-guard leak:** Phase 33 listening-guide _"the 1 is likely around various points"_ (fixed by 33b with a positive-replacement clause), Phase 34 Isabelle kizomba_tutor _"try a half-time feel by stepping only on 1 and 3 to match the shifting energy."_ Polish caught the Isabelle leak but the rule itself wasn't strengthened.

Three line-wrap snags (Phase 32 / 33 / 34) added to the case for a single canonical wording. The wording was already drifting between prompts — `kizomba_tutor` said _"Do NOT name a downbeat / '1' position — kizomba downbeat detection is unreliable and out of scope. Talk about the steady pulse only."_ while `listening_guide` (post-33b) said the much stronger _"Do NOT name a downbeat, 'the 1', or any specific count position. Kizomba's downbeat is acoustically subtle and detection is unreliable. If the music's lack of a clear downbeat needs acknowledging, frame it as 'the pulse is felt rather than heard' or 'the bass carries the pulse' — never as 'the 1' or 'the downbeat'..."_

The Phase 34 doc anchored this work as Phase 35 explicitly:

> Phase 35 — shared metric-guard helper string + harden with positive replacement. Now urgent rather than tech-debt: the Calo Pascoal "0.34" leak is a clean rule violation despite explicit forbidding. Lifting the metric-guard wording into a shared module-level constant lets us strengthen it once and inherit everywhere.

## Hypothesis

Two changes will materially reduce the leak rate observed in Phase 34:

1. **Lift the rule wording.** Two module-level constants, `_METRIC_GUARD_RULE` and `_KIZOMBA_DOWNBEAT_GUARD_RULE`, defined once and interpolated into every consuming prompt. Future hardening becomes a one-line edit.
2. **Strengthen with positive replacements** (Phase 32 lesson):
   - Metric guard: explicit "Instead of phrases like 'percussiveness of 0.22', 'beat clarity 0.34', or '0.16 percussiveness', translate to qualitative language: 'drum-light feel', 'unusually low percussiveness', 'a clear percussive grid', 'pulse felt through the bass'..." Direct response to the Calo Pascoal leak.
   - Kizomba downbeat guard: explicit "(no 'step on 1 and 3', no 'land on count 4', no 'count 1, 2, 3, 4')" enumeration. Direct response to the Isabelle leak.

Plus the polish-by-default flip in the demo, which trades a second LLM call for consistently cleaner output during the demo recording.

## What changed

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — added two module-level constants:
  - `_METRIC_GUARD_RULE` — superset of all six prompts' previous metric-guard wording (covers `beat-clarity`, `percussiveness`, `RMS`, `onset-density` / `onsets/beat`, `accent-pattern arrays`, `tempo-stability`, `beat-strength values`) plus the new positive-replacement clause.
  - `_KIZOMBA_DOWNBEAT_GUARD_RULE` — the Phase-33b listening-guide version (most evolved), strengthened with explicit forbidden-position examples (`'step on 1 and 3'`, `'land on count 4'`, `'count 1, 2, 3, 4'`).
- **Five prompts refactored** to interpolate the shared helpers via f-string at module-load time: `QUESTION_LISTENING_GUIDE`, `QUESTION_KIZOMBA_TUTOR`, `QUESTION_KIZOMBA_DRILLS`, `QUESTION_SONG_ARC`, `QUESTION_DANCER`. The `{style}` placeholder survives because it lives in non-f-string elements of the prompt tuple. Per-prompt addenda (kizomba_tutor's "If tempo helps, mention it at most once...", drills' "The phase time span is enough numeric grounding") were preserved inline.
- **The downbeat guard now applies to `kizomba_tutor` and `kizomba_drills` in its strengthened form** — previously they had a much weaker negative-only version. This is the change that addresses the Phase 34 Isabelle leak at the prompt level (instead of relying on polish to catch it).
- **Polish kept untouched.** `KIZOMBA_TUTOR_POLISH_SYSTEM` and `build_kizomba_tutor_polish_prompt` were not refactored — different shape, no observed leak, scope creep.
- **[tests/test_prompts.py](../../tests/test_prompts.py)** — three new tests:
  - `test_metric_guard_rule_canonical_wording` — pins the canonical phrasing of `_METRIC_GUARD_RULE`, including the Phase-34-derived positive-replacement clause.
  - `test_kizomba_downbeat_guard_rule_canonical_wording` — pins the canonical phrasing including the Phase-34-derived specific-position enumeration (`'step on 1 and 3'`, `'land on count 4'`).
  - `test_shared_guards_used_in_consuming_prompts` — asserts each consuming prompt actually contains the shared helper text. Catches a future refactor that accidentally drops the helper.
- **Three existing tests updated** to assert against the new canonical wording instead of the old per-prompt wording: `test_question_kizomba_tutor_hides_raw_metrics_from_final_answer`, `test_question_kizomba_drills_hides_raw_metrics`, `test_question_kizomba_drills_forbids_downbeat_and_requires_duration`.
- **[notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb)** — three markdown cells reframed:
  - Tutor section heading: was "What Gemma teaches — one-pass kizomba tutor", now "What Gemma teaches — kizomba tutor, one-pass and polished" with explicit framing that polish is the demo recording's default and one-pass is shown for transparency.
  - Polish heading: was "Optional polished rewrite", now "Polished rewrite — the demo's recommended kizomba_tutor output". Removed the "Opt-in (doubles LLM cost)" framing.
  - Demo-closing summary: replaced the "Optional polish pass" bullet with a "Polished kizomba tutor by default" bullet that explains the trade-off.

No code-cell edits — `kiz_polished` was already running by default; the change is editorial framing.

## Evidence / test results

**Tests (clean run after Phase 35 refactor):**
```
$ python -m pytest
================= 408 passed, 1 skipped, 64 warnings in 47.41s =================
```
405 baseline → 408 (3 new shared-helper tests). No regressions in the 5 refactored prompts; existing per-prompt tests pass after wording update.

**Live run on 7 tracks (Filomena + 6-track extended set) against `gemma-4-26b-a4b-it`:**

What worked:
- **Zero metric-decimal leaks across all 7 listening_guide outputs.** The Calo Pascoal-class `0.34` Phase-34 leak is fully gone. The positive-replacement clause did its job.
- **Zero `step on 1 and 3` leaks across all kizomba_tutor outputs.** Isabelle's main ×8, the Phase-34 trigger, now says _"try a half-time feel by slowing your walk to match the pulse"_ — uses "half-time feel" but never names 1 and 3. The hardened downbeat guard caught this.
- **kizomba_tutor section roles still working** — Daniel Santacruz still produces 11 substantive role-named lines. No regression.
- **Bachata side stayed clean** apart from one borderline phrase (see below).

What still leaked: **3 of 7 listening_guide outputs leaked the word "downbeat"** (Filomena, Calema, Tu_Es_um_Erro). Down from 5/7 in Phase 34, but not zero. The pattern was identical across all three: _"Because the downbeat is acoustically subtle/ambiguous/not clearly defined..."_

**Diagnosis: self-induced echo from helper rationale.** The Phase 35 `_KIZOMBA_DOWNBEAT_GUARD_RULE` used the word "downbeat" three times in its own rationale text:
> _"...Kizomba's **downbeat** is acoustically subtle and detection is unreliable. If the music's lack of a clear **downbeat** needs acknowledging, frame it as 'the pulse is felt rather than heard' or 'the bass carries the pulse' — never as 'the 1' or 'the **downbeat**'..."_

The model was paraphrasing the helper at the user. _"Because the downbeat is acoustically subtle..."_ is essentially a direct echo of _"Kizomba's downbeat is acoustically subtle..."_ The Phase 35 positive-replacement clause worked (the model is also saying _"the pulse is felt rather than heard"_ — also straight from the helper). But the rule-text itself taught the model the very word it shouldn't write. **Lesson: helper rationale text becomes echoed vocabulary. Negative rules should keep the forbidden token only in the forbidden-token list, never in declarative explanation.**

**Borderline issue (not addressed):** the bachata listening_guide once used _"during the high-energy segments where the **onset density** increases significantly"_ — qualitative use of analysis jargon, no decimal. Borderline against "no analysis jargon"; deferred.

## Phase 35b — same-commit iteration after the self-induced echo finding

The 3-of-7 "downbeat" echo isn't acceptable as ship state, and the fix is small: rewrite `_KIZOMBA_DOWNBEAT_GUARD_RULE` to keep "downbeat" only inside the forbidden-token list, removing it from all declarative rationale text, and add an explicit meta-instruction _"not in narration, not in negation, not when explaining why kizomba is hard to count"_.

**What changed in 35b:**

- `_KIZOMBA_DOWNBEAT_GUARD_RULE` rewritten — the rationale no longer contains _"Kizomba's downbeat is acoustically subtle..."_, _"the music's lack of a clear downbeat..."_, or _"never as 'the 1' or 'the downbeat'"_. The rule now opens with _"Do NOT use the word 'downbeat' or the phrase 'the 1' anywhere in your output — not in narration, not in negation, not when explaining why kizomba is hard to count."_ The forbidden-position enumeration (`step on 1 and 3`, `land on count 4`, `count 1, 2, 3, 4`) and the positive-replacement clause (_"the pulse is felt rather than heard"_, _"the bass carries the pulse"_) are kept verbatim.
- `test_kizomba_downbeat_guard_rule_canonical_wording` updated — the test now asserts the new wording (`do not use the word 'downbeat'`, `not in narration`, `not in negation`) and adds three regression checks that the helper does **not** contain the previously-echoed phrases (`downbeat is acoustically`, `downbeat is subtle`, `lack of a clear downbeat`). If a future refactor reintroduces declarative downbeat-mentions in the helper, the test fires.

**35b tests (clean):**
```
$ python -m pytest
================= 408 passed, 1 skipped, 64 warnings in 45.48s =================
```

**35b live re-run on the same 7 tracks:**

- **The "downbeat" echo is gone across all 7 listening_guide outputs.** Filomena, Calema, Tu_Es_um_Erro all clean. The "not in narration, not in negation" meta-instruction worked.
- **No regression in positive replacement.** Listening guides still produce phrasings like _"the pulse is felt rather than heard"_ and _"the bass carries the pulse"_ where appropriate.
- **No regression in section roles, kizomba_tutor coaching, drills, or polish.** All clean.
- **One new leak surfaced — same family, different prompt.** Bachata song_arc:
  > _"This track is distinguished by an unusually low **percussiveness of 0.16**, meaning the melodic content carries the rhythm more than the drums."_

  `0.16` is **not in the actual analysis** for this track (bachata section-table P× values range from 0.27 to 1.46). The value came from the helper's own example list — `'0.16 percussiveness'` was listed as a forbidden phrasing. The model lifted the literal decimal as a value to quote on this track. **This is a generalisation of the 35b lesson:** it's not just forbidden *words* that get echoed from helper rationale — it's forbidden *example values* too. Same failure mode, different vocabulary.

## Phase 35c — same-commit iteration, parallel fix to 35b

The lesson at this point is clear: **anything specific in the helper rationale becomes vocabulary the model reaches for**. Forbidden-word example → echoed (35b). Forbidden-decimal example → echoed (35c).

**What changed in 35c:**

- `_METRIC_GUARD_RULE` rewritten — the example list `"'percussiveness of 0.22', 'beat clarity 0.34', or '0.16 percussiveness'"` was removed entirely. Replaced with: _"Do NOT use any specific decimal number from the analysis as a quantity in your output — not in narration, not as a distinguishing feature, not when explaining why a section is hard. Constructions like 'percussiveness of <number>' or 'beat clarity of <number>' are forbidden in any form."_ The forbidden categories list and the positive-replacement phrases ("drum-light feel" etc.) are kept verbatim.
- `test_metric_guard_rule_canonical_wording` updated — asserts the new wording (`do not use any specific decimal number`, `not in narration`, `not as a distinguishing feature`, `<number>` placeholder) plus three regression checks that the helper does **not** contain `0.22`, `0.34`, or `0.16` as substrings. If a future refactor reintroduces specific decimal examples, the test fires.

**35c tests (clean):**
```
$ python -m pytest
================= 408 passed, 1 skipped, 64 warnings in 45.06s =================
```

**35c live re-run on the same 7 tracks:** clean across the board.

- **Zero raw decimals in any Gemma output** across all 12+ LLM calls (listening_guide × 7, song_arc × 2, kizomba_tutor × 7 one-pass + 7 polished, drills × 1, dancer × 1). The only `0.NN` matches in the dump files come from the DSP `describe_sections` table itself, which is appropriate (that's the analysis layer reporting metrics, not Gemma narrating them).
- **Zero `downbeat` word in any Gemma output.** All `downbeat` matches come from the DSP table (`downbeat offset = 2 (confidence = 0.14)`, `low downbeat confidence 0.19`). 35b's "not in narration, not in negation" rule held up.
- **Bachata song_arc fixed.** Previous 35b run: _"distinguished by an unusually low **percussiveness of 0.16**"_. Post-35c: _"distinguished from typical bachata by its unusually low percussiveness, meaning the rhythm is carried more by melodic content than by drums."_ Qualitative, no decimal lifted from the helper.
- **No regressions.** Section roles still applied across the kizomba_tutor outputs. Drills format clean. Polish output reads consistently strong. Bachata `dancer` clean. Listening guides keep the positive-replacement phrasing (`"the pulse is felt rather than heard"`, `"the bass carries the pulse"`, `"feel the underlying pulse"`) where appropriate.
- **No new awkward phrasing from abstract `<number>` placeholder.** The model didn't echo the placeholder back. The new wording reads naturally in narration.

## What worked (after 35c live re-run)

- **The shared metric-guard / kizomba-downbeat-guard refactor architecturally pays off.** When Phase 35 found a leak (Calo Pascoal `0.34`), Phase 35b found a different one (Filomena/Calema/Tu_Es echoes), and Phase 35 live re-run found a third (bachata `0.16`), each fix was a single helper edit + a single test update. Five consuming prompts inherit the fix automatically.
- **Three-iteration learning curve recorded.** 35a structural refactor → 35b rationale-text echo fix → 35c example-value echo fix. Each iteration narrowed the helper to safer ground. The architectural lesson now lives in this doc as a 3-point checklist for future helper edits.
- **Every Gemma output across the seven kizomba tracks plus Propuesta Indecente landed cleanly on the demo-recording threshold.** The demo flow (DSP → listening_guide → song_arc → tutor (one-pass + polished) → drills) is in shippable shape.

## What did not work / limitations (after 35c live re-run)

- **Bachata `onset density` qualitative leak (carried forward from Phase 35).** Borderline; not addressed in 35c. _"during the high-energy segments where the onset density increases significantly"_ — uses analysis jargon as a phrase but no decimal. Defer until live evidence shows it's a real demo problem.
- **"Normal" track no-role kizomba_tutor (carried forward from Phase 34).** Still no role names on its main groups. Coaching is still substantive. Defer; non-deterministic edge case.
- **Polish output occasionally drops a per-phase coaching focus** that the one-pass had (e.g. removing "follow the bass line" hints). Polish polishes language but sometimes flattens detail. Acceptable trade-off; not worth iterating.
- **f-string interpolation footgun is still present** as documented earlier — if a future helper text contains `{...}` it will break consuming `{style}`-templated prompts. Mitigation: code review on future helper edits.

## Decision / takeaway

**Ship Phase 35 + 35b + 35c together as a single commit.** The shared helpers replace three drifted versions of the same rule with one canonical wording, and three iterations have proven it leak-free across 12+ LLM calls on the seven evaluation tracks. The architectural lesson is recorded.

**Architectural lesson (final form, three-point checklist for future helpers):**

1. Does the helper rationale use the *forbidden word* in any form (declarative, negation, "do not name")? If yes, replace with a generic noun (`'rhythmic anchor'` instead of `'downbeat'`) and add an explicit "not in narration, not in negation" meta-instruction.
2. Does the helper rationale list *specific example values* (decimals, named instruments, P# patterns) the model could lift as content? If yes, replace with a placeholder (`<number>`, `<some-instrument>`, `Pn`) so the model can't quote the example as a value.
3. Does the helper end with a clear *positive replacement* the model can use instead? If yes, the negative rule + positive replacement together gives the model both a what-not and a what-instead.

Phase 33b and Phase 35 each had to learn one of these the hard way. Phase 35b/35c proved both apply to the same helper. The next prompt that adds a new rule should run this checklist first.

## What worked (after 35b live re-run)

_TBD after 35b live re-run._

## What did not work / limitations (after 35b live re-run)

_TBD after 35b live re-run. Carry-forward watch list:_

- **f-string interpolation footgun.** If a future prompt adds a `{...}` placeholder inside the helper text it will conflict with `.format(style=...)` on consuming prompts. Mitigation: helpers contain no `{` or `}` characters today and a code review on future helper edits should keep them out.
- **Shared helper for `dancer` might over-specify on bachata.** The metric-guard wording lists kizomba-style examples ("pulse felt through the bass") that are slightly off-style for bachata. The model should generalise but watch for awkward bachata phrasing.
- **Bachata `onset density` qualitative leak.** Borderline; deferred. Not a hard decimal violation but uses analysis jargon. Would need additional positive-replacement wording in `_METRIC_GUARD_RULE` ("instead of 'onset density', say 'how dense the rhythm feels'") if it becomes more common.

## Decision / takeaway

**Architectural lesson worth recording:** prompt rationale text becomes echoed vocabulary. Negative rules should keep the forbidden token (and forbidden example values) only in the forbidden-token list, never as declarative explanation or concrete examples. Phase 33b strengthened the kizomba downbeat guard with rationale to make the rule "more emphatic"; Phase 34 confirmed the strengthening helped on `step on 1 and 3`; Phase 35 rolled the strengthened rule out to all kizomba prompts; Phase 35 live evidence revealed the echo failure mode (declarative downbeat references); Phase 35b removed the rationale echo source; Phase 35 live re-run revealed the *same* failure mode applied to numeric examples; Phase 35c removed those too.

The lesson generalises beyond this rule — the next time we add a strengthening rationale to a prompt rule, ask:

1. Does the rationale use the forbidden word in any form? (35b lesson)
2. Does the rationale list specific example values the model could lift? (35c lesson)
3. If yes to either, replace with a generic placeholder (`<number>`, `<some-word>`) and an explicit "not in narration" meta-instruction.

If the 35c live re-run shows the `0.16`-class leak is gone and no new regressions: ship Phase 35+35b+35c together. If a residual leak persists across more than 1-of-12 LLM calls, the next move is the **structural post-processor** that the project has flagged since Phase 29 — it validates output for forbidden tokens and repairs or regenerates. Higher engineering cost but eliminates non-determinism.

## Next step

1. **35c live re-run on the same 7 tracks.** Verify the bachata song_arc `0.16` leak is gone. Verify the abstract phrasing doesn't introduce new awkwardness.
2. **Phase 36 candidate — rhythm anatomy.** Brainstorm item #6. A one-time per-style explainer that runs at the top of the demo and describes the *anatomy* of the genre's rhythm. Lands on the same "help the learner understand the music" thread. Now that 35a/b/c have hardened the helpers' wording discipline, rhythm anatomy can use them from day one.
3. **Structural post-processor (only if 35c leak rate is still >0).** Higher engineering cost; principled fix for non-determinism.
