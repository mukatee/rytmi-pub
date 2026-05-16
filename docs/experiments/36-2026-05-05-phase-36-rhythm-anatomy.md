# 2026-05-05 — Phase 36: Rhythm anatomy (per-style genre-literacy intro)

## Goal

Add a Gemma mode that explains what a *genre* sounds like, structurally, before any specific track is shown. `QUESTION_RHYTHM_ANATOMY` is style-templated, runs once per learning session, and produces one short paragraph (~120 words) covering tempo range, time signature, what carries the pulse, where the heavy emphasis lands, and the structural arc the learner will see in tracks below it.

Reframes the demo opening: instead of jumping straight into a specific kizomba/bachata track, the learner first gets the *genre* in plain language. Mirrors how a teacher would frame a class — _"here's what kizomba sounds like, broadly... now let's hear a specific song."_

## Context / prior state

Phase 33 (`d8c8972`) added the per-track listening guide. Phase 34 (`92389ad`) fixed kizomba_tutor's `continues` filler. Phase 35 (`24a60c3`, three-iteration arc 35a/b/c) lifted the metric-guard and kizomba-downbeat-guard wording into shared helpers and proved them leak-free across 12+ LLM calls on the seven evaluation tracks.

The brainstorm round before Phase 33 enumerated seven candidate teaching modes; #6 (rhythm anatomy) was anchored as the next phase across the Phase 33-35 docs. Phase 35's experiment doc closed: _"now that 35a/b/c have hardened the helpers' wording discipline, rhythm anatomy can use them from day one."_

The writeup's second-pass framing — _"Gemma helps the dancer hear and connect with what the music is doing"_ — has the listening_guide making this concrete at the per-track level. Phase 36 makes it concrete at the genre level. Together they give the demo flow a clean opening narrative: **genre intro → track-specific listening → coaching → drills**. This flow is also worth promoting to the writeup's central frame in a follow-up editorial pass.

## Hypothesis

A new `QUESTION_RHYTHM_ANATOMY` prompt that:

- Is **style-templated** (`{style}` placeholder; works for kizomba and bachata cleanly).
- Produces **one short prose paragraph** (~120 words, capped at 150).
- Inherits the Phase 35 shared helpers (`_METRIC_GUARD_RULE`, `_KIZOMBA_DOWNBEAT_GUARD_RULE`) from day one — no new wording to harden, no new leak surface.
- Is **explicitly forbidden** from referring to "this track" or quoting timestamps; the per-track listening_guide owns that role.
- Is **explicitly forbidden** from movement coaching; the tutor and drills own that role.

…will produce a genre intro that lands cleanly for both kizomba (no "the 1", uses syncopation / off-beat / bass-led-pulse vocabulary) and bachata (free to reference the güira pattern and the bongo-tumba grounding the "1" — the kizomba downbeat guard does not apply for non-kizomba styles).

## What changed

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — added `QUESTION_RHYTHM_ANATOMY` constant, registered as `ALL_QUESTIONS["rhythm_anatomy"]`. Style-templated, prose paragraph format, interpolates the Phase 35 shared helpers via f-string, includes the standard movement-coaching forbid + analysis-jargon-instrument forbid + length cap.
- **[tests/test_prompts.py](../../tests/test_prompts.py)** — 4 new tests:
  - `test_question_rhythm_anatomy_registered_and_grounded` — registered, style-templated, references canonical structural-arc vocabulary (intro/main/break/build/peak/outro).
  - `test_question_rhythm_anatomy_forbids_movement_coaching` — same differentiator as listening_guide; rhythm_anatomy is genre explanation, not movement coaching.
  - `test_question_rhythm_anatomy_is_genre_not_track` — must speak about the genre, not invent a hypothetical track or quote timestamps.
  - `test_question_rhythm_anatomy_uses_shared_helpers` — verifies `_METRIC_GUARD_RULE` and `_KIZOMBA_DOWNBEAT_GUARD_RULE` are interpolated into the prompt; catches a future refactor that drops the helpers.
- **[tests/test_llm.py:80-87](../../tests/test_llm.py#L80-L87)** — `test_all_questions_keys` updated to include `"rhythm_anatomy"`.
- **[notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb)** — markdown + code cell pair inserted right after each style's analyze step (and before the per-track work):
  - Kizomba: after `demo-kizomba-analyze`, before `demo-kizomba-dsp-md`.
  - Bachata: after `demo-bachata-run`, before `demo-bachata-gemma`.
  - Imports updated with `QUESTION_RHYTHM_ANATOMY`.
  - Output dump cell updated to capture both `kiz_anatomy` and `bach_anatomy` at the head of each style's section.
- **[notebooks/09_kizomba_extended.ipynb](../../notebooks/09_kizomba_extended.ipynb)** — single markdown + code cell pair inserted after the model-load cell, BEFORE the per-track helper. Loads the first track to satisfy the `explain_rhythm` API shape, runs `rhythm_anatomy` once, stores result in a module-level `RHYTHM_ANATOMY` for the dump cell. New `RUN_RHYTHM_ANATOMY` toggle in the config cell (default True). Intro markdown updated to call out the Phase 36 reframe.

No `llm.py` changes — the prompt runs through the existing `explain_rhythm()` pipeline. The "speak about the genre, not this track" rule keeps the model honest even though we pass an analysis for input-shape reasons.

## Evidence / test results

**Tests (clean run after Phase 36 changes):**
```
$ python -m pytest
================= 412 passed, 1 skipped, 64 warnings in 45.20s =================
```
408 baseline → 412 (4 new rhythm_anatomy tests). No regressions in any earlier prompt's tests.

**Live run on 7 tracks (Filomena + 6-track extended set + bachata Propuesta Indecente) against `gemma-4-26b-a4b-it`:**

### Kizomba rhythm_anatomy (notebook 00, ~110 words)

```
Kizomba is a rhythmic genre typically characterized by a tempo range between 85
and 110 BPM, usually set in a 4/4 time signature. Rather than relying on a heavy
percussive grid, the pulse is often carried by the bass line and melodic content,
creating a feel where the rhythm is felt through the weight of the music rather
than just heard through drums. The rhythmic anatomy often features syncopation
and off-beat emphasis, requiring a listener to connect with the underlying flow.
A typical track follows a structural arc that moves from an intro through various
main sections of varying energy, often including a distinct break for stillness,
before reaching a peak and settling into an outro.
```

What landed:
- **Tempo range** ✓ (85–110 BPM — accurate for kizomba).
- **Time signature** ✓ (4/4).
- **Pulse carrier** ✓ ("bass line and melodic content").
- **Off-beat emphasis** ✓ ("syncopation and off-beat emphasis").
- **Structural arc** ✓ (intro → main → break → peak → outro, in canonical phase-label vocabulary).
- **Genre-level, not track-specific** ✓ ("Kizomba is...", "A typical track follows...").
- **No "downbeat" word, no "the 1", no raw decimals.** Phase 35b/c shared-helper discipline held.

### Bachata rhythm_anatomy (notebook 00, ~110 words)

```
Bachata is a Latin dance genre set in a 4/4 time signature, typically played at
a tempo between 120 and 135 BPM. The rhythmic foundation is driven by a
combination of melodic content and percussion, such as bongos, which provide the
essential pulse. While the underlying meter remains steady, the rhythmic
character often features specific accents that punctuate the phrase. A standard
track follows a structural arc that begins with an intro, moves through various
main sections and breaks, incorporates a build and a peak of high energy, and
finally settles into an outro.
```

What landed:
- **Tempo range** ✓ (120–135 BPM — accurate for bachata).
- **Time signature** ✓ (4/4).
- **Pulse carriers** ✓ — bongos mentioned (correct for bachata; the güira isn't named explicitly but "specific accents that punctuate the phrase" covers it).
- **Structural arc** ✓ — intro → main → break → build → peak → outro.
- **Genre-level, not track-specific** ✓ ("Bachata is...", "A standard track follows...").
- **No "downbeat" word.** The kizomba guard doesn't apply but the model didn't reach for "the 1" either; it talked in pulse/accent terms. Acceptable — slightly less concrete than it could be (no güira naming), but clean.

### Kizomba rhythm_anatomy (notebook 09)

Same shape; ran once on the seed (first kizomba track from the extended set). Reads as a clean per-genre intro, not as commentary on the seed track. The "speak about the genre, not this track" rule held even with the per-track analysis as input.

### One regression — but in listening_guide, not rhythm_anatomy

Tu_Es_um_Erro listening_guide (Phase 33 prompt, not Phase 36):

> _"...Because the beat clarity is moderate and **the downbeat position is uncertain**, you may need to listen for the underlying pulse rather than relying on a strict count..."_

Single "downbeat" mention — same failure mode as Phase 35b's pre-fix state, on a different track. **Down from 3/7 (Phase 35) to 1/7 (Phase 35b/c) to 1/7 (Phase 36 — same listening_guide as 35c, fresh non-deterministic run).** The Phase 35b/c hardening reduced the rate but didn't eliminate it; non-determinism still allows occasional slips.

This is **not a Phase 36 regression** — it's a residual of the listening_guide downbeat guard's interaction with Tu_Es_um_Erro's specific structure (subtle intro + break sections invite "downbeat is uncertain" framing). Notable but not blocking.

## What worked

- **Phase 36 itself is clean.** Both kizomba and bachata genre intros land as genuine genre framing, not track narration.
- **Day-one inheritance of Phase 35 helpers paid off.** No new wording to harden; the metric guard and kizomba downbeat guard worked correctly on the new prompt without iteration.
- **Demo flow narrative now explicit.** _genre intro → DSP analysis → listening_guide → song_arc → tutor → drills_ runs cleanly per style. The opening genre paragraph frames everything below it.
- **No regressions in Phase 33 / 34 / 35 wins (with one exception, see below).** All section roles applied, drills format correct, polish output strong, no raw decimals anywhere in 12+ LLM calls.
- **Notebook 09 genre intro one-shot pattern works.** Loading just the first track to seed the genre intro is acceptable cost (~10s analyse) for the demo recording.

## What did not work / limitations

- **Tu_Es_um_Erro listening_guide downbeat slip** (1/7 tracks). Not a Phase 36 issue; pre-existing residual non-determinism from the Phase 35b helper. Polish doesn't catch it because polish runs on `kizomba_tutor`, not `listening_guide`. Options for future hardening: (a) extend polish to listening_guide, (b) add a structural post-processor that strips "downbeat" from listening_guide outputs, (c) accept as 1-in-7 non-determinism. Defer.
- **Bachata genre intro is slightly less concrete than it could be.** Mentions bongos but not the güira pattern by name. The "do not invent specific instruments" rule may have been over-applied. Acceptable for demo; could be loosened in Phase 37a.
- **Sub-style awareness still deferred.** Phase 36 produces ONE paragraph per genre; the user's note that kizomba has Angolan / urbankiz / tarraxo / etc. is anchored as Phase 37a (sub-style enumeration in same prompt).

## Decision / takeaway

**Ship Phase 36.** The new `rhythm_anatomy` prompt achieved its stated goal across both styles. Phase 35 architectural lessons paid forward — no new helper hardening was needed. The Tu_Es_um_Erro listening_guide leak is a separate concern with a separate fix path (and the rate is unchanged from Phase 35c, so it's not a Phase 36 regression).

**Lesson worth recording:** when a phase introduces a new prompt that reuses shared helpers from an earlier phase, those helpers should be live-tested in the new context but the testing burden is dramatically lower than for a from-scratch prompt. Phase 36 needed zero iteration to land, where Phases 33 / 34 / 35 needed 1-3 each. Architectural compounding works.

## Next step

1. **Phase 36 live run** on notebooks 00 and 09. Confirm both styles' intros read as genre framing and not as track narration.
2. **Phase 37a — sub-style enumeration in rhythm_anatomy.** Expand the prompt to add 2-3 sentences listing the major sub-styles per genre and their *rhythmic* distinguishers. Genre-literacy framing, no per-track claim. Cheap; same prompt, expanded scope.
3. **Writeup editorial pass — promote the demo flow.** Once Phases 36 and 37a land, revisit `docs/kaggle_writeup.md` and make the _genre intro → track listening → coaching → drills_ flow the central narrative. ~30 minutes of editorial work.
4. **Demo recording prep** — at this point the prompts are stable enough to film against. Storyboard against the new flow.
