# 2026-05-10 — Phase 40d: Unified timeline + same-label transitions + notebook 09 broader application

## Goal

After Phase 40c (commit `c22be4a`) shipped the re-entry-primary prompt rewrite, two follow-ups landed in user feedback:

1. **Unified storytelling.** The polished `kizomba_tutor` and the verified `kizomba_transitions` were sold as separate outputs. A learner reading the notebook got two parallel narratives (per-phase coaching, per-boundary coaching) when they wanted one chronological story: P1 → T1 → P2 → … → T_n → P_n+1.

2. **Broader application.** Phase 40 evidence existed only on Filomena Maricoa _Teu Toque_. The user asked for transitions across `notebooks/09_kizomba_extended.ipynb` to validate the design across diverse songs (Charbel _E Magic_ for instrumentals + breaks, Daniel Santacruz _Lento_ for main-rich structure, Calo Pascoal for long-main, etc.).

User decisions captured this turn:
- **Same-label transitions: include them, but make them optional.** Try energy/role-shift transitions at boundaries where the section label doesn't change (`main ×4 [medium] → main ×2 [high]`). Default ON for the first run; flag flip-able to off if the same-label coaching reads as cruft vs the section-role vocabulary already in `kizomba_tutor`.
- **Combined scope: Phase 40d covers the unified timeline + same-label transitions + notebook 09 in one phase.**

## Hypothesis

A pure post-processing helper (`format_unified_timeline`) that interleaves P# and T# lines produces the chronological narrative the user wants without forcing extra LLM content. Adding an `include_same_label` flag to `extract_transitions` lets us empirically evaluate whether same-label energy-shift transitions add useful coaching or just duplicate the section-role vocabulary already in `kizomba_tutor`. Wiring the flow into notebook 09 gives us evidence on a diverse song set in one cycle.

## What changed

### Code (5 modules touched, 1 new helper)

- **[src/rytmi/dsp.py](../../src/rytmi/dsp.py)** — `extract_transitions(phases, *, include_same_label: bool = False)`. Default behaviour preserved (label-change boundaries only). With `include_same_label=True`, every consecutive phase boundary becomes a `Transition`, including same-label energy/role shifts. `describe_transitions(analysis, *, include_same_label: bool = False)` mirrors the flag so notebook displays match what the prompt sees.

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — three changes:
  - `_format_transitions_block(phases, *, include_same_label: bool = False)` — flag threaded through, plus the rendered block now includes `energy: <from_e> → <to_e>` per transition so the model can reason about same-label energy shifts.
  - `QUESTION_KIZOMBA_TRANSITIONS` — added a new rule branch for `<from_label>` == `<to_label>` cases. Coaches the role shift using the section-role vocabulary already in `kizomba_tutor` (sustaining → building → returning → closing); names subtler audible cues (bass density, percussion thickening) that match same-label transitions; explicitly tells the model to keep these lines short. Word cap bumped 200 → 220 to absorb the extra lines on rich tracks.
  - `format_unified_timeline(tutor_text, transitions_text)` — pure post-processing helper. Parses P# from the tutor output via a new `_KIZOMBA_TUTOR_P_LINE_RE` regex and T# via the existing `_KIZOMBA_TRANSITION_LINE_RE`. Sorts by `(time, kind)` where T# (kind=0) precedes P# (kind=1) at equal times so the transition reads as the bridge into the next phase. Falls back to passthrough under headers when the tutor text yields no parseable P# lines.

- **[src/rytmi/llm.py](../../src/rytmi/llm.py)** — `explain_rhythm` and `explain_all` both accept `include_same_label_transitions: bool = False`. `explain_all` only forwards the flag for the `kizomba_transitions` question key (other prompts ignore the transitions block). The `explain_all` verifier dispatch passes the flag to `extract_transitions` so the verifier sees the same set the prompt was given.

- **Test suite — 10 new tests; 458 passed + 1 skipped (was 448).** No regressions.
  - `tests/test_dsp.py` (3 new): default excludes same-label, flag-on emits energy shifts, Filomena 8-phase arc yields 4 vs 7 transitions.
  - `tests/test_prompts.py` (7 new): block includes energy field, prompt has same-label rule branch with role vocabulary, and 5 unifier tests covering chronological interleave, T#-before-P# at equal times, empty-transitions passthrough, parseable-tutor fallback, and same-label interleave between same-label P# lines.

### Notebooks

- **[notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb)** — `demo-imports` adds `format_unified_timeline` import + new `INCLUDE_SAME_LABEL_TRANSITIONS = True` flag. Transitions code cell (`28ab7b58`) now extracts and prompts with the flag. New markdown + code cell pair (`66711b18` + `0e9cca86`) inserted after the transitions cell renders the unified timeline. Output dump (`1447fabb`) extended with the unified timeline entry.

- **[notebooks/09_kizomba_extended.ipynb](../../notebooks/09_kizomba_extended.ipynb)** — `config` cell adds the same imports + `RUN_KIZOMBA_TRANSITIONS = True` and `INCLUDE_SAME_LABEL_TRANSITIONS = True` flags. Per-track helper (`helper-cell`) extended to run transitions extraction + prompt + verifier per track and print the result alongside the tutor + drills outputs. Output dump cell (`78cbb753`) extended to capture transitions table, T# lines, verifier stats, raw Gemma draft, and the per-track unified timeline (built from polished tutor when available, draft otherwise).

## Evidence / test results

**Tests (clean run after all changes):**
```
$ python -m pytest
================= 458 passed, 1 skipped, 64 warnings in 45.81s =================
```

448 (Phase 40c baseline) → 458 (10 new Phase 40d tests). No regressions.

**Live run on notebook 00 (Filomena, with flag=True):** ✅ confirmed.
- 7 transitions extracted as predicted (4 label-change + 3 same-label `main → main` energy shifts at 59s/80s/121s).
- Same-label T# lines coach the role shift using prompt vocabulary: T2 (medium → high) "as the percussion thickens, travel a little more and add intention"; T3 (high → medium) "as the energy settles, keep the basic and hold a steady frame"; T4 (medium → high) mirrors T2.
- Unified timeline reads as a single chronological narrative P1 → T1 → … → T7 → P8. The transition lines bridge into the next phase as designed.
- Verifier stats: `parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7`. Clean.
- Read-aloud assessment: the high-stakes T# lines (T1 intro→main, T5 main→break, T6 break→main, T7 main→outro) are exactly where a kizomba learner most needs help and earn their line. The same-label main→main T# lines have **moderate redundancy** with the polished tutor's role-naming vocabulary (sustaining / building / returning) — they paraphrase rather than complement on this track. They retain unique value via the audible cue ("percussion thickens", "energy settles") that P# does not carry.

**Live run on notebook 09 (extended set, with flag=True):** ✅ design holds across the pool.
- Cross-track structural quality: clean. `boundaries_invented=0` and `skipped_lines=0` on **16 of 17 tracks**.
- One verifier issue surfaced: **Daniel Santacruz _Lento_, T9 (222s, main → main)** — the model emitted `[main → main, beat: clear → high/medium]` (confused beat with energy in the bracket). Verifier correctly dropped the malformed line and filled it with the deterministic fallback. Stats: `boundaries_missing_filled=1 skipped_lines=1`.
- The fallback that filled it was the original Phase 40 template `"In the last 8-count of the main, prepare for the shift; on entering the main, settle into the new feel."` — count-based anticipation, exactly what 40c forbade in the prompt. **Bug:** the structural fallback path silently re-introduced the language the prompt rewrite engineered out. Fix below in the Decision section.
- Word-cap pressure: **none observed**. Richest tracks delivered 9-10 T# lines well within the 220-word cap (Charbel 9, Don Kikas 9, MIKA Mendes 10, Daniel Santacruz 10). The 200 → 220 bump was sufficient; Phase 41 top-N filtering not justified by this evidence.
- Long-main tracks (Calo Pascoal `main ×12`, Isabelle Felicien): 5 and 3 transitions respectively, all label-change. Same-label flag does not pile up content because the segmenter merged the runs. Design degrades gracefully.
- Same-label T# lines across the pool **converge on ~3 stock phrases** ("as the percussion thickens / energy lifts, travel a little more and add intention", "as the energy settles, keep the basic and hold a steady frame", "as the energy fades, contract your movement…"). Within a single track this reads natural; in batch scope the repetition is visible (e.g. Bonga T2/T5 near-identical). This is a viewing artifact of the batch dump, not a per-track quality issue.

## What worked / didn't / decision

**Worked:**
- `format_unified_timeline` is the right shape. Pure post-processing, no extra LLM call, single chronological narrative. Ship it as the canonical demo surface.
- Re-entry-primary prompt rewrite (40c) held up across the broader pool. Scanned ~80 model-produced T# lines across 17 tracks and found **zero count-based anticipation language** in Gemma output. The prompt rule is sticking.
- Same-label flag opt-in design is the right granularity. Notebook-level `True` for single-song demo coherence, library-level `False` for batch use.
- Verifier structural quality is solid: `boundaries_invented=0` on 17/17 tracks (the model never hallucinated a boundary), `skipped_lines=0` on 16/17 (one malformed bracket caught and filled).

**Didn't:**
- Same-label main→main T# lines have moderate redundancy with the polished tutor's role-naming vocabulary. They are **not noise**, but they don't carry their own weight as well as label-change transitions. Their unique value is the audible-cue anchor (bass density, percussion thickening) — which is also their justification for shipping.
- The original Phase 40 fallback template wording was count-based ("In the last 8-count of the X, prepare for the shift…"), so any time the model botches a transition line, the verifier silently re-introduced the language 40c was supposed to ban. Caught here only because the broader notebook 09 run made the bad path observable.

**Decisions:**
1. **Unified timeline ships as the canonical demo surface.** Use it in the storyboard for the Filomena demo.
2. **Same-label transitions: keep `INCLUDE_SAME_LABEL_TRANSITIONS=True` in notebooks; library default stays `False`.** The opt-in story matches the value gradient — useful in single-song demo context, repetitive in batch context. Don't flip the library default based on aggregate-view repetition; that's a viewing artifact.
3. **Fallback template wording rewritten to be re-entry-primary, never count-based.** Done in this commit: `_fallback_transition_tail` in [src/rytmi/prompts.py](../../src/rytmi/prompts.py) now mirrors the prompt's branch language. New regression test `test_verify_transitions_fallbacks_never_use_count_based_language` in [tests/test_prompts.py](../../tests/test_prompts.py) exercises every fallback branch and asserts none of the banned anticipation phrases ("8-count", "8 count", "in the last", "in the final", "after N beats", "counts before") appear in the cleaned output. Tests: 459 passed (was 458). The Daniel Santacruz T9 fill on the next notebook 09 run will read "as the energy shifts, keep the basic and hold a steady frame" instead of the count-based string.

## Next step

### Limitations identified in 40d, framed as future work

These are visible cracks in the current output that the demo will be honest about and that future phases should address. They are the recurring theme of "the system reads as templated rather than song-specific," surfacing in three places:

1. **Coaching depth: from generic to song-specific.** Two artifacts of this:
   - **Drills are visibly weaker than transitions.** Notebook 09 stats: `kizomba_drills` skipped_lines 4-10 across the pool, with most "verified" drill lines collapsing to the literal template "Drill: practice steady weight transfers through this section." The model invents 12-25 phases, the verifier collapses back to the original 6-11, and the surplus turns into template fill.
   - **The transitions verifier fallback is a deterministic template.** When Gemma emits a malformed line (e.g. Daniel Santacruz T9), the verifier substitutes pre-written prose. This violates the project's "code identifies, **Gemma writes**, code verifies" signature: in the failure case, code is writing. The new wording is no longer count-based, but it is still a deterministic string the user could reasonably pick on.
   - **Probable direction:** richer per-phase / per-transition DSP context fed into prompts (one-line audible-cue fingerprint per phase: "bass-led, sparse percussion, vocals carry the line"); on-failure **targeted re-prompt to Gemma** ("Your line for T9 had a malformed bracket; the correct bracket is `[main → main, energy: medium → high]`. Rewrite just T9.") instead of deterministic substitution. Likely Phase 41 / 42 work.

2. **Transitions as connective tissue, not isolated bracket lines.** Same-label main→main T# lines on Filomena converge with `kizomba_tutor`'s role-naming vocabulary; across notebook 09 the same ~3 stock phrases recur. The bracket metadata Gemma sees is local (this transition's energy delta and beat clarity) — it has no view of "T2 returns to the energy of T0" or "this break echoes the intro." Linking transitions to phases they bridge and to repeated motifs in the song's arc would let them carry their own weight.

3. **Phases as a composite arc, not isolated entries.** P# lines currently read as independent items. They could reference each other ("returning to the energy of P2"), call out repeated motifs, name the song's overall shape. Same instinct as #2 applied upstream. Would also pull drills toward concreteness because each drill could anchor on what makes its phase distinct from neighbors.

These three threads share one root: **prompts get local context, not arc-aware context.** A future phase that synthesizes a one-pass "song arc summary" (a few lines naming the overall shape) and feeds it into every per-phase / per-transition prompt is the most likely shared fix.

### Immediate next actions before the deadline (demo-facing)

1. **Storyboard update (`docs/demo_storyboard.md`).** Reframe the Close (drop "what's next: transitions" since they ship). Restructure Act 3 around **Filomena _Teu Toque_ + Charbel _E Magia_** as a contrast pair: Filomena is the strong, forward-beat, energetic example shown end-to-end in Act 2; E Magia is a slower, more sensual feel shown as a 2-3 section highlight reel — the same pipeline adapting to a clearly different kizomba feel. Generalization without overclaiming.
2. **Writeup update (`docs/kaggle_writeup.md`).** Six modes → seven for kizomba. Highlight the unified timeline as the integration surface where "code identifies → Gemma writes → code verifies" is most visible. Add a candid limitations paragraph naming the three threads above as future work — being honest about the cracks reads stronger than hiding them.
3. **Stretch (if time permits): trial the targeted-retry fallback.** Replace the deterministic substitution path in `verify_kizomba_transitions_output` with a one-shot re-prompt to Gemma carrying the malformed input, the expected bracket, and the re-entry-primary rule. Even a small evidence base showing this works on the Daniel Santacruz T9 case would let the writeup say "Gemma writes; if it fails, Gemma rewrites" instead of "code substitutes." Out of scope only if the storyboard / writeup / video work absorbs the remaining time.

### Deferred / dropped

- **Phase 40b — bachata transitions.** Defer. Bachata is out of the demo video.
- **Per-boundary approach-window DSP** — defer; subsumed by the broader per-phase fingerprint direction in limitation #1.
- **Top-N transition selection** — drop; no word-cap pressure observed across 17 tracks, richest delivered 9-10 lines comfortably under cap.
- **Same-label flag default flip** — closed; keep notebook=True / library=False.
