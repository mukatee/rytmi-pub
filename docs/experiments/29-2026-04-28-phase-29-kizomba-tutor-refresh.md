# 2026-04-28 — Phase 29: kizomba tutor prompt refresh

## Goal

Turn the fixed kizomba beat tracker into better learner-facing coaching.
Phase 28 made the beat tracker real again (F=0.678 on 19 tap takes after
the mel-filterbank fix + `wait_ms=450`), but notebook 07 still sounded
like a metrics report rather than a dance tutor.

The goal of this phase is to make `kizomba_tutor` translate beat-clarity
and section structure into practical movement guidance for a
beginner/improver learner.

## Context / prior state

The first post-fix notebook 07 pass showed that the DSP was now mostly
good enough for learner-facing work: Baila, Filomena, and Bonga produced
stable beat markers, and the remaining Charbel / Filomena issues were
mostly localized to non-dance sections, section-label disagreements, or
short wrong-phase recovery moments.

The tutor prompt was the weak link. It was grounded, but too numeric.
Example outputs before this phase:

```text
P1: 0s–13s, low energy [beat: clear] — Anchor your step here at 108 BPM starting at 0.15s; the beat clarity is 0.67.
P6: 148s–159s, low energy [beat: clear] — This break at 148s is a safe anchor; use the stillness to reset.
```

Those lines are technically tied to the analysis, but they are weak
coaching. A beginner does not know what to do with a fractional
beat-clarity score, and "anchor at 108 BPM" is less useful than a body
cue.

## Hypothesis

The DSP numbers should stay inside the prompt context, but the final
answer should convert them into movement strategy:

- what the section asks from the body (settle, walk, reduce, reset,
  build, avoid chasing percussion),
- one safe concrete option (small weight shifts, mark the pulse in
  place, walk evenly, count 4 or 8 beats internally),
- and how to build from or simplify relative to the previous section.

For the current MVP, the default learner level should be
beginner/improver. Exact moves should be examples, not commands.

## What changed

- `src/rytmi/prompts.py`
  - Rewrote `QUESTION_KIZOMBA_TUTOR` so Gemma acts like a
    beginner/improver dance coach, not a metrics narrator.
  - It now asks for movement strategy plus a safe option: small weight
    shifts, marking the pulse in place, reducing travel, walking evenly,
    counting internally, waiting for the next stable pulse, or building
    gradually from the previous section.
  - It explicitly says not to quote beat-clarity decimals,
    onsets/beat, percussiveness, RMS ratios, or repeated BPM values in
    the final answer. Phase time spans remain enough numeric grounding.
  - It keeps the style guardrail: do not name a kizomba downbeat / "1".
  - It warns that `break` should not automatically mean silence or
    stillness.

- `tests/test_prompts.py`
  - Updated the `kizomba_tutor` prompt test from "must keep numeric
    anchoring" to "must translate metrics into learner-facing movement
    coaching".
  - Added a regression test that the prompt hides raw metrics from the
    final learner-facing answer.

No DSP code changed in this phase.

## Evidence / test results

Commands run:

```bash
/home/dr/koodit/kaggle-gemma4-rytmi/.venv/bin/python -m pytest tests/test_prompts.py -q
/home/dr/koodit/kaggle-gemma4-rytmi/.venv/bin/python -m ruff check src/rytmi/prompts.py tests/test_prompts.py
/home/dr/koodit/kaggle-gemma4-rytmi/.venv/bin/python -m pytest tests/ -q
```

Results:

- prompt tests: `24 passed`
- ruff on touched Python files: passed
- full test suite: `379 passed, 1 skipped`

Notebook 07 was re-run manually on three representative tracks.

### Baila Kizomba Amor

```text
P1: 0s–13s, intro [beat: clear] — Feel the comfortable slow pulse together with minimal movement; just small weight shifts to connect.
P2: 13s–212s, main ×16 [beat: clear] — It is safe to trust the steady pulse; try a steady walk-step and follow the bass line.
P3: 212s–233s, peak [beat: clear] — Use the clear pulse to add more expression and stronger saídas as the energy rises.
P6: 302s–314s, outro [beat: clear] — The pulse remains easy to follow, so slow down and return to minimal movement to end gently.
```

This is a clear improvement over the old "108 BPM / clarity 0.67"
language. It gives a simple arc: connect with small shifts, walk the
steady pulse, add expression at the peak, reduce at the outro.

### Filomena / Teu Toque

```text
P1: 0s-12s, intro [beat: clear] — Trust the steady pulse and use small weight shifts to find your connection.
P2: 12s-59s, main ×4 [beat: clear] — It is safe to trust the pulse; try a steady walk-step to travel a little more.
P6: 148s-159s, break [beat: clear] — This is a quieter section; pause and hold, using stillness as part of your dance.
P7: 159s-195s, main ×3 [beat: clear] — Re-enter the pulse with a steady walk-step.
```

This is mostly better, especially the re-entry cue. The weak line is
the `break`: even though the prompt warns not to assume silence or
stillness, Gemma still chose "pause and hold". Future prompt work should
prefer "reduce travel / mark the pulse / reset" for clear-beat breaks.

### Bonga

```text
P1: 0s-13s, intro [beat: moderate] — Stay compact and test the pulse with small weight shifts.
P2: 13s-65s, main ×4 [beat: moderate] — continues, avoid chasing extra percussion and just feel the steady pulse.
P4: 158s-165s, peak [beat: moderate] — Use this energy to travel a little more with your walk-steps.
P7: 287s-301s, outro [beat: subtle] — The pulse is hard to lock onto; make movement smaller and just mark the pulse in place.
```

Bonga is the strongest result. It gives compact movement, avoids
chasing extra percussion, allows a little more travel at the peak, and
gives a concrete fallback when the pulse becomes subtle.

## What worked

- The tutor stopped leaking raw analysis numbers into the final answer.
- The output now gives beginner-usable actions: small weight shifts,
  steady walk-step, compact movement, avoiding extra percussion, gradual
  travel, and marking the pulse in place.
- The prompt still stays grounded in the phase labels and beat-feel
  labels, and it still avoids claiming a meaningful kizomba "1".
- The output is simple enough for beginner/improver coaching. It does
  not jump into advanced timing concepts too early.

## What did not work / limitations

- The wording is still generic in places, especially repeated
  `continues` lines.
- `break` handling still needs one more tightening pass. In Filomena,
  Gemma still wrote "pause and hold" for a clear-beat break. That may
  be valid sometimes, but it should not be the default because several
  detected breaks still have strong beat and singing.
- The prompt has no explicit learner-level parameter yet. Beginner,
  improver, intermediate, and advanced coaching should eventually use
  different language and different movement options.
- The tutor is not yet a deep kizomba teacher. It gives safe movement
  strategies, but not detailed partner connection, body mechanics,
  musical phrasing, or styling choices.

## Decision / takeaway

Ship this prompt version as the first useful `kizomba_tutor` refresh.
The main product bottleneck is no longer the beat tracker or raw DSP
numbers; it is turning structured analysis into coaching language.

For the MVP, defaulting to beginner/improver movement strategy is the
right level. The tutor should offer grounded options, not prescribe a
single exact move.

## Next step

1. Re-run notebook 07 on all 5 tap-reference kizomba tracks and keep the
   outputs as Phase 29 evidence.
2. Make a small follow-up prompt tweak for `break` labels: for clear-beat
   breaks prefer "reduce travel / keep the pulse / reset" over
   "pause-and-hold" unless the beat is subtle.
3. Consider adding a `learner_level` option later:
   - beginner: concrete physical actions,
   - improver: movement quality and choices,
   - intermediate: transitions and contrast,
   - advanced: suspension, delayed weight changes, and interpretation.
4. Keep Phase 30 DSP work conditional. The strongest possible future DSP
   direction is a periodic-pulse / tempo-continuity tracker for wrong-phase
   recovery, but only if the tutor validation shows learner-facing harm.

---

## 2026-04-28 — Phase 29b: self-critique polish + break-handling tweak

### Goal

Pick up the two follow-ups Phase 29 explicitly flagged: (1) the
`break`-label phrasing tweak so clear-beat breaks stop defaulting to
"pause and hold", and (2) the notebook 07 self-critique trial committed
in `575a8cc`. Move the trial from notebook-only with hardcoded drafts
into a reusable helper, and re-run notebook 07 across all 5 kizomba
tap-reference tracks (not just Baila / Filomena / Bonga) so the demo
sprint going into the 2026-05-18 deadline has demoable coaching content.

### What changed

1. **One-pass prompt tweak** — `QUESTION_KIZOMBA_TUTOR` in
   `src/rytmi/prompts.py` now spells out recovery vocabulary on
   `break` labels. The old rule said only "do not assume silence or
   stillness". The new rule names the failure mode ("do not default to
   'pause and hold'"), reserves stillness for genuinely `subtle` beats,
   and tells the model what to suggest on `clear` / `moderate` breaks:
   reduce travel, keep a small pulse in the body, reset, then reconnect
   on the next phase. This makes the discovery from the self-critique
   trial cheaper — every one-pass output now gets the better break
   handling without paying for a second LLM call.

2. **Reusable polish helper** — moved the notebook's `SELF_CRITIQUE_*`
   prompt scaffolding into `src/rytmi/prompts.py` as
   `KIZOMBA_TUTOR_POLISH_SYSTEM` and
   `build_kizomba_tutor_polish_prompt(track_name, draft)`. Added
   `polish_kizomba_tutor_output(draft, processor, model, track_name=...)`
   in `src/rytmi/llm.py` next to `explain_rhythm`. The helper is a thin
   wrapper around `generate(...)` — no new backend code, no caching, no
   retry, matching the rest of the module. The rewrite preserves every
   P# header, time span, and beat tag from the draft and only edits the
   coaching text.

3. **Notebook 07 refresh** — replaced the hardcoded 3-track `TUTOR_DRAFTS`
   dict with a live loop over the 5 kizomba tap-reference tracks (Baila,
   Filomena, Charbel, Criola, MIKA). Bonga drops out of the smoke set;
   Charbel takes over as the honest "hard case" because it is the one
   with F=0.399 against tap-reference and clear `beat: subtle` sections
   — exactly the case where the tutor should surface uncertainty rather
   than overclaim danceability. The polish cell now imports
   `polish_kizomba_tutor_output` and renders one-pass + polished output
   side by side per track.

4. **Tests** — extended `tests/test_prompts.py` with five Phase 29b
   tests: the new break-handling vocabulary in `QUESTION_KIZOMBA_TUTOR`,
   the polish system prompt's overreach guards, the polish builder's
   draft + track-name embedding, structural preservation rules
   (P# headers, time spans, beat tags untouched, no add/remove
   sections), and rubric guards (no raw metrics, no downbeat / "1",
   recovery vocabulary mirrored on `break` labels).

### What worked (from the prior nb07 trial)

- The self-critique pass clearly improved Filomena's clear-beat break:
  the one-pass draft suggested "pause and hold"; the rewrite said
  "reduce travel and keep a small pulse in your body to reset". The new
  one-pass tweak should land that phrasing on the first call.
- Baila and Bonga rewrites both became more natural and less repetitive
  — fewer empty `continues` lines, more concrete movement strategy.
- Polished output preserved P# headers, time spans, and beat tags
  faithfully across all three tracks tested.

### What the 5-track end-to-end run surfaced

- Filomena's break is now phrased as "reset and reduce travel; keep a
  small pulse in your body" on the **first** call, confirming the
  break-handling tweak landed.
- Charbel's `beat: subtle` intro stays honest in both one-pass and
  polished output ("pulse is hard to lock onto; keep movement small
  with tiny weight shifts to find the connection"). No overclaiming.
- The polish pass consistently replaces empty `continues` lines with
  concrete movement strategy, and tightens "follow the bass" into
  "letting the bass guide the depth of your steps" / "letting the bass
  line anchor your weight shifts".
- **Label-slot bug found on Baila** — Gemma occasionally placed the
  energy descriptor (`low energy`, `low, medium energy`) into the
  section-name slot of the `P#: ..., <label> [beat: ...]` line instead
  of the section name (`intro`, `main ×16`, `peak`, `outro`). Root
  cause: the phase summary line in the analysis block puts both the
  section name and the energy descriptor on the same line, and the
  format spec in the prompt only said `<label>` without disambiguating.
  Fix: tightened the format spec to name the slot `<section>`,
  enumerated the canonical section names (`intro`, `main`, `break`,
  `short_break`, `build`, `peak`, `outro`), and explicitly forbade the
  energy descriptor in that slot. Polish can't repair a wrong label
  after the fact (it preserves draft headers), so the fix lives on the
  one-pass side. Test added in `tests/test_prompts.py`.

### Risks / what to watch

- A rewrite pass can preserve or amplify ungrounded language already
  present in the draft (e.g. "bass guide" phrasing seen in earlier Baila
  output). The polish system prompt forbids new instruments / musical
  facts but cannot guarantee removal of ones the draft introduced. Any
  future move to make polish a default should add a stricter content
  filter or run polish before the original ungrounded phrase is
  produced.
- Polish doubles LLM cost and latency. Keeping it opt-in is the right
  default until cost/latency posture is understood.
- Charbel's `beat: subtle` sections need a sanity-read after running
  notebook 07 end-to-end: if the polish pass smooths over the
  uncertainty into confident-sounding coaching, that is the kind of
  learner-facing harm that would trigger Phase 30 DSP work.

### Decision / takeaway

- Polish stays **opt-in**. One-pass output (with the break-handling
  tweak) remains the documented baseline.
- The break-handling tweak ships in `QUESTION_KIZOMBA_TUTOR` so every
  one-pass call benefits without paying for a second LLM call.
- Notebook 07 is now the demo source for kizomba tutor content going
  into the video sprint. The 5 tap-reference tracks cover the full
  difficulty spread (Baila / Criola = clear, Filomena / MIKA =
  mostly-clear, Charbel = honest-subtle).
- Phase 30 DSP (phase-recovery / tempo-continuity) remains deferred and
  conditional on tutor evaluation showing learner-facing harm.

### Next step

1. Run notebook 07 end-to-end against the local Ollama endpoint and
   capture per-track one-pass + polished output as Phase 29b evidence.
   Eyeball Charbel specifically for over-confident coaching on
   `beat: subtle` sections.
2. If polish is safe across all 5 tracks, consider a small `polish=True`
   flag on `explain_rhythm` (or a `polished` key in `explain_all`) so
   downstream callers can opt in without re-importing the helper.
   Defer until after the demo sprint unless it unblocks demo content.
3. Begin demo-readiness sprint: end-to-end demo notebook / script,
   video script outline, and Kaggle writeup skeleton. Phase 29b output
   is the seed material.