# 2026-05-09 — Phase 39b: Bachata coaching surface wired into demo notebook

## Goal

Wire `QUESTION_BACHATA_TUTOR` and `QUESTION_BACHATA_DRILLS` (Phase 39) into [notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb), retire `QUESTION_DANCER` from the bachata flow, and produce a parallel six-mode-per-style demo flow that matches what the writeup already promises.

## Context / prior state

Phase 39 (commit `49c4222`) shipped the bachata coaching prompts and the `explain_all` verifier dispatch — six new tests, the structural drill verifier reused without modification. But the demo notebook still ran the old bachata flow:

- **kizomba in notebook 00** (six modes): rhythm_anatomy → describe_sections + timeline → listening_guide → song_arc → kizomba_tutor (one-pass + polished) → kizomba_drills (verified).
- **bachata in notebook 00** (four modes, asymmetric): rhythm_anatomy → describe_sections + timeline → listening_guide → song_arc → **dancer** (the generic 4-section narrative).

The asymmetry meant the writeup overstated what the demo showed. [docs/kaggle_writeup.md:54,56](../../docs/kaggle_writeup.md#L54-L56) lists "kizomba_tutor / bachata_tutor" and "kizomba_drills / bachata_drills" in the per-style flow, but a viewer running the notebook saw `dancer` instead. Phase 39b closes that gap.

User decisions (this phase):
- **Retire `QUESTION_DANCER`** from the bachata flow rather than keep it alongside. Mirror the kizomba structure exactly. The 4-section narrative is dropped — `listening_guide` already orients the learner, and the new `bachata_tutor` covers per-phase coaching.
- **No bachata polish pass** — Phase 39 didn't add `polish_bachata_tutor_output`, and the prompt is structurally simpler than kizomba's (count anchoring is honest in bachata, not forbidden). If live runs reveal recurring slips, polish becomes a Phase 40 candidate.

## Hypothesis

Bachata coaching parity in the demo is purely a notebook-wiring problem. The Phase 39 prompts are tested and the verifier is style-agnostic, so mirroring the kizomba section structure cell-for-cell on the bachata side, swapping `dancer` for `bachata_tutor` + `bachata_drills`, and updating the output dump should produce a clean parallel flow that the demo recording can showcase.

## What changed

All changes in [notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb); no source code, prompts, tests, or other docs touched.

- **`demo-imports`** — dropped `QUESTION_DANCER`; added `QUESTION_BACHATA_DRILLS` and `QUESTION_BACHATA_TUTOR`. Imports re-sorted alphabetically.
- **`demo-bachata-header`** — rewrote the "kizomba-specific tooling is bypassed" sentence. Now frames the bachata flow as **same six-mode shape as kizomba**, with **inverted honesty about the "1"** (bachata anchors on the count when `downbeat_confidence` supports it; kizomba forbids naming a downbeat). Calls out that the structural drills verifier is style-agnostic.
- **`demo-bachata-gemma` deleted; replaced with four cell pairs** mirroring the kizomba section structure:
  1. Listening guide (md `768b6a29` + code `d5d1381e`)
  2. Song arc (md `24543994` + code `8a36d33b`)
  3. Bachata tutor (md `1d640443` + code `5f986c51`) — markdown calls out the inverted-honesty stance and the no-polish decision.
  4. Bachata drills with verifier (md `8da8e7ae` + code `39ea9b87`) — markdown calls out that `verify_kizomba_drills_output` is style-agnostic and was reused for bachata in Phase 39 without modification. Code mirrors the kizomba drills cell exactly: raw → verified → cleaned → verifier stats line.
- **`demo-closing`** — added an "Inverted-honesty parity across styles" bullet and noted the no-polish-for-bachata decision in the polish bullet.
- **`1447fabb`** (output dump) — replaced the `bach_dancer` entry with four bachata entries (`bachata_tutor`, `bachata_drills (verified)`, verifier stats line, raw drills draft), in the same order the kizomba dump uses.

## Evidence / test results

**Tests (clean run after notebook edits):**
```
$ python -m pytest
================= 424 passed, 1 skipped, 64 warnings in 45.85s =================
```

Same baseline as before the edits (no source code changed in this phase). The test count discrepancy with Phase 39's doc (430 claimed) appears to be stale doc text — the actual collected suite is 424 + 1 skipped.

**Live run on Propuesta Indecente** (`google/gemma-4-26b-a4b-it`, captured in [notebooks/00_demo_outputs.md](../../notebooks/00_demo_outputs.md)):

- **DSP analysis context:** 123.0 BPM, 24 sections, 268s duration, **`downbeat_confidence=0.19` (low)**, `vocal_env=yes`. Every section was tagged `beat: moderate` — no `beat: clear` and no `beat: subtle` sections in this track. The Phase 38 vocal-aware labeller carved one `instrumental` sub-section (P9, 187–195s).

- **Bachata tutor:** 11 P# lines (P1–P11), every line substantive, no filler. Vocabulary lands as expected for a bachata tutor — "8-count", "basic", "hip action", "bongo pattern", "mambo footwork", "turns and combinations". Section-arc framing is clean: P1 intro, P2 break, P3–P5 main (establishing/sustaining), P6 build, P7 peak ("commit fully to high-energy combinations"), P8 main returning, P9 instrumental ("Maintain your internal 8-count through the medium energy" — Phase 38 `instrumental` label woven in naturally without prompt-side enumeration), P10 main, P11 outro.

- **Bachata drills (verified):** `parsed=7 repaired_ranges=1 duplicate_phases=0 filled_missing=2 skipped_lines=0 output_lines=9`. Gemma drafted `P8-P10: main (155s-254s)` as a single range, but P9 is `instrumental` (not `main`), so the verifier rejected the cross-label range and split it into separate P8 / P9 / P10 lines (`filled_missing=2` accounts for the new P9 and P10 lines populated from the original drill text). Style-agnostic verifier reuse confirmed end-to-end. Bachata-specific anchoring vocabulary present in drills: `1-2-3-tap, 5-6-7-tap basic`, `count 8 internally`, `re-enter on a fresh 1`, `finish on a clean 8`.

- **Output symmetry:** `00_demo_outputs.md` has parallel bachata and kizomba sections (rhythm_anatomy → describe_sections → listening_guide → song_arc → tutor → drills, with kizomba additionally showing the polish line). No `dancer` output anywhere.

## What worked / didn't / decision

**What worked:**
- **Notebook wiring is the entire change** — no prompt or verifier changes needed for live parity. Phase 39's tested foundation held.
- **Style-agnostic verifier proved out end-to-end on bachata.** First real cross-label range repair (`P8-P10: main` over a `main / instrumental / main` boundary) was caught and split correctly. `filled_missing=2` is verifier behavior reusing the original drill text for the new lines — functionally valid, slight cosmetic redundancy (P9 and P10 share drill text). Acceptable for the demo.
- **Phase 38 `instrumental` label woven in naturally.** Tutor P9 and drills P9 both reference the instrumental section without the prompt enumerating it. Architectural lesson from Phase 38 (the model is robust to new section vocabulary) holds for bachata coaching too.
- **No metric leaks, no fabricated section labels, no count over-anchoring.** Despite low `downbeat_confidence` (0.19), the tutor doesn't claim to anchor on the 1 — it gives generic basic coaching tied to bongo/percussion timing, which is the honest move at this confidence level.

**What didn't (or wasn't exercised):**
- **Honest-1 inverted-honesty stance not exercised on this track.** Every section came back `beat: moderate` and `downbeat_confidence=0.19`. To see the bachata tutor explicitly anchor on the 1 ("step on the 1", "land the basic on 1") we need a track with `beat: clear` sections AND high `downbeat_confidence`. To see the recovery vocabulary fallback we need `beat: subtle`. Propuesta Indecente exercises the *moderate-clarity / low-confidence* middle band well; the high and low ends are still untested in 00_demo's evidence. Bachata extended-set evidence (a future Phase 40b candidate) is where the inverted-honesty stance would get its full live test.
- **Verifier `filled_missing` produces near-duplicate drill lines.** P9 and P10 in the cleaned output share the same drill text ("stay compact and test the pulse with small steps"). Functionally correct; cosmetically a minor smell. Out of scope for 39b; could be a Phase 40 verifier-quality follow-up.

**Decision:** Ship Phase 39b. Notebook 00 now produces parallel coaching output for both styles, the writeup's "demo flow per style" claim matches what the notebook actually shows, and the verifier handled bachata's first real cross-label range cleanly. The honest-1 inverted-honesty stance remains untested at the high-confidence and subtle-clarity extremes — flag for Phase 40 (bachata extended-set evidence) but don't gate 39b on it.

## Next step

1. **Storyboard polish-pass beat decision** — answer the open question in [docs/demo_storyboard.md](../../docs/demo_storyboard.md) (whether to add a polish before/after clip in Act 3 at the cost of compressing song_arc or listening_guide). Now that bachata has parity, the storyboard could also add a short bachata coaching beat in Act 3 if there's a clean way to fit it.
2. **Recording prep** — pre-render notebook 00 outputs end-to-end with the new bachata flow, finalize storyboard, capture the 3-minute pitch screen recording.
3. **Phase 40 candidates** (post-recording, conditional):
   - **Bachata extended-set evidence.** Run `bachata_tutor` + `bachata_drills` against a broader bachata pool (a parallel to `notebooks/09_kizomba_extended.ipynb`, or just an extension of notebook 05). Targeted at a track with `beat: clear` + high `downbeat_confidence` (to exercise the count-anchor branch) and one with `beat: subtle` (to exercise the recovery-vocab fallback). The Propuesta run only exercised the moderate-clarity middle band.
   - **Verifier `filled_missing` cosmetic fix.** When the verifier splits a cross-label range into multiple lines, both new lines reuse the original drill text verbatim, producing near-duplicates (P9 / P10 in this run). A small refinement (e.g. flag the "split" lines in the output, or vary the drill text per label) would polish the output. Functionally not a blocker.
   - **Bachata polish pass.** Only if a future live run shows recurring slips. The Propuesta one-pass output was clean enough to ship; defer.
